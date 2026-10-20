"""Greece, the Theban Tribunal's western mainland, as of 1220: Epiros,
Macedonia and Thessaly, Attica and Boeotia, Euboea and the Morea, with
the lodge of Gigas south-west of Sofia; the covenants Epidauros, Erebos
and Hedyosmos (the Ionian phyle), Oikos tou Eleous (Aegean) and Gigas
(Propontian), and every living magus of theirs; Delphi and Pythia;
Celaenea's hidden laboratory on Mount Cyllene; the mainland's auras,
regiones and vis; and Epiros, the Kingdom of Thessaloniki, the Duchy of
Athens, the Principality of Achaea, Bulgaria, the Church and the towns,
in paraphrase of The Sundered Eagle chapter five (with chapter three for
the covenants' politics, and chapters nine to twelve where they add to
a site chapter five describes).

The ruined covenants of the mainland (Thumachia, Novocastrum, and
Dorostolon, whose site now lies in Transylvanian lands) are tribunal.py's,
put in the places here in its finish. The creatures (the Gorgona, the
Stymphalian birds, the koukouvaouns of Aetos, Delphi's sibyl) are the
Bestiary's and are only named in the places they haunt; the hedge
traditions, cults and leagues (the Daughters of Erictho, the Eleusinian
cult, the Paulicians, Kampe's Lovers, the League Against Idolatry) are
realms.py's. Keys: the region is places["greece"], its parts
places["epiros"], ["macedonia"], ["attica"], ["euboea"] and ["morea"];
Delphi is places["delphi"]; Celaenea's laboratory is
places["cyllene_laboratory"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.world import FULL
from ..builder import Builder, paragraphs, secrets
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Neighbour, Tribunal
    from . import Theban

BONISAGUS = "house_bonisagus"
CRIAMON = "house_criamon"
EX_MISC = "house_ex_miscellanea"
GUERNICUS = "house_guernicus"
JERBITON = "house_jerbiton"
TREMERE = "house_tremere"
TYTALUS = "house_tytalus"

#: The lead line of a covenant's notes, before its secrets.
STORYGUIDE = "What the players do not know."

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
    if tribunal is None:
        tribunal = next(iter(b.saga.tribunals), None)
    assert tribunal is not None, "tribunal.py builds the Tribunal first"
    _region(theban)
    _epiros(theban)
    _macedonia(theban)
    _attica(theban)
    _euboea(theban)
    _morea(theban)
    _epidauros(theban, b, tribunal)
    _erebos(theban, b, tribunal)
    _gigas(theban, b, tribunal)
    _hedyosmos(theban, b, tribunal)
    _oikos(theban, b, tribunal)
    _pythia(theban, b)
    _lords(theban, b)
    _churches(theban, b)
    _towns(theban, b)
    _factions(theban, b)


# ------------------------------------------------------------- the region


def _region(theban: Theban) -> None:
    _add(
        theban,
        "greece",
        "Greece",
        summary=paragraphs(
            "The Tribunal's western mainland, the Greece of legend: the "
            "country of the titans and the old gods, thick with ancient "
            "sanctuaries and ruins, where former gods, faeries and ghosts "
            "still keep to temples, woods and peaks. Its people are as "
            "pious as they are superstitious, and rightly wary of the "
            "nymphs, guardian spirits and restless dead abroad at night; "
            "the nereids, above all, are everywhere.",
            "Once the mind and soul of the ancient world, Greece faded "
            "under Christian Byzantium into a province overshadowed by "
            "Constantinople, raided by pagan Slavs and Christian Bulgars "
            "from the north and, in the last century, ravaged more than "
            "once by the Normans of Sicily. Since the Fourth Crusade it has "
            "broken into four main realms, all but Epiros ruled by Latin "
            "crusaders: the Principality of Epiros in the north-west, the "
            "Kingdom of Thessaloniki in the north-east, the Duchy of Athens "
            "and the Principality of Achaea in the Morea.",
            "Bulgaria lies to the north, the Adriatic and Ionian seas to "
            "the west and the Aegean to the east; gulfs and peninsulas "
            "stretch the coast to thousands of miles, and almost nowhere "
            "is more than fifty miles from the sea, so there are no great "
            "rivers. Inland it is mountain and forest with some plains; "
            "the coasts and plains grow grain and olives (the grain fed "
            "Constantinople until lately), and silk is the south's richest "
            "trade. The Via Egnatia, the Tribunal's chief road, crosses the "
            "north from Durazzo to Thessaloniki and on to Constantinople.",
            "Hermetically, the western mainland (Thessaly, Epiros and the "
            "Peloponnese) is the Ionian phyle, whose covenants are Erebos, "
            "Epidauros and Hedyosmos; Boeotia, Euboea and Macedonia belong "
            "to the Aegean phyle, with Oikos tou Eleous at Thessaloniki; "
            "and Gigas, far north beyond the mountains near Sofia, counts "
            "with the Propontian phyle. Delphi's oracle is kept for the "
            "Tribunal by a lone Criamon maga.",
            "Vis on the mainland (each in its place): Delphi's omphalos "
            "and eternal flame (Intellego and Creo, gathered for the "
            "Tribunal), the Stone Ship of Corfu (Rego, the Tribunal's), the "
            "Castalian Spring (Imaginem), the lightning mushrooms of "
            "Olympos (Creo), the Magnesian stones (Terram and Imaginem), "
            "the Rharian Field at Eleusis (Herbam), Marathon (Creo, and "
            "Perdo the Tribunal will not touch), the mountains of Euboea "
            "(Perdo), and, held by covenants, the Blood of Medusa and the "
            "theatre at Epidauros and the bats of Erebos.",
        ),
        **KNOWN_ORDER,
    )


# ---------------------------------------------------------------- Epiros


def _epiros(theban: Theban) -> None:
    region = theban.places["greece"]
    epiros = _add(
        theban,
        "epiros",
        "Epiros",
        inside=region,
        summary=paragraphs(
            "'The mainland', as against the Ionian isles: a broad, mostly "
            "mountainous country in the north-west of Greece, on the edge "
            "of the ancient Greek world and so poor in classical remains, "
            "though Durazzo and the Via Egnatia running east from it "
            "matter greatly. It is now the heart of the Principality of "
            "Epiros, the largest of the new realms, born of the Greek "
            "revolt against the Latins.",
            "The Pindos Mountains run down its eastern side, the spine of "
            "Greece from the north to the Gulf of Corinth: steep peaks, "
            "gorges, pine and beech woods and high pastures, home to "
            "superstitious Vlach herders, half nomadic, with some farmers, "
            "weavers and traders.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "bridge_of_arta",
        "The Bridge of Arta",
        inside=epiros,
        realm="Infernal",
        aura=2,
        summary=secrets(
            paragraphs(
                "A graceful bridge of pale stone on long slender arches "
                "over the Arachthos at Arta. For as long as anyone "
                "remembers, forty-five master masons and sixty apprentices "
                "built it by day and watched it fall into the river by "
                "night, until, after Michael Komnenos came, a great black "
                "raven told the chief mason to give up his lovely wife if "
                "he wanted it to stand and to escape his new lord's anger. "
                "He agreed and tried to trick the bird, and failed: his "
                "wife died walled into the footings, cursing that men "
                "would fall from the bridge as birds fall from the sky.",
                "The finished bridge has a treacherous Infernal aura of 2, "
                "and the raven still watches it. Whoever crosses gains +2 "
                "to Greedy (or Greedy +2) until the next day, and with "
                "merchants and townsfolk crossing all day, Arta's market "
                "has turned sordid and dishonest.",
            ),
            "The raven could perhaps be driven off, but the bridge might "
            "fall with it, and the ruler of Epiros would want to know who "
            "brought it down.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "stone_ship",
        "The Stone Ship of Corfu",
        inside=epiros,
        realm="Faerie",
        aura=2,
        summary=paragraphs(
            "Off Corfu's harbour stands a magnificent galley of dark "
            "granite: the Phaiakian ship King Alcinous gave Odysseus when "
            "the island was Scheria, unsinkable, sure in the thickest fog "
            "and steered by its captain's thought alone, until Poseidon "
            "turned it to stone to punish the Phaiakians. Its Faerie aura "
            "of 2 rises to 4 in the winter storm.",
            "Each winter a great storm rises on the eastern shore, the "
            "ship sails again, apparently crewed by Odysseus and his men, "
            "and an army of tritones (see Aegaea) comes with the breakers "
            "to take or sink it. Their tridents are Rego vis, a source the "
            "Tribunal counts as its own, but only for whoever can win them "
            "in that deadly fight, so volunteers for the service are few. "
            "Aegaea's magi, the obvious experts, say loyalty to their "
            "patron, a lord of the tritones, keeps them out of it; they "
            "seem to enjoy talking others into going, and give only "
            "riddling hints of how the sea army might be beaten.",
            "Seirenes of House Ex Miscellanea suggest a siren song could "
            "loose the ship from whatever holds it, as the sirens once "
            "tempted Odysseus.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "lake_ohrid",
        "Lake Ohrid",
        inside=epiros,
        summary=paragraphs(
            "The larger of the two great lakes among the northern "
            "mountains of Epiros, more than twenty miles long, its water "
            "deep, blue and perfectly clear; a Bjornaer passing through "
            "once said strange and magical fish of great beauty live in "
            "it. The Via Egnatia follows its north shore through Ohrid, "
            "the old Bulgarian capital. The shore settlements, the "
            "peaceful monastery of St Naum among them, lie in a strong "
            "Divine aura, but out in the middle of the lake a Magic aura "
            "holds sway, the home of a powerful genius loci (the book "
            "gives neither aura's strength).",
        ),
        **KNOWN_REGION,
    )
    prespa = _add(
        theban,
        "lake_prespa",
        "Lake Prespa",
        inside=epiros,
        realm="Faerie",
        summary=paragraphs(
            "A little south-east of Ohrid and higher in the mountains, a "
            "lake that drains into Ohrid by hidden channels underground. "
            "Hardly anyone lives there; it has a Faerie aura (of no stated "
            "strength) and many limniads, lake and marsh nereids, who are "
            "glimpsed dancing on the water in the morning mist, or "
            "bathing, and who lure travellers off the Via Egnatia a few "
            "miles away.",
            "A handful of these weak-willed men, most of them mute or "
            "simple, live with the limniads in a shabby village on the "
            "shore, where heaps of loot taken from bewitched merchants are "
            "hidden; their children by the limniads are mostly misshapen "
            "or foul-tempered.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "golem_grad",
        "Golem Grad",
        inside=prespa,
        realm="Divine",
        summary=(
            "Snake Island, a small island in Lake Prespa with a Divine "
            "aura (strength not given), lived on by devout folk and "
            "crawling with snakes. The limniads are afraid of the snakes "
            "and keep away."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "via_egnatia",
        "The Via Egnatia",
        inside=region,
        summary=paragraphs(
            "The Tribunal's most important road, laid by Gnaeus Egnatius, "
            "Roman consul of Macedonia: nearly seven hundred miles from "
            "Durazzo on the Adriatic, through the mountains of northern "
            "Epiros, through Thessaloniki, then along the north shores of "
            "the Aegean and the Sea of Marmara across Thrace to "
            "Constantinople, door to the Black Sea and Asia. Centuries of "
            "Byzantine repair keep most of it sound, though rain can cut "
            "it in the Epirote hills.",
            "The Sicilian armies came along it, and the Latin Empire and "
            "its vassals now lean on it for contact and trade with the "
            "West. With much of its western stretch in his hands, the "
            "ruler of Epiros could choke the Latin Empire whenever he "
            "chose; in 1217 he took the Latin emperor Peter of Courtenay "
            "on it.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        theban,
        "mount_pelister",
        "Mount Pelister",
        inside=epiros,
        summary=(
            "A green, pine-clad peak over eight thousand feet high, "
            "looming from the east over Monastiri, an ancient city a dozen "
            "miles east of the lakes. Its foot, by the River Dragor, is "
            "one of the places rumoured to hide the Basilica of Ten "
            "Thousand Columns, a great temple of Apollon once home to a "
            "cult of Hyperborean wizards."
        ),
        **RUMOURED,
    )
    _add(
        theban,
        "dodona",
        "Dodona",
        inside=epiros,
        aura=4,
        summary=paragraphs(
            "The oldest sanctuary in Greece, high in a valley on the west "
            "side of the Pindos, where Aristotle thought the Greeks first "
            "arose. Before the Olympians it was an oracle of the titaness "
            "Rhea, whose priestesses heard her answers in the rustle of "
            "the sacred oaks; Zeus took it over later, and King Pyrrhus "
            "built him a temple. A bishop felled the last oak in the fifth "
            "century. It is a deserted, timeless place of a few Roman "
            "ruins, chiefly a large amphitheatre; the grove has a Magic "
            "aura of 4.",
            "The Seekers of the Fallen think many secrets of the titans "
            "lie here, perhaps even a regio holding the way into the "
            "magical Garden of Eden. Some decades ago they replanted the "
            "grove's oaks, and they have restored an arch at its far side, "
            "against the mountain, between two rampant stone lions: they "
            "take it for a gate to a Magic regio, guarded by the lions, "
            "but cannot yet make it open.",
        ),
        **KNOWN_TRIBUNAL,
    )


# ----------------------------------------------- Macedonia and Thessaly


def _macedonia(theban: Theban) -> None:
    region = theban.places["greece"]
    macedonia = _add(
        theban,
        "macedonia",
        "Macedonia and Thessaly",
        inside=region,
        summary=paragraphs(
            "The north-eastern lands of Greece, between the Aegean and "
            "Bulgaria: Macedonia, Alexander's homeland, to the north-east, "
            "and the wide Thessalian plain to the south, parted by the "
            "Cambunian Mountains. The whole was the Kingdom of "
            "Thessaloniki, whose Greeks welcomed Boniface of Montferrat as "
            "a liberator in 1204; now most of Thessaly, Larissa with it, "
            "has fallen to Epiros, and the kingdom shrinks year by year.",
            "In Macedonia a man who has lived very wickedly may turn into "
            "a wild boar as he dies: a wilderness demon, a mazzik, has "
            "taken his corpse. The boar haunts his kin and neighbours for "
            "forty days, then goes off to the mountains to live wild.",
            "The Gorgona, Alexander's cursed half-sister Thessaloniki, "
            "roams the whole northern Aegean, most often near "
            "Thessaloniki's harbour (see the Bestiary). She asks sailors "
            "whether Alexander lives: to the answer that he lives and "
            "reigns she calms the sea with her lyre, but to the answer "
            "that he is dead she sinks the ship with a great wave. She is "
            "the two-tailed mermaid of the city's emblem.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "mount_athos",
        "Mount Athos",
        inside=macedonia,
        realm="Divine",
        aura=5,
        summary=paragraphs(
            "The Holy Mountain: a wooded headland of the Chalkidiki "
            "climbing to the peak of Athos, over six thousand feet above "
            "the sea, with monasteries clinging to its cliffs and slopes. "
            "God has warded it against anything female, beast or woman. "
            "The whole promontory has a Divine aura of 5; monasteries and "
            "cells often reach 7, altars 8, and some holy spots on the "
            "mountain itself 9.",
            "Monks have retreated here since the eighth century, and the "
            "first great house, the Great Lavra, opened in 955. They live "
            "as hermits in caves and cells, in lavrai that meet only for "
            "Sunday's service, or in koinobia under St Basil's Rule and an "
            "abbot. Gifts from Byzantine nobles wanting prayers for their "
            "souls and from pious common folk feed them, and boats and "
            "male pilgrims come constantly. See the Holy Community for its "
            "government.",
        ),
        **KNOWN_ORDER,
    )
    olympos = _add(
        theban,
        "olympos",
        "Mount Olympos",
        inside=macedonia,
        realm="Faerie",
        levels=[
            Builder.level(
                "The cloud regio",
                5,
                "Faerie",
                notes=(
                    "The Faerie regio that wraps the mountain, climbed by "
                    "following brief glimpses of the peak up into the "
                    "clouds. The book gives no aura for the lower levels."
                ),
            ),
            Builder.level(
                "The realm above the clouds",
                10,
                "Faerie",
                enter=(
                    "Through a great gate of cloud kept by the three Horae "
                    "(Spring, Summer and Winter); hard to pass, but some "
                    "magi have done it and come back."
                ),
                notes=(
                    "Possibly part of Elysium. Windless, cloudless and "
                    "blinding with sun on snow and crystal: the palaces of "
                    "the Olympians, Zeus's black-marble throne on its seven "
                    "rainbow steps, Hera's ivory one, the gods' court and "
                    "banquet hall, and their ambrosia and nectar, thought "
                    "a fabulous source of vis."
                ),
            ),
        ],
        summary=paragraphs(
            "The greatest mountain of Greece, at the east end of the "
            "Cambunians, home of the twelve Olympians in crystal palaces "
            "above the clouds. Storm cloud and lightning nearly always hide "
            "it; now and then the clouds part on a snow-capped summit "
            "impossibly high above. Local priests tell villagers to keep "
            "away.",
            "On the lower slopes, wild country of wolves and bears, a "
            "speckled mushroom grows exactly where Zeus's lightning struck "
            "the ground: food of the immortals, worth 2 pawns of Creo vis, "
            "and eaten it gives -3 to that year's Aging roll. Very few know "
            "the secret. Unclaimed.",
            "Climbing into the clouds leads through the Faerie regio that "
            "covers the mountain to the top level, a Faerie aura of 10. "
            "Magi who have got in came to watch the gods unseen, to match "
            "wits or magic with them, or simply because it is a strong "
            "place to study; Merinita magi come for Mystery initiations. "
            "Above the gate the summit palace of Zeus and Hera looks over "
            "the whole of Greece; to the north lie the kitchens, forges, "
            "armouries and servants' halls, and lower down the homes of "
            "lesser gods and the stables and menageries of celestial "
            "steeds and sacred beasts.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        theban,
        "forge_olympos",
        "The Forge of Hephaistos under Olympos",
        inside=olympos,
        realm="Faerie",
        aura=4,
        summary=(
            "One of the smith god's holiest forges, at the foot of "
            "Olympos: Hephaistos made every building and furnishing of the "
            "mountain and the gods' golden shoes that walk on water and "
            "air, and several legendary pieces of his work lie here. It is "
            "a cult site of House Verditius's Mysteries with a Faerie aura "
            "of 4, in the charge of the covenant of Ingasia; its only "
            "inhabitant now is Theorus the Old of Verditius."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "cambunian_mountains",
        "The Cambunian Mountains",
        inside=macedonia,
        summary=secrets(
            paragraphs(
                "The range between Macedonia and Thessaly, crowned by "
                "Olympos at its eastern end: the old homeland of the "
                "Witches of Thessaly. The covenant of Erebos lies in a "
                "long valley on its northern side.",
                "The Daughters of Erictho, the Witches of Thessaly who "
                "would not join the Order, hide among these mountains and "
                "are Erebos's enemies, clashing with it over ground and "
                "magical resources.",
            ),
            "Cyra, Erebos's patron, curses whoever comes into the valley "
            "meaning the covenant harm.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "larissa_spring",
        "The Spring of Larissa",
        inside=macedonia,
        summary=(
            "The spring whose kindly nymph gave Larissa its name. She is "
            "still glimpsed now and then and the townsfolk revere her as "
            "a saint; she and the horse of the Thessalian plain are the "
            "city's two old emblems. The book gives no aura."
        ),
        **KNOWN_LOCALLY,
    )
    meteora = _add(
        theban,
        "meteora",
        "Meteora",
        inside=macedonia,
        realm="Divine",
        aura=3,
        summary=secrets(
            paragraphs(
                "'Hanging in the heavens': a forest of huge sandstone "
                "pillars, some over a thousand feet tall, near the "
                "north-west edge of the Thessalian plain where the "
                "Salambria leaves the Pindos. On top, especially when mist "
                "fills the plain, one feels marooned on a little island "
                "near Heaven. The skete of Doupiani lives here, and most "
                "pillars have Divine auras from 3 to 6, each named for the "
                "mystic experience found on it (the Pillar of Dreams, of "
                "Solitude and so on).",
                "Giant Divine eagles nest among the pillars: a devout, "
                "humble hermit who falls may be caught and carried back up "
                "to his cave, or to a still more dangerous ledge, and they "
                "often bring scraps to starving hermits, though not to "
                "those fasting by choice.",
                "The tallest, Agio Pnevma, the Tower of the Holy Ghost, "
                "has the strongest aura, and its summit is thought a gate "
                "to Heaven; no mortal who reached it ever came back to "
                "say so.",
                "Several vis sources are believed to lie here, but magi "
                "rarely come. The last one tried to fly up the Agio "
                "Pnevma; his levitation failed, perhaps in punishment for "
                "his pride, and the vultures ate him.",
            ),
            "",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "pyrgos_diavolou",
        "Pyrgos Diavolou",
        inside=meteora,
        realm="Infernal",
        aura=4,
        summary=paragraphs(
            "The Tower of the Devil, the one unholy pillar of Meteora, "
            "with an Infernal aura of 4 and a colony of foul vultures "
            "that harry and attack anyone who climbs it.",
            "Some hermits climb it to stay as long as they can, as a "
            "test of faith, and it would serve as the ordeal of a Mystery "
            "initiation. For forty days and nights, Christ's time in the "
            "desert, the vultures torment the climber and three "
            "temptations come: stones the birds bring become fresh loaves, "
            "agonising poison if eaten; high up, a vulture urges him to "
            "leap, since the eagles save the devout, and he dies if he "
            "does; and at the summit an alluring vision of the Devil shows "
            "him all he longs for, granting an Infernal Blessing if he "
            "accepts.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "magnesia",
        "The Magnesian Coast",
        inside=macedonia,
        summary=paragraphs(
            "The south-east of Thessaly, known since antiquity for stones "
            "and minerals that alchemists and magi prize, above all the "
            "magnes in two kinds. The male magnes, some of them Terram vis, "
            "are dark lodestones that pull at iron (+7 to control iron, +3 "
            "divination); set one on a scrap of parchment, add a certain "
            "powder, and mystic symbols appear. The female, a little "
            "paler, are Imaginem vis and make glass perfectly clear when "
            "added to it (+3 purification, +2 invisibility). Unclaimed.",
        ),
        **KNOWN_TRIBUNAL,
    )
    pelion = _add(
        theban,
        "mount_pelion",
        "Mount Pelion",
        inside=macedonia,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "A hooked peninsula at Thessaly's south-eastern tip, six miles "
            "across and twenty long, with no human settlement: one "
            "overgrown, mountainous maze of oak and beech, choked with "
            "undergrowth and deadfall, under a Faerie aura of 3, and hard "
            "to find one's way through. Here Peleus wed the nymph Thetis, "
            "who bore Akhilles.",
            "It is the home of the centaurs, faeries as wild as stallions "
            "and as civil as men in equal parts, who challenge intruders to "
            "fierce, often deadly contests of fighting, hunting or racing, "
            "and celebrate with drunken feasts.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "cave_of_chiron",
        "The Cave of Chiron",
        inside=pelion,
        realm="Faerie",
        aura=3,
        summary=(
            "On Mount Pelion proper, the forest's highest point at the "
            "north of the peninsula, the cave of Chiron, first and wisest "
            "of the centaurs, unmatched in astrology and medicine and "
            "famed for his divinations; he taught Herakles, Asklepios, "
            "Akhilles, Theseus, Jason and many more. Seekers and Merinita "
            "magi have gone into Pelion to learn from him, and not all of "
            "them came back."
        ),
        **KNOWN_TRIBUNAL,
    )


# ------------------------------------------------- Attica and Boeotia


def _attica(theban: Theban) -> None:
    region = theban.places["greece"]
    attica = _add(
        theban,
        "attica",
        "Attica and Boeotia",
        inside=region,
        summary=paragraphs(
            "The heartland of ancient Greece: Boeotia, round Thebes, and "
            "south of it the peninsula of Attica, round Athens, bitter "
            "rivals of old, divided by the wooded limestone hills of "
            "Kithaeron, a much-fought border now scattered with faerie "
            "sites and the ruins of old forts. Both are the Duchy of "
            "Athens, under Otto de la Roche.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "kithaeron",
        "The Kithaeron Mountains",
        inside=attica,
        realm="Faerie",
        summary=paragraphs(
            "The hills between Boeotia and Attica, backdrop of many "
            "battles and legends, now dotted with faerie sites and ruined "
            "fortifications (no aura is given).",
            "When Kadmus founded Thebes he slew the dragon there and sowed "
            "its teeth as Athene told him; the Spartoi, the 'sown men', "
            "sprang up full-grown and armed, children of Ares. Most fought "
            "him, five helped him build his city, and when Athens finally "
            "beat Thebes their race withdrew to a forgotten spot in these "
            "hills, where they may yet remain.",
        ),
        **RUMOURED,
    )
    parnassos = _add(
        theban,
        "parnassos",
        "Mount Parnassos",
        inside=attica,
        summary=(
            "The sacred mountain west of the Boeotian plain, wooded and "
            "uninhabited, above Delphi's terraced sanctuary and the "
            "Castalian Spring."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "delphi",
        "Delphi",
        inside=parnassos,
        aura=7,
        summary=secrets(
            paragraphs(
                "The most famous oracle of the ancient world, once asked "
                "by kings, emperors, tyrants and philosophers about "
                "politics, war and religion, and famed for answers that "
                "came true, if often darkly put. It lies on a terraced "
                "plateau among crags below Parnassos: the Temple of "
                "Apollon at the centre of a small cluster of temples, "
                "ruins and an amphitheatre. The oracle itself has a Magic "
                "aura of 9, the rest of the sanctuary 7; the omphalos and "
                "its ties to the titans make Magic, not Faerie, the "
                "stronger here.",
                "It is in the keeping of the Tribunal and the Order. A "
                "lone Criamon maga lives here as the oracle under the old "
                "ceremonial name, Pythia, and in time picks her successor "
                "(often her filia), who after initiation into the "
                "oracle's Mysteries takes the name and role without "
                "announcement; so, though many magae have served, Pythia "
                "is thought of as one lasting being. Magi come to consult "
                "her before great ventures, the founding of a covenant or "
                "the taking of a patron, and often before important "
                "Tribunal decisions. How much of the future she sees, if "
                "any, is unclear, but her riddles nearly always prove wise "
                "in the end. Supplicants are received only from spring to "
                "autumn; they bring money or valuables, and larger gifts "
                "later if the prophecy bears fruit.",
                "The temple, which Pythia uses as her laboratory, is "
                "richly adorned with these gifts. In its secret inner room, "
                "the adyton, is the omphalos, the hollow egg-shaped navel "
                "stone carved with a woven net, said to mark the centre of "
                "the earth: the stone Rhea swaddled and gave Kronos to "
                "swallow in place of Zeus. Vapours rising from a small hole "
                "in it are Intellego vis, which Pythia breathes to "
                "prophesy; and an eternal flame burns in an inner hearth, "
                "a strong Creo vis source, any fire lit from it burning "
                "for ever without fuel. Pythia gathers both for the "
                "Tribunal, a common source of the polity, after taking "
                "what she needs.",
                "Herophile, the Delphic Sibyl, dwells in the same precinct "
                "but is not, and never was, the Pythia; she prophesies only "
                "for those of royal blood, however thin (see the Bestiary "
                "for a sibyl).",
            ),
            "The Absent Oracle: visitors may find only a young girl who "
            "says she is Pythia's apprentice, that her mistress is away, "
            "and repeats a last prophecy that seems to foretell both the "
            "disappearance and its rescuers. Whether Pythia has been "
            "taken or is being eccentric, the riddle must be solved to "
            "bring her back.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        theban,
        "castalian_spring",
        "The Castalian Spring",
        inside=parnassos,
        realm="Faerie",
        aura=4,
        summary=(
            "A pool at the foot of a great pair of cliffs on the lower "
            "slopes of Parnassos, its water and rocks dazzlingly bright, "
            "under a Faerie aura of 4. Those going up to the oracle wash "
            "their hair here and leave gifts of vis for Pythia in niches "
            "cut in the cliff. Their hair seems to soak up some of the "
            "light, and trimmed it yields Imaginem vis. Its old guardian "
            "was the she-serpent Python, Gaia's daughter, whom Apollon "
            "killed."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "palace_of_the_lamia",
        "The Palace of the Lamia",
        inside=attica,
        realm="Faerie",
        summary=secrets(
            paragraphs(
                "A shore of the Gulf of Corinth some miles south of "
                "Parnassos, where a lamia (see the Bestiary) rises from the "
                "sea whenever a young man pipes on the beach, and promises "
                "him an easy, delightful life at her side. If he refuses she "
                "tears him apart; if he accepts she drags him under and "
                "drowns him.",
            ),
            "Sometimes the man is instead carried to her palace beneath "
            "the waves and given that life, and she teaches him many "
            "secrets she has gathered: a perilous way to study, with "
            "great rewards. Many lamiae can initiate Mystery Virtues.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "eleusis",
        "Eleusis",
        inside=attica,
        aura=4,
        summary=paragraphs(
            "The sanctuary of the Eleusinian Mysteries, fourteen miles "
            "north-west of Athens, where Demeter found her daughter Kore "
            "again and made peace with her fate; King Keleus was among "
            "the first initiates. The site has a Magic aura of 4, rising "
            "to 6 in the great forty-two-columned telesterion.",
            "Each year initiates walk the Sacred Way from Athens through "
            "the Forest of Daphni, drink the kykeon at nightfall, and meet "
            "Hekate as a three-handed crone with dagger, golden key and "
            "rope; she gives the chosen, the epoptai, a password to the "
            "inner rite, and tells the mystai to wait a year. The Lesser "
            "Mystery each March grants Self-Confident; the Greater, every "
            "fifth August, may grant Death Prophecy (the cult itself is "
            "described with the realms).",
            "The rite ends with an all-night feast and bull sacrifice in "
            "the Rharian Field, where grain first grew: a potent source "
            "of Herbam vis.",
        ),
        **RUMOURED,
    )
    _add(
        theban,
        "marathon",
        "The Tumulus of Marathon",
        inside=attica,
        aura=3,
        summary=secrets(
            paragraphs(
                "On a small plain in eastern Attica in sight of the "
                "Aegean, a big grassy cone, Magic aura 3, over the 192 "
                "Athenians who fell beating the Persians; an old stone "
                "before it bears Simonides's verse.",
                "Every September, on the anniversary, the ghost of the "
                "herald Pheidippides runs the 26 miles to Athens and looks "
                "up at the Acropolis. If Greeks rule there he cries "
                "victory and dies again, leaving his sandals, each with 3 "
                "pawns of Creo vis. If barbarians hold it he turns away "
                "silent and fades, and the next nightfall the 192 wake and "
                "fight their way across Attica, attacking anything in their "
                "path, to storm the Acropolis after a few days.",
                "That is Otto de la Roche's problem: the local Greeks will "
                "not fight their own dead, he must hold the city with "
                "several hundred crusaders and mercenaries, and as an "
                "excommunicate he can expect no help from Heaven. The "
                "beaten ghosts leave weapons and gear holding Perdo vis, "
                "which the Tribunal has so far declined to gather rather "
                "than profit from a Greek defeat, even a symbolic one.",
            ),
            "The Perdo vis vanishes soon after the battle, and no one "
            "knows who or what is collecting it.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "column_haralambos",
        "The Column of St Haralambos",
        inside=attica,
        realm="Divine",
        summary=(
            "A lone column on the road from Athens to Piraeus, raised some "
            "generations ago by forty women. They bought a cart and calves "
            "and a silver vessel, wrote on it the name of every disease "
            "the townsfolk could catch, buried the lot, and set the column "
            "over it in honour of St Haralambos, guardian against plague. "
            "Athens has had no epidemic since. The book gives no aura."
        ),
        **KNOWN_LOCALLY,
    )


# ------------------------------------------------------------- Euboea


def _euboea(theban: Theban) -> None:
    region = theban.places["greece"]
    euboea = _add(
        theban,
        "euboea",
        "Euboea",
        inside=region,
        summary=paragraphs(
            "A long, narrow island shaped like a seahorse, nearly a "
            "hundred miles from north-west to south-east, the Tribunal's "
            "second largest after Candia, joined to the mainland only by "
            "the bridge at Chalkis. It is dry, so farming is poor, but "
            "rich in marble. Its Aegean coast is rocky and harbourless, "
            "notorious for storms and wicked currents; much of the Persian "
            "fleet was wrecked there before Salamis.",
            "William the Bad of Sicily landed ten thousand men from 164 "
            "ships in 1157 and sacked every coastal town; the island never "
            "recovered and is now thinly peopled. Since the Fourth Crusade "
            "it is the Lordship of Negroponte (see the Islands), the "
            "Veronese Triarchy's baronies, now split in six under Venetian "
            "bailiffs. Aegaea lies on the sea floor off its coast.",
            "Byzantine scholars comparing Homer, Ovid and Apollodorus with "
            "the Old Testament hold that Herakles was Samson, and his "
            "Labors trials the Devil set him; so places of his virtue tend "
            "to be Divine, and those of his foes and Labors Infernal.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "euripus",
        "The Euripus Strait",
        inside=euboea,
        summary=(
            "The narrows at Chalkis, halfway down the Euboic Sea, little "
            "more than a hundred feet wide and crossed by a wooden "
            "drawbridge. Its fierce tides change direction many times a "
            "day, often without warning; Aristotle tried to explain them, "
            "failed, and threw himself in. The genius loci of the Euboic "
            "Sea lives in the strait and dreads its being filled in, "
            "cutting its sea in two, so it keeps the tides violent to deter "
            "mortals. The folk of Chalkis used to keep the bridge up and "
            "sail no ships through, to soothe it; the island's new Latin "
            "lords are far less careful."
        ),
        **KNOWN_LOCALLY,
    )
    mountains = _add(
        theban,
        "euboea_mountains",
        "The Mountains of Euboea",
        inside=euboea,
        summary=(
            "Zeus and Hera were married here, and the marriage went so "
            "badly that the honour turned to a curse: Hera in a rage "
            "wrecked the wedding place with an earthquake that tore Euboea "
            "from the mainland and broke its mountain chain into three "
            "clumps. Earth spirits war among them, there are several "
            "sources of Perdo vis, and earthquakes are still frequent. "
            "Unclaimed."
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "aetos",
        "Aetos",
        inside=mountains,
        realm="Faerie",
        summary=(
            "A peak near Karystos with a village on each side, Kastania "
            "to the east and Neohori to the west, each guarded by a "
            "koukouvaoun (a stoicheion; see the Bestiary): Kastania's a "
            "cow, Neohori's a golden-horned ox. When the villages quarrel "
            "their spirits fight. At the last quarrel Kastania's was "
            "pushed over a cliff and buried by a rockslide, and ever since "
            "the village has suffered tremors as it struggles to get out, "
            "its luck has turned and its crops have failed."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "baths_of_herakles",
        "The Baths of Herakles",
        inside=euboea,
        realm="Divine",
        aura=4,
        summary=(
            "A hot spring near the north coast, on the slopes of Mount "
            "Gaetsades (over four thousand feet), where sulphurous water "
            "pours over yellowed rock straight into the sea: one of the "
            "places Herakles rested, the healing water springing up to "
            "refresh him. Divine aura 4; it cures gout and rheumatism, and "
            "medicinal herbs grow on the slopes about it."
        ),
        **KNOWN_LOCALLY,
    )


# -------------------------------------------------------------- the Morea


def _morea(theban: Theban) -> None:
    region = theban.places["greece"]
    morea = _add(
        theban,
        "morea",
        "The Morea",
        inside=region,
        summary=paragraphs(
            "The Peloponnese, the southern peninsula of Greece, tied to "
            "Attica only by the Isthmus of Corinth, and named for its many "
            "moreai, the mulberry trees whose leaves feed the silkworms: "
            "a fertile land of silk. It is the Principality of Achaea, "
            "twelve small Frankish baronies under Geoffrey II de "
            "Villehardouin.",
            "Herakles worked several Labors here: the Nemean Lion at "
            "Nemea between Lake Stymphalia and Corinth, the Hydra at the "
            "little Lake Lerna in the south-east, the Erymanthian Boar on "
            "Mount Erymanthos in the north, the Augean stables in Elis to "
            "the west, and the Stymphalian Birds. Copying a Labor is a "
            "favourite Gauntlet for Theban apprentices of House Flambeau.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "isthmus",
        "The Isthmus of Corinth",
        inside=morea,
        summary=paragraphs(
            "The rocky neck joining the Morea to Attica, four miles wide "
            "at its narrowest, with the Examilion, a six-mile Byzantine "
            "wall of the sixth century, just north of it. Ships once "
            "crossed it too, triremes hauled by slaves along a paved "
            "track, the Diolkos, now a disused ruin; goods are carried "
            "across between Corinth's two ports instead.",
            "Roman emperors dreamt of a canal, and Nero began one with six "
            "thousand slaves and spades; it died with him. Centuries later "
            "the aptly named Severus of House Guernicus took up the idea "
            "and made real progress with ritual Perdo Terram before he was "
            "Marched. His great cut is still there.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "angistri",
        "Angistri",
        inside=morea,
        summary=(
            "A little island of the Saronic Gulf some twenty miles "
            "south-east of the Isthmus, plagued by a hen the size of a "
            "cow that raids the crops with its huge brood and fouls the "
            "fields with its giant droppings. A witch cast out of the main "
            "village took her revenge by sowing magic grain; a hen ate it "
            "and grew monstrous."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "lake_stymphalia",
        "Lake Stymphalia",
        inside=morea,
        realm="Infernal",
        aura=4,
        summary=(
            "The Morea's largest lake, twenty miles west of Corinth, ringed "
            "and hidden by thick dark forest, with an Infernal aura of 4 "
            "and the dreadful stink of black, poisoned water. Herakles "
            "drove off the Stymphalian Birds here with Hephaistos's bronze "
            "clappers and his arrows, but long after they came back (see "
            "the Bestiary), and they have plagued the fields and villages "
            "round about ever since: black birds big enough to carry off a "
            "small man and fierce enough to kill and eat a grown one, with "
            "brass feathers whose spiked tips they shoot, and a metallic "
            "shriek. Their coming is a dire omen."
        ),
        **KNOWN_REGION,
    )
    arcadia = _add(
        theban,
        "arcadia",
        "Arcadia",
        inside=morea,
        realm="Faerie",
        summary=paragraphs(
            "The mountainous heart of the Morea, a thinly peopled forest "
            "wilderness, and also a Faerie realm, the realm of new "
            "stories and adventures; whichever was named for the other, "
            "the higher one climbs in the one, the nearer one comes to the "
            "other. Thresholds and guardians of every kind are scattered "
            "through it, on peaks, in groves and caves or met on any path, "
            "making it one of the easiest ways into the realm, and Merinita "
            "magi from all over the Tribunal and beyond love it. A lost "
            "traveller or magus stumbling out of the Arcadian wilds with no "
            "idea where he is is not a rare sight.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        theban,
        "vizie",
        "Vizie",
        inside=arcadia,
        summary=(
            "A village in the southern foothills of Arcadia, not far from "
            "Sparta, of dog-headed cynocephali who farm and keep sheep. "
            "Their neighbours steal their grain and goats, so they must go "
            "to war to survive, and the peasants round about call them "
            "man-eating monsters; peace between the two seems unlikely. If "
            "they were baptised and prayed to St Christopher, himself born "
            "dog-headed, they would lose their canine looks."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "cyllene_laboratory",
        "Celaenea's Laboratory on Mount Cyllene",
        inside=arcadia,
        summary=secrets(
            paragraphs(
                "Mount Cyllene in the north of Arcadia, where Hermes is "
                "said to have been born. Celaenea of Bonisagus, a Seeker "
                "of Hedyosmos obsessed with the god's legends, keeps a "
                "secret laboratory here, sure that by divining the nature "
                "of Hermes she can reach the very roots of magic. The book "
                "gives no aura.",
            ),
            "Proximios means to tell her that Lucian of Aegaea hopes to "
            "raise the forgotten gods, trusting her love of Hermes to turn "
            "her against him and his league.",
        ),
        **RUMOURED,
    )
    zakynthos = _add(
        theban,
        "zakynthos",
        "Zakynthos",
        inside=morea,
        realm="Faerie",
        summary=paragraphs(
            "An island twenty miles long in the Ionian Sea west of the "
            "Morea, nominally Venice's, and one of the strangest and most "
            "superstitious in Greece: faeries and the faerie-blooded "
            "abound, and so do Gifted children, so that magi of the Ionian "
            "phyle come regularly to look for them. Hardly a native lacks "
            "some faerie blood or a small supernatural knack.",
            "Nereids are commoner here than anywhere; whole villages have "
            "married them, some of those villages have vanished for years "
            "at a time, and nereid blood here makes children fair and "
            "families famous for beauty. The drakoi of Zakynthos have one "
            "fiery eye and often uncanny sight; their mortal children are "
            "ugly, dim, huge or strong, and a drakos father hunting a "
            "husband for his graceless daughter is an old joke. Few houses "
            "are built, since a passer-by may leave his shadow in the new "
            "foundations, and it becomes a pergalio: a black-skinned, "
            "blue-eyed faerie child that wanders harmlessly and goes away "
            "in time if its help is accepted, but turns jealous and "
            "spiteful if refused.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "nereid_queen",
        "The Mountain of the Queen of the Nereids",
        inside=zakynthos,
        realm="Faerie",
        aura=6,
        summary=(
            "The highest peak at the heart of Zakynthos, Faerie aura 6, "
            "home of the nereids and their queen, the Great Lady or "
            "Mistress of Earth and Sea: largest, wisest and strongest of "
            "them, beautiful in a white gown and golden belt, often seen "
            "dancing among her nereids in the brooks and pools or before "
            "her plain palace. A man struck with her belt goes mute, weak "
            "or simple. She takes children away to live with her for many "
            "years, though she treats them well. She is mysterious but "
            "high-minded, and one may bargain with her for fair dealing or "
            "justice."
        ),
        **KNOWN_REGION,
    )


# ---------------------------------------------------------------- Epidauros


def _epidauros(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    morea = theban.places["morea"]
    site = _add(
        theban,
        "epidauros_sanctuary",
        "The Sanctuary of Epidauros",
        inside=morea,
        aura=5,
        summary=paragraphs(
            "The old asklepieion on a quiet hillside near the shore of "
            "the north-east Morea, in Achaea: a small huddle of ancient "
            "Greek buildings in every state of repair, under a Magic aura "
            "of 5, where the magi have their sancta. Its heart is the Hall "
            "of Repose (the Enkoimeteria), a great shared hall like a "
            "hospital where the gravest or most important patients are "
            "laid, and which is in Hermetic terms a laboratory specialised "
            "in healing and longevity, though it does not look like one.",
            "The other buildings stand empty and crumbling, one of the "
            "outermost holding a leper colony. In the hillside is a great "
            "theatre unused since Roman times, its acoustics so perfect "
            "that the faintest sound on stage carries to the back row; "
            "Imaginem vis can be gathered there. Below lies a small town, "
            "where the covenfolk live among the townsfolk; its church "
            "gives it a Divine aura too weak to trouble the sanctuary.",
        ),
        **KNOWN_ORDER,
    )
    summary = paragraphs(
        "A small, venerable covenant of the Ionian phyle, in the ancient "
        "healing sanctuary of Asklepios, renowned for its service to the "
        "Tribunal: it heals the sick and keeps magi young, and many of the "
        "Tribunal's magi live under a Longevity Ritual made by one of its "
        "specialists. Most of the Tribunal-funded Longevity Rituals are "
        "made here, the recipient sleeping in the Hall of Repose, and "
        "magi of other Tribunals come seeking its help too.",
        "The asklepieion goes back to the fourth century BC, built on the "
        "god's supposed birthplace by a cult of pharmakeutria, physician "
        "magi, who tended the throngs of pilgrims; the Goths sacked it at "
        "the end of the fourth century AD and it lay empty until wizards "
        "of the Theban League revived it before the Order was founded. "
        "Magi have been there ever since, apart from a spell of Tremere "
        "usurpers in the ninth century who were driven out at the "
        "Sundering; since then its record has been long, honourable and "
        "quiet.",
        "It has only three or four magi, all experts in Corpus, healing or "
        "longevity, led by its eldest, Xenias the Leper. Each spends a "
        "season a year as a physician at the sanctuary and usually another "
        "making a Longevity Ritual, so it draws only selfless magi not "
        "wrapped up in their own studies. Local people know to come when "
        "they are sick, and are usually treated, and the place keeps a "
        "little of its ancient fame among mortals.",
        "Its servants and few soldiers were all healed or saved by the "
        "magi and have sworn their lives to its service: lepers, outcasts "
        "and reformed criminals, many of whom came as a last hope and have "
        "nowhere else to go, most with some disability from punishment or "
        "injury (tongues cut out, limbs lost, blinded or castrated).",
    )
    what_matters = _lines(
        "Vis: the Blood of Medusa, 16 pawns of extraordinary Corpus vis a year, kept in a basin atop a carved stele by the statue of Asklepios in the Hall of Repose",
        "Vis: Imaginem from the ancient theatre",
        "Vis: a small stipend from the Tribunal for healing magi",
        "Laboratory: the Hall of Repose, shared, specialised in healing and longevity; Tribunal-funded Longevity Rituals are made there",
        "Library: an unrivalled collection on Medicine and outstanding books on Creo and Corpus",
        "Boon: Powerful Ally (Asklepios, the covenant's patron)",
        "Boon: Aura (Magic 5); Prestige (healers of the Tribunal); Loyal Covenfolk",
        "Hook: Hermetic Services (a season of healing and a Longevity Ritual from each magus a year)",
        "Hook: Distorted Covenfolk (maimed, leprous and outcast servants)",
        "Tension: prejudice against lepers keeps many magi from Xenias, and magic cannot cure leprosy",
        "Tension: healing the Prince of Achaea or his kin would be meddling with mundanes, and refusing would make enemies",
    )
    notes = paragraphs(
        "The Blood of Medusa. Athene gave Asklepios the blood of the "
        "gorgon's right vein, which heals, as that of her left vein kills. "
        "Drunk in quantity (a whole year's 16 pawns, so almost never "
        "allowed) it drops Incapacitating Wounds at once to Heavy, makes "
        "every later Recovery roll for current wounds succeed, and cures "
        "any disease or ailment; legend says it can even raise the dead, "
        "though magi say that has not been done for over a century. A dose "
        "of 4 pawns used in making a Longevity Ritual gives +12 to the Lab "
        "Total, and drunk it works a Chirurgeon's Healing Touch on the "
        "drinker.",
        "Patron: Asklepios, chief Greek god of medicine, a Magic spirit "
        "bound to the sanctuary, who is willing to be its patron because "
        "the magi honour the place and keep it to its purpose. He has no "
        "body and does not speak, but is felt most at the end of the Hall "
        "of Repose, by his statue. Sleepers in the Hall, the sick "
        "above all, often have visions of him guiding them to a cure; they "
        "gain +12 to their next Wound Recovery roll, and +6 to the Lab "
        "Total of a Longevity Ritual made for them there.",
        "Healing in the Theban way: the healer pays the vis and earns a "
        "token, the healed returns half; magi needing magical healing most "
        "often come here. Any magus may make a Longevity Ritual for the "
        "Tribunal for a token or two, and these are traditionally made at "
        "Epidauros.",
        "The book gives no founding year (only before the Order's "
        "founding) and no season. Two magi are unnamed.",
        secrets(
            STORYGUIDE,
            _lines(
                "Healing the Realm: Geoffrey II of Achaea, in whose land the covenant lies, falls gravely ill, and his wife Agnes begs the magi for a cure. Refuse, and if he dies they make an enemy of her and leave a war of succession; heal him, and a rival accuses him of dealing with pagan sorcerers. Either way the covenant could be charged with interfering with mundanes.",
                "Magi of Epidauros wonder whether the nectar and ambrosia Tantalus is said to have stolen could improve Longevity Rituals.",
            ),
        ),
    )
    epidauros = b.covenant(
        "Epidauros",
        tribunal=tribunal,
        founded=None,
        place=site,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        unnamed_magi=2,
        detail=FULL,
        season="Summer",
    )
    theban.covenants["epidauros"] = epidauros
    b.book(
        epidauros,
        "The library of Epidauros",
        "Other",
        language="Classical Greek",
        description=(
            "No books are named. Narrow by design: the finest collection "
            "on Medicine anywhere, with outstanding books on Creo and "
            "Corpus, and little beyond its healing work."
        ),
    )
    m = theban.magi
    m["xenias"] = b.magus(
        "Xenias the Leper",
        covenant=epidauros,
        house=TYTALUS,
        age=165,
        summary=paragraphs(
            "Epidauros's leader in name, simply as its eldest, looking a "
            "hundred and seven: a magus aegrotus, a leper magus, like all "
            "his kind among the Tytalus deeply gifted for healing and "
            "longevity, and probably the Tribunal's greatest expert in "
            "both. He seems a scruffy old man in a ragged leper's robe, a "
            "linen veil over his face and gloves to the elbow hiding how "
            "old and shrivelled he is, and a bell on his robes clanks "
            "constantly to warn of his disease.",
            "Though heavily marked by Twilight he is easy enough to "
            "approach, if anyone does: the prejudice against lepers is not "
            "only a mundane one, and no magic cures leprosy.",
        ),
        traits={"Dutiful": 3, "Calm": 3, "Driven": 2},
    )
    m["galla"] = b.magus(
        "Galla",
        covenant=epidauros,
        house=EX_MISC,
        age=78,
        summary=paragraphs(
            "An herbalist of the Pharmacopoiean tradition, looking "
            "fifty-two: a Root-Cutter, she can lower the vis cost of "
            "healing rituals, a great help to her covenant. Lame and "
            "silver-haired in a plain grey shawl, she walks awkwardly with "
            "her talisman staff, and her snake familiar noses out herbs in "
            "the hills. She is usually the one who deals with visitors.",
        ),
        traits={"Careworn": 3, "Earthy": 2, "Venomous": 1},
    )


# ------------------------------------------------------------------ Erebos


def _erebos(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    mountains = theban.places["cambunian_mountains"]
    valley = _add(
        theban,
        "erebos_valley",
        "The Valley of Erebos",
        inside=mountains,
        aura=2,
        summary=secrets(
            paragraphs(
                "A long, mostly empty valley on the north side of the "
                "Cambunian Mountains at the edge of Thessaly, home of the "
                "covenant of Erebos. There is no common building: the "
                "magi's sancta are strung along several miles of it with "
                "no plan, most in hillside and cliff caves, a few in "
                "cottages or tree houses. The valley's Magic aura is mostly "
                "2, with other auras in a few spots.",
                "Nearby is a bat-haunted cave complex, once a sanctuary "
                "of a chthonic cult of Hecate. The magi harvest Perdo vis "
                "from its bats, but have not gone in because of the "
                "cultists' traps.",
            ),
            "Cyra, the patron, curses anyone entering the valley with ill "
            "intent towards Erebos.",
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "An old but little-known covenant of the Ionian phyle, all of "
        "House Ex Miscellanea, sworn to preserve the Tribunal's native "
        "traditions of magic; its magi share a valley in the Cambunian "
        "Mountains but keep apart from each other and from the wider "
        "Tribunal, and it is among the most secretive covenants of all.",
        "In the later ninth century, soon after the Sundering, Ex "
        "Miscellanea came to the Tribunal, among them a filius of Pralix "
        "sent to deal with the troublesome Witches of Thessaly. A few of "
        "the witches, led by the maga Cyra, were won over and joined the "
        "Order; Cyra would not move, so she founded a covenant in her "
        "tradition's homeland to shelter all the native Greek traditions "
        "Tremere had threatened, and named it Erebos, another name for "
        "Hades meaning blackness or shadow. Since then new magi from Greek "
        "traditions have drifted there expecting a welcome; most found it "
        "cool, and stayed anyway.",
        "Counted by heads it is among the biggest covenants in the "
        "Tribunal, close to a dozen magi: Witches of Thessaly, members of the Cult of Orpheus, "
        "Pharmacopoieans, and one or more Slavic magi who say they were "
        "hounded out of the Transylvanian Tribunal. Traditions with "
        "several members meet among themselves, but there is no council "
        "and no council chamber. The leader is always a Witch of "
        "Thessaly of Cyra's line, who handles practical matters, sharing "
        "out books and vis, and is often called on to settle the petty "
        "quarrels that flare between traditions; the current one is "
        "young Destasia, with her mater Megethia still there but lost in "
        "ever longer Twilights.",
        "Erebos has no covenfolk as such: most magi keep their own "
        "servants, guards and retainers, and some none. The autocrat, who "
        "holds the covenant's slender purse and stores, answers to "
        "Destasia alone, which gives her real power.",
        "The Tribunal thinks poorly of it, for its secrecy, the unwillingness "
        "of some members to volunteer services, and the sinister air of the "
        "witches who lead it. House Tremere calls it little better than a "
        "devil-worshippers' nest, and Erebos and Gigas, to its north, "
        "loathe each other.",
    )
    what_matters = _lines(
        "Vis: Perdo from the bats of Hecate's cave near the valley",
        "Library: no books named; the leader shares out the books and vis",
        "Boon: Local Ally (Cyra, the covenant's patron)",
        "Boon: Hedge Tradition (the native traditions it shelters)",
        "Hook: Fractured Council (no council; magi of rival traditions quarrel)",
        "Hook: Infamous (secretive, reluctant to serve, led by witches)",
        "Hook: Rival (the Daughters of Erictho in the mountains; the Tremere of Gigas)",
        "Tension: the autocrat, loyal only to Destasia, controls the purse",
        "Tension: young magi of Erebos are among those the League of the Vigilant may be steered to accuse",
    )
    notes = paragraphs(
        "Patron: Cyra, the founder, who passed into Final Twilight only a "
        "couple of decades after founding it but did not wholly vanish. "
        "She comes back now and then as a cryptic guide and guardian of "
        "her followers, who have taken her as their patron spirit, most "
        "often as her old familiar, a great white owl with bright red eyes "
        "much like the koukouvaouna, a guardian spirit of northern Greece; "
        "otherwise as a gaunt woman with glowing red eyes, in a black "
        "shawl, gripping an obsidian staff enchanted for destruction.",
        "The book gives no founding year (the later ninth century) and no "
        "season. Nine magi are unnamed.",
        secrets(
            STORYGUIDE,
            _lines(
                "Cyra is most likely a Magic spirit, but given the dark magic of the Witches of Thessaly she might be Infernal.",
                "Proximios, through the League of the Vigilant, means to set demon-hunters on the young magi of Erebos as supposed diabolists.",
            ),
        ),
    )
    erebos = b.covenant(
        "Erebos",
        tribunal=tribunal,
        founded=None,
        place=valley,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        unnamed_magi=9,
        detail=FULL,
        season="Summer",
    )
    theban.covenants["erebos"] = erebos
    b.book(
        erebos,
        "The books of Erebos",
        "Other",
        language="Classical Greek",
        description=(
            "No books are named. Each magus keeps his own, mostly in the "
            "lore of his own native tradition, and the leader shares out "
            "what the covenant holds in common."
        ),
    )
    m = theban.magi
    m["destasia"] = b.magus(
        "Destasia",
        covenant=erebos,
        house=EX_MISC,
        age=43,
        summary=paragraphs(
            "A Witch of Thessaly descended from Cyra, looking thirty-seven, "
            "who has lately inherited the rule of Erebos young. She knows "
            "the magic of defixiones, curse tablets, and specialises "
            "accordingly in Perdo and Corpus. Elegant, athletic and "
            "black-haired, she would be handsome but for the ritual scars "
            "across her face, thought to come from a Mystery ordeal.",
        ),
        traits={"Overbearing": 2, "Vengeful": 2, "Moody": 1},
    )
    m["megethia"] = b.magus(
        "Megethia",
        covenant=erebos,
        house=EX_MISC,
        age=None,
        summary=(
            "Destasia's mater, a Witch of Thessaly and the former leader of "
            "Erebos, still at the covenant but more and more absent in "
            "long episodes of Twilight. The book gives only her name."
        ),
    )
    b.link(m["megethia"], "characters", m["destasia"], "Her filia and successor")


# ------------------------------------------------------------------- Gigas


def _gigas(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    region = theban.places["greece"]
    lodge = _add(
        theban,
        "gigas_lodge",
        "The Hunting Lodge of Gigas",
        inside=region,
        aura=1,
        summary=(
            "A hunting lodge in a small patch of forest at the very "
            "northern end of a rich, fertile valley south-west of Sofia, in "
            "Bulgarian lands: the most northerly Theban covenant. To draw "
            "no notice in this crowded country the lodge is kept small and "
            "the magi's sancta are mostly underground. The wood has a weak "
            "Magic aura (the book gives no number; 1 here)."
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "House Tremere's chief holding in the Tribunal, of the Propontian "
        "phyle, set up to remind Thebes of Tremere's strength just to the "
        "north. It is often at odds with the rest of the Tribunal, yet its "
        "distance from the other covenants makes it a neutral ground for "
        "peace treaties and pacts of goodwill and non-aggression. It is no "
        "covenant's vassal, but it answers to Coeris, the Tremere domus "
        "magna in Transylvania, across the Tribunal border, and reports "
        "there all the news the usual channels miss.",
        "It was founded in 1023 as a place where magi and favoured "
        "companions wounded in the Schism War could recover. The Tribunal "
        "distrusted it from the start, and more so after 1069, when it "
        "admitted only Tremere. Its six members are mostly Boustaphan's "
        "Hermetic descendants; it has room for nine, hosts Tremere from "
        "abroad, and gives support and even temporary membership to any "
        "Tremere moving to the Tribunal.",
        "Several members loudly condemn Theban customs as the Order's "
        "magic debased by 'vulgar paganism' and want the Tribunal brought "
        "back into line with the rest of the Order: they champion Latin "
        "over Greek, seek precedents to add to the Peripheral Code, and "
        "review as many laws as they can when drawn to the Legislative "
        "Board. They claim a small win in the permanent logothete of 1186, "
        "which they did not propose but campaigned for. Its leader is "
        "said to have remarked that even the Roman Republic fell to a "
        "tyrant, which, if true, hints at what the House would do should "
        "the slow road fail. With Oikos tou Eleous it makes up the League "
        "Against Idolatry.",
    )
    what_matters = _lines(
        "Library: no books named; records Boustaphan will not open to outsiders",
        "Boon: Hidden Resources (underground sancta under a modest lodge)",
        "Hook: Superiors (Coeris, the Tremere domus magna)",
        "Hook: House Covenant (Tremere only since 1069)",
        "Hook: Hermetic Politics (its campaign to normalise the Tribunal)",
        "Tension: feud with Erebos, which it thinks a nest of diabolists",
        "Tension: Hedyosmos, which it suspects of the Sundering; Tremere are not welcome there",
        "Tension: the Tremere appeal to the Grand Tribunal of 1228 to retry the League of Advisors",
    )
    notes = paragraphs(
        "Patron in name only: Gigas has never accepted that a covenant "
        "needs a patron spirit, which smacks of idolatry to it, and in "
        "protest names its leader's familiar as its official patron. "
        "Čovek is a silver wolf of a line that has given familiars to many "
        "great Tremere, every leader of Gigas among them; to be chosen by "
        "one is an honour. It counts as no Boon.",
        "The book gives no season. Three magi are unnamed. A Tremere who "
        "comes to Gigas from another Tribunal, as a guest or a temporary "
        "member, is a metoikos until the Assembly grants a decree of "
        "citizenship; the book names none of them, so the register lists "
        "only Boustaphan, Monorchis and Allectores, all politai.",
        secrets(
            STORYGUIDE,
            _lines(
                "Proximios hopes to convince Aiakia that Gigas's Tremere brought about the fall of Constantinople and plan to strike at her covenant, and Tisiphon that they have escaped justice; Boustaphan would never open Gigas's records to clear them.",
            ),
        ),
    )
    gigas = b.covenant(
        "Gigas",
        tribunal=tribunal,
        founded=1023,
        place=lodge,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        unnamed_magi=3,
        detail=FULL,
        season="Summer",
    )
    theban.covenants["gigas"] = gigas
    b.book(
        gigas,
        "The library of Gigas",
        "Other",
        language="Latin",
        description=(
            "No books are named. The covenant keeps its records of the "
            "Tremere in Thebes and its reports for Coeris, which "
            "Boustaphan opens to no outsider."
        ),
    )
    m = theban.magi
    m["boustaphan"] = b.magus(
        "Boustaphan",
        covenant=gigas,
        house=TREMERE,
        age=114,
        summary=paragraphs(
            "Leader of Gigas and senior Tremere of the Tribunal, one of "
            "the few of his House to hold his own sigil, looking a robust "
            "sixty-four. As his House's Tribune in Thebes he uses the "
            "proxy votes the young Tremere give him to reform the Tribunal "
            "as Coeris directs; he keeps carefully above the quarrels his "
            "covenant and House pick with Theban custom, though he almost "
            "surely backs most of them.",
            "He dresses as a minor noble and is often out hunting with a "
            "hawk on his wrist; the locals take him for an exile from "
            "fallen Constantinople. His silver wolf Čovek is the "
            "covenant's patron in name. He seeks immortality through his "
            "line and has trained apprentice after apprentice since he "
            "could Open the Arts, gladly taking at the Apprentice "
            "Presentation the children no one else wants, and giving them "
            "a place in the service of his House.",
        ),
        traits={"Level-Headed": 2, "Wolf": 2, "Close-Mouthed": 1, "Jovial": -1},
    )
    m["monorchis"] = b.magus(
        "Monorchis",
        covenant=gigas,
        house=TREMERE,
        age=58,
        summary=paragraphs(
            "Looks forty-two. His parents had him made a eunuch to help "
            "him to a fine career in the palace bureaucracy; his Gift "
            "awoke quickly enough for him to stop the surgery before it "
            "was finished. Boustaphan, who kept spies in the imperial "
            "palace, found him and brought him to Gigas to train.",
            "Perhaps because he so nearly became a man of ink and "
            "parchment, he is fiercely anti-intellectual: he will not "
            "read, studies the Arts mostly from vis, and holds that the "
            "Order has lost its intuitive bond with magic to the written "
            "word, dry logic and endless philosophy. He has made friends "
            "in House Criamon and, rumour says, in some esoteric Mystery "
            "Cults. His Form is Ignem, which he treats as a search for the "
            "light of the soul.",
        ),
        traits={"Stubborn": 3, "Zealous": 3, "Mystical": 1},
    )
    m["allectores"] = b.magus(
        "Allectores",
        covenant=gigas,
        house=TREMERE,
        age=46,
        summary=paragraphs(
            "Gigas's chief negotiator and envoy, and the easiest of its "
            "magi to talk to, looking thirty-three. His role may seem at "
            "odds with a martial House, but the Tremere know diplomacy "
            "matters as much as readiness for war, and value him; he plays "
            "up his seeming misfit in the House's ranks to win sympathy "
            "from those he deals with. He is said to carry a faerie "
            "blessing that makes everyone he meets think well of him.",
        ),
        traits={"Reasonable": 3, "Silver-Tongued": 3, "Calm": 1},
    )
    b.link(
        m["boustaphan"],
        "characters",
        m["monorchis"],
        "Found him and brought him to Gigas to train",
    )


# --------------------------------------------------------------- Hedyosmos


def _hedyosmos(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    morea = theban.places["morea"]
    caves = _add(
        theban,
        "hedyosmos_caves",
        "The Nekyomanteion of Mount Minthe",
        inside=morea,
        levels=[
            Builder.level(
                "The labyrinth",
                0,
                notes=(
                    "Beneath the covenant's levels, a maze of passages and "
                    "caverns whose Magic aura is aligned with Terram and "
                    "grows stronger the further in one goes (the book "
                    "gives no numbers). Somewhere in it a way into the "
                    "Magic Realm is thought to open, onto the Underworld "
                    "prison of the titans; Minthe guards a gate into "
                    "Tartaros. The covenant warns people off, but uses "
                    "some chambers for its cult."
                ),
            )
        ],
        summary=paragraphs(
            "The ruins of a nekyomanteion, a shrine of the dead, on the "
            "slopes of Mount Minthe in Elis; in antiquity a temple of "
            "Hades, one of his few cult centres, for only the Eleans were "
            "known to worship him. Below it lies the covenant of "
            "Hedyosmos, wholly underground: winding caves joined by "
            "twisting passages, each cavern with several entrances, easy "
            "to get lost in. Each magus has a cave or several as a "
            "sanctum, always shut by a door, and a sanctum mark glows "
            "silver for a moment at the touch of anyone with Magic "
            "Resistance, so no one trespasses by mistake. The book gives "
            "no strength for the Magic aura, which is aligned with Terram "
            "and deepens below.",
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "A covenant of the Ionian phyle shared by House Guernicus and "
        "House Tytalus, an alliance some think sinister, and earning "
        "its grim name: by every account it squats over a door to the "
        "Underworld, and its magi are masters of stygian magic, of earth, "
        "the dead and malice. Yet it has always stood firmly for the "
        "Hermetic polity; some doubt its motives, none its loyalty.",
        "It is among the oldest covenants of the Tribunal: wizards lived "
        "there for at least a century before the Order. Three founders of "
        "the Theban League came from it, the youngest of them taught the "
        "Art by Guernicus in person; already given to venerating "
        "chthonic spirits, it embraced Guernicus's revived Terrae Cult and "
        "became one of its chief seats. Its Guernici and Tytalan "
        "theurgists are widely believed to have been central to the "
        "Sundering of Tremere in 848, and had both the motive and the "
        "skill. It shrugged off the Corruption of Tytalus and the Schism "
        "War alike, and mundane wars and Hermetic upheavals since. "
        "Tremere magi are not welcome.",
        "No light or speech is allowed in the common areas: magi and "
        "companions may light and talk in their own caves as long as "
        "nothing leaks into the passages or shared chambers. Even the "
        "kitchens are dark, all food cooked outside or bought in the "
        "nearby village and kept warm with hot stones in covered baskets, "
        "and in places old enchantments make light or sound impossible. "
        "Everyone talks in a sign language pressed with the fingers into "
        "the listener's palm, and Hedyosmos Lore is needed not to get lost.",
        "Its magi often advise the Judicial and Legislative Boards, and "
        "always vote for whatever does least harm. Anyone needing a skilled "
        "debater for a decree can usually hire one for the neutralisation "
        "of one of the debater's shards, though they refuse causes they "
        "think bad for the polity; and its magic is as easy to get. "
        "Aiakia, the archon, knows several rituals, Conjuring the Mystic "
        "Tower among them, and casts them for others for the ritual's vis "
        "and the neutralisation of a shard, hers or a sodalis's.",
        "Covenfolk work mostly in the dark: most are fluent in the sign "
        "language, valued servants have enchantments to see, and all the "
        "grogs are trained to fight foes they cannot see, so that the "
        "polemarch sometimes borrows them for Marches against magi given "
        "to invisibility. Several have the Dowsing Virtue, often born of "
        "the strongly aligned aura in those born there, and through them "
        "the covenant has found seams of gold, silver and gems that make "
        "it fabulously rich, all worked through intermediaries to avoid "
        "any charge of meddling.",
    )
    what_matters = _lines(
        "Income: hidden mines of gold, silver and gemstones found by dowsing covenfolk, worked through intermediaries",
        "Library: Ausculator's works on Terram, and the covenant's records of the time of the Sundering",
        "Mysteries: Initiation Scripts of the threskeia geine for Divination and Augury (Geomancy), Summoning (of Terram-aligned Magic beings), Dowsing, Puissant Terram, Silent Magic and Spirit Familiar",
        "Services: debaters for decrees, and Aiakia's rituals, each for the neutralisation of a shard",
        "Boon: Powerful Ally (Minthe, the covenant's patron)",
        "Boon: Wealth; Vast and Labyrinthine; Veteran Fighters (grogs who fight blind)",
        "Hook: Uncontrolled Portal (the gate to Tartaros in the labyrinth)",
        "Hook: Infamous (stygian magic and dark rumours)",
        "Hook: Rival (House Tremere, which wants its records of the Sundering)",
        "Tension: its Terrae Cult is the heart of Kampe's Lovers, who would loosen Hades's hold on the titans",
    )
    notes = paragraphs(
        "The Cult of the Earth. Guernicus was the last of a cult of the "
        "earth's mysteries and refounded it in his last years among some "
        "apprentices; it has since taken in magi of other Houses but is "
        "always led by a Guernicus. In Greece, as the threskeia geine "
        "(the cultus terrae elsewhere), it has taken over the old "
        "functions of Hades, the chief Underworld god, without "
        "worshipping him. All eight magi of Hedyosmos belong. Its "
        "Summoning is a variant that calls any Magic being aligned to "
        "Terram (spirits, magical beasts, elementals made de novo by "
        "scouring) and is not Infernal. Its ordeals usually leave a "
        "Restriction (feet on bare earth), Afflicted Tongue by mutilation, "
        "Deficient Auram or No Sense of Direction.",
        "Patron: Minthe, a Magic Daimon, once Hades's lover: when he took "
        "Persephone she boasted he would come back to her and drive the "
        "girl from his halls, and Demeter trod her into dust, from which "
        "grew mint, Hades's sacred herb. She guards one of the entrances "
        "to the Underworld, thought a way into the Magic Realm, and for "
        "centuries the covenant has venerated her rather than Hades. Being "
        "set over a gate into Tartaros, where the titans lie, she is "
        "central to its hopes.",
        "Rumours, mostly spread by Tremere: that Tremere's chief "
        "lieutenants were imprisoned and questioned here in the Sundering "
        "and the knowledge used for the rituals that broke the House, some "
        "of their ghosts still captive; that the Tremere dead sent through "
        "the Gate of Eurydice at Coeris come out, bodies or spirits, in "
        "the labyrinth; and that its wealth comes from turning human "
        "bones into gold.",
        "Porphyrion of Tytalus left ten years ago for Rome, where he is "
        "said to have found the Jar of Pandora, and then for Normandy. "
        "The book gives no founding year (before the Order) and no "
        "season. Three magi are unnamed.",
        secrets(
            STORYGUIDE,
            _lines(
                "Kampe's Lovers, centred on Hedyosmos's cult, mean to weaken Hades's power over the titans' prison and set them free to bring a golden age of magic; this is the Theban cult's aim, not the Terrae Cult's at large.",
                "Ausculator's mater vanished; he says she will not return, and most think she went into the lower labyrinth and never came out.",
                "Vrakos the cook, beneath the magi's notice, has been won over by Askalaphos, the faerie tattletale of Hades whom Demeter cursed into a screech owl. He has become a priest of Hades, holds secret rites in the depths and quietly recruits among the servants; for now he asks only offerings of milk, honey and a black ram's blood.",
                "The Estate of Hades: Askalaphos means in time to make the covenant a temple of Hades again and rid it of the magi; the Aegis of the Hearth stands in his way, and he wonders how to get himself invited into the ritual.",
                "Proximios hopes to turn Aiakia and Tisiphon against Gigas, and Celaenea against Lucian of Aegaea.",
            ),
        ),
    )
    hedyosmos = b.covenant(
        "Hedyosmos",
        tribunal=tribunal,
        founded=None,
        place=caves,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        unnamed_magi=3,
        detail=FULL,
        season="Summer",
    )
    theban.covenants["hedyosmos"] = hedyosmos
    b.book(
        hedyosmos,
        "The works of Ausculator on Terram",
        "Other",
        art="Terram",
        language="Classical Greek",
        author="Ausculator of Guernicus",
        description=(
            "Ausculator's books on Terram, famous across the Order and "
            "dear for their exceptional quality; a genuine copy is known "
            "by the glitter of mica dust worked into the parchment. The "
            "book gives no titles, levels or Qualities."
        ),
    )
    b.book(
        hedyosmos,
        "The records of the Sundering",
        "Other",
        language="Classical Greek",
        description=(
            "Hedyosmos's records of the years of the Sundering. House "
            "Tremere officially cares nothing for its details, but many of "
            "its magi would dearly like to read them."
        ),
    )
    m = theban.magi
    m["ausculator"] = b.magus(
        "Ausculator",
        covenant=hedyosmos,
        house=GUERNICUS,
        age=162,
        summary=paragraphs(
            "'The Listener', leader of Hedyosmos since his mater left the "
            "post fifty years ago, and head of the Terrae Cult in the "
            "Tribunal, looking eighty-eight; a remarkable Longevity Ritual "
            "keeps his body sound. Statuesque, snow-haired, he is wholly "
            "blind, his eyes white without iris or pupil, and often paints "
            "eyes on his lids as on a marble statue; his skin is cool and "
            "he wears a plain tunic with an embroidered hem. He moves as "
            "little as he can and can freeze so still that strangers take "
            "him for a statue, standing for hours or days; that he does so "
            "more and more makes some think Twilight is swallowing him. "
            "His familiar is an imago, a spirit of sound, bound through "
            "the Mystery of the Spirit Familiar.",
            "He is reckoned the Tribunal's greatest master of Terram, and "
            "his books are famous far afield. His mater has vanished from "
            "the Tribunal; he says she will not come back, but not whether "
            "she died or passed into Final Twilight.",
        ),
        traits={"Patient": 6, "Discreet": 3, "Stubborn": 2},
    )
    m["aiakia"] = b.magus(
        "Aiakia",
        covenant=hedyosmos,
        house=GUERNICUS,
        age=61,
        summary=paragraphs(
            "The archon of the Tribunal, elected by the archai in 1214, "
            "looking fifty-three. Ausculator's youngest filia, she is being "
            "groomed to succeed him when Twilight finally takes him: not "
            "the cult's most powerful member, but the one who knows its "
            "rituals best. Her speciality is caves and underground ways; "
            "she has explored many cave systems in the Tribunal and beyond "
            "and brought back secrets she only half understands. She also "
            "has a remarkable mastery of earth elementals, and casts "
            "rituals such as Conjuring the Mystic Tower for others at the "
            "price of the vis and a shard's neutralisation.",
        ),
        traits={"Loyal": 2, "Touchy": 2, "Friendly": -2},
    )
    m["tisiphon"] = b.magus(
        "Tisiphon",
        covenant=hedyosmos,
        house=TYTALUS,
        age=70,
        summary=paragraphs(
            "A Quaesitor with a misguided sense of honour, looking "
            "fifty-one, and a member of the Titanoi, the Tytalan Mystery "
            "Cult; he is the most prominent of Kampe's Lovers. He takes up "
            "cases where a magus seems to have escaped the Order's justice, "
            "and tries to set them right by fierce speeches at Tribunal, "
            "by petition after petition to the Legislative Board, and, "
            "failing all else, by Wizard's War. His spirit familiar is an "
            "Aspect of the Erinyes, the threefold Daimons of vengeance. The "
            "Titanoi leave him little time for the Terrae Cult, of which he "
            "is a member in name only.",
        ),
        traits={"Vengeful": 3, "Champion of Others' Woe": 2, "Dependable": -1},
    )
    m["celaenea"] = b.magus(
        "Celaenea",
        covenant=hedyosmos,
        house=BONISAGUS,
        age=48,
        summary=paragraphs(
            "A Seeker of the direct line of Lucian Triamonae, who founded "
            "the Seekers, which she thinks should win her the respect of "
            "her peers (it does not), looking forty-four. She is obsessed "
            "with the legends of Hermes, keeps a hidden laboratory on Mount "
            "Cyllene where the god was supposedly born, and believes that "
            "divining his nature will lay bare the roots of magic itself.",
        ),
        traits={"Proud": 3, "Idealistic": 1, "Calm": -2},
    )
    m["polydegmon"] = b.magus(
        "Polydegmon",
        covenant=hedyosmos,
        house=TYTALUS,
        age=None,
        summary=(
            "The best known of the Tribunal's 'Stygian' magi, who study "
            "binding magic, an art commonly thought suspect and perhaps "
            "Infernal because the Goetic Arts lead the field. He practises "
            "a non-Hermetic tradition of binding, unique in the Tribunal "
            "until he trains an apprentice. Chapter nine names him; the "
            "book gives no House or age (Tytalus, among the covenant's "
            "Tytalan theurgists, is assumed here)."
        ),
    )
    b.link(m["ausculator"], "characters", m["aiakia"], "His youngest filia and heir")
    b.link(
        m["celaenea"],
        "places",
        theban.places["cyllene_laboratory"],
        "Her hidden laboratory",
    )


# --------------------------------------------------------- Oikos tou Eleous


def _oikos(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    macedonia = theban.places["macedonia"]
    convent = _add(
        theban,
        "koukoubiou",
        "The Convent of Koukoubiou",
        inside=macedonia,
        realm="Divine",
        aura=2,
        summary=paragraphs(
            "A tiny convent inside Thessaloniki's walls, in a walled villa "
            "with a small orchard and a lovely flower garden, kept by "
            "Sisters Anna and Theocharista Psellus with six nuns loyal to "
            "them. Their private chapel, Divine aura 4, is their "
            "laboratory, their prayers and chant the focus of their magic; "
            "elsewhere in the villa the aura is 2, and in the walled gardens "
            "1.",
            "The Seirene twins live in the royal palace with only four "
            "slaves, using a room of their apartment as a cramped "
            "laboratory, and are looking for something better, not least "
            "because they quarrel.",
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "The House of Mercy, one of the last Jerbiton covenants in the "
        "Tribunal, of the Aegean phyle, in Thessaloniki, and known as the "
        "Ladies of Thessaloniki for its four magae. It is no single place "
        "but an alliance of magae bound, somewhat like a lavra, by a "
        "typikon (charter) to defend one another and to restore the "
        "city's health of body and soul. All four are holy magae, under "
        "vows of poverty, chastity and obedience and a heavy round of "
        "devotions; holy magae of three traditions, they have little use "
        "for vis, books or lab texts and hold few common resources, quite "
        "unlike most covenants.",
        "Two holy magae founded it after the Sicilian sack of 1185, when "
        "five thousand citizens died, holy places were deliberately "
        "desecrated and a strong Infernal aura rose over the ruined "
        "streets. They soon found a wide diabolist ring tied to the "
        "Paulician heresy and set about fighting it and the demonic "
        "corruption of the citizens, and still preach and dispute against "
        "the Paulicians who live lawfully within the walls, whose evil few "
        "suspect, so that most take the nuns for bigots. The Infernal "
        "auras have much faded, but the fight for the city's soul goes on.",
        "They worked to heal the wounded in body and spirit, and when "
        "Constantinople fell their example showed what could be done for "
        "a broken city. Even so, three of the magi, the men, took the "
        "signs for the end of days and left for Rome, believing they were "
        "needed there; only the sisters stayed. In 1207 they called on "
        "St Demetrios against the besieging Bulgarian tsar, and "
        "are sure the tsar died that October by the saint's own hand. The "
        "same year twins of the Seirene tradition came from Lesbos and "
        "at once drew the covenant into court affairs through their quiet "
        "support of Queen Margaret of Hungary, whose son Demetrios was "
        "already a great favourite of the nuns.",
        "It is devoted to the protection of King Demetrios, the veneration "
        "of his namesake saint, and the survival of Thessaloniki, "
        "capital since 1205 of a kingdom attacked by Bulgarians and "
        "Epirotes and torn by the quarrel over the boy king's regency and "
        "William of Montferrat's claim; a siege seems likely within a "
        "year unless the new Latin emperor steps in. With Gigas it makes "
        "up the League Against Idolatry, which wants the Ceremony of "
        "Propitiation banned.",
    )
    what_matters = _lines(
        "Laboratory: the chapel of Koukoubiou (Divine aura 4), and the twins' cramped room in the royal palace",
        "Resources: very few in common; the nuns live on their own wealth",
        "Boon: Powerful Ally (Saint Demetrios, the covenant's patron)",
        "Boon: Urban (Thessaloniki); Informants (the royal court through the twins)",
        "Hook: Mundane Politics (the boy king, the regency and the Montferrat claim)",
        "Hook: War Zone (Epiros closes in; a siege is expected within a year)",
        "Hook: Heretics (the Paulicians within the walls)",
        "Tension: the twins argue with each other and want better laboratories",
        "Tension: Nonna would oppose any man joining the covenant",
        "Tension: the League Against Idolatry's petition against the Propitiation divides the Tribunal",
    )
    notes = paragraphs(
        "Patron: St Demetrios, martyred Roman soldier and patron of "
        "Thessaloniki (see the Hagios Demetrios).",
        "Covenfolk: none as such, and no grogs; the magae and their own "
        "people do whatever is needed. Anna runs the convent as mother "
        "superior, and her six novices are mostly widows of the recent "
        "wars. One, the cantankerous, sullen Gemma, has been there since "
        "1185 and knows the sisters are far older than they look; she puts "
        "it down to God's grace, while loudly complaining of the "
        "unfairness. The nuns do their own housework, with one hired man, "
        "John the gardener.",
        "Founded 1185. The book gives no season.",
    )
    oikos = b.covenant(
        "Oikos tou Eleous",
        tribunal=tribunal,
        founded=1185,
        place=convent,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        aura=4,
        realm="Divine",
        detail=FULL,
        season="Summer",
    )
    theban.covenants["oikos_tou_eleous"] = oikos
    b.book(
        oikos,
        "The books of the Ladies of Thessaloniki",
        "Other",
        language="Greek",
        description=(
            "No books are named, and as holy magae the sisters need few. "
            "Theocharista's own reading in Neo-Platonic philosophy and the "
            "Cappadocian Fathers on the Trinity is the nearest thing to a "
            "library."
        ),
    )
    m = theban.magi
    m["anna"] = b.magus(
        "Anna Psellus",
        covenant=oikos,
        house=JERBITON,
        age=112,
        summary=paragraphs(
            "Mother Anna, looking sixty-two, spiritual head of Koukoubiou, "
            "a small retreat of the kind Byzantine ladies found when they "
            "would rather not enter a great convent; she and her sister "
            "founded it straight after the sack of 1185 and laboured to "
            "rebuild the city and heal its wounds, the spiritual ones "
            "above all. Strong-willed and clear of purpose, having seen at "
            "first hand what sin and the Infernal do, she rules her nuns "
            "with an iron hand, thinks herself a soldier of the spirit, and "
            "has no patience with stupidity, cowardice or compromise.",
            "When she must she can be civil, even play the meek servant, "
            "while skewering her betters with a dry wit inherited from "
            "her grandfather, a celebrated scholar and courtier. She serves "
            "the city and God only, and some say in that order.",
        ),
        traits={"Pious": 6, "Devoted to Thessaloniki": 3, "Brash": 1},
    )
    m["theocharista"] = b.magus(
        "Theocharista Psellus",
        covenant=oikos,
        house=JERBITON,
        age=109,
        summary=(
            "Anna's younger sister, looking sixty-three, who has always "
            "lived in her shadow: as kind and self-effacing as Anna is bold, "
            "but strong in her own quiet way. A brilliant scholar of "
            "Neo-Platonic philosophy with a deep grasp of theology, above "
            "all the Cappadocian Fathers on the Holy Trinity, she holds the "
            "covenant together with her patient, loving calm."
        ),
        traits={"Peacemaker": 3, "Humble": 2, "Scholarly": 2},
    )
    m["nereida"] = b.magus(
        "Nereida",
        covenant=oikos,
        house=EX_MISC,
        age=31,
        summary=(
            "Nonna's twin, a Seirene, looking twenty-two. Her music works "
            "on courage, but a Restriction stops her ever using it on a "
            "man she is drawn to, a real trouble for one so romantic. She "
            "waits on the queen's household at court. She has kept a "
            "Longevity Ritual since just after her Gauntlet to keep her "
            "looks, a vanity the other magae think sinful."
        ),
        traits={"Fearless": 6, "Romantic": 3, "Vain": 2},
    )
    m["nonna"] = b.magus(
        "Nonna",
        covenant=oikos,
        house=EX_MISC,
        age=31,
        summary=(
            "Nereida's twin and her opposite in all but looks, which are "
            "nearly identical but for their apparent ages (Nonna looks her "
            "age), to much confusion at court. Men do not interest her at "
            "all. A close friend of Queen Margaret of Hungary, now living "
            "in Athens, she is fond of King Demetrios but would rather have "
            "seen Margaret rule. She has just come back from years at "
            "Empress Yolanda's court in Constantinople, and her drive to "
            "empower women and barely hidden scorn for men's failings may "
            "set her against her sister and the others; she would fight "
            "any man's admission to the covenant."
        ),
        traits={"Courageous": 3, "Nurturing": 2, "Assertive": 1},
    )
    b.link(m["anna"], "characters", m["theocharista"], "Her younger sister")
    b.link(m["nereida"], "characters", m["nonna"], "Her twin sister")


# ------------------------------------------------------------------ Pythia


def _pythia(theban: Theban, b: Builder) -> None:
    theban.magi["pythia"] = b.magus(
        "Pythia",
        covenant=None,
        house=CRIAMON,
        age=None,
        summary=secrets(
            paragraphs(
                "The oracle of Delphi: a lone Criamon maga living in the "
                "Temple of Apollon, which is her laboratory, under the "
                "ancient oracle's ceremonial name. Each Pythia chooses her "
                "successor, often her filia, who takes the name after "
                "initiation into the oracle's Mysteries without telling "
                "anyone, so Pythia is treated as one enduring person. Magi "
                "consult her before founding a covenant, adopting a patron "
                "or a great Tribunal decision; she breathes the omphalos's "
                "vapours to prophesy and gathers Delphi's Intellego and "
                "Creo vis for the Tribunal after taking her own share. She "
                "sees supplicants only between spring and autumn.",
                "The book gives no age; her present self is not described.",
            ),
            "In the Absent Oracle a girl claiming to be her apprentice "
            "meets visitors with the news that Pythia is gone.",
        ),
    )
    b.link(
        theban.magi["pythia"],
        "places",
        theban.places["delphi"],
        "Her temple and oracle",
    )


# ------------------------------------------------------------------ lords


def _lords(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    w["epiros"] = b.lord(
        "Principality of Epiros",
        title="duke",
        wealth="Wealthy",
        seat="Arta",
        ruler="Theodore Komnenos Doukas",
        place=p["epiros"],
        summary=secrets(
            paragraphs(
                "The largest of the new realms of Greece, born of the Greek "
                "revolt against the Latins. Its founder, Michael Komnenos "
                "Doukas, cousin of the emperors Isaac II and Alexios III, "
                "served the Latins in the Morea until William de "
                "Champlitte crushed him at the Olive Grove (Koundouros) "
                "in 1205; he fell back to Arta and built a realm there, "
                "savage and faithless, changing Church and allies at will. "
                "He struck at Thessaloniki with Venice in 1210, betraying "
                "his son-in-law the infant king, was excommunicated for "
                "crucifying three Latin priests, had to bow to Emperor "
                "Henry, then from 1213 seized the Adriatic and Ionian coast "
                "from Venice, Corfu and Durazzo among it. In 1215 a "
                "servant driven past bearing by his cruelty stabbed him, "
                "and nobody mourned.",
                "His half-brother Theodore, who fled to Nicaea in 1204 and "
                "came over to Epiros in 1210, succeeded him, the bastard "
                "son having fled. Theodore is as ruthless and grasping: he "
                "has taken Ohrid and Pelagonia from the Bulgarians and most "
                "of Thessaly, captured the Latin emperor Peter of Courtenay "
                "on the Via Egnatia in 1217 (presumed dead, many of his men "
                "murdered or dead in prison), and with a strong army of "
                "Frankish mercenaries is closing on Thessaloniki. He has "
                "not yet called himself emperor, but Constantinople's "
                "throne is plainly his goal, and he holds the western Via "
                "Egnatia, by which he could strangle the Latin Empire. "
                "The book calls him both Theodore Dukas and Theodore "
                "Komnenos.",
            ),
            "Arta's new castle has an Infernal aura from Michael's "
            "depravities, guarded by a flock of sinister ravens.",
        ),
    )
    w["thessaloniki_kingdom"] = b.lord(
        "Kingdom of Thessaloniki",
        title="duke",
        wealth="Wealthy",
        seat="Thessaloniki",
        ruler="King Demetrios of Montferrat",
        place=p["macedonia"],
        summary=paragraphs(
            "Founded by Boniface of Montferrat, who, passed over for the "
            "Latin throne, marched on Thessaloniki in 1204 and was hailed "
            "as a liberator from bad emperors across Macedonia and "
            "Thessaly; his brother Renier's marriage to Maria Komnenos "
            "gave him a lawful claim, and his own to Margaret of Hungary, "
            "Isaac II's widow, made it firmer. When he died in 1207 his "
            "heir was their two-year-old son Demetrios, named for the "
            "city's saint, beloved of the great Greek families for his "
            "Angelos mother; he was crowned at four in 1209 and is now "
            "fifteen.",
            "Margaret's regency was popular until she married Nicholas "
            "St Omer of Thebes; Emperor Henry then named his brother "
            "Eustace regent, wedded to Michael of Epiros's daughter, forced "
            "the Frankish lords who favoured William VI of Montferrat to "
            "submit, and saved the boy from a Venetian, Bulgarian and "
            "Epirote alliance. After Henry died in 1216 Emperor Peter "
            "accepted William's claim and Margaret fled into exile, "
            "leaving her son behind; Peter's presumed death at Epirote "
            "hands let Demetrios keep his crown. Now Epiros attacks in "
            "earnest from the north and west, much land is lost, the "
            "fighting is constant, and the city seems unlikely to hold "
            "much longer.",
            "Relations with its Greek subjects are far better than the "
            "Latin Empire's: Boniface's system still stands, every vassal "
            "owing a season of garrison and a season of war each year, "
            "Greeks with exactly the same rights and dues as Latins. Its "
            "army is mostly Byzantine, with Frankish lords and mercenaries "
            "of doubtful loyalty minding their own estates, so a Frankish "
            "kingdom with a Greek army fights a Greek principality with a "
            "Frankish one. Count Oberto of Biandrate is the boy's deadly "
            "enemy.",
        ),
    )
    w["athens"] = b.lord(
        "Duchy of Athens",
        title="duke",
        wealth="Wealthy",
        seat="The Acropolis, Athens",
        ruler="Otto de la Roche",
        answers_to=w["thessaloniki_kingdom"],
        place=p["attica"],
        summary=paragraphs(
            "Otto de la Roche of Burgundy set up the duchy in 1205 and has "
            "styled himself duke since 1208; to the Greeks he is "
            "Megas Kyr, Great Lord. He did homage first to Boniface as "
            "King of Thessaloniki, supports Demetrios, and has also done "
            "homage to the Latin emperor; Athens is deep in the war "
            "against both Epiros and the Bulgarians.",
            "A devout Catholic, he founded the Cistercian house at Daphni "
            "and has made the Parthenon the Cathedral of Our Lady inside "
            "the newly fortified Acropolis, where he lives. He calls "
            "Orthodox priests heretics, has turned many out of their posts "
            "into poverty and abuses them whenever he can, denying their "
            "ordination as a dodge to escape his labour dues and taxes; "
            "the pope has excommunicated him for it and demanded amends, "
            "and whether he will obey is uncertain. He holds the Image of "
            "Edessa, to the fury of Eastern churchmen. As an excommunicate "
            "he gets no Divine help against the ghosts of Marathon.",
        ),
    )
    w["thebes_lords"] = b.lord(
        "Lords of Thebes",
        title="baron",
        wealth="Wealthy",
        seat="Thebes",
        ruler="Guy de la Roche and Nicholas St Omer, jointly",
        answers_to=w["athens"],
        place=p["attica"],
        summary=(
            "Thebes is held jointly by Otto de la Roche's brother Guy and "
            "Nicholas St Omer. In 1207, after Boniface's death, Nicholas "
            "married his widow Margaret of Hungary, her third marriage "
            "(she had first been Emperor Isaac II Angelos's wife), and the "
            "queen lives with him at Thebes."
        ),
    )
    w["achaea"] = b.lord(
        "Principality of Achaea",
        title="duke",
        wealth="Wealthy",
        seat="Andravida",
        ruler="Geoffrey II de Villehardouin",
        place=p["morea"],
        summary=secrets(
            paragraphs(
                "The Morea's twelve small baronies. Geoffrey I de "
                "Villehardouin, shipwrecked at Modon on his way to Syria, "
                "fought for a Greek warlord there, fled north when the "
                "next one turned on him, and met his old friend William de "
                "Champlitte in Boniface's camp; seeing the Morea in "
                "near-anarchy, they set out to win it. William's victory "
                "at the Olive Grove over an Epirote army ten times larger "
                "made the principality in 1204. William died in 1209 on "
                "his way home, leaving Geoffrey regent until the heir "
                "Robert came within a year and a day; Geoffrey and the "
                "Venetians saw that he did not, and Geoffrey took the "
                "throne. The Greek resistance faltered after Leo Sgouros "
                "rode his horse off the walls of Acrocorinth in 1208, and "
                "the whole Morea was taken by 1211; in thanks Geoffrey gave "
                "the Cistercians land at Zaraka.",
                "Geoffrey II succeeded in 1218. He is married to Agnes de "
                "Courtenay, daughter of the late Empress Yolanda and "
                "Emperor Peter, and is on good terms with the Latin Empire "
                "and the Venetians, whose trade is making the principality "
                "rich. Generous to Greek and Latin alike, he is popular, and "
                "unlike Athens's duke he gets on with the Orthodox clergy, "
                "excusing them tax and military service while taxing Latin "
                "church lands, to the pope's annoyance. Epidauros lies in "
                "his lands. The book names no seat; Andravida is history's.",
            ),
            "If he falls gravely ill, Agnes will come to Epidauros begging "
            "for a cure (Healing the Realm).",
        ),
    )
    w["bulgaria"] = b.lord(
        "Tsardom of Bulgaria",
        title="duke",
        wealth="Wealthy",
        seat="Tarnovo",
        ruler="Ivan Asen II",
        place=theban.places["greece"],
        summary=paragraphs(
            "The northern neighbour of Greece, whose Christian armies once "
            "overran it and whose tsar Kaloyan besieged Thessaloniki in "
            "1207, until (the city says) St Demetrios rode out and speared "
            "him; the Bulgarians whisper that his Cuman captain murdered "
            "him. It has lost Ohrid and Pelagonia to Epiros, and allied "
            "with Venice and Epiros against Thessaloniki in 1210. Gigas "
            "lies in its lands, in a fertile valley south-west of Sofia.",
            "The book names Boril as the current tsar; history has Ivan "
            "Asen II, who deposed him in 1218, ruling in 1220. The book "
            "names no capital; Tarnovo is history's.",
        ),
    )


# ---------------------------------------------------------------- churches


def _churches(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    w["archbishop_thessaloniki"] = b.church(
        "Latin Archbishopric of Thessaloniki",
        church="Archbishop's cathedral",
        place=p["macedonia"],
        summary=(
            "Its cathedral is the city's Hagia Sophia, a smaller copy of "
            "Constantinople's, lately given to the Western Church. The "
            "Latin archbishop, who tutored King Demetrios as a boy, is his "
            "noted friend and supporter. Orthodox and Latin churches live "
            "peaceably side by side in the city, though the Latin hierarchy "
            "is on top."
        ),
    )
    w["hagios_demetrios"] = b.church(
        "Hagios Demetrios, Thessaloniki",
        church="Large urban church",
        place=p["macedonia"],
        summary=secrets(
            paragraphs(
                "The city's foremost church, an ancient basilica over the "
                "old Roman forum and shrine of its patron, St Demetrios, a "
                "martyred Roman soldier whose relics give off the scent of "
                "myrrh. His miracles have saved the city from Slav armies "
                "many times; if it is gravely threatened he rises from his "
                "shrine and fights beside its defenders, and with St George "
                "he is patron of the crusades, which may be why the Fourth "
                "Crusade wisely left the city alone. The great Fair of "
                "St Demetrios is held outside the walls for six days each "
                "October, where traders from across Europe meet Arab and "
                "Jewish merchants of Africa and the Levant.",
                "Priests still struggle to explain 1185: some say William "
                "the Good's war on the vile Andronikos was just and the "
                "saint would not rise for such an emperor, even helping the "
                "attackers, when the catapults and archers inexplicably ran "
                "dry and the walls gave way as if by magic. But he still "
                "rises for a just cause: in early October 1207 a shining "
                "armoured rider came out against the besieging Bulgarians "
                "and killed Tsar Kaloyan with a spear, and many on the "
                "walls saw it. He is the patron of Oikos tou Eleous, whose "
                "sisters invoked him that day.",
            ),
            "",
        ),
    )
    w["rotunda_st_george"] = b.church(
        "Rotunda of St George, Thessaloniki",
        church="Large urban church",
        place=p["macedonia"],
        summary=(
            "The oldest church in Greece: squat, round and enormously "
            "thick-walled, which has let it outlast the centuries."
        ),
    )
    w["holy_community_athos"] = b.church(
        "The Holy Community of Mount Athos",
        church="Monastery or nunnery",
        order="Orthodox (Rule of St Basil)",
        ruler="The protos",
        place=p["mount_athos"],
        founded=955,
        summary=paragraphs(
            "The monastic republic of the Holy Mountain, which the Latin "
            "rulers have left exactly as it was. Most monasteries join in "
            "electing the protos, 'the first', who speaks for the "
            "community to the outside world; three, the Great Lavra "
            "(founded 955, the first great house), Vatopedi and Iviron, "
            "stay independent, and their abbots wield much influence of "
            "their own, even beyond the protos's.",
            "Its houses span many peoples: Iviron is Georgian, Panteleemon "
            "Russian, Zographou Bulgarian, the Serbs have Hilander, "
            "Armenian monks are common, and three Benedictine monasteries "
            "of the Latin rite have been built over the centuries. A "
            "monstrous drakos once crawled from the sea to settle in the "
            "Karakalou monastery.",
        ),
    )
    w["ohrid_archbishopric"] = b.church(
        "Archbishopric of Ohrid",
        church="Archbishop's cathedral",
        place=p["lake_ohrid"],
        summary=(
            "The see of the former Bulgarian capital, with dozens of "
            "ancient churches; the Bulgarian Church's head there is now "
            "under Epirote rule since Theodore took the city. The placid "
            "monastery of St Naum stands on the lake shore."
        ),
    )
    w["larissa_archbishopric"] = b.church(
        "Archbishopric of Larissa",
        church="Archbishop's cathedral",
        place=p["macedonia"],
        founded=None,
        summary=(
            "Larissa has been an archbishop's seat since the fifth "
            "century; it is now in Epirote hands with the rest of Thessaly."
        ),
    )
    w["doupiani"] = b.church(
        "The Skete of Doupiani, Meteora",
        church="Monastery or nunnery",
        order="Orthodox hermits",
        place=p["meteora"],
        summary=(
            "A small community of hermit monks among the pillars of "
            "Meteora, named for the pillar that holds its common chapel of "
            "the Theotokos, founded by the first monk, Varnavas, in the "
            "tenth century. Some hermits live high in caves and cracks in "
            "the sheer rock, where they have painted crude frescoes, and "
            "rough rope pulleys haul up food, goods and even men; the ropes "
            "are changed only when they break, as God wills."
        ),
    )
    w["daphni"] = b.church(
        "Abbey of Daphni",
        church="Monastery or nunnery",
        order="Cistercian",
        ruler="Otto de la Roche, patron",
        place=p["attica"],
        summary=(
            "Between Athens and Eleusis, on the Sacred Way. Its old Greek "
            "monks, friendly to the Eleusinian cult, had made a Christian "
            "house of a sanctuary of Apollon (mystics to some, heretics to "
            "most), and the procession of initiates stopped there; it was "
            "sacked in 1205 and given to the Cistercians, which has made "
            "the cult's way harder."
        ),
    )
    w["zaraka"] = b.church(
        "Abbey of Zaraka",
        church="Monastery or nunnery",
        order="Cistercian",
        ruler="Geoffrey II de Villehardouin, patron",
        place=p["arcadia"],
        summary=(
            "Land in Arcadia that Geoffrey I gave the Cistercians in "
            "thanks for the conquest of the Morea, where an imposing Gothic "
            "monastery is now going up."
        ),
    )
    w["our_lady_athens"] = b.church(
        "Cathedral of Our Lady, Athens",
        church="Archbishop's cathedral",
        place=p["attica"],
        summary=(
            "The Parthenon, Athene's great temple on the Acropolis, lately "
            "made a Latin cathedral by Otto de la Roche, inside the newly "
            "walled citadel where he lives; with the Acropolis it is the "
            "seat of the duchy."
        ),
    )


# ------------------------------------------------------------------- towns


def _towns(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    epiros, kingdom = w["epiros"], w["thessaloniki_kingdom"]
    athens, achaea = w["athens"], w["achaea"]

    def town(key: str, name: str, summary: str, **kw: Any) -> None:
        w[key] = b.town(name, summary=summary, **kw)

    town(
        "arta",
        "Arta",
        "Once a minor town, on the site of Corinthian Ambracia (named for "
        "an Amazon princess, Apollon's granddaughter) and later King "
        "Pyrrhus's capital; Michael Komnenos made it the capital of Epiros "
        "after Koundouros, and in fifteen years it has swollen with "
        "refugees from the troubled east and south, Constantinople "
        "included. Its formidable new castle has an Infernal aura and a "
        "guard of sinister ravens, and its churches' Divine auras are "
        "weak in proportion. Its market, across the cursed bridge, is a "
        "grubby, treacherous place.",
        charter="Noble lord",
        ruler="Theodore Komnenos Doukas",
        answers_to=epiros,
        place=p["epiros"],
    )
    town(
        "durazzo",
        "Durazzo",
        "Dyrrhachium, the biggest and one of the oldest cities of Epiros, "
        "in a sheltered Adriatic harbour, a port since time out of mind "
        "with ships running constantly to Italy and Venice, and the west "
        "end of the Via Egnatia, so a link between the West and the "
        "Orthodox East: busy and cosmopolitan, with Italians, Venetians, "
        "Greeks, Bulgars, Jews and Vlachs. Venice took it in 1204; Epiros "
        "has since taken it back.",
        charter="Noble lord",
        answers_to=epiros,
        place=p["epiros"],
    )
    town(
        "corfu",
        "Corfu",
        "Korkyra to the Greeks: the port town halfway down the east shore "
        "of the large hilly island off the Epirote coast, Venetian until "
        "Michael Komnenos took it in 1214. The Stone Ship stands just "
        "outside its harbour.",
        charter="Noble lord",
        answers_to=epiros,
        place=p["epiros"],
    )
    town(
        "ohrid",
        "Ohrid",
        "The venerable episcopal city on Lake Ohrid's north shore, on the "
        "Via Egnatia, former capital of the Bulgarian Empire, with dozens "
        "of old churches; taken from the Bulgarians by Theodore of Epiros.",
        charter="Church",
        answers_to=epiros,
        place=p["lake_ohrid"],
    )
    town(
        "monastiri",
        "Monastiri",
        "An ancient city a dozen miles east of the lakes, under Mount Pelister.",
        charter="Noble lord",
        answers_to=epiros,
        place=p["epiros"],
    )
    town(
        "thessaloniki",
        "Thessaloniki",
        "The Co-Queen of the empire, second only to Constantinople: over "
        "100,000 souls, bigger than Paris, founded by King Cassander near "
        "old Therma and named for his wife, Alexander's half-sister. St "
        "Paul preached in its synagogues and wrote it two epistles, and "
        "Cyril and Methodius took the Gospel from here to Bulgaria. A "
        "mile-long harbour faces the sea, huge Byzantine walls the other "
        "three sides; within are Roman arches and statues, a vast "
        "hippodrome, an imperial mint, the Rotunda of St George, the "
        "Hagia Sophia (now the Latin cathedral) and above all the Hagios "
        "Demetrios. Mostly Greek, with small Italian and Jewish "
        "communities.\n\n"
        "The Sicilians sacked it in 1185, killing thousands, but it "
        "recovered; the Fourth Crusade passed it by, so it keeps much of "
        "its Byzantine splendour, a hint of what the Queen of Cities was. "
        "Oikos tou Eleous is here; Paulicians live lawfully within the "
        "walls; the Gorgona haunts the harbour; and the armies of Epiros "
        "close in from north and west.",
        population=100000,
        charter="Noble lord",
        ruler="King Demetrios",
        answers_to=kingdom,
        place=p["macedonia"],
    )
    town(
        "serres",
        "Serres",
        "A castle town of the kingdom where Emperor Henry imprisoned "
        "Count Oberto of Biandrate in chains in 1209.",
        charter="Noble lord",
        answers_to=kingdom,
        place=p["macedonia"],
    )
    town(
        "larissa",
        "Larissa",
        "The ancient chief city of Thessaly, an archbishop's seat since "
        "the fifth century, in the middle of the wide, fertile plain, now "
        "ruled from Epiros. It is named for the kindly nymph of a local "
        "spring, still sometimes seen and honoured as a saint; she and "
        "the horse, for the plain's famous horses and horsemen, are its "
        "emblems.",
        charter="Noble lord",
        answers_to=epiros,
        place=p["macedonia"],
    )
    town(
        "thebes",
        "Thebes",
        "The city that names the Tribunal, founded by Kadmus at the south "
        "edge of the Boeotian plain on the Delphic oracle's word; its "
        "citadel, the Kadmea, bears his name. Alexander razed it, and for "
        "a thousand years it was a shadow of itself until silk came in "
        "the tenth century: within two centuries its weavers were the "
        "empire's best, surpassing Constantinople, with dyes from Athens. "
        "Roger II of Sicily carried the whole industry, workers and all, "
        "off to Sicily in the twelfth century, so the secret reached the "
        "West, but Thebes recovered fully. With 30,000 people, many of "
        "them silk growers and weavers, it is easily the second city of "
        "Greece. Queen Margaret lives here.",
        population=30000,
        charter="Noble lord",
        ruler="Guy de la Roche and Nicholas St Omer",
        answers_to=w["thebes_lords"],
        place=p["attica"],
    )
    town(
        "athens",
        "Athens",
        "So old that its founding is lost: Athene and Poseidon vied to be "
        "its patron, and it chose her olive tree over his spring, so "
        "olive groves still bless it. Fallen from favour under the "
        "Christian empire, it is still a large, prosperous port of about "
        "10,000, often visited by Venetians, with surplus grain and "
        "olives, fine dyes and soaps for the silk trade, and the marble "
        "quarries of Penteli in the hills nearby. The Acropolis and its "
        "new Latin cathedral are the duke's seat. The Column of "
        "St Haralambos on the Piraeus road keeps plague away.",
        population=10000,
        charter="Noble lord",
        ruler="Otto de la Roche",
        answers_to=athens,
        place=p["attica"],
    )
    town(
        "chalkis",
        "Chalkis",
        "Euboea's main town, named for the copper and bronze workers who "
        "first lived there; its colonists named the Chalkidiki. A sturdy "
        "old fortress commands it, a classic base for invading the "
        "mainland, and its wooden drawbridge over the Euripus is the "
        "island's only link to Boeotia. Seat of the central barony of "
        "Negroponte; the northern sits at Oreoi and the southern at "
        "Karystos.",
        charter="Noble lord",
        place=p["euboea"],
    )
    town(
        "corinth",
        "Corinth",
        "Founded by Korinthos, of the sun god's line, beside the "
        "Isthmus with ports on both the Saronic and Corinthian gulfs; "
        "its temple of Aphrodite once kept thousands of prostitutes, and "
        "St Paul wrote its Christians two epistles. Earthquakes, Goths and "
        "the Sicilians have ruined it again and again, yet it remains a "
        "busy port of 10,000, the largest town of the Morea. The great "
        "fortress of Acrocorinth, 1,500 feet up behind it, still commands "
        "the Isthmus; Leo Sgouros leapt to his death from its walls in "
        "1208.",
        population=10000,
        charter="Noble lord",
        answers_to=achaea,
        place=p["morea"],
    )
    town(
        "epidauros_town",
        "Epidauros",
        "The small town below the sanctuary, where the covenfolk of "
        "Epidauros live among ordinary folk; its church gives it a Divine "
        "aura too weak to trouble the sanctuary above.",
        charter="Noble lord",
        answers_to=achaea,
        place=p["epidauros_sanctuary"],
    )
    town(
        "sofia",
        "Sofia",
        "The Bulgarian city north-east of Gigas's valley, in a busy, "
        "well-peopled country where the Tremere keep their lodge small.",
        charter="Noble lord",
        answers_to=w["bulgaria"],
        place=theban.places["greece"],
    )


# ---------------------------------------------------------------- factions


def _factions(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    w["montferrat_party"] = b.faction(
        "The Montferrat Party",
        faction="Other",
        decides="Its leader",
        ruler="Count Oberto II of Biandrate",
        place=p["macedonia"],
        wants="William VI of Montferrat on the throne of Thessaloniki in place of Demetrios",
        offers="Frankish swords and plots at court",
        summary=secrets(
            "The Frankish lords of the Kingdom of Thessaloniki who back "
            "the claim of William VI, Marquis of Montferrat, Boniface's son "
            "by his first wife Helena del Bosco, against his half-brother "
            "the boy king. Their moving spirit, Count Oberto II of "
            "Biandrate, forced Queen Margaret from the regency, and in "
            "1209 conspired with Emperor Henry, but when Henry heard "
            "Margaret out he saw the justice of her cause and had the "
            "count chained in the castle at Serres. Freed years later, "
            "Oberto swore revenge on the emperor and still works "
            "tirelessly for William; he is King Demetrios's mortal enemy.",
            "Oberto may have poisoned Henry in 1216, though others blame "
            "his Bulgarian empress Maria.",
        ),
    )
    w["thessalonian_greeks"] = b.faction(
        "The Greek Families of Thessaloniki",
        faction="Family",
        decides="A council",
        place=p["macedonia"],
        wants="Their city kept whole and Byzantine, under a king of Angelos blood",
        offers="The loyalty of the townsfolk, Byzantine troops, money",
        summary=(
            "The great Greek houses and citizens of the Co-Queen, who love "
            "King Demetrios for his Angelos mother, supported Margaret's "
            "regency, and give the kingdom its largely Greek army. Under "
            "Boniface's settlement they hold exactly the rights and dues "
            "of the Latins, which keeps them loyal to a Frankish crown "
            "against the Greek prince of Epiros."
        ),
    )


# ------------------------------------------------------------- finishing


def _lord_named(theban: Theban, *words: str) -> Neighbour | None:
    """The lord another part made whose name holds all `words`."""
    for neighbour in theban.b.saga.neighbours:
        if neighbour.kind == "lord" and all(
            word.casefold() in neighbour.name.casefold() for word in words
        ):
            return neighbour
    return None


def finish(theban: Theban) -> None:
    """Tie the Frankish realms to the Latin Empire once
    constantinople.py has made it."""
    empire = _lord_named(theban, "Latin Empire")
    if empire is None:
        return
    for key in ("thessaloniki_kingdom", "achaea"):
        theban.world[key].answers_to = empire.id


# --------------------------------------------------------------- stats

P = Profile
GREEK = "Greek"
THEBAN = "Area Lore: Theban Tribunal"


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


#: Each magus the book sketches without a stat block, by character key.
PROFILES: dict[str, Profile] = {
    "xenias": P(
        strong="int sta per",
        weak="pre com",
        arts={"Cr": 9, "Co": 9, "Re": 4, "In": 4, "Vi": 3, "He": 2},
        abilities={
            "Medicine": (6, "longevity"),
            "Chirurgy": (4, "wounds"),
            "Magic Theory": (6, "longevity rituals"),
            "Philosophiae": 2,
        },
        virtues=[
            "Leper Magus",
            _art("Affinity with {art}", "corpus"),
            "Twilight Prone",
            "Dutybound",
        ],
        native=GREEK,
    ),
    "galla": P(
        strong="per int sta",
        weak="dex qik",
        arts={"He": 8, "Co": 6, "Cr": 6, "Pe": 3, "An": 3},
        abilities={
            "Herbalism": (5, "healing roots"),
            "Medicine": (4, "herbal remedies"),
            "Animal Ken": (2, "snakes"),
            "Area Lore: Morea": 2,
            "Folk Ken": 2,
        },
        virtues=["Herbalism", "Lame", "Humble"],
        native=GREEK,
    ),
    "destasia": P(
        strong="pre sta dex",
        arts={"Pe": 8, "Co": 7, "Me": 4, "In": 3, "Re": 3},
        abilities={
            "Infernal Lore": (2, "witches"),
            "Magic Lore": (3, "curses"),
            "Leadership": (3, "magi"),
            "Area Lore: Thessaly": 3,
            "Athletics": 2,
        },
        virtues=[
            "Curse-Throwing",
            _art("Affinity with {art}", "perdo"),
            "Disfigured",
            "Wrathful (Minor)",
            "Dark Secret",
        ],
        native=GREEK,
    ),
    "megethia": P(
        strong="int pre sta",
        arts={"Pe": 8, "Co": 6, "Me": 6, "Vi": 4, "In": 3},
        abilities={
            "Magic Lore": (4, "curses"),
            "Infernal Lore": (3, "witches"),
            "Area Lore: Thessaly": 3,
        },
        virtues=["Curse-Throwing", "Twilight Prone", "Reclusive"],
        age=110,
        native=GREEK,
    ),
    "boustaphan": P(
        strong="int pre com",
        arts={"Re": 7, "Me": 6, "Pe": 5, "Vi": 5, "An": 4, "Cr": 3},
        abilities={
            "Leadership": (5, "Tremere"),
            "Intrigue": (4, "Tribunal politics"),
            "Code of Hermes": 4,
            "Teaching": (4, "apprentices"),
            "Hunt": (3, "hawking"),
            "Animal Handling": 2,
            "Ride": 2,
            "Etiquette": 2,
        },
        virtues=[
            "Good Teacher",
            "Hermetic Prestige",
            "Skilled Parens",
            "Ambitious (Minor)",
            "Dutybound",
            "Close Family Ties",
        ],
        native="Bulgarian",
        hermetic="Latin",
    ),
    "monorchis": P(
        strong="sta per pre",
        weak="int com",
        arts={"Ig": 9, "Cr": 5, "Pe": 4, "Mu": 4, "Vi": 3},
        abilities={
            "Enigmatic Wisdom": 0,
            "Concentration": (3, "spell concentration"),
            "Penetration": (4, "Ignem"),
            "Magic Lore": 2,
            "Artes Liberales": 0,
            "Organization Lore: Theban Tribunal": 1,
        },
        virtues=[
            _art("Affinity with {art}", "ignem"),
            _art("Puissant {art}", "ignem"),
            "Restricted Learning",
            "Obsessed (Minor)",
            "Driven (Minor)",
        ],
        native=GREEK,
        hermetic="Latin",
    ),
    "allectores": P(
        strong="com pre per",
        weak="str",
        arts={"Me": 7, "Im": 5, "In": 5, "Re": 4, "Cr": 3},
        abilities={
            "Charm": (5, "first impressions"),
            "Etiquette": (4, "magi"),
            "Intrigue": (3, "treaties"),
            "Folk Ken": (3, "magi"),
            "Bargain": 3,
            "Code of Hermes": 3,
        },
        virtues=["Gentle Gift", "Dutybound", "Close Family Ties", "Proud (Minor)"],
        native="Bulgarian",
        hermetic="Latin",
    ),
    "ausculator": P(
        strong="int sta per",
        weak="dex qik",
        arts={"Te": 12, "Re": 6, "Cr": 5, "In": 5, "Mu": 4, "Vi": 4, "Im": 3},
        abilities={
            "Magic Theory": (7, "Terram"),
            "Hedyosmos Lore": (5, "the labyrinth"),
            "Concentration": (4, "stillness"),
            "Teaching": (3, "writing"),
            "Code of Hermes": 4,
            "Awareness": (4, "hearing"),
            "Magic Lore": (3, "the titans"),
        },
        virtues=[
            _art("Affinity with {art}", "terram"),
            _art("Puissant {art}", "terram"),
            "Spirit Familiar",
            "Good Teacher",
            "Blind",
            "Twilight Prone",
        ],
        native=GREEK,
    ),
    "aiakia": P(
        strong="int sta per",
        weak="com pre",
        arts={"Te": 9, "Re": 6, "Cr": 5, "In": 4, "Vi": 4, "Au": 3},
        abilities={
            "Hedyosmos Lore": (4, "the labyrinth"),
            "Code of Hermes": (5, "the Peripheral Code"),
            "Magic Lore": (4, "caves"),
            "Survival": (3, "underground"),
            "Leadership": 2,
        },
        virtues=[
            "Dowsing",
            "Summoning",
            "Dutybound",
            "Wrathful (Minor)",
            "Afflicted Tongue",
            "Obsessed (Minor)",
        ],
        native=GREEK,
    ),
    "tisiphon": P(
        strong="pre com int",
        arts={"Pe": 7, "Me": 6, "In": 6, "Re": 4, "Vi": 4, "Te": 2},
        abilities={
            "Code of Hermes": (6, "Wizard's War"),
            "Artes Liberales": (4, "rhetoric"),
            "Certamen": 3,
            "Intrigue": 2,
            "Magic Lore": (2, "the titans"),
        },
        virtues=[
            "Spirit Familiar",
            "Wrathful (Minor)",
            "Obsessed (Minor)",
            "Reckless (Minor)",
        ],
        native=GREEK,
    ),
    "celaenea": P(
        strong="int per com",
        arts={"In": 8, "Vi": 7, "Me": 5, "Im": 4, "Te": 3},
        abilities={
            "Magic Lore": (5, "Hermes"),
            "Faerie Lore": (3, "the old gods"),
            "Philosophiae": 3,
            "Magic Theory": (5, "Vim"),
            "Hedyosmos Lore": 1,
        },
        virtues=[
            "Book Learner",
            "Obsessed (Major)",
            "Proud (Minor)",
        ],
        native=GREEK,
    ),
    "polydegmon": P(
        strong="int sta pre",
        arts={"Re": 8, "Vi": 7, "Me": 5, "Co": 3, "Te": 3},
        abilities={
            "Magic Lore": (5, "binding"),
            "Infernal Lore": (2, "the Goetic Arts"),
            "Hedyosmos Lore": 3,
            "Penetration": (4, "Vim"),
        },
        virtues=[
            ("Minor Magical Focus", {"focus": "binding spirits"}),
            "Infamous",
            "Reclusive",
        ],
        age=90,
        native=GREEK,
    ),
    "anna": P(
        strong="pre com int",
        arts={"Cr": 6, "Pe": 5, "Me": 5, "Vi": 5, "In": 4, "Co": 4},
        abilities={
            "Theology": (5, "the Orthodox Church"),
            "Dominion Lore": (4, "saints"),
            "Infernal Lore": (3, "Paulicians"),
            "Leadership": (4, "nuns"),
            "Etiquette": 3,
            "Charm": 2,
            "Area Lore: Thessaloniki": 4,
        },
        virtues=[
            "Holy Magic",
            "Pious (Major)",
            "Monastic Vows (Hermetic)",
        ],
        native=GREEK,
    ),
    "theocharista": P(
        strong="int com per",
        weak="str",
        arts={"Cr": 6, "Me": 6, "In": 5, "Co": 4, "Vi": 4},
        abilities={
            "Philosophiae": (5, "Neo-Platonism"),
            "Theology": (5, "the Trinity"),
            "Dominion Lore": 3,
            "Teaching": 2,
            "Area Lore: Thessaloniki": 3,
        },
        virtues=[
            "Holy Magic",
            "Pious (Minor)",
            "Humble",
            "Monastic Vows (Hermetic)",
        ],
        native=GREEK,
    ),
    "nereida": P(
        strong="pre com qik",
        arts={"Me": 8, "Im": 6, "Cr": 4, "Re": 4, "Au": 3},
        abilities={
            "Music": (5, "singing"),
            "Etiquette": (3, "the royal court"),
            "Charm": 3,
            "Intrigue": 2,
            "Area Lore: Thessaloniki": 2,
        },
        virtues=[
            "Holy Music",
            "Restriction",
            "Monastic Vows (Hermetic)",
            "Proud (Minor)",
        ],
        native=GREEK,
    ),
    "nonna": P(
        strong="pre com int",
        arts={"Me": 8, "Im": 5, "Cr": 4, "Re": 4, "In": 3},
        abilities={
            "Music": (5, "singing"),
            "Etiquette": (4, "the royal court"),
            "Intrigue": (3, "Constantinople"),
            "Folk Ken": 2,
            "Area Lore: Thessaloniki": 2,
        },
        virtues=[
            "Holy Music",
            ("Social Contacts", {"group": "Queen Margaret's circle"}),
            "Monastic Vows (Hermetic)",
            "Proud (Minor)",
        ],
        native=GREEK,
    ),
    "pythia": P(
        strong="per int pre",
        arts={"In": 9, "Me": 6, "Vi": 5, "Cr": 4, "Ig": 3},
        abilities={
            "Enigmatic Wisdom": (5, "prophecy"),
            "Magic Lore": (4, "oracles"),
            "Awareness": (3, "omens"),
            "Etiquette": 2,
        },
        virtues=["Premonitions", "Visions", "Twilight Prone", "Reclusive"],
        age=70,
        native=GREEK,
    ),
}


def stats(theban: Theban) -> None:
    """Generated stats for the magi of Greece, none of whom has a printed
    stat block."""
    b = theban.b
    for key, profile in PROFILES.items():
        apply(b, theban.magi[key], profile)
