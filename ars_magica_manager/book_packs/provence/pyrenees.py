"""The Pyrenees and the Hispanic March, as of 1220: the mountains and the
lands either side of them (the Basque country, Navarre, Castile's border,
the crown of Aragon's counties and Andorra), their sites, auras, vis and
creatures; the three Pyrenean covenants, Aedes Mercurii (its two sites,
the Dorsum on Pic du Midi d'Ossau and the Templum in the Cirque de
Gavarnie, joined by a Mercere Portal), Bellaquin in Andorra and Miniata
Sophia in the cave of Niaux, with their magi and libraries; and the
mundane world of kings, counts, bishops, abbeys, towns, the almogavars
of the Andorra Company and the sorginak covens, in paraphrase of Faith &
Flame chapter six, with the votes and politics of chapter three.

Places south of the mountains are kept (decision P15). The ruined
covenants of the region (Val-Negra's chapterhouse near Girona, the
outpost at Saint Jean Pied-de-Port, Mistridge, Windgraven) are
tribunal.py's, and Val-Negra's site val_negra.py's, which may set it
inside places["mount_perditu"]. Creatures (Pyrene, Lehen Sugea, the
drakes of Soule, the jentilak, laminak and aker) are described in the
summaries of the places they haunt. The Count of Foix is described in
chapter seven too: `finish` makes him only when no other part has.

Records are kept under slugs: the region places["pyrenees"], the
covenant sites places["aedes_dorsum"], places["aedes_templum"],
places["ordino"] and places["niaux_cave"]; the covenants
covenants["aedes_mercurii"], covenants["bellaquin"] and
covenants["miniata_sophia"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...arms import Arms
from ..builder import Builder, joined_lines, paragraphs, titled, vf_art
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from . import Provence

FLAMBEAU = "house_flambeau"
TREMERE = "house_tremere"
MERCERE = "house_mercere"
JERBITON = "house_jerbiton"
CRIAMON = "house_criamon"
VERDITIUS = "house_verditius"
TYTALUS = "house_tytalus"
EX_MISC = "house_ex_miscellanea"

#: The lead line of a covenant's notes, before its secrets.
KNOWN_ORDER = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY = {"status": "Known", "known": "Locally"}
RUMOURED = {"status": "Rumoured", "known": "Locally"}


def _add(provence: Provence, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and keep it under `key` for the other parts."""
    place = provence.b.place(name, **kw)
    provence.places[key] = place
    return place


def build(provence: Provence) -> None:
    b = provence.b
    tribunal = provence.tribunal
    assert tribunal is not None, "tribunal.py builds the Tribunal first"
    _region(provence)
    _basque_country(provence)
    _high_pyrenees(provence)
    _upper_aragon(provence)
    _catalonia(provence)
    _andorra(provence)
    _niaux(provence)
    _aedes_mercurii(provence, b, tribunal)
    _bellaquin(provence, b, tribunal)
    _miniata_sophia(provence, b, tribunal)
    _lords(provence, b)
    _churches(provence, b)
    _towns(provence, b)
    _factions(provence, b)


# ------------------------------------------------------------- the region


def _region(provence: Provence) -> None:
    _add(
        provence,
        "pyrenees",
        "The Pyrenees and the Hispanic March",
        summary=paragraphs(
            "The mountain wall between Provence and Iberia, and the realms "
            "that climb it from the south: the kingdoms of Castile and "
            "Navarre in the west, the crown of Aragon (the kingdom of Aragon "
            "and the county of Barcelona, together called Catalonia) in the "
            "centre and east, and tiny Andorra in the middle, the last of "
            "Charlemagne's marcher counties. The frontier itself is marked "
            "only by iron crosses set on lonely slopes and by the watersheds "
            "where the thaw runs off one way or the other. The ruling houses "
            "here are knotted together by marriage with each other and with "
            "England, Burgundy, Toulouse and Montpellier, and they care as "
            "much about the war against the Moors as about the crusade in "
            "Provence. The book treats the southern lands only where they "
            "touch the mountains.",
            "Hermetically the mountains are the Tribunal's conservative "
            "heartland. Aedes Mercurii, the Cult of Mercury's great temple "
            "and fortress, leads a bloc that wants no part in the crusade; "
            "Bellaquin, a banking covenant in Andorra, dreams of a Catalan "
            "Tribunal; and the Criamon of Miniata Sophia study painted caves "
            "near Foix. Val-Negra, the first domus magna of House Flambeau, "
            "lies lost on Mount Perditu. If the Tribunal ever moves against "
            "the crusaders, the Pyrenean covenants may walk out and ask the "
            "Grand Tribunal of 1228 for a Tribunal of their own. There are no "
            "Templar houses in Andorra or the mountains.",
            "Caves honeycomb the range, many big enough for a covenant, but "
            "drakes, worms and now and then a wyvern lair in them, so a new "
            "covenant may have to evict a tenant first.",
            "The Basques. Their country covers the western mountains and the "
            "Biscay coast, across the Provençal and Iberian Tribunals: Labourd, "
            "Lower Navarre and Soule on the French side, Upper Navarre under "
            "Castile's shadow, and Álava, Biscay and Gipuzkoa held by Castile. "
            "A Basque is one who speaks Euskara, a tongue kin to no other, "
            "with its own strange numerals; many also speak Occitan, and some "
            "northern Basques feel more Occitan than Basque. They have no "
            "kingdom of their own but keep their land, language and customs, "
            "own their farms rather than serving lords, and are content. "
            "Family names come from the place a house stands. Women own "
            "property, hold office and speak in council more than elsewhere, "
            "though men lead. Nearly all are Christian, but a quiet pagan "
            "minority is let be, and Jews, Muslims and heretics who learn the "
            "language are tolerated. They are hardy mountaineers, whalers and "
            "cod fishers, lately using the stern rudder, and they crew ships "
            "from the Mediterranean to the North Sea.",
            "Basque myth. The old faith is chthonic: Mari, an earth mother of "
            "weather and fortune, drives a chariot of storm clouds behind "
            "great goats and mates with her consort Sugaar, and both bring "
            "storms, droughts and luck good and bad; she lives in a mountain "
            "cave whose place changes with the teller, appears as a young "
            "woman in red, a burning woman, a tree or a thunderbolt, and "
            "takes red beasts' shapes or a black he-goat's. She may be a "
            "Magic daimon, a faerie living on worship, or a demon's mask; "
            "nobody can be sure. Sugaar is the Great Dragon and the genius "
            "loci of the whole range, a serpent up to seven hundred feet long "
            "or a black ram, a storm or a warrior, said to have been bound to "
            "the mountains by the Archangel Michael. Their brood are the "
            "drakes, worms, many-headed herensuge and venomous vibria of the "
            "Pyrenees; their son Mikelatz is a wild storm spirit; Atxular, "
            "Mari's son by a pious man, turned from black magic to protect "
            "Christians and justifies Christian sorginak; and Jaun Zuria, the "
            "White Lord, first lord of Biscay, was Sugaar's son.",
            "Other beings. The jentilak, giants who held the land before men, "
            "raised the dolmens, taught farming and smithing, and are said to "
            "have thrown boulders at Roland; a few linger on the peaks as "
            "magical beings or faeries, and one, Olentzero, brings children "
            "gifts at Christmas. The one-eyed, man-eating tartalo may be their "
            "degenerate kin. The laminak are river fae, builders and "
            "spinners, who teach sorginak and raise bridges and churches for "
            "a price; whoever steals a lamia's golden comb commands her, and "
            "none may tread holy ground. Aker, goat-men of the mountain "
            "meadows, are called by sorginak to teach weather lore and herbs "
            "or harry enemies, and demons sometimes pose as aker.",
            "The sorginak are Basque folk witches descended from Mari's "
            "priestesses (P11: their powers are not modelled). The unGifted "
            "live quietly in the villages; the Gifted live apart, some "
            "trained as folk witches and some Hermetically, and bully their "
            "weaker sisters. At least 61 unGifted and about nine Gifted "
            "sorginak meet in 13 covens across western Provence and "
            "north-western Iberia, at Friday gatherings called akelarre in "
            "caves and stone circles, with grand conclaves at Zugarramurdi. "
            "Most defer to Dama, the Praeco, at Mimizan; three Hermetically "
            "trained sorginak keep apart from her. Their favoured powers are "
            "Animal Ken, Dowsing, Flight, Healing, Hex, Second Sight and "
            "Shapeshifting; a warped sorgina of some lines slowly becomes a "
            "lamia, wholly so at Warping 10. A covenant in the Basque country "
            "will have dealings with a coven, friendly or not.",
        ),
        **KNOWN_ORDER,
    )


# -------------------------------------------------------- Basque country


def _basque_country(provence: Provence) -> None:
    region = provence.places["pyrenees"]
    basque = _add(
        provence,
        "basque_country",
        "The Basque Country and Navarre",
        inside=region,
        summary=paragraphs(
            "The western mountains and their northern valleys. Labourd runs "
            "from the Bay of Biscay to Mount Rhune and is the heart of Basque "
            "culture, full of sorginak; its count lost Bayonne after rebelling "
            "against Henry II. Lower Navarre, a land of hills and valleys "
            "that has swung between Gascony and Navarre, now owes Navarre and "
            "is run by a royal sheriff with no lord; it lives off the Way of "
            "St James, which musters at Ostabat and climbs to Roncevaux, and "
            "is known for pink sandstone, wild pottok ponies and the "
            "Irouleguy wine of Roncevaux's monks, while its many dolmens hint "
            "that jentilak once lived here. Soule, on the Oloron opposite "
            "Béarn, speaks Euskara and little else.",
            "South of the passes lies Upper Navarre, whose capital Pamplona "
            "grows rich on pilgrims. The Bitter Lord (a story seed): the "
            "Count of Labourd thinks of hiring sorginak to curse, frighten and "
            "blackmail Bayonne's officers, then offering to lift the trouble "
            "in exchange for the town's fealty.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        provence,
        "mount_rhune",
        "Mount Rhune",
        inside=basque,
        aura=4,
        summary=paragraphs(
            "The mountain at Labourd's eastern edge, its slopes strewn with "
            "stone circles, dolmens and old burial mounds where the sorginak "
            "of Labourd hold their akelarre. It has a Magic aura of 4. A coven "
            "from round Ustaritz, the county's capital, flies here as ravens "
            "for its Friday sabbat.",
            "Lehen Sugea, a seven-headed, winged, fire-breathing dragon, is "
            "said to sleep deep inside the mountain.",
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "zugarramurdi",
        "The Cave of Zugarramurdi",
        inside=basque,
        aura=4,
        summary=paragraphs(
            "A vast cave mouth opening on a broad meadow, with a stream "
            "running through the gallery: a gathering place of folk witches "
            "since antiquity. Every third year at midsummer sorginak from "
            "Normandy, Iberia and Provence meet here for a great conclave of "
            "strange rites and initiations, and trade vis and secrets.",
            "Its aura is Magic 4, but vis drawn from it is Infesta, tainted "
            "by the Infernal (Realms of Power: the Infernal). No covenant "
            "claims it.",
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "roncevaux",
        "Roncevaux Pass",
        inside=basque,
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "The pass on the Way of St James where Charlemagne's rearguard "
            "was destroyed in 778, with a hostel for pilgrims, the Chapel "
            "of Puerto de Ibañeta and a stone where Roland is said to have "
            "fallen; the real battlefield is in the Valcarlos below, which "
            "Verditius magi visit for their mystery rites. Sancho VII gave the "
            "church part of his spoils from Las Navas de Tolosa, among them "
            "the great emerald from the sultan's turban, and it keeps Our "
            "Lady of Roncevaux, a cedar and silver statue a deer is said to "
            "have led the priests to. The Divine aura is 3 over the whole "
            "area, and 4 on the battle's anniversary.",
            "The Basques tell the battle as an ambush by lightly armed "
            "mountaineers; the Song of Roland makes it four hundred thousand "
            "Saracens. Both are told true: the Saracens came with Basque "
            "guides and jentil mercenaries. Faeries feed on the tale and draw "
            "mortals in to replay it, with Roland facing Moors or a band of "
            "Basques as suits the faeries' game.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        provence,
        "mount_urkulu",
        "The Tower on Mount Urkulu",
        inside=basque,
        summary=(
            "A half-ruined Roman tower on Mount Urkulu, looking north and "
            "south and down on the road through Roncevaux; many call it a "
            "Mercurian site. The sheriff's garrison keeps watch from it for "
            "travellers, but leaves smartly every Friday, when a busy coven "
            "of sorginak holds akelarre inside its walls, often calling up a "
            "wild aker to teach or serve, or using ecstatic magic to answer "
            "questions and pay back insults (a story seed)."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "caves_of_soule",
        "The Caves of Soule",
        inside=basque,
        summary=(
            "Soule's limestone hills, pitted with sinkholes and caverns, house "
            "a few drakes and worms said to be Sugaar's offspring, and a "
            "great many laminak, who are believed to teach their secrets to "
            "the Basque folk witches."
        ),
        **RUMOURED,
    )
    _add(
        provence,
        "caves_of_betharram",
        "The Caves of Betharram",
        inside=region,
        summary=(
            "A cave system on the northern, Toulousain side of the mountains, "
            "running nearly three kilometres underground through several big "
            "galleries along an underground river: a possible covenant site, "
            "if whatever drake or worm lairs there can be put out."
        ),
        **KNOWN_LOCALLY,
    )


# ---------------------------------------------------------- high peaks


def _high_pyrenees(provence: Provence) -> None:
    region = provence.places["pyrenees"]
    high = _add(
        provence,
        "high_pyrenees",
        "The High Pyrenees",
        inside=region,
        summary=(
            "The central range above Béarn and Bigorre, the wildest country "
            "in the Tribunal: glaciers and pine forest, the Cirque de "
            "Gavarnie, Mount Perditu and the Breach of Roland, and the "
            "distinctive peak of Pic du Midi d'Ossau, seen from Pau on a clear "
            "day. Aedes Mercurii holds both of its sites here, and Val-Negra "
            "lies lost among these peaks."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        provence,
        "mount_perditu",
        "Mount Perditu",
        inside=high,
        summary=paragraphs(
            "The highest mountain of the range, clad in pines and glaciers, "
            "and named the lost mountain for how far it lies from anywhere. "
            "It belongs with the Breach of Roland; its three summits are said "
            "to be three sisters whose faith and grief changed them when "
            "Visigoths razed their village. Pyrene's ghost (see the Cairn of "
            "Pyrene) is sometimes seen at its foot or at the Breach.",
            "Val-Negra, the fallen domus magna of House Flambeau, lies hidden "
            "in a regio on its slopes, two miles south of Aedes Mercurii's "
            "Templum.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        provence,
        "breach_of_roland",
        "The Breach of Roland",
        inside=high,
        aura=2,
        summary=paragraphs(
            "A notch forty paces wide between cliffs a hundred paces high, in "
            "the ridge above the Cirque de Gavarnie, which Roland is said to "
            "have cut when he tried to break Durendal as he lay dying, though "
            "Roncevaux is over a hundred miles off.",
            "Its aura of 2 is sometimes Magic and sometimes Divine, at random, "
            "which hints at something very strange.",
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "cairn_of_pyrene",
        "The Cairn of Pyrene",
        inside=high,
        aura=4,
        status="Rumoured",
        known="In the region",
        summary=paragraphs(
            "Pyrene's hidden tomb, somewhere deep in the range. The tale: "
            "Heracles, a guest at her father's court on his way to steal "
            "Geryon's cattle, seduced her in drink; she bore a serpent, fled "
            "to tell the trees her grief, and was torn apart by beasts. "
            "Heracles came back, heaped stones over what was left of her and "
            "commanded the land to keep her name, and the hills piled up "
            "stone on stone into the Pyrenees. Magical beasts are said to "
            "haunt the place, and the site, Magic 4, joins a network of regiones "
            "that runs through the whole range.",
            "Vis: on the night of her death her ghost weeps before the cairn "
            "until dawn, and the dew that gathers in a hollow of the boulder "
            "where she sits holds 4 pawns of Mentem vis (unclaimed).",
            "Pyrene the Spectre: a ghost of Magic Might 14 (Mentem), a pale, "
            "lovely, raven-haired woman in a torn linen dress, her lower legs "
            "mangled and her feet bloody, her face streaked with tears. She "
            "can turn invisible at will (Second Sight still sees her) and take "
            "solid form, calms and commands magical creatures, and knows the "
            "passes and the mountains' regio paths. She speaks Euskara, "
            "Occitan, Latin and Gothic, is grieving, reclusive and proud, "
            "fears daylight, and carries three pawns of Mentem vis in her "
            "dress.",
            "Story questions: what does she know of Heracles; what became of "
            "the serpent she bore, a vouivre perhaps; and could she be talked "
            "into sharing the regio network made when the mountains were "
            "born?",
        ),
    )


# ----------------------------------------------------------- Upper Aragon


def _upper_aragon(provence: Provence) -> None:
    region = provence.places["pyrenees"]
    aragon = _add(
        provence,
        "upper_aragon",
        "Jaca, Sobrarbe and Ribagorza",
        inside=region,
        summary=(
            "The mountain counties of the crown of Aragon, ruled by James I's "
            "regents until he comes of age. Jaca, also called the county of "
            "Aragon, once belonged to Navarre and became the core of the "
            "Aragonese kingdom; Sobrarbe and Ribagorza, joined by marriage "
            "since the tenth century, have many Basques and a remnant of "
            "Muslims living peaceably among the Christians, and Ribagorza "
            "holds the highest peaks of the range. South of the mountains."
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "mallos_de_riglos",
        "The Mallos de Riglos",
        inside=aragon,
        summary=paragraphs(
            "Near-vertical pillars of sedimentary rock in the foothills, some "
            "three hundred paces tall. Six miles east on a limestone bluff "
            "stands Castle Loarre, an eleventh-century fortress lately given "
            "new outer walls and towers by Pedro II, with its village beneath "
            "and a house of Augustinian canons from Montearagón inside.",
            "A Giant Witch (a story seed): the people of Loarre say a jentil "
            "sorgina lives among the pillars. She was once the witch of a "
            "village called Foz de Escalettes, but as her size showed the "
            "villagers fled, and she drew more rock up out of the ground to "
            "hide in. Magic auras and vis sources are common round her.",
        ),
        **RUMOURED,
    )


# -------------------------------------------------------------- Catalonia


def _catalonia(provence: Provence) -> None:
    region = provence.places["pyrenees"]
    catalonia = _add(
        provence,
        "catalonia",
        "The Catalan Counties",
        inside=region,
        summary=paragraphs(
            "The eastern Pyrenees under the crown of Aragon. Besalu, joined "
            "to Barcelona early in the twelfth century, is thick with "
            "monasteries (the nuns of Sant Joan de les Abadesses, Santa María "
            "de Ripoll, Bañolas, Camprodón, Sant Pau de Fenollet), and its "
            "northern castles of Tautavel, Vingrau, Queribus and Aguilar guard "
            "remote passes and now shelter Cathar refugees. Conflent, the Têt "
            "valley, is Nuno Sanche's, with strong castles and the fortified "
            "town of Villefranche-de-Conflent, under Mount Canigou.",
            "Cerdagne, also Nuno Sanche's, is still scarred by Raymond Roger "
            "of Foix's raids of 1195 to 1203, when he burned churches and "
            "attacked monasteries pressing his claim to Andorra; the crusade "
            "cut the recovery short, and most Divine auras here are fading "
            "remnants. Its Segre valley, the only one in the range that runs "
            "east to west, gets the sun and good harvests. Pallars is remote "
            "and snowbound in winter, all but ungoverned. Urgell is ruled "
            "from La Seu d'Urgell by the dying Countess Elvira.",
            "Contested County (a story seed): the Count of Ager claims "
            "Aurembiaix cannot inherit Urgell; if history runs its course he "
            "seizes the county in the winter of 1220 and she flees, a "
            "possible companion or patron. In 1228 James I has her marriage "
            "annulled, takes her as his mistress and confirms her rights for "
            "the town of Lleida. Several counties of Roussillon belong to "
            "the same lords and are told of with the Narbonnais.",
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "mount_canigou",
        "Mount Canigou",
        inside=catalonia,
        summary=(
            "The mountain filling Conflent's northern sky, with the abbeys of "
            "Saint-Martin-du-Canigou and Saint-Michel-de-Cuxa high on its "
            "flanks."
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "valleys_of_pallars",
        "The Valleys of Pallars",
        inside=catalonia,
        summary=(
            "Looking for a Lord (a story seed): a covenant in one of Pallars's "
            "many valleys or ruined keeps would be left alone for a good "
            "while, the land being remote and its count away at the crusade. "
            "That lasts until Roger II succeeds in 1234 and takes a close "
            "interest in the county and anyone governing it; meanwhile the "
            "covenant may have to compete for vis with the Basque sorginak or "
            "Dama's cult."
        ),
        **KNOWN_LOCALLY,
    )
    galamus = _add(
        provence,
        "galamus",
        "The Gorges de Galamus",
        inside=region,
        realm="Divine",
        aura=2,
        summary=paragraphs(
            "A stark, high-walled canyon where the Agly squeezes through the "
            "foothills, two days from Perpignan, with the hermitage of St "
            "Anthony clinging to its walls since at least the seventh "
            "century. The hermitage has a Divine aura of 2.",
            "At the entrance an old stone bears the word square SATOR AREPO "
            "TENET OPERA ROTAS, which some read as a line about the "
            "ploughman and the seed, and others as a charm to put out fire "
            "without water.",
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "magdalene_pool",
        "The Magdalene's Pool",
        inside=galamus,
        aura=3,
        summary=(
            "A pool deep in a cave below the hermitage, fed by a spring "
            "dedicated to Mary Magdalene, with a Magic aura of 3; it is said "
            "to heal."
        ),
        **KNOWN_LOCALLY,
    )


# ---------------------------------------------------------------- Andorra


def _andorra(provence: Provence) -> None:
    region = provence.places["pyrenees"]
    andorra = _add(
        provence,
        "andorra",
        "Andorra",
        inside=region,
        summary=paragraphs(
            "The last of Charlemagne's Pyrenean marches: five parishes "
            "(Canillo, Encamp, Ordino, La Massana and Sant Julià de Lòria), "
            "each a handful of mountain villages, about three thousand souls "
            "in all. No lord lives here; the Andorrans claim a charter from "
            "Charlemagne making them sovereign for their service against the "
            "Moors. The Bishop of Urgell and the Count of Foix both claim the "
            "land, neither can enforce it, and the Andorrans ignore them or "
            "set one against the other; the heaviest tribute anyone recalls "
            "was a present of hams and local produce.",
            "Small as it is, Andorra prospers, selling livestock, wool and a "
            "fine mountain wine on both sides of the range, and its rivers "
            "carry a modest trade route between Toulouse and Catalonia that "
            "keeps it independent but not cut off. Wealthy pilgrims linger "
            "for the scenery before going on west. Every Andorran, rich "
            "landowner or hired hand, counts himself his own sovereign.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        provence,
        "ordino",
        "Ordino",
        inside=andorra,
        aura=3,
        summary=(
            "The parish and village of Ordino in Andorra, where Bellaquin's "
            "large house stands in a pocket of Magic aura 3 among the "
            "villagers' homes; the covenant's fortified manor lies at the edge "
            "of town where a road climbs the mountain that overlooks most of "
            "Andorra. Bellaquin's grogs join the local militia's patrols."
        ),
        **KNOWN_TRIBUNAL,
    )


# ------------------------------------------------------------------ Niaux


def _niaux(provence: Provence) -> None:
    region = provence.places["pyrenees"]
    _add(
        provence,
        "niaux_cave",
        "The Cave of Niaux",
        inside=region,
        aura=4,
        summary=paragraphs(
            "A cave system in the hidden Vicdessos valley, about a day's "
            "ride south of Foix and a little north of Castle Miglos and "
            "the village of Niaux: three kilometres of galleries, "
            "formations and grottos, and above all paintings older than "
            "the Flood. The main gallery is covered with horses, oxen, "
            "bison, antelope and handprints, and more are scattered down "
            "the passages. The cave has a Magic aura of 4, the main "
            "gallery 5. Miniata Sophia lives here; the Redcaps record its "
            "site as the village of Niaux.",
        ),
        secrets=[
            titled(
                "The regio in the cave",
                "A regio lies in the Cave of Niaux, easily entered by magic at "
                "the new moon, the equinoxes and the solstices: an ancient "
                "magical form of the cave where shamans from before the Flood "
                "dance, drum and paint new pictures on the walls.",
            ),
            titled(
                "Stumbling in",
                "The only way to stumble into the regio of the Cave of Niaux is "
                "to drum or paint on the walls by firelight at a solstice.",
            ),
            titled(
                "The Criamon's last initiation",
                "The Criamon go to the regio of the Cave of Niaux for the last "
                "initiation of the Avenue of Adulation.",
            ),
        ],
        levels=[
            Builder.level(
                "The cave of the first painters",
                5,
                enter="By magic at the new moon, equinoxes and solstices; by "
                "drumming or painting by firelight at a solstice",
                notes="The book gives no aura; the main gallery's 5 is assumed.",
            )
        ],
        **KNOWN_TRIBUNAL,
    )


# ---------------------------------------------------------- Aedes Mercurii


def _aedes_mercurii(provence: Provence, b: Builder, tribunal: Tribunal) -> None:
    high = provence.places["high_pyrenees"]
    dorsum = _add(
        provence,
        "aedes_dorsum",
        "Aedes Mercurii: the Dorsum (Pic du Midi d'Ossau)",
        inside=high,
        aura=5,
        summary=paragraphs(
            "Aedes Mercurii's better-known site, carved into the summit of Pic "
            "du Midi d'Ossau, about ninety kilometres north-west of "
            "Val-Negra. It began in the early 900s as a garrison for "
            "Val-Negra's wars and has been enlarged ever since into a huge "
            "fortress of towers, domes and rotundas hollowed from the rock. "
            "Outside it is grim, reached by a narrow track winding along the "
            "chasms; inside its maze of halls clashes in every style, since "
            "each newcomer builds on. Nobody living there knows all it holds, "
            "and many labs and sanctums lie untouched since their owners died "
            "or passed into Twilight. The whole mountain has a Magic aura of "
            "5.",
            "It is called the Dorsum, the back of the temple, because the "
            "Templum is usually reached from here through a great Mercere "
            "Portal in an archway between two courtyards. Deep inside smoulders "
            "one of the forges of Hephaestus, kept by the priest of Vulcan.",
        ),
        **KNOWN_TRIBUNAL,
    )
    templum = _add(
        provence,
        "aedes_templum",
        "Aedes Mercurii: the Templum (Cirque de Gavarnie)",
        inside=high,
        aura=4,
        summary=paragraphs(
            "Aedes Mercurii's second site, a chapter of the covenant: plain "
            "low buildings round a majestic stone temple in the middle of the "
            "Cirque de Gavarnie, about two miles north of Val-Negra. The "
            "Temple of Mercury looks older than Christ; some say the old Order "
            "of Mercury built it, others that Priamitus and the Cult of "
            "Mercury's founders made it look ancient. It is three hundred feet "
            "long, ringed with carved columns, beautiful within, with old "
            "ancient altars all round, and its holy of holies lies eastward.",
            "The Magic aura is 4 across the Cirque and the outbuildings and 8 "
            "inside the temple itself. It is joined to the Dorsum by a Mercere "
            "Portal.",
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "The Cult of Mercury's covenant in the high Pyrenees, about eighteen "
        "magi on two sites joined by a Mercere Portal: the fortress of the "
        "Dorsum on Pic du Midi d'Ossau and the Templum in the Cirque de "
        "Gavarnie, close by the lost site of Val-Negra. Its device is a "
        "fiery dragon devouring its own tail.",
        "On the eve of the Schism War many of Val-Negra's Flambeau, moved "
        "by one magus's vision, left the domus magna with magi of other "
        "Houses and took over a nearby outpost and Val-Negra's lesser halls "
        "across the mountains, among them the great temple of Mercury that "
        "gave the covenant its name. When Val-Negra fell its survivors "
        "joined them, and Aedes Mercurii declared itself a Provençal "
        "covenant. After the war it put about that Val-Negra was gone and "
        "its legacy had passed to Aedes Mercurii, and its own heavy losses "
        "in the fighting made the claim believable. It is counted among the "
        "strongest covenants of the region, though nothing like Val-Negra "
        "at its height.",
        "Its magi hold themselves the last unbroken heirs of the Order of "
        "Mercury and each serves as a priest (flamen) of a Roman god fitting "
        "their magic. For most, the Tremere above all, this is ceremony: "
        "naming a patron god is like naming a spell for him, and the few true "
        "pagans are thought odd. The priests of Mars, nearly all Flambeau, "
        "and of Pluto, mostly Tremere, are the strongest factions; the "
        "Verditius keep a small priesthood of Vulcan; Aintza leads that of "
        "Janus, Ricardus serves Bacchus, and Midius is High Priest of "
        "Mercury and flamen of the Tribunal.",
        "Eleven magi live at the Dorsum and seven at the Templum, and the "
        "covenfolk split the same way. The two halves show one face to "
        "outsiders but have drifted apart since the war: the Templum's magi "
        "keep faith with what they see as the pagan, historical ways of the "
        "Order of Mercury, while the Dorsum's are united only by hatred of "
        "Castra Solis and their claim to Val-Negra's inheritance.",
        "Politically it is contentious and rebellious, the difficult "
        "stepchild of the Tribunal, which many think dangerous fanatics. It "
        "leads the conservative bloc of the mountains (with Ara Maxima Nova, "
        "Stella Durus and Miniata Sophia), holding that magi have no business "
        "in mundane quarrels and should wait out the crusade in their "
        "isolation, despises the Mithraian Flambeau of Castra Solis for "
        "calling their covenant the domus magna, and fights any new covenant "
        "in the region that will not ally with it, though its magi agree on "
        "nothing but blocking Castra Solis, so newcomers get mixed answers.",
    )
    what_matters = joined_lines(
        "Site: two sites joined by a Mercere Portal, the Dorsum fortress (aura 5) and the Templum (aura 4, 8 inside the Temple of Mercury)",
        "Vis: the book names no source",
        "Library: the casting notes of the Mercurian ritual Set the Stones of the Via, kept with reverence in the Templum",
        "Library: a copy of the lesser Mercurian ritual Link the Rent Path, unstudied for centuries",
        "Library: many books written by Malfortis, and Ricardus's tractatus",
        "Enchantment: one of the forges of Hephaestus, deep in the Dorsum, kept by Ruberus as priest of Vulcan",
        "Boon: Natural Fortress, Vast and Labyrinthine (the Dorsum), Mystical Portal (the Mercere Portal), Legendary Site (the Temple of Mercury), Ceremonies (the Mercurian rites)",
        "Hook: Fractured Council (Templum against Dorsum); Rival (Castra Solis); Pagans (a few true pagans among its priests); Hermetic Politics (leader of the conservative bloc)",
        "Tension: Flammarcus calls himself Pontifex Maximus and leader, but Oxioun led the covenant at the 1207 Tribunal and Ophilio's word would carry if he chose to use it",
        "Tension: the Dorsum's hatred of Castra Solis against the Templum's pagan traditionalism",
        "Tension: the Mercurians despise the Neo-Mercurian orders of other Tribunals as traitors and fools",
        "Hook: lost outposts at Saint Jean Pied-de-Port (razed 1177, perhaps with a lapis mercurius), north of Girona, and the portal to Val-Negra, abandoned when the Schism War began",
        "Hook: sanctums of magi dead or in Twilight, untouched in the Dorsum's depths",
        "Hook: Priamitus's original ritual scroll may lie hidden in Val-Negra",
    )
    notes = paragraphs(
        "Votes: 18 at Tribunal, the second bloc after the Coenobium "
        "(chapter three's table).",
        "Tribunals: it hosted the Tribunal of 1207, where Oxioun of Tytalus "
        "spoke at length for keeping out of mundane affairs. In 1214 the "
        "meeting moved from Toulouse to Castra Solis, to its anger, and its "
        "magi threatened to walk out, which could have voided the Tribunal; "
        "Tibaut and the Chief Redcap averted it. If the Tribunal of 1221 "
        "decides to act against the crusaders and the Church, the bloc it "
        "leads may boycott the 1227 meeting and, with the four covenants a "
        "Tribunal needs, ask the 1228 Grand Tribunal to let it secede.",
        "The Cult of Mercury (P13, a note, not a record): the rebirth of the "
        "Mercurian religion began at Val-Negra under Priamitus of Mercere "
        "with Apromor of Flambeau's support, flourished in the early 900s, "
        "and had split into many groups by the Schism War. The cult seeks "
        "the 37 Great Rites of the Roman priesthood; a few know non-Hermetic "
        "Mercurian rituals, worked only with the most loyal. Promising magi "
        "may be invited to join. Its flamen opens each day of Tribunal in "
        "masks and coloured robes, speaking for the gods; few take it "
        "seriously, the devout of Castra Solis think it blasphemy, yet the "
        "flamen have real hidden influence. The initiation into Mercurian "
        "Magic, the Consecration of Priamitus, ends at an ancient temple of "
        "Mercury such as this one on the Mercuralia, 15 May.",
        "After the Schism War a priest of Janus here, Petrarchus of "
        "Guernicus, tried to join the Way of St James to the Via Domitia by "
        "a Mercurian ritual into one great road network, and failed.",
    )
    hidden = [
        titled(
            "Protendus's office",
            "Protendus works as an unofficial, tacitly approved Quaesitor, "
            "against Tytalan influence from the north; he keeps it quiet by "
            "oaths enforced with certamen.",
        ),
        titled(
            "Ruberus and Garus",
            "Ruberus is secretly a friend of Garus, Primus of Flambeau.",
        ),
        titled(
            "Ruberus and Dama",
            "Ruberus secretly loves Dama, the Praeco.",
        ),
        titled(
            "Flammarcus's ambition",
            "Flammarcus may stop at nothing to become Primus when Garus dies.",
        ),
    ]
    aedes = b.covenant(
        "Aedes Mercurii",
        tribunal=tribunal,
        founded=1003,
        place=dorsum,
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(
            notes,
            "The book gives no founding year (the split came just before the "
            "Schism War; 1003 is assumed) and no season (Autumn is assumed).",
        ),
        secrets=hidden,
        aura=5,
        season="Autumn",
        unnamed_magi=7,
    )
    provence.covenants["aedes_mercurii"] = aedes
    Builder.link(templum, "covenants", aedes, "A chapter of Aedes Mercurii")
    Builder.link(dorsum, "places", templum, "Joined by a Mercere Portal")
    _aedes_magi(provence, b, aedes)
    b.book(
        aedes,
        "Set the Stones of the Via (casting notes)",
        "Other",
        description=(
            "Notes and details for casting the great Mercurian ritual that "
            "lays down a via mercuria of enchanted Roman milestones (a "
            "non-Hermetic ritual, Effect level 36, a season's work needing 36 "
            "pawns of vis and 36 pounds of silver in materials). Kept in the "
            "Templum. As a source of Insight for integrating True Mercurian "
            "Road Magic it adds 6 to the roll (Ancient Magic). Another copy "
            "may be in Fenicil's library at Magvillus, and Priamitus's "
            "original scroll may be hidden in Val-Negra."
        ),
    )
    b.book(
        aedes,
        "Link the Rent Path",
        "Other",
        description=(
            "A copy of the lesser Mercurian ritual (ReTe(Cr), Ease Factor 18) "
            "that joins separate viae mercuriae, ties a new lapis mercurius "
            "into a network, or replaces one lost milestone; kept in the "
            "Templum and unread for centuries, the old roads being broken. "
            "Adds 3 as a source of Insight into True Mercurian Road Magic."
        ),
    )
    b.book(
        aedes,
        "The library of Aedes Mercurii",
        "Other",
        description=(
            "The covenant's library, inherited in part from Val-Negra's "
            "halls; the book names no titles beyond the Mercurian rituals. "
            "Malfortis has written many of its books, and Ricardus fills it "
            "with tractatus most of the Dorsum find distasteful. Berezi the "
            "Redcap brings books for the western magi from the Roman "
            "Tribunal."
        ),
    )


def _aedes_magi(provence: Provence, b: Builder, aedes: Covenant) -> None:
    m = provence.magi
    m["flammarcus"] = b.magus(
        "Flammarcus",
        covenant=aedes,
        house=FLAMBEAU,
        age=121,
        summary=paragraphs(
            "Priest of Mars at the Dorsum, who looks about seventy-five, "
            "styles himself Pontifex Maximus and thinks himself the "
            "covenant's leader. Like many at the Dorsum he is a Christian "
            "and treats the priesthood as ceremony. He worships the memory "
            "of Flambeau the Founder and holds that Castra Solis has "
            "corrupted the Founder's story: his research says Flambeau was "
            "no Mithraian but a Mercurian who held some of the Order of "
            "Mercury's lost rites. Most magi think him overzealous and "
            "cannot see why it matters so to him. He burns to become "
            "Primus of Flambeau as soon as Garus dies.",
        ),
        secrets=[
            titled(
                "How far Flammarcus would go",
                "He may be willing to do anything at all to become Primus of Flambeau.",
            ),
        ],
        traits={"Passionate": 2, "Ruthless": 2},
    )
    m["protendus"] = b.magus(
        "Protendus",
        covenant=aedes,
        house=TREMERE,
        age=112,
        summary=paragraphs(
            "The senior Tremere of the Tribunal (he looks eighty-three), "
            "priest of Pluto on the covenant's council, and said to be a "
            "necromancer without equal. He answers, with some "
            "reluctance, to the exarch of Iberia, who he thinks resents "
            "the House's weakness in Provence. He has trained several "
            "apprentices and urges young Tremere to make their names, but "
            "the House's last venture, Lariander, vanished twenty years "
            "ago, and he suspects the crusaders and the Merinita around "
            "Castra Solis. He belongs to the Vexillation of the Golden "
            "Thread, a secret Tremere society sworn to foil the schemes of "
            "House Tytalus. Though he holds six sigils he mostly stays out "
            "of Tribunal politics, abstaining unless his House is touched "
            "or a Tremere warns him. He is the likeliest magus to look "
            "into the deaths of Senex and Tibaut.",
        ),
        secrets=[
            titled(
                "Protendus's office",
                "He acts as an unofficial Quaesitor, tacitly allowed, whose "
                "rank and secrecy let him investigate discreetly and by methods "
                "Quaesitors would not use; he guards the secret with oaths "
                "backed by certamen.",
            ),
            titled(
                "Protendus and the Tytali",
                "He has kept the northern Tytali from gaining a foothold so "
                "far, but suspects they now work through the Mithraian Flambeau "
                "of Castra Solis.",
            ),
        ],
        traits={"Reclusive": 2, "Secretive": 2},
    )
    m["ophilio"] = b.magus(
        "Ophilio",
        covenant=aedes,
        house=MERCERE,
        age=172,
        summary=(
            "A Gifted Mercere of the Templum, looking eighty-five, long the "
            "High Priest of Mercury and now retired, and one of his House's "
            "longevity specialists. The other magi respect him and step "
            "carefully round him; he seldom comes to council and would rather "
            "spend his time among the covenfolk, but authority he chose to "
            "claim would be accepted, if grudgingly."
        ),
        traits={"Gregarious": 2, "Opinionated": 2},
    )
    m["midius"] = b.magus(
        "Midius",
        covenant=aedes,
        house=FLAMBEAU,
        age=94,
        summary=(
            "High Priest of Mercury, keeper of the Templum and flamen of the "
            "Provençal Tribunal, who opens each day of its meetings with the "
            "Cult's rite; he looks about fifty. After many years under "
            "Ophilio in the temple he still feels himself the old magus's "
            "subordinate and longs to impress him, and he attends Tribunal "
            "in Ophilio's place."
        ),
        traits={"Loyal": 2, "Submissive": 2},
    )
    m["pila"] = b.magus(
        "Pila",
        covenant=aedes,
        house=FLAMBEAU,
        age=103,
        summary=(
            "Priest of Mars at the Dorsum, in charge of the covenant's "
            "defences, which she takes very seriously, fanatically some "
            "would say. She stands firmly behind Flammarcus and his version "
            "of the Founder's story, counts herself a true Hoplite in the old "
            "sense of the word, and goes into battle armed like a Greek foot "
            "soldier; otherwise she seems mild and unremarkable, looking "
            "about seventy-nine."
        ),
        traits={"Courageous": 2, "Dedicated": 2},
    )
    m["malfortis"] = b.magus(
        "Malfortis",
        covenant=aedes,
        house=FLAMBEAU,
        age=87,
        summary=(
            "Another priest of Mars, though no warmonger: an excellent "
            "teacher and a strong writer who has filled the library with "
            "books, and who answers every letter at length, if seldom warmly. "
            "He backs Flammarcus's view of the Founder. Unusually for a "
            "Flambeau he fights with his bare hands, and he specialises in "
            "Corpus. He looks forty-four."
        ),
        traits={"Engaging": 2, "Expressive": 2},
    )
    m["ricardus"] = b.magus(
        "Ricardus",
        covenant=aedes,
        house=FLAMBEAU,
        age=82,
        summary=(
            "Priest of Bacchus at the Dorsum, looking forty-two, openly "
            "homosexual and rumoured to have lusty tastes. Most of the "
            "Dorsum dislike his company and his interests, above all the "
            "many tractatus he writes on them, but he is sociable and has a "
            "hand in nearly everything the council does, so at Tribunal he is "
            "often supported, uncomfortably. He is said to be skilled in Creo "
            "and Mentem."
        ),
        traits={"Disturbing": 2, "Sensual": 2},
    )
    m["aintza"] = b.magus(
        "Aintza",
        covenant=aedes,
        house=EX_MISC,
        age=87,
        summary=paragraphs(
            "One of the few priestesses at Aedes and head of the priesthood of "
            "Janus, living at the Templum with the other haruspices. She is a "
            "Hermetic Haruspex, one of a small band of oracular magi said to "
            "have been offered a place in House Flambeau who refused it for "
            "Ex Miscellanea. She thinks nothing of the difference between the "
            "sexes and blames her lower standing on her House, not on being a "
            "woman. She is a pagan and the chief mystagogue of the covenant's "
            "Neo-Mercurian branch. She looks fifty-nine.",
            "Her familiar Elias is a magical cat with two mouths, two noses "
            "and three eyes, which she believes an aspect of Janus inhabits; "
            "she makes a point of including him in all her magic.",
        ),
        traits={"Combative": 2, "Mysterious": 2},
    )
    m["ruberus"] = b.magus(
        "Ruberus",
        covenant=aedes,
        house=VERDITIUS,
        age=99,
        summary=paragraphs(
            "Priest of Vulcan and keeper of the forge of Hephaestus deep "
            "in the Dorsum, and head of the Confraternity of Roland, "
            "Verditius magi who make magic swords (Houses of Hermes: "
            "Mystery Cults). He looks forty-one. One of the few at Aedes "
            "with no grudge against Castra Solis, he admires and respects "
            "Garus, the Flambeau Primus, but the forge obliges him to stay "
            "on good terms with his covenant-mates.",
        ),
        secrets=[
            titled(
                "Ruberus and Garus",
                "He hides his friendship with Garus.",
            ),
            titled(
                "Ruberus and Dama",
                "He admires and secretly loves Dama, the Praeco, and would do "
                "nearly anything to protect her.",
            ),
        ],
        traits={"Conciliatory": 2, "Relaxed": 2},
    )
    m["oxioun"] = b.magus(
        "Oxioun",
        covenant=aedes,
        house=TYTALUS,
        age=None,
        summary=(
            "A Tytalus named as leader of Aedes Mercurii at the Tribunal of "
            "1207, which the covenant hosted, where he argued at length that "
            "magi must keep out of mundane affairs; he and the Mercurian bloc "
            "were content to wait out events in their mountains. The book "
            "lists him as a possible parens for Tytalus characters and says "
            "nothing more of him."
        ),
    )
    m["berezi"] = b.magus(
        "Berezi",
        covenant=aedes,
        house=MERCERE,
        age=48,
        summary=(
            "A Redcap resident at the Dorsum, looking thirty-five, descended "
            "from one of the Milvi Antiquiti (Houses of Hermes: True "
            "Lineages). She often spends her two seasons of service carrying "
            "books between Aedes Mercurii and her mother's covenant in the "
            "Roman Tribunal for the magi of western Provence, and owns a magic "
            "device that turns her, and whatever she carries, into a bird."
        ),
        traits={"Prone to Wanderlust": 2, "Proud": 2},
    )


# ---------------------------------------------------------------- Bellaquin


def _bellaquin(provence: Provence, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "A Jerbiton covenant of five magi in a large house in the village of "
        "Ordino, Andorra: remote, yet deep in both mundane and Hermetic "
        "business. Its device is a red plumed hawk holding a scroll within a "
        "gold ring.",
        "It was founded in 1016, late in the Schism War, by Flambeau who "
        "rebuilt an abandoned castle by magic as a stronghold, the Chateau de "
        "Penne in Tarn, high above the Aveyron a day north-north-east of "
        "Toulouse. The war ended before it fought, the Flambeau left, and the "
        "Jerbiton have held it since. The castle was famed as one of the "
        "loveliest seats of the Order. Peasants settled round it, the magi "
        "found themselves managing land, then playing at lords over a private "
        "fief with vassals and puppet domains granted to friends. Jealous "
        "neighbours twice charged them with breaking the Oath, and twice the "
        "Tribunal found they had brought no ruin on their sodales; they "
        "stayed just inside the Code and were prized as a bridge between "
        "mundane and Hermetic society.",
        "In the end their feudal ties caught them between two warring allies. "
        "Helping either would break the Code, helping neither would break "
        "their oaths, and their compromise, paying scutage to both and "
        "selling healing elixirs to both, convinced both sides, egged on by "
        "senior churchmen who wanted the magi gone, that Bellaquin had "
        "stirred up the war for profit. A surprise assault, helped by a "
        "treacherous companion, destroyed the castle and killed several magi; "
        "possibly other magi arranged it. Archmagi had advised a fallback, "
        "and the survivors took what they could from hidden reserves, "
        "destroyed the rest, left the site to mundane proxies and moved to "
        "Andorra in 1202. No one brought charges, since the damage fell only "
        "on Bellaquin.",
        "Twenty years on it is richer than ever on a smaller scale, and many "
        "call it a new covenant that had a quick spring and summer after the "
        "old one's winter; its magi hold that nothing broke but the address, "
        "and they kept their charter. Locally they pass for kindly rich "
        "outsiders who bring distant merchants' trade; in the Order they "
        "cultivate an air of casual indifference and some unhealthy "
        "stubbornness. No trade happens at the covenant, but it sits at the "
        "centre of a merchant network on both sides of the mountains reaching "
        "to Germany and Italy, and it banks for magi and mundanes alike: not "
        "lending, but moving funds across distances as the Templars do, by "
        "magic, to an agreed place at agreed times, or with more effort almost "
        "anywhere.",
        "Of the old members only Valgravian remains, with Antoinette, filia "
        "of an old member; three died in the attack, two left the Tribunal, "
        "and three more have since died or passed into Twilight. Bellaquin "
        "has room and wealth for more and would welcome promising young magi.",
    )
    what_matters = joined_lines(
        "Vis: nearly 100 pawns in store, and sources yielding about 30 pawns a year (not named)",
        "Income: banking, moving funds for magi and mundanes; a merchant network from Iberia to Germany and Italy",
        "Income: the Andorrans' fairs, where Castra Solis and Ara Maxima Nova send agents to gather news",
        "Defence: an Aegis of the Hearth of the 8th magnitude; the Andorra Company of almogavars; a fortified manor above the town",
        "Laboratories: every magus's lab customised, with one empty lab used as a storeroom",
        "Boon: Wealth, Hermetic Services (banking), Veteran Fighters (the almogavars), Local Ally (the Andorrans)",
        "Hook: Infamous (the fall of its first site); Mundane Politics; Divided Loyalty (three rival groups of covenfolk)",
        "Ambition: a Catalan Tribunal; more magi in the region mean more influence",
        "Tension: Valgravian feels a stranger among the newer members and misses the poets and musicians of old",
        "Tension: Antoinette's hidden love for Captain Michael, and Michael and Artemis's unspoken attraction",
    )
    notes = paragraphs(
        "Votes: 5 at Tribunal. Bellaquin likes new covenants: the more the merrier.",
        "Covenfolk: three groups who do not much like each other. The "
        "almogavars of the Andorra Company replaced the old turb as custodes "
        "when Robert came; the original covenfolk, few, ageing and mildly "
        "resentful, stayed on in other roles; and the largest group are "
        "Ordino Andorrans working for wages, a few as specialists. Newer "
        "magi brought their own shield grogs: Artemis is always guarded by "
        "two lean, leather-clad men trained at Coeris whom she calls the "
        "Danior, and Antoinette brought back four Scandinavian warrior women "
        "from an Itinerarium as sanctum guards, to impress Michael and outdo "
        "the Tremere.",
        "Tolomae, the Cathar sympathiser who led the Procrustean League and "
        "urged open war on the Church, is called Tolomae of Bellaquin; House "
        "Jerbiton cast him out in 1216, and he was Marched and slain early in "
        "1218 (chapter three also calls the Coenobium his former covenant).",
    )
    hidden = [
        titled(
            "What the Danior are",
            "Rumour says the Danior are homunculi, less open to Mentem magic, "
            "easily mended, and with a bloody habit of twisting Artemis's "
            "orders.",
        ),
        titled(
            "Antoinette's affair",
            "Antoinette fears Michael will learn of her affair with Carolus of "
            "the Rhine Tribunal during a Jerbiton fosterage at Oculus "
            "Septentrionalis.",
        ),
        titled(
            "The fall of the first Bellaquin",
            "Other magi may have engineered the fall of the first Bellaquin.",
        ),
    ]
    bellaquin = b.covenant(
        "Bellaquin",
        tribunal=tribunal,
        founded=1016,
        place=provence.places["ordino"],
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        aura=3,
        season="Autumn",
    )
    provence.covenants["bellaquin"] = bellaquin
    _bellaquin_magi(provence, b, bellaquin)
    b.book(
        bellaquin,
        "The library of Bellaquin",
        "Other",
        description=(
            "What the survivors carried from the Chateau de Penne in 1202, "
            "and what two decades of wealth have added; the book names no "
            "books. Valgravian's own spells to make and enhance music would "
            "be found here as Lab Texts, and Stella Durus sends Jean Marie's "
            "paradoxographia and letters on gossip and courtly love."
        ),
    )


def _bellaquin_magi(provence: Provence, b: Builder, home: Covenant) -> None:
    m = provence.magi
    m["valgravian"] = b.magus(
        "Valgravian",
        covenant=home,
        house=JERBITON,
        age=114,
        summary=paragraphs(
            "Archmage, the oldest magus of the covenant and an immigrant from "
            "the Rhine Tribunal, who looks seventy-seven. He drew up the "
            "contingency plan that saved Bellaquin and led it through the "
            "move. He still keeps distant contact with a few noble friends, "
            "far more carefully than before, giving only advice and Longevity "
            "Rituals to the two or three closest. He devotes himself to "
            "running the covenant smoothly, leaves members wide freedom in "
            "their offices, but keeps talking to them about their tasks, "
            "which some find tiresome; he is a brother to the older members "
            "and a father to the younger.",
            "An old friend of Constantine who has known Antoinette since her "
            "birth, he hardly knows the others and sometimes feels a stranger "
            "at home; he remembers Bellaquin as a covenant of poets and "
            "musicians and misses the troubadours. His magic centres on music "
            "(a Minor Magical Focus): spells to make or enrich music, and a "
            "necklace that records the wearer's performance and plays it back. "
            "His archmage's challenge is a performance that moves him to "
            "tears. His sigil: horns faintly sounding a fanfare.",
        ),
        traits={
            "Dedicated to the prosperity of Bellaquin": 3,
            "Compassion for old friends": 1,
        },
    )
    m["constantine"] = b.magus(
        "Constantine",
        covenant=home,
        house=JERBITON,
        age=67,
        summary=(
            "A merchant and master banker, looking forty-nine, who runs "
            "Bellaquin's transfers through a network of trusted contacts built "
            "on his travels and his Imaginem magic. An old friend of "
            "Valgravian, he sold off and moved old Bellaquin's assets and "
            "made the covenant a rich Andorran landowner; he imagined its "
            "present shape but leaves management to Valgravian and minds the "
            "money. Strict and serious, and daunting to young magi, he grows "
            "merry among friends and family, helps his sodales gladly but "
            "expects favour for favour, and collects coins, especially from "
            "far or ancient lands. Antoinette is his daughter. His sigil is a "
            "light dusting of gold on the target or in the air about him."
        ),
        traits={"Avarice": 3, "Gluttony": 2, "Jovial": 1, "Serious": 1},
    )
    m["robert_vasquez"] = b.magus(
        "Robert Vasquez",
        covenant=home,
        house=FLAMBEAU,
        age=59,
        summary=(
            "The covenant's champion, looking forty-two, invited by "
            "Valgravian for his name as a skilled fighter and an honourable "
            "magus; his Gentle Gift suited Valgravian's vision. He insisted "
            "Bellaquin also take in Artemis to help him, recruited the "
            "almogavars of the Andorra Company and is their overall commander, "
            "and means to give every soldier at least one lesser enchanted "
            "device, a task barely begun. A widower whose wife died in "
            "childbirth, he brought two children: Michael, unGifted, now "
            "captain of the guard, and Carmen, who finished her apprenticeship "
            "here, was Gauntleted five years since and has gone from the "
            "Tribunal. His sigil leaves a faint taste of ash on the air."
        ),
        traits={
            "Brave": 3,
            "Protective of children": 3,
            "Honorable": 2,
            "Overconfident": 1,
        },
    )
    m["artemis"] = b.magus(
        "Artemis",
        covenant=home,
        house=TREMERE,
        age=49,
        summary=paragraphs(
            "Bellaquin's Guardian, in charge of its security, a "
            "Blatantly Gifted Tremere invited at Robert's insistence for "
            "her name for dedication and discipline. She looks "
            "thirty-three, is strong in Corpus, and is second in command "
            "of the Andorra Company, working closely with Captain "
            "Michael; the two are drawn to each other and will not admit "
            "it, out of duty and propriety. Two guards trained at Coeris, "
            "the Danior, never leave her side. Her sigil is a dull ache in "
            "the teeth of those she targets or stands near as she casts.",
        ),
        secrets=[
            titled("What the Danior are", "The Danior may be homunculi of her making."),
        ],
        traits={"Disciplined": 3, "Loyal to Order of Hermes": 3},
    )
    m["antoinette"] = b.magus(
        "Antoinette",
        covenant=home,
        house=JERBITON,
        age=26,
        summary=paragraphs(
            "Constantine's daughter (chapter three gives her surname as "
            "LeBarre), eight when the first covenant fell, who has known "
            "only Andorra and was apprenticed here; she has the Gentle "
            "Gift and is a budding Imaginem specialist whose sigil is "
            "barely audible whispers. She has long loved Captain Michael "
            "in secret, watching him grow into a bold, able man, and has "
            "thought of telling him, since she could give him children and "
            "her father grandchildren, but fears what Artemis would do. "
            "She would seek out a Verditius to arm Michael's soldiers, or "
            "a certamen master to teach her to beat Artemis or find the "
            "Tremere's weak Arts.",
        ),
        secrets=[
            titled(
                "Antoinette's fling",
                "She also fears Michael will learn of her fling with Carolus of "
                "the Rhine Tribunal during a Jerbiton fosterage at Oculus "
                "Septentrionalis.",
            ),
        ],
        traits={"Creative": 2, "Expressive": 2},
    )


# --------------------------------------------------------- Miniata Sophia


def _miniata_sophia(provence: Provence, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "A young Criamon covenant of four magi in the cave of Niaux, in the "
        "hidden Vicdessos valley about a day's ride south of Foix. Its device "
        "is a white hand, fingers raised and spread, on an ochre disc. It was "
        "founded about forty years ago by the eremite Leonarda, drawn by the "
        "cave's paintings, and announced itself at the Tribunal of 1193, "
        "registering its site with the Redcaps as the village of Niaux.",
        "Its magi seldom leave the cave and the hills round it, yet they have "
        "come to the last four Tribunals, always voting and arguing with "
        "knowledge. They make no alliances and show no leanings: they vote "
        "for whatever seems most morally apt, or abstain, and generally hold "
        "no opinion of other magi, who mostly return the favour. Some call "
        "it an underground reflection of the Cave of Twisting Shadows.",
        "Their Path is their own version of Walking Backwards (see "
        "Houses of Hermes: Mystery Cults) and live self-sufficiently, troubling the "
        "village as little as they can. Each magus in turn spends a season "
        "living in Niaux as a guest of the villagers, sharing Parma with a "
        "village ambassador and helping with whatever the town needs, "
        "keeping magic out of sight and working the most useful spells after "
        "dark; that season they do no lab work and wear leper's robes, to hide "
        "any Enigmatic stigmata and keep strangers off, which supports the "
        "story that they are hermits seeking enlightenment in the cave. Every "
        "third day the magus in the village brings supplies to the cave "
        "mouth, where another meets them. The season serves newcomers as the "
        "Avenue of Surrender and Station of the Service to Harmony, and "
        "reminds the rest of that lesson.",
        "The rest of the year they study their Arts, the texts they trade "
        "by letter, and the paintings, seeking the magic hidden in the "
        "pigments. Leonarda holds the paintings to be an expression of the "
        "Enigma and has woven them into three later initiations "
        "(the Avenues of Healing, of Adulation and of a Thousand Beautiful "
        "Faces, with their Stations). The last Avenue, which ends at the "
        "Threshold of Repose, is still ahead of her, and she cannot yet see "
        "how the paintings would fit it.",
        "There are no grogs: the Criamon feel no need. Arnaud de Miglos, the "
        "local viscount and Foix's vassal, protects the village from his "
        "garrisoned castle, and the villagers, who supply the covenfolk "
        "mostly at second hand, always pay their taxes promptly and so draw "
        "no notice. A few covenfolk are hunters who could fight if they had "
        "to and keep watch only as they range; a couple of well-travelled "
        "ones fetch things the magi want; and the little community sends out "
        "small loads of iron mined in the hills and worked into ingots and "
        "rods.",
    )
    what_matters = joined_lines(
        "Income: iron mined in the hills and worked into ingots and rod stock",
        "Library: texts traded by correspondence; the cave paintings themselves, studied as the Enigma",
        "Mystery: the Path of Walking Backwards, with the paintings built into later initiations",
        "Boon: Regio (the painters' cave); Seclusion; Local Ally (Niaux and Arnaud de Miglos)",
        "Hook: Hidden Resources; Missing Aura in the village; Mundane Politics (the French crown's claims on Foix after 1226)",
        "Ally: the Redcap Embeth, who visits twice a year and points interested Criamon to Niaux after vetting them",
        "Rule: an outsider must earn deep trust before visiting even the covenfolk in Niaux; a magus arriving by chance is welcomed but must swear never to reveal the site",
    )
    notes = paragraphs(
        "Votes: 4 at Tribunal, cast for the most morally apt course or not "
        "at all. In 1221 they are expected to side with the conservatives "
        "who would wait out the crusade.",
        "Story seeds. Multiplicity of Wisdom: someone after the secrets "
        "of Fertility magic (Ancient Magic) may try to find the covenant "
        "after meeting its members at Tribunal. The French king may try to "
        "seize Niaux in 1226 or 1227 when the Count of Foix resists royal "
        "claims, perhaps with inquisitors hunting Cathars, the count's wife "
        "being one. Aptly Put: a case the characters must win at Tribunal "
        "needs Miniata Sophia's votes, so they must show their cause is the "
        "apt one, or their opponents' the base one, by digging at the "
        "gathering itself.",
    )
    miniata = b.covenant(
        "Miniata Sophia",
        tribunal=tribunal,
        founded=1180,
        place=provence.places["niaux_cave"],
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(notes, "Founded about forty years before 1220."),
        aura=4,
        season="Spring",
        unnamed_magi=1,
    )
    provence.covenants["miniata_sophia"] = miniata
    m = provence.magi
    m["leonarda"] = b.magus(
        "Leonarda",
        covenant=miniata,
        house=CRIAMON,
        age=89,
        summary=(
            "Founder of Miniata Sophia, from Aragon across the mountains, who "
            "looks fifty-seven. Soon after her Gauntlet a fellow Criamon at "
            "the Cave of Twisting Shadows told her of the painted caves; "
            "wanting a new road along her Path and believing the first homes "
            "of mankind held old wisdom, she wandered until she found Niaux. "
            "She befriended the villagers, who were glad of her help many "
            "times, and her skill in Creo, Rego, Corpus and Vim built the "
            "ties that keep the covenant so well informed: for two visits a "
            "year she gave the Redcap Embeth a Longevity Ritual and boots "
            "that work the Leap of Homecoming."
        ),
        traits={"Pious": 3, "Calm": 2, "Nurturing": 2, "Patient": 2},
    )
    m["tumbarius"] = b.magus(
        "Tumbarius",
        covenant=miniata,
        house=CRIAMON,
        age=40,
        summary=(
            "A Mentem specialist from Northumbria who works with ghosts and "
            "spirits, and treats them callously, since they will have another "
            "chance in the next Cycle. Nominally Christian, he hunts for "
            "epiphanies in ancient philosophy, apocrypha, Judaism and Islamic "
            "learning, and has begun writing to kabbalists in Arles to work "
            "the Tree of Life into his labyrinthine meditations. Bad arthritis "
            "plagues him, worst in the winters he spends in Niaux."
        ),
        traits={"Open-minded": 3, "Inquisitive": 2, "Ruthlessly dedicated": 2},
    )
    m["hans"] = b.magus(
        "Hans",
        covenant=miniata,
        house=CRIAMON,
        age=54,
        summary=(
            "Second son of an Aachen merchant, put in a seminary as a boy until "
            "a visiting Criamon who could sense the Gift offered him another "
            "life. He looks forty, is endlessly curious and a student of "
            "languages, and loves his seasons in Niaux, where the children call "
            "him Grandfather Hans; his Gentle Gift makes him the village's "
            "favourite ambassador. He means to enjoy this life to the full and "
            "live as aptly as he can while seeking the Enigma, and is in no "
            "hurry along the Path. His Arts are Rego, Imaginem and Terram."
        ),
        traits={"Cheerful": 3, "Sociable": 2, "Curious": 2},
    )


# ------------------------------------------------------------------ lords


def _lords(provence: Provence, b: Builder) -> None:
    w = provence.world
    p = provence.places
    w["castile"] = b.lord(
        "King of Castile",
        title="duke",
        wealth="Wealthy",
        manors=40,
        seat="Burgos",
        ruler="Ferdinand III",
        place=p["pyrenees"],
        arms=Arms("Gules", charge="Tower", charge_tincture="Or"),
        summary=paragraphs(
            "Ferdinand III, son of the King of León, has held Castile since "
            "1217, when his mother gave it up to him after her young brother "
            "Henry I, thirteen, was killed by a falling roof tile. Henry's "
            "father Alfonso VIII, a champion of the Reconquista and founder "
            "of the Order of Santiago, took Álava, Gipuzkoa and Biscay from "
            "Navarre by force while Sancho VII was in Africa seeking Almohad "
            "help. Ferdinand claims overlordship of Navarre, which renewed its "
            "vassalage and joined Castile, Aragon and Portugal against the "
            "last Almohads. South of the mountains.",
            "The arms are Castile's castle, drawn as a tower.",
        ),
    )
    w["navarre"] = b.lord(
        "King of Navarre",
        title="duke",
        wealth="Wealthy",
        seat="Pamplona",
        ruler="Sancho VII",
        answers_to=w["castile"],
        place=p["basque_country"],
        summary=(
            "Sancho VII has lived retired in the monastery of Tudela since "
            "his victory at Las Navas de Tolosa (1212). He is Richard the Lionheart's "
            "brother-in-law (Richard married his sister Berengaria, the queen "
            "of England who never saw England) and kept good terms with King "
            "John; Alfonso VIII of Castile was at once his cousin, his "
            "brother-in-law and by turns his foe and ally. His sister, the "
            "regent Blanca, minds the war in the south, and his brother "
            "Ramiro, Bishop of Pamplona, wields most authority in the capital. "
            "The crown holds Lower Navarre through a sheriff."
        ),
    )
    w["lower_navarre"] = b.lord(
        "Sheriff of Lower Navarre",
        title="landed",
        ruler="the king's sheriff",
        answers_to=w["navarre"],
        place=p["basque_country"],
        summary=(
            "Lower Navarre has no lord of its own: a royal sheriff collects "
            "the taxes and keeps the king's law in its towns and hamlets, and "
            "his garrison watches the Roncevaux road from the tower on Mount "
            "Urkulu, except on Fridays."
        ),
    )
    w["biscay"] = b.lord(
        "Lord of Biscay",
        title="baron",
        wealth="Wealthy",
        ruler="Diego López",
        answers_to=w["castile"],
        place=p["basque_country"],
        summary=(
            "Diego López led the vanguard at Las Navas eight years ago and, "
            "with his kin, claims descent from Jaun Zuria, the White Lord, "
            "first lord of Biscay, whose true father was the dragon Sugaar in "
            "human shape. The dragon's blood may run on in the line as "
            "Mythic Blood, Magic Blood or Blood of Heroes. Castile annexed "
            "Biscay, Álava and Gipuzkoa in 1200."
        ),
    )
    # Gascony makes the Count of Labourd; the Pyrenees add his feud.
    w["labourd"] = w["count_labourd"]
    w["labourd"].summary += (
        " With Bayonne's trade tied to Cornwall and Aquitaine he has "
        "little hope of it back; bitter, he thinks of buying the "
        "sorginak's curses to bring the town to heel."
    )
    w["soule"] = b.lord(
        "Viscount of Soule",
        title="baron",
        seat="Mauléon",
        ruler="Ramon Guillem IV",
        place=p["basque_country"],
        summary=(
            "Ramon Guillem IV, viscount since 1217, rules the Basque "
            "viscounty between the Oloron (the border with Béarn), Lower "
            "Navarre and the valleys of Barétous and Salazar, from Mauléon."
        ),
    )
    w["aragon"] = b.lord(
        "King of Aragon and Count of Barcelona",
        title="duke",
        wealth="Wealthy",
        manors=40,
        seat="Zaragoza",
        ruler="James I (a minor, under regents)",
        place=p["catalonia"],
        summary=(
            "The crown of Aragon unites the kingdom of Aragon and the county "
            "of Barcelona. Pedro II the Catholic, husband of Marie of "
            "Montpellier, died fighting Simon de Montfort at Muret in 1213, "
            "and his son James I, twelve, lives at Zaragoza. His great-uncle "
            "Sancho of Barcelona, Count of Roussillon and Cerdagne, and "
            "Sancho's son Nuno Sanche, who holds Conflent, Cerdagne, "
            "Vallespir and Roussillon, are regents (both described with the Narbonnais). "
            "Loyal nobles plan to marry James to Eleanor, daughter of Alfonso "
            "VIII of Castile, on his thirteenth birthday in 1221, to steady "
            "the realm until he comes of age in 1223. The crown claims Jaca, "
            "Sobrarbe and Ribagorza, Besalu, Urgell and Pallars."
        ),
    )
    aragon = w["aragon"]
    w["pallars"] = b.lord(
        "Count of Pallars",
        title="count",
        ruler="Roger I de Pallars",
        answers_to=aragon,
        place=p["valleys_of_pallars"],
        summary=(
            "Roger I, brother of the Count of Comminges, married the countess "
            "in 1217; she cares only for scripture and not at all for "
            "ruling, and he is away fighting the Cathars with the crusade, "
            "so Pallars goes almost ungoverned. His son Roger II succeeds in "
            "1234 and is far more watchful."
        ),
    )
    w["urgell"] = b.lord(
        "Countess of Urgell",
        title="count",
        seat="La Seu d'Urgell",
        ruler="Elvira, widow of Ermengol VIII",
        answers_to=aragon,
        place=p["catalonia"],
        summary=(
            "Ermengol VIII, who fought off Foix's raids from 1195 and captured "
            "Raymond Roger in 1203, died in 1208. His widow Elvira rules from "
            "La Seu d'Urgell, but she is ill and not expected to see out the "
            "winter of 1220, and she is hastily preparing their daughter "
            "Aurembiaix to succeed her, having married her in 1212 to the "
            "Castilian noble Álvaro Pérez de Castro to strengthen her claim."
        ),
    )
    w["ager"] = b.lord(
        "Count of Ager",
        title="count",
        ruler="Guerau IV de Cabrera",
        answers_to=aragon,
        place=p["catalonia"],
        summary=(
            "Urgell's cousin, who says Aurembiaix cannot inherit and threatens "
            "to take the county by force when the countess dies; if history "
            "is followed he seizes it in the winter of 1220."
        ),
    )
    w["miglos"] = b.lord(
        "Viscount of Miglos",
        title="landed",
        seat="Castle Miglos",
        ruler="Arnaud de Miglos",
        place=p["niaux_cave"],
        summary=(
            "Arnaud de Miglos, the local viscount and a vassal of Foix, keeps "
            "a garrison in his castle a little south of Niaux and protects "
            "the village, whose people pay their taxes on time and so draw "
            "none of his attention to Miniata Sophia."
        ),
    )
    Builder.link(w["miglos"], "covenants", provence.covenants["miniata_sophia"])


# ----------------------------------------------------------------- church


def _churches(provence: Provence, b: Builder) -> None:
    w = provence.world
    p = provence.places
    w["bishop_of_urgell"] = b.church(
        "Bishop of Urgell",
        church="Bishop's cathedral",
        order="secular clergy",
        place=p["catalonia"],
        summary=(
            "His parishes stretch across Cerdagne, Pallars and Urgell, and he "
            "claims Andorra, as the Count of Foix does, though neither can make "
            "the Andorrans obey. Foix's raids from 1195 burned many of his "
            "churches; in 1203 the bishop was handed the captured count and "
            "passed him on to Pedro II."
        ),
    )
    w["bishop_of_pamplona"] = b.church(
        "Bishop of Pamplona",
        church="Bishop's cathedral",
        order="secular clergy",
        ruler="Ramiro, the king's brother",
        place=p["basque_country"],
        summary=(
            "Ramiro, brother of Sancho VII, holds most real authority in "
            "Pamplona while the king lives retired at Tudela. Pamplona and "
            "Urgell are the Basques' two sees."
        ),
    )
    w["ripoll"] = b.church(
        "Santa María de Ripoll",
        church="Monastery or nunnery",
        order="Benedictine",
        place=p["catalonia"],
        summary=(
            "The religious heart of Catalonia, burial place of the counts of "
            "Barcelona and Besalu since the ninth century, and a famous seat "
            "of learning with over four hundred manuscripts. It rules the "
            "abbeys of Saint-Martin-du-Canigou and Montserrat in Conflent. Its "
            "carved portal shows, in seven bands, God enthroned in Heaven and "
            "scenes of Moses, of David and Solomon, of Jonah and of "
            "Cain and Abel. Divine aura 4."
        ),
    )
    w["abadesses"] = b.church(
        "Sant Joan de les Abadesses",
        church="Monastery or nunnery",
        order="nuns",
        place=p["catalonia"],
        summary="A monastery of women in the county of Besalu.",
    )
    w["canigou"] = b.church(
        "The Abbeys of Canigou",
        church="Monastery or nunnery",
        order="Benedictine",
        answers_to=w["ripoll"],
        place=p["mount_canigou"],
        summary=(
            "Saint-Martin-du-Canigou, a daughter of Ripoll, and "
            "Saint-Michel-de-Cuxa stand high on the slopes of Mount Canigou "
            "above Conflent."
        ),
    )
    w["leyre"] = b.church(
        "San Salvador de Leyre",
        church="Monastery or nunnery",
        order="Cistercian",
        place=p["basque_country"],
        summary=(
            "A Cistercian house near Pamplona, famed for its old abbot St "
            "Virila, already renowned by 920, who sat rapt for three hundred "
            "years listening to a nightingale to understand eternity, and woke "
            "unaged, unaware the time had passed. A Timeless Monk (a story "
            "seed): might he have been an early pious magus, and what "
            "might his relics in the crypt reveal?"
        ),
    )
    w["roncevaux_abbey"] = b.church(
        "The Abbey of Roncevaux",
        church="Monastery or nunnery",
        place=p["roncevaux"],
        summary=(
            "The monks of Roncevaux keep the pass's chapel and hostel and make "
            "the Irouleguy wine of Lower Navarre. Their church holds the "
            "sultan's emerald from Las Navas and the cedar and silver statue "
            "of Our Lady of Roncevaux."
        ),
    )
    w["loarre_canons"] = b.church(
        "The Canons of Loarre",
        church="Chapel",
        order="Augustinian canons",
        place=p["mallos_de_riglos"],
        summary=(
            "Augustinian canons from Montearagón who have served inside "
            "Castle Loarre since Pedro I granted them the right."
        ),
    )


# ------------------------------------------------------------------ towns


def _towns(provence: Provence, b: Builder) -> None:
    w = provence.world
    p = provence.places
    w["pamplona"] = b.town(
        "Pamplona",
        ruler="Bishop Ramiro",
        answers_to=w["navarre"],
        place=p["basque_country"],
        summary=(
            "Navarre's capital on the right bank of the Arga, rich from the "
            "pilgrims of the Way of St James coming down from the Tunnel Way "
            "and Roncevaux, whom its people are proud to help on to Compostela. "
            "Centuries of war have made it something of a fortress, high-walled, "
            "where folk speak slowly and mind their own business. Many Basques "
            "and Occitan settlers live here, and wandering trobairitz in the "
            "Provençal style are much liked. The Romans kept a garrison here, "
            "Pompaelo. South of the mountains."
        ),
    )
    w["saint_jean"] = b.town(
        "Saint-Jean-Pied-de-Port",
        answers_to=w["navarre"],
        place=p["basque_country"],
        summary=(
            "A town at the foot of the Roncevaux road, razed by Richard the "
            "Lionheart in 1177 in a war that also destroyed Aedes Mercurii's "
            "large outpost here, whose covenfolk the townsfolk already "
            "suspected of witchcraft. Some Hermetic historians think a lapis "
            "mercurius once stood in a Mercurian temple in the town, now lost."
        ),
    )
    w["mauleon"] = b.town(
        "Mauléon",
        ruler="Ramon Guillem IV",
        answers_to=w["soule"],
        place=p["basque_country"],
        summary="Capital of the viscounty of Soule.",
    )
    w["zaragoza"] = b.town(
        "Zaragoza",
        answers_to=w["aragon"],
        place=p["pyrenees"],
        summary=(
            "The political heart of Aragon, where the boy king James I lives. "
            "Charlemagne's failed siege of it in 778 sent him back over the "
            "Pyrenees to Roncevaux. South of the mountains."
        ),
    )
    w["villefranche"] = b.town(
        "Villefranche-de-Conflent",
        answers_to=w["aragon"],
        place=p["catalonia"],
        summary=(
            "A heavily fortified eleventh-century town where the Têt meets the "
            "Cady, the seat of Conflent's government."
        ),
    )
    w["la_seu"] = b.town(
        "La Seu d'Urgell",
        ruler="Countess Elvira",
        answers_to=w["urgell"],
        place=p["catalonia"],
        summary="The see of the Bishop of Urgell and the seat of the county.",
    )
    w["andorra_la_vella"] = b.town(
        "Andorra la Vella",
        population=3000,
        place=p["andorra"],
        summary=(
            "The town where the five Andorran parishes send representatives "
            "once a year to settle the affairs of the land; the population "
            "given is all Andorra's."
        ),
    )
    w["niaux"] = b.town(
        "Niaux",
        answers_to=w["miglos"],
        place=p["niaux_cave"],
        summary=(
            "A village of the Vicdessos valley below Castle Miglos that "
            "supplies Miniata Sophia, mostly at second hand, and hosts one of "
            "its magi each season as a leper-robed guest; its children call "
            "Hans Grandfather. It pays its taxes promptly and draws no "
            "attention."
        ),
    )


# --------------------------------------------------------------- factions


def _factions(provence: Provence, b: Builder) -> None:
    w = provence.world
    p = provence.places
    w["andorrans"] = b.faction(
        "The Parishes of Andorra",
        faction="Council or assembly",
        decides="A council",
        members=3000,
        place=p["andorra"],
        rules="No lords and no vassals: each Andorran is his own sovereign",
        wants="To stay free of the Bishop of Urgell and the Count of Foix",
        offers="Livestock, wool, mountain wine and a quiet road between Toulouse and Catalonia",
        summary=(
            "The five parishes of Andorra, whose representatives meet yearly "
            "at Andorra la Vella. They play the bishop and the count against "
            "each other, sell over both sides of the range, and take Bellaquin "
            "for a helpful company of rich foreigners."
        ),
    )
    Builder.link(w["andorrans"], "covenants", provence.covenants["bellaquin"])
    w["andorra_company"] = b.faction(
        "The Andorra Company",
        faction="Brigands and mercenaries",
        decides="Its leader",
        members=18,
        ruler="Captain Michael, son of Robert Vasquez",
        place=p["ordino"],
        rules="Robert Vasquez is overall commander, Artemis second in command",
        offers="About eighteen disciplined almogavars, two of them sergeants",
        summary=(
            "Robert Vasquez's company of elite almogavars, raised in Iberia "
            "and France and gathered at Bellaquin as its turb. Their old "
            "captain was eaten by a mountain drake on a vis hunt three years "
            "ago, and Michael, Robert's unGifted son, thirty, who served as "
            "his secretary and protégé, has led them since and made them a "
            "disciplined force. Robert means to give each a lesser enchanted "
            "device for protection, stamina or keener senses."
        ),
    )
    Builder.link(w["andorra_company"], "covenants", provence.covenants["bellaquin"])
    w["sorginak"] = b.faction(
        "The Sorginak Covens",
        tradition="trad_sorginak",
        faction="Hedge coven",
        decides="A council",
        members=70,
        place=p["basque_country"],
        rules="Friday akelarre in caves and stone circles; feuds among sorginak are sorginak business",
        wants="Their auras and vis kept from Hermetic hands; deference to Dama",
        offers="Healing, hexes, flight, shapechanging, second sight; vis and secrets traded at Zugarramurdi",
        summary=paragraphs(
            "Thirteen covens of Basque folk witches in western Provence and "
            "north-western Iberia, at least 61 unGifted and about nine Gifted, "
            "who trade news, favours, apprentices and vis among themselves. "
            "Some nine live in or near Bayonne, others round Pau in Béarn, in "
            "Soule and in mountain villages, and many more south of the "
            "mountains. Only the Gifted, who have all sworn the Oath, count "
            "as members of the Order, and most of the Tribunal treats them "
            "as eremites; nearly all defer to Dama at Mimizan. They meet at "
            "least one Friday a month, the keenest every week, and the Gifted "
            "pagans bully the pious and unGifted into attending.",
            "Their power has faded since Charlemagne, under Christianity, "
            "rival hedge wizards (Suevi sorcerers, Visigoth artificers, "
            "Moorish sahirs) and the Order. The Diedne took sorginak into "
            "their House, which split the covens; the first sorginak joined "
            "Ex Miscellanea in 955, and some changed House in the Schism War "
            "to prove loyalty. Power, Unorganized (a story seed): a Tytalus "
            "or Trianoma wanting to break the big covenants' hold on the "
            "Tribunal might court the sorginak as a voting bloc.",
        ),
    )
    w["hermetic_sorginak"] = b.faction(
        "The Hermetic Sorginak",
        tradition="trad_hermetic_sorginak",
        faction="Hermetic group",
        decides="Its leader",
        members=3,
        place=p["basque_country"],
        wants="To guard their secrets and stand apart from Dama's cult",
        summary=(
            "Three Gifted sorginak trained in Hermetic magic, each living "
            "alone, who refuse Dama's cult of personality and form a faction "
            "of their own (chapter three counts four Ex Miscellanea sorginak "
            "eremites). Their tradition descends from a coven that worked "
            "with two Bonisagus brothers to fit sorginak powers into Hermetic "
            "theory; most were killed soon after by drakes Moorish sahirs "
            "lured to their covenant, so few remain. They look down on other "
            "sorginak, and their rivalries can turn deadly."
        ),
    )
    w["crestias"] = b.faction(
        "The Crestias",
        faction="Family",
        place=p["basque_country"],
        summary="An outcast people among the Basques, speaking Euskara and "
        "sharing most customs, but marked by their looks and a few odd "
        "ways. They may own no weapons, horses or dogs, marry only each "
        "other, live apart on the poorest land, and enter church by their "
        "own door to screened pews. Nobody remembers why. Most are "
        "Christian, with more pagans and old superstitions than other "
        "Basques. At akelarre they are revered rather than scorned, and "
        "said to be stronger in dark magic.",
        secrets=[
            titled(
                "Not of the people",
                "Basque slang calls the Crestias not of the people, which may "
                "mean the leftovers of some invader, or that they are not "
                "wholly human.",
            ),
        ],
    )


# ----------------------------------------------------------------- finish


def finish(provence: Provence) -> None:
    """The Count of Foix, whom chapter seven also describes: the record
    another part made, or one made here; then his vassal and Andorra's
    claim are tied to him."""
    b = provence.b
    foix = next(
        (n for n in b.saga.neighbours if n.kind == "lord" and "Foix" in n.name),
        None,
    )
    if foix is None:
        foix = b.lord(
            "Count of Foix",
            title="count",
            wealth="Wealthy",
            seat="Chateau de Foix",
            ruler="Raymond Roger I",
            place=provence.places["pyrenees"],
            summary=(
                "Raymond Roger I, a troubadour, a kinsman of Raimond VI of "
                "Toulouse and married to a Cathar, fights the crusade though "
                "no Cathar himself. Pressing his claim to Andorra against the "
                "Bishop of Urgell, he ravaged Cerdagne and Urgell from 1195 "
                "until Urgell's count captured him in 1203; Pedro II freed "
                "him, and even enlarged his lands, to keep him loyal before "
                "the crusade. His castle above the town of Foix has sheltered "
                "Cathars. Arnaud de Miglos is his vassal."
            ),
        )
    provence.world.setdefault("count_of_foix", foix)
    provence.world["miglos"].answers_to = foix.id


# ------------------------------------------------------------------ stats

P = Profile
OCCITAN = "Occitan"


#: Each magus of the Pyrenees the book sketches without a stat block, by
#: the key in provence.magi.
PROFILES: dict[str, Profile] = {
    "flammarcus": P(
        strong="int pre com",
        arts={"Ig": 6, "Pe": 5, "Cr": 3, "Re": 3, "In": 3, "Me": 2},
        abilities={
            "Intrigue": (4, "House Flambeau"),
            "Leadership": (3, "magi"),
            "Organization Lore: Cult of Mercury": (3, "the Founder's history"),
            "Artes Liberales": 2,
            "Single Weapon": 2,
        },
        virtues=["Hermetic Prestige", "Ambitious (Major)"],
        reputations={"Pontifex Maximus of Aedes Mercurii (Hermetic)": 3},
        native=OCCITAN,
    ),
    "protendus": P(
        strong="int per sta",
        arts={"Me": 7, "Co": 6, "In": 5, "Pe": 4, "Re": 4, "Vi": 3},
        abilities={
            "Code of Hermes": (4, "investigation"),
            "Intrigue": (3, "House Tytalus"),
            "Folk Ken": (2, "magi"),
            "Magic Lore": (3, "ghosts"),
            "Teaching": 2,
        },
        virtues=[vf_art("Affinity with {art}", "mentem"), "Secretive", "Reclusive"],
        reputations={"Necromancer (Hermetic)": 3},
        native=OCCITAN,
    ),
    "ophilio": P(
        strong="int com sta",
        arts={"Cr": 7, "Co": 7, "Re": 4, "Vi": 4, "In": 3, "Mu": 3},
        abilities={
            "Medicine": (4, "aging"),
            "Organization Lore: Cult of Mercury": (4, "rites"),
            "Ride": 2,
            "Folk Ken": (2, "covenfolk"),
        },
        virtues=["Hermetic Prestige", "Proud (Minor)"],
        reputations={"Former High Priest of Mercury (Hermetic)": 3},
        native=OCCITAN,
    ),
    "midius": P(
        strong="int pre com",
        arts={"Ig": 5, "Pe": 4, "Cr": 4, "Im": 3, "Re": 3, "Vi": 3},
        abilities={
            "Organization Lore: Cult of Mercury": (4, "rites"),
            "Magic Lore": (3, "Roman rites"),
            "Etiquette": 2,
        },
        virtues=["Mercurian Magic", "Weak-Willed", "Dutybound", "Humble"],
        reputations={"Flamen of the Provençal Tribunal (Hermetic)": 2},
        native=OCCITAN,
    ),
    "pila": P(
        strong="sta str dex",
        weak="com",
        arts={"Ig": 7, "Pe": 5, "Cr": 4, "Te": 3, "Re": 3},
        abilities={
            "Single Weapon": (4, "spear"),
            "Leadership": (2, "grogs"),
            "Awareness": (3, "sentry duty"),
            "Athletics": 2,
        },
        virtues=["Warrior", "Driven (Minor)"],
        native=OCCITAN,
    ),
    "malfortis": P(
        strong="int com sta",
        arts={"Co": 7, "Re": 4, "Cr": 4, "Pe": 4, "Ig": 3},
        abilities={
            "Teaching": (5, "Arts"),
            "Brawl": (4, "fist"),
            "Artes Liberales": (3, "rhetoric"),
            "Profession: Scribe": 2,
        },
        virtues=["Good Teacher", "Driven (Minor)"],
        native=OCCITAN,
    ),
    "ricardus": P(
        strong="int pre com",
        arts={"Cr": 7, "Me": 7, "Im": 3, "Re": 3, "In": 2},
        abilities={
            "Charm": (3, "magi"),
            "Carouse": 3,
            "Intrigue": (2, "covenant council"),
            "Artes Liberales": 2,
        },
        virtues=["Busybody"],
        native=OCCITAN,
    ),
    "aintza": P(
        strong="int per pre",
        arts={"In": 7, "Im": 4, "Me": 4, "An": 3, "Vi": 3},
        abilities={
            "Magic Lore": (3, "omens"),
            "Organization Lore: Cult of Mercury": (3, "mysteries"),
            "Animal Ken": (2, "cats"),
            "Living Language: Occitan": 4,
        },
        virtues=["Premonitions", "Visions", "Pagan (Minor)"],
        native="Euskara",
    ),
    "ruberus": P(
        strong="int dex per",
        arts={"Te": 6, "Ig": 5, "Re": 4, "Cr": 4, "Mu": 3},
        abilities={
            "Craft: Blacksmith": (4, "swords"),
            "Single Weapon": (2, "sword"),
            "Organization Lore: Confraternity of Roland": 3,
        },
        virtues=["Inventive Genius", "Secretive"],
        native=OCCITAN,
    ),
    "oxioun": P(
        strong="int pre com",
        arts={"Re": 5, "Me": 5, "Im": 4, "In": 3, "Vi": 3},
        abilities={
            "Intrigue": (4, "Tribunal politics"),
            "Leadership": (3, "magi"),
            "Guile": 2,
        },
        virtues=["Hermetic Prestige", "Ambitious (Minor)"],
        age=120,
        native=OCCITAN,
    ),
    "berezi": P(
        gifted=False,
        strong="per com sta",
        native="Euskara",
        abilities={
            "Ride": (3, "mountain tracks"),
            "Area Lore: Provençal Tribunal": (4, "covenants"),
            "Organization Lore: Order of Hermes": 3,
            "Code of Hermes": 2,
            "Dead Language: Latin": 3,
            "Living Language: Occitan": 4,
            "Bargain": (2, "books"),
        },
        virtues=["Redcap", "Magic Items", "Proud (Minor)", "Wanderlust"],
    ),
    "valgravian": P(
        strong="int pre com",
        arts={"Im": 7, "Cr": 6, "Co": 5, "Re": 4, "Me": 4, "Mu": 3},
        abilities={
            "Music": (5, "singing"),
            "Etiquette": (4, "nobles"),
            "Leadership": (3, "covenant affairs"),
            "Intrigue": 2,
            "Medicine": (2, "aging"),
        },
        virtues=[
            ("Minor Magical Focus", {"focus": "music"}),
            "Hermetic Prestige",
            "Busybody",
            "Dutybound",
        ],
        reputations={
            "Archmage (Hermetic)": 4,
            "Canny (Hermetic)": 3,
            "Capable Musician (Local)": 3,
        },
        native="High German",
    ),
    "constantine": P(
        strong="int com per",
        arts={"Im": 7, "In": 5, "Re": 5, "Mu": 4, "Te": 3},
        abilities={
            "Bargain": (5, "funds"),
            "Etiquette": (2, "merchants"),
            "Intrigue": 2,
            "Folk Ken": (2, "merchants"),
            "Living Language: Catalan": 3,
        },
        virtues=[
            ("Social Contacts", {"group": "merchants and bankers"}),
            "Greedy (Minor)",
        ],
        native=OCCITAN,
    ),
    "robert_vasquez": P(
        strong="sta str int",
        arts={"Ig": 7, "Pe": 6, "Re": 4, "Co": 3, "Te": 3},
        abilities={
            "Single Weapon": (4, "sword"),
            "Leadership": (3, "soldiers"),
            "Brawl": 2,
            "Ride": 2,
            "Living Language: Occitan": 4,
        },
        virtues=[
            "Gentle Gift",
            "Overconfident (Minor)",
            "Lost Love",
            "Close Family Ties",
        ],
        native="Castilian",
    ),
    "artemis": P(
        strong="int sta per",
        weak="pre",
        arts={"Co": 8, "Re": 5, "Pe": 4, "In": 4, "Vi": 3},
        abilities={
            "Leadership": (3, "guards"),
            "Awareness": (3, "intruders"),
            "Code of Hermes": 3,
        },
        virtues=[
            "Blatant Gift",
            "Strong-Willed",
            vf_art("Affinity with {art}", "corpus"),
            "Dutybound",
        ],
        native=OCCITAN,
    ),
    "antoinette": P(
        strong="int pre com",
        arts={"Im": 6, "Cr": 3, "Mu": 3, "Me": 3},
        abilities={
            "Etiquette": (2, "nobles"),
            "Charm": 2,
            "Music": 2,
        },
        virtues=["Gentle Gift", "Dark Secret"],
        native=OCCITAN,
    ),
    "leonarda": P(
        strong="int per pre",
        arts={"Cr": 6, "Re": 6, "Co": 6, "Vi": 6, "In": 3},
        abilities={
            "Medicine": (3, "aging"),
            "Teaching": (3, "the Path"),
            "Folk Ken": (2, "villagers"),
            "Living Language: Occitan": 4,
        },
        virtues=["Good Teacher", "Pious (Minor)"],
        native="Aragonese",
    ),
    "tumbarius": P(
        strong="int per sta",
        arts={"Me": 7, "In": 4, "Re": 3, "Vi": 3},
        abilities={
            "Magic Lore": (3, "ghosts"),
            "Philosophiae": (2, "metaphysics"),
            "Infernal Lore": 1,
        },
        virtues=[
            "Second Sight",
            vf_art("Affinity with {art}", "mentem"),
            "Arthritis",
            "Driven (Minor)",
        ],
        native="English",
    ),
    "hans": P(
        strong="int com pre",
        arts={"Re": 6, "Im": 6, "Te": 6, "In": 3},
        abilities={
            "Living Language: Occitan": 4,
            "Folk Ken": (3, "villagers"),
            "Charm": 2,
            "Teaching": (2, "children"),
        },
        virtues=[
            "Gentle Gift",
            "Carefree",
            "Optimistic (Minor)",
            "Compassionate (Minor)",
        ],
        native="High German",
    ),
}


def stats(provence: Provence) -> None:
    """Generated stats for every magus of the Pyrenees: the book prints
    no stat block for any of them."""
    for key, profile in PROFILES.items():
        apply(provence.b, provence.magi[key], profile)
