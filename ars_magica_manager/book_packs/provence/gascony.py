"""Gascony, the Provençal Tribunal's western wedge, as of 1220: the English
crown's province of Guyenne and Gascony, the Way of St James and its
knightly orders, the Médoc and Oriande la Fée's Rosefleur, the Landes,
Bayonne and the Basque coast, Béarn and Bigorre; Castra Solis, the domus
magna of House Flambeau, with its outlying sites at Mimizan (the
Praeco's tower) and near Poitiers (Marie of Merinita's manor); Tres'
Band; their magi, libraries and vis; and the lords, sees, towns and
orders of the region, in paraphrase of Faith & Flame chapter five (and
chapter three for the covenants' politics and votes).

Dama of Merinita, the Praeco, is made here with her printed stat block,
and her secret (the deaths of Senex and Tibaut, and Maju) is under
Secrets in her summary; tribunal.py names her Praeco, and stories.py
owns The Serpent's Venom and the Six Deadly Spirits as threats. The
ruined covenants of Gascony (Bachlach's Hermitage, Nemetannais, the two
lost Diedne sites) are tribunal.py's. Creatures (Oriande la Fée, the
unicorn of Bazas, the Lou Carcolh, the matagots, the demons of the
interdict, Maju) are described in the summaries of the places they
haunt, since there is no bestiary yet; the sorginak covens and Basque
beings are in place notes.

Records are kept in the Provence dicts under slugs: the region is
places["gascony"], the covenant sites places["castra_solis_site"],
places["mimizan"] and places["poitiers_manor"]; the covenants
covenants["castra_solis"] and covenants["tres_band"]; the magi under
their first names (magi["dama"], magi["rebecca"], magi["garus"],
magi["marcus_minor"], magi["troya"], magi["marie"], magi["beatrice"],
magi["tres"])."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import (
    Builder,
    StatBlock,
    joined_lines,
    paragraphs,
    titled,
    vf_ability,
    vf_art,
    vf_focus,
)
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from . import Provence

FLAMBEAU = "house_flambeau"
MERINITA = "house_merinita"
GUERNICUS = "house_guernicus"
EX_MISC = "house_ex_miscellanea"

# The lead line of a covenant's notes, before its secrets.
KNOWN_ORDER = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY = {"status": "Known", "known": "Locally"}
RUMOURED = {"status": "Rumoured", "known": "Locally"}
SECRET = {"status": "Secret", "known": "Locally"}


def _add(provence: Provence, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = provence.b.place(name, **kw)
    provence.places[key] = place
    return place


def build(provence: Provence) -> None:
    b = provence.b
    tribunal = provence.tribunal
    if tribunal is None:
        tribunal = next(iter(b.saga.tribunals), None)
    assert tribunal is not None, "tribunal.py builds the Tribunal first"
    _region(provence)
    _bordeaux_and_medoc(provence)
    _bazas_and_garonne(provence)
    _agenais_and_armagnac(provence)
    _basque_coast(provence)
    _bearn_and_bigorre(provence)
    _castra_solis_sites(provence)
    _castra_solis(provence, b, tribunal)
    _tres_band(provence, b, tribunal)
    _lords(provence, b)
    _churches(provence, b)
    _towns(provence, b)
    _factions(provence, b)


# ------------------------------------------------------------- the region


def _region(provence: Provence) -> None:
    if "gascony" in provence.places:
        return
    _add(
        provence,
        "gascony",
        "Gascony",
        summary=paragraphs(
            "The Tribunal's western third in 1220: Guyenne and Gascony, "
            "reckoned part of the duchy of Aquitaine, a wedge of wild country "
            "that runs from Bordeaux up the Garonne and south-east to "
            "Charlemagne's Cross by Roncevaux, and takes in the whole Atlantic "
            "shore down to Bayonne. Three settled districts cluster round its "
            "three cities: Bordeaux in the north; Auch, the archbishop's seat "
            "on high ground toward Toulouse; and Bayonne in the south-west, "
            "where Gascon country gives way to Basque. Between them lie "
            "untilled moor, forest and marsh.",
            "The English crown has held the province hard ever since Richard "
            "the Lionheart settled at Bayonne and broke the local barons. The "
            "dukes have always ruled from Bordeaux and left the rest alone "
            "save for the odd show of strength down the Garonne; young Henry "
            "III comes to visit his mother Isabella, who lives close by.",
            "The Way of St James, after Rome and Jerusalem the most travelled "
            "pilgrimage in Mythic Europe, crosses much of the duchy on good "
            "roads. Of its five routes through the Tribunal, four (the "
            "coastal English Way through Bordeaux and Bayonne, the Via "
            "Turonensis from Paris by Tours, the Via Lemovicensis from Vézelay "
            "by Limoges, and the Via Podiensis from Le Puy, called the Via "
            "Gebennensis by those starting at Geneva) meet at Ostabat before "
            "the climb to Roncevaux; only the Via Tolosana from Arles, which "
            "Italians favour, takes another pass. Palmers wear the scallop "
            "shell, keep journals of their stops, and find hospitals, hostels "
            "and churches with relics all along the way; Aymeric Picaud's "
            "Liber Peregrinationis made the journey famous. Military orders "
            "hold commanderies on donated land to guard them and to raise "
            "money for the Holy Land: the Templars have twenty in Gascony.",
            "When Innocent III laid England under interdict in 1208, Gascony "
            "fell under it as the king's land, and many of its churches stood "
            "shut for six years. In the empty interior, far from the pilgrim "
            "roads, a band of six demons took root, and Infernal auras are "
            "common still: even in towns the Dominion holds by day, the "
            "Infernal often takes the night. The interdict left Divine auras "
            "weak or strange, and none below 7 is more than six years old.",
            "The six spirits arrived with the interdict, each bent on one "
            "deadly sin. A demon settles on a community, possesses its "
            "leading people and through them draws the rest into sin until "
            "an Infernal aura closes over the place; a host who dies "
            "unrepentant comes back as a lesser demon or a ghost. Greed has "
            "gone to the bridge of St Thibery, and Gluttony and Wrath ride "
            "with the armies in the Narbonnais and the Toulousain, but three "
            "remain in Gascony. Cenodoxus Superbia, Lord of Pride and Envy "
            "(Infernal Might 40, a lord of the Vessels of Iniquity), plays the "
            "patron and muse to craftsmen, swelling their pride and then "
            "spreading a contagious envy among those around them until whole "
            "guilds rot; he appears as a well-dressed man or woman with a "
            "dagger and fine tools, leaves the dagger lying about when "
            "tempers run high, can lend a craftsman a great Characteristic or "
            "a bonus to his craft for a price, and is strong enough to pass "
            "many an Aegis; eight pawns of Vim lie in his tongue and eyes. "
            "Julian (or Julia), the Tempter of the Way (Infernal Might 15), a "
            "raven-haired young rogue in pilgrim's dress, draws the devout "
            "aside, seduces them, travels with them and contrives that they "
            "are caught in the act at the worst moment; he rides his victims "
            "by night, and three pawns of Vim lie in his belt buckle. Both "
            "keep to crowded places: Bordeaux, Bayonne and the ferry at "
            "Blaye. Adrian, the Voice of Safety (Infernal Might 30, a spirit "
            "of deceit), wanders from inn to inn as a handsome troubadour or "
            "trobairitz with a guitar, singing of the horrors done in the "
            "name of faith and breeding the sloth of acedia: no one should "
            "go on crusade, nor defend the Cathars either, for it would ruin "
            "their families and only fatten the nobles; six pawns of Vim lie "
            "in his hands, and crusaders are proof against him.",
            "The faeries of the region, from the courtly fae to nymphs, "
            "sirens, trolls and fauns, are called the Dames Blanches, and all "
            "own Oriande la Fée of Rosefleur in the Médoc as their queen, "
            "though most pay her only lip service until she comes in person. "
            "Drakes and worms have lately begun to harry pilgrims, worst near "
            "Ostabat.",
            "The Basques have lived in the south-west since before Rome; they "
            "are expert whalers and hardy fighters, and their customs are the "
            "heart of the land. About fifteen folk witches, the sorginak, are "
            "scattered through the villages of Gascony and the Basque "
            "country, and most defer to Dama of Merinita at Mimizan. They "
            "keep the old faith in Mari and in her consort Sugaar, the "
            "serpent, whose name Dama's familiar wears among them.",
        ),
        **KNOWN_ORDER,
    )


# ------------------------------------------------- Bordeaux and the Médoc


def _bordeaux_and_medoc(provence: Provence) -> None:
    region = provence.places["gascony"]
    _add(
        provence,
        "bordeaux_mithraeum",
        "The True Mithraeum of Bordeaux",
        inside=region,
        summary="A natural cavern under the southern quarter of Bordeaux.",
        secrets=[
            titled(
                "The Roman temple",
                "Roman soldiers of the garrison made the cavern under Bordeaux "
                "a temple of Mithras, and it has lain buried and forgotten for "
                "centuries.",
            ),
            titled(
                "Kaeso's secret",
                "Only Kaeso of Flambeau knew where the true mithraeum was: "
                "fearing the barbarians then holding Bordeaux would find it, he "
                "told no one in the Order and built a second temple upriver, "
                "where Castra Solis now stands, so that the true one kept its "
                "power undimmed.",
            ),
            titled(
                "What the Flambeau believe",
                "Most Flambeau believe the temple under Castra Solis is Kaeso's own.",
            ),
            titled(
                "The Great Temple",
                "Many high initiates of the Legion of Mithras believe their "
                "rumoured Great Temple lies somewhere in France.",
            ),
            titled(
                "Storyguide Notes",
                "The book gives no aura for the true mithraeum.",
            ),
        ],
        **SECRET,
    )
    _add(
        provence,
        "belin",
        "Belin",
        inside=region,
        summary=paragraphs(
            "A small hamlet on the Leyre south of Bordeaux, with a keep and a "
            "church; folk say Eleanor of Aquitaine was born here. A generous "
            "charter draws craftsmen, and Henry III likes to stay in the "
            "castle when he visits.",
            "Olivier de Viennes, Ogier the Dane and others of Charlemagne's "
            "Twelve Peers lie in the church. The churchyard has a Divine "
            "aura of 4 and smells strongly of something very sweet: on the "
            "anniversary of Ogier's death the scent can heal a sick penitent, "
            "and on the anniversary of Roncevaux it carries 5 pawns of "
            "Divine-tempered Creo vis, held by no covenant. Ogier's sword "
            "Cortana, of the same steel as Durendal and once Tristan's, is "
            "gone from his tomb: Oriande la Fée claims to have it.",
        ),
        realm="Divine",
        aura=4,
        **KNOWN_REGION,
    )
    medoc = _add(
        provence,
        "medoc",
        "The Médoc",
        inside=region,
        summary=paragraphs(
            "The triangle of country west and north of Bordeaux between the "
            "Atlantic and the mouth of the Gironde, mostly marsh and wet "
            "ground. Rome kept a post here to guard the coast road; in the "
            "ninth century a castle of white limestone, Blanquefort, rose on "
            "its ruins to watch two roads: the Levade from Bordeaux north to "
            "Soulac, and the Channel Soulac south to Bayonne, the main artery "
            "of the English Way of St James, which runs from Soulac to St "
            "Jean Pied-de-Port to join the other routes before Roncevaux.",
            "Hundreds of dolmens are strewn through its fens, their Faerie "
            "auras ranging from 1 up to 5. Most house faeries of the Dames Blanches "
            "who serve the Queen of Rosefleur in tormenting pilgrims, and "
            "the stronger beings lair at the stronger stones. Trolls among "
            "them try to lure travellers off the road to eat them; others "
            "coax pilgrims to live wild until the weather kills them; others "
            "only ask for a dance or a small service before letting a "
            "traveller by, and plague those who refuse. They wear the shapes "
            "known all over Mythic Europe, so every pilgrim recognises their "
            "tales.",
            "The inner circle of Dama's cult meets in the Médoc, in the "
            "realm of its faerie queen.",
        ),
        realm="Faerie",
        aura=1,
        **KNOWN_REGION,
    )
    rosefleur = _add(
        provence,
        "rosefleur",
        "Rosefleur",
        inside=medoc,
        realm="Faerie",
        aura=2,
        levels=[
            Builder.level(
                "The marsh shore",
                2,
                "Faerie",
                notes="The lowest of six levels: the first touch of the "
                "court's paradise over the muddy shore.",
            ),
            Builder.level("The outer gardens", 3, "Faerie"),
            Builder.level("The castle approaches", 4, "Faerie"),
            Builder.level("The bailey", 5, "Faerie"),
            Builder.level("The towers", 6, "Faerie"),
            Builder.level(
                "The heart of the castle",
                7,
                "Faerie",
                notes="Oriande's court, where her Might rises to 60.",
            ),
        ],
        summary=paragraphs(
            "A faerie castle in a regio of six levels on the western shore "
            "near the tip of the Médoc: slender towers, streaming banners "
            "and smooth dressed stone amid a paradise of beasts and flowers, "
            "nothing like the wet, wind-scoured land at the mundane level. "
            "The aura climbs from 2 at the edge to 7 at the castle's heart. "
            "Its people go naked most of the time and put on gossamer court "
            "dress when their queen receives guests. On the mundane level "
            "one can still trace the footings of the little shrine where "
            "the Gauls worshipped her as a form of Sirona, goddess of healing "
            "and springs.",
            "Oriande la Fée (Faerie Might 50, Herbam; 60 within her own "
            "demesne) claims lordship from the north bank of the Gironde south "
            "to the Pyrenees and east to the Camargue. Once a giver of gifts, "
            "she remade herself as a challenger on the Roman roads and then "
            "the Way of St James, drawing vitality from the stories she "
            "forces on knights and pilgrims: she makes them forget their "
            "journeys and keeps them while they amuse her, seizes hostages or "
            "treasures and demands quests or ransoms, sends a lesser fae to "
            "pick a fight with travellers and then demands they carry her "
            "letters to other faerie nobles as amends, shadowing them with "
            "fresh trials. She looks a beautiful olive-skinned woman with "
            "moss-grown wooden antlers in wild, flowered hair, amber eyes "
            "like frozen sap and a gown of leaves and cobweb, trailing "
            "fireflies or snowflakes as the season runs, and nature flourishes "
            "where she treads. She can put a man to sleep with a word, turn "
            "him into a hare or squirrel until her terms are met, wipe out "
            "his memory of home, sway a crowd with her storytelling, and ride "
            "the wind as whirling leaves; she bears a glass-bladed dagger "
            "that becomes whatever weapon a favoured knight wishes and marks "
            "him as hers in her lands, and 10 pawns of Herbam vis lie in her "
            "antlers. Iron and the Divine hurt her, and she loses interest "
            "in her playthings once they turn fae themselves.",
            "She has sheltered many magi as refugees, vassals or allies, "
            "among them Maugris and Dama, who spent long years at her court "
            "seeking the mysteries of Story Magic. She claims to hold "
            "Cortana. Oberon or the Boar King of Normandy might court or "
            "quarrel with her, and some wonder whether Isabella of "
            "Angoulême's undying beauty is her gift.",
        ),
        **KNOWN_REGION,
    )
    provence.places["rosefleur"] = rosefleur


# --------------------------------------------- Bazas and the Garonne


def _bazas_and_garonne(provence: Provence) -> None:
    region = provence.places["gascony"]
    _add(
        provence,
        "bazas_landes",
        "The Moors of Bazas",
        inside=region,
        summary=paragraphs(
            "Marsh and heath south-west of Bazas, on the edge of the Landes, "
            "with a few good stands of pine and oak that the locals cut only "
            "now and then. Shepherds watch their flocks from stilts above the "
            "fens. Tres and his band hide in this hard country between stays "
            "in their sancta: with so many pilgrims about nobody notices a "
            "party on the road or camping in the open, and the moors put off "
            "all but the most stubborn visitors.",
            "The shepherds tell of a shining white beast at the edges of the "
            "woods, which looks out from the trees for a moment and goes "
            "back; a sighting means three days' safety for the flock. It is a "
            "unicorn (Divine Might 20, Animal): a charger-sized horse with "
            "cloven goat's hooves, a beard, a lion's tail and a slender "
            "spiral horn, which can tell a virgin by her eyes, wraps itself "
            "in white light when roused to righteous fury, cures poison by "
            "touch, and is weakened by virgin women. Four pawns of "
            "Divine-aligned Animal vis lie in its horn. The Valerenes of "
            "Agen seek it eagerly.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "roquetaillade_caves",
        "The Caves of Roquetaillade",
        inside=region,
        summary="Caves near Roquetaillade Castle by Langon, home to a company of "
        "faerie masons. Each new lord de La Motte enlarges the castle "
        "with their help, which is how the square four-towered keep has "
        "grown so grand.",
        secrets=[
            titled(
                "The masons' pact",
                "The masons are bound by a pact to finish one building work for "
                "each new lord of the family. Its terms are secret, told only by "
                "a dying lord to his son.",
            ),
        ],
        realm="Faerie",
        **RUMOURED,
    )
    _add(
        provence,
        "marmande",
        "The Ruins of Marmande",
        inside=region,
        summary=paragraphs(
            "A walled town on the Garonne that Richard the Lionheart founded "
            "around 1195. The count of Toulouse held it by 1209; de "
            "Montfort's men took it in 1212 and again in 1213 after a revolt, "
            "and it went over to King John when an English army came near in "
            "1214, until the English fell back after Bouvines. Just after "
            "Christmas 1218 crusaders of Prince Louis under Centule "
            "d'Astarac laid siege; after nine months the garrison yielded "
            "and marched out on terms that were kept. Then, on the Bishop of "
            "Saintes's word, Amaury de Montfort's men killed all five "
            "thousand townsfolk, women and children too, and even the beasts, "
            "saying it was needed to keep God's favour on their arms, then "
            "burned the town and razed what they could. Many say the young "
            "Amaury did it to avenge his father, killed at Toulouse.",
            "In 1220 it is a field of rubble and ash where the charred bones "
            "of the dead lie unburied. The Infernal aura is 6, rising to 7 on "
            "26 September, the anniversary, when those with Second Sight see "
            "the ground drenched in the slaughter as if it had rained from "
            "the sky. Ghosts are common, and so are crows corrupted by "
            "feeding on the dead.",
        ),
        realm="Infernal",
        aura=6,
        **KNOWN_REGION,
    )


# ----------------------------------------- the Agenais and Armagnac


def _agenais_and_armagnac(provence: Provence) -> None:
    region = provence.places["gascony"]
    _add(
        provence,
        "auch_mithraea",
        "The Mithraea under Auch Cathedral",
        inside=region,
        summary=paragraphs(
            "Catacombs beneath the burnt-out cathedral in the middle of Auch, "
            "which was raised over several temples of Mithras. Six whole "
            "tauroctony altars of white marble stand hidden there, where "
            "initiates once purified themselves and were admitted to the "
            "mysteries. The altars and the chamber round them hold a Magic "
            "aura of 3; the cathedral above, a cleared site with a few "
            "stretches of new wall since the fire of 1170, has no Divine aura "
            "at all.",
        ),
        aura=3,
        **RUMOURED,
    )
    _add(
        provence,
        "lou_carcolh_cave",
        "The Lou Carcolh's Cavern",
        inside=region,
        summary=paragraphs(
            "A cave in the hills near Bayonne where the mountains begin, the "
            "lair of the Lou Carcolh (Magic Might 25, Animal): a vast snail "
            "with a dragon's head, a beard of a score of tentacles that reach "
            "a hundred paces to drag prey into a mouth of forearm-long fangs, "
            "a lumpy shell and a pebbled hide that turns most blades. It "
            "slides over any rubble, feels for prey through the air with its "
            "tentacles, and must eat people. It seldom strays far and mostly "
            "takes pilgrims, which keeps it fed for now. Five pawns of Animal "
            "vis lie in its tentacles.",
            "The sorginak know of it and keep away, but watch it closely; now "
            "and then one leads meddling knights, prying magi or foolish "
            "bandits to its cave, to feed it and be rid of them. The "
            "answers to some questions lie in its lair.",
        ),
        **KNOWN_LOCALLY,
    )


# ------------------------------------------------ the Basque coast


def _basque_coast(provence: Provence) -> None:
    region = provence.places["gascony"]
    _add(
        provence,
        "biscay_whaling_grounds",
        "The Whaling Grounds of Bayonne",
        inside=region,
        summary=paragraphs(
            "The coastal waters off Bayonne and the Basque shore, watched "
            "from tall lookout towers, the vigias. When whales, the sarda, "
            "are sighted, the whalers launch a fleet of small boats and chase "
            "them with harpoons and throwing spears into the shallows. The "
            "sarda is a huge, ill-tempered beast with a sweet breath, a "
            "pebbled hide and a tail that lies flat, which smashes or "
            "overturns boats that harry it.",
            "Whales of Virtue hold Animal vis in their bones and Aquam vis in "
            "their baleen; no covenant claims them. Rebecca of Mimizan flies "
            "over her home village's boats in albatross form, and the whalers "
            "follow her as a lucky sign.",
        ),
        **KNOWN_LOCALLY,
    )


# ------------------------------------------------ Béarn and Bigorre


def _bearn_and_bigorre(provence: Provence) -> None:
    region = provence.places["gascony"]
    _add(
        provence,
        "pau_ford",
        "The Shepherds' Ford at Pau",
        inside=region,
        summary=paragraphs(
            "The crossing of the Gave de Pau below Pau's two square towers, "
            "used by shepherds driving flocks to and from the mountain "
            "pastures since time out of mind. Tufts of wool caught on the "
            "brambles along the drove road yield 4 pawns of Creo vis at the "
            "spring equinox and 4 of Muto at the autumn equinox; no covenant "
            "holds them.",
            "A covenant might be founded in the towers if it guarded the "
            "crossing, kept the village and took fair tolls for the young "
            "William of Béarn, who would turn a blind eye to its oddities; "
            "but that comes perilously close to serving as court wizards.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "lourdes_spring",
        "The Healing Spring of Lourdes",
        inside=region,
        summary=paragraphs(
            "A spring in a bend of the Gave de Pau by Lourdes, one of the "
            "invigorating baths the Romans prized in Bigorre, said to heal. "
            "Its water drawn at the first snowmelt yields 4 pawns of Creo "
            "vis, held by no covenant.",
            "On the anniversary of Mirat's baptism the top of the castle "
            "tower has a Divine aura of 2. The lord of the castle in 778, the "
            "Moor Mirat, held out against Charlemagne until an eagle dropped "
            "a great trout at his feet; he threw it down to the besiegers, "
            "who took it to mean the castle could hold for ever and left. "
            "Bishop Turpin of Le Puy persuaded him that the eagle and the "
            "retreat were miracles of the Virgin; Mirat gave gifts to the "
            "Black Virgin of Le Puy, yielded the castle, was baptised, and "
            "took the name Louerda, the rose, which the town now bears.",
        ),
        **KNOWN_LOCALLY,
    )


# --------------------------------------------- the Castra Solis sites


def _castra_solis_sites(provence: Provence) -> None:
    region = provence.places["gascony"]
    site = _add(
        provence,
        "castra_solis_site",
        "Castra Solis",
        inside=region,
        summary=paragraphs(
            "Limestone hills on the Garonne about halfway between Bordeaux "
            "and La Réole, where the domus magna of House Flambeau looks like "
            "a rich manor or Roman villa among vineyards and fields that grow "
            "neither wine nor wheat: they are tourney grounds for the House's "
            "many contests. The Magic aura is only 3.",
            "At the foot of the cliffs a network of riverside caves, inside "
            "the Aegis and warded besides, climbs under oyster-crusted arches "
            "to a large underground temple, believed by most Flambeau to be "
            "Kaeso's Roman mithraeum.",
        ),
        aura=3,
        **KNOWN_ORDER,
    )
    _add(
        provence,
        "castra_solis_mithraeum",
        "The Mithraeum of Castra Solis",
        inside=site,
        summary=paragraphs(
            "The temple under Castra Solis, reached by hidden stairs from "
            "the library to the chambers behind it. Generations of "
            "Christian milites and pious magi have given it a Divine "
            "aura of 4, and it is a church in all but name: the rites "
            "for the Legion of Mithras's younger initiates are close to "
            "baptism, communion and the last rites. Tombs in the caves "
            "hold fallen milites in holy ground; the former Primus "
            "Entisimon lies here, but Kaeso does not.",
        ),
        secrets=[
            titled(
                "Which temple is the true one",
                "The Mithraeum of Castra Solis is a copy, built when Bordeaux "
                "fell to the raiders; the true temple lies under Bordeaux and "
                "was kept secret so that its power would endure.",
            ),
        ],
        realm="Divine",
        aura=4,
        **KNOWN_TRIBUNAL,
    )
    _add(
        provence,
        "mimizan",
        "Dama's Tower at Mimizan",
        inside=region,
        summary=paragraphs(
            "A chapter of Castra Solis: Dama of Merinita's tower on the "
            "swampy shore on the north side of the lake outside "
            "Mimizan, a squat block of stone three storeys high over a "
            "cellar used for storage. Dama lives and works on the top "
            "floor, guests lodge on the second and the servants on the "
            "first. The Redcaps call it Mimizan covenant, but at Tribunal "
            "it counts as part of Castra Solis. It began as one of the "
            "Hoplites' outposts in the long war with the raiders, and "
            "Dama has kept it since the century after the Schism War; "
            "she was born close by.",
            "The Faerie aura is 4, centred on a muddy black rock almost "
            "buried at the water's edge, near the ruins of a Gaulish "
            "shrine where priests made many sacrifices; the wild coast "
            "and marshes round about often hold pockets of Faerie aura. "
            "A very strong Aegis of the Hearth (level 50, cast with "
            "Wizard's Communion and a casting tablet) guards the tower, "
            "and Dama's Veil of Haunting Terror, laid along the game "
            "trail that rings the grounds and runs out to the main road, "
            "fills anyone without Magic Resistance who sets foot on it "
            "with visions of their worst fear and an overwhelming urge to "
            "run. The locals fear the marsh and tell ghost stories of the "
            "things down that trail. Only a small track from the "
            "south-west is left clear, and Redcaps know to use it.",
            "Dama and Rebecca are its only magi, with Rebecca's "
            "apprentice Alexa and their servants.",
        ),
        secrets=[
            titled(
                "The black rock",
                "The black rock at Mimizan is where the Gauls drowned captives "
                "for Maju, then worshipped as Teutates; an inscription lies "
                "under the mud, and votive silver rings lie in the lake.",
            ),
            titled(
                "The cloaked aura",
                "Dama's Tower at Mimizan is Infernal now, but Maju keeps the "
                "aura cloaked so it seems Faerie, at a constant cost to its "
                "Might.",
            ),
            titled(
                "Why the place is frightening",
                "Dama made Mimizan frightening on Maju's advice, saying the "
                "Veil protects it from crusaders.",
            ),
        ],
        realm="Faerie",
        aura=4,
        **KNOWN_TRIBUNAL,
    )
    _add(
        provence,
        "mimizan_copse",
        "The Copse of Mimizan",
        inside=provence.places["mimizan"],
        summary=paragraphs(
            "A stand of scrub trees inland from Dama's tower on the north "
            "side of the lake, with a Faerie aura of 3. Every year twelve "
            "Basque folk witches and some Ex Miscellanea magi meet here with "
            "Dama to help her and to plan the coming months; she leads the "
            "gathering and initiates many of them into the Matres and "
            "Matrones. Nearly all honour her as a grande dame, and a few "
            "revere her as a saint.",
            "The sorginak of the Basque covens, at least sixty-one unGifted "
            "and about nine Gifted in thirteen covens across the west of the "
            "Tribunal and north-west Iberia, trade news, favours, apprentices "
            "and vis among themselves and mostly defer to Dama; they also "
            "gather at akelarre. Only the Gifted, who have sworn the Oath, "
            "belong to the Order. About nine Gifted sorginak live in or near "
            "Bayonne in Labourd, others round Pau in Béarn, in Soule and in "
            "Pyrenean villages; three Hermetic sorginak who live alone keep "
            "out of Dama's circle.",
        ),
        realm="Faerie",
        aura=3,
        **SECRET,
    )
    _add(
        provence,
        "poitiers_manor",
        "Marie's Manor near Poitiers",
        inside=region,
        summary=paragraphs(
            "A chapter of Castra Solis: Marie of Merinita's manor house near "
            "Poitiers in Poitou, which counts as part of the covenant though "
            "it stands in lands usually reckoned the Normandy Tribunal's. "
            "Marie attends the Provençal Tribunal and is working to push its "
            "border north by spreading the language and culture of the south "
            "through Aquitaine; since the Tribunal runs wherever Occitan is "
            "spoken, the claim may have to be settled with Normandy.",
        ),
        **KNOWN_TRIBUNAL,
    )


# ------------------------------------------------------------ Castra Solis


def _castra_solis(provence: Provence, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "The domus magna of House Flambeau, whose device is a flaming yellow "
        "sun, and one of the strongest covenants in the Tribunal. It is the "
        "home of every kind of warrior magus the House breeds, from soldierly "
        "Mithraians to knightly milites, and its seventeen magi are mostly "
        "Flambeau. Its outlook is still northern, and Primus Garus sets most "
        "of its course: it backs the crusade and the Church, its attitudes "
        "are very Christian and its aims very political. It is generous to "
        "those who work with it and deeply distrusts Tytali, refusing help to "
        "any new covenant with many of them.",
        "Kaeso, a Christian wizard who joined House Flambeau in 809, drew his "
        "strength from an old underground temple of Mithras in the hills by "
        "the Garonne. Though he sat at Tribunal for Val-Negra and spent his "
        "years in the mountains beside Apromor, his master, and the Founder, he "
        "raised there the Hoplites, soldier magi first known for hurling "
        "Pilum of Fire from behind a mighty Parma; fighting the sahirs of "
        "Iberia, merciful Kaeso made 'join or die' mean 'join', bringing many "
        "foes into the House. He rose to the inner circle of the Legion of "
        "Mithras, and most Hoplites followed him into the cult.",
        "In the 840s raids on the western coast grew, and by 850 the "
        "Flambeau took the Norse raiders and their vitkir for an organised "
        "Order of Odin. Kaeso fortified his temple near Bordeaux with the "
        "House's backing and named the camp Castra Solis, the camp of the "
        "sun, under a sun quartered in four. Bordeaux fell to the pagans two "
        "years later; the Hoplites, unsure how far the Code let them strike "
        "at mundanes and unwilling to burn the city, were ambushed again and "
        "again by the rune wizards, and Kaeso was among the dead. In 855 the "
        "survivors built a true stronghold, Sinapis, in Anjou, and Castra "
        "Solis became a mobile camp of tents, seen from outside as Sinapis's "
        "offshoot. The war smouldered for over a century; the Hoplites' "
        "outposts, warded with the Aegis, became covenants counted as part of "
        "Castra Solis, Mimizan among them. The Hoplites told the Grand "
        "Tribunal of 997 of the raiders' three coastal settlements burned and "
        "the vikings gone. By then magi of other Houses, Tremere and "
        "Guernicus above all and one notable Greek maga of Merinita, had "
        "joined them, but the Diedne, who suffered from the raids, would not "
        "fight beside such pious Mithraians, deepening the Hoplites' "
        "suspicion of them.",
        "When the Schism War opened with the Diedne's capture of the portals "
        "at Harco and the assault on Val-Negra, the Primus returned to Castra "
        "Solis to direct the House and seemed to abandon Val-Negra; most of "
        "the Gascon Diedne fled, many burning their sites behind them. Peace "
        "came at last, the new Primus stayed and built, and Castra Solis "
        "became the domus magna. When the Normandy Tribunal split in 1103, "
        "it led the faction that joined the enlarged Provençal Tribunal, "
        "bringing the magi of Sinapis, who gave up their site, Mimizan and "
        "other small covenants. It has been stable and powerful ever since, "
        "and hosted the bitter Tribunal of 1214 when Toulouse was besieged.",
        "Its magi range from the newly gauntleted to the frail Primus. In the "
        "last twenty years two older magi of House Guernicus who lived here, "
        "each Presiding Quaesitor in turn and both younger than Garus, have "
        "died, and everyone, Garus included, expects him to be next. The "
        "Praeco Dama and her filia Marie are members though they live at "
        "Mimizan and near Poitiers; Beatrice of Guernicus is registered here "
        "but lives in the Arelat.",
    )
    what_matters = joined_lines(
        "Votes: 17 at Tribunal, plus the votes of the Praeco and (if Beatrice is confirmed) the Presiding Quaesitor",
        "Library: a fine collection with a military bent (described in Houses of Hermes: Societates; no books named in Faith & Flame)",
        "Enchantments: many devices kept to defend the House when needed",
        "Vis: Rebecca's personal source, 5 pawns of Corpus each spring equinox from afterbirth rendered at a hillside shrine",
        "Vis: Dama carries 15 pawns of Faerie Vim in three gold rings and can raise 25 more within a week through her cult",
        "Vis: Rebecca keeps 15 pawns of Corpus in a string of animal skulls",
        "Income: the House's sponsorship of tourneys on the covenant's fields",
        "Chapters: Mimizan (Dama and Rebecca) and the manor near Poitiers (Marie); Beatrice's sanctum at Glanum counts as a small chapter too",
        "Portal: none; the Primus never thought one needed",
        "Boon: Aura (Magic 3); Manor House; Prestige (domus magna); Veteran Fighters (the milites); Famous Resident (the Primus)",
        "Hook: House Covenant; Chapter House; Hermetic Politics; Superiors (the House looks to it)",
        "Cult: the Legion of Mithras, whose inner circle under Marcus Minor truly leads the covenant; services in its mithraeum (Divine 4) are near-sacraments",
        "Tension: Aedes Mercurii claims Val-Negra's legacy and the title of domus magna, and Flammarcus means to be Primus when Garus dies",
        "Tension: Garus is ancient and the succession is open; Garus is not of the Legion's inner circle",
        "Tension: Beatrice has fallen out with Garus, or with a society of the Arelat, and keeps away",
        "Tension: Dama is openly pagan, which unsettles the pious magi",
        "Tension: Marie's push to carry the Tribunal's border into Poitou and Aquitaine",
        "Tension: the faidits want the milites' backing, even open magic, against the crusaders",
        "Hook: Garus owns one of the old Redcap lanterns that light the way through Val-Negra's regio",
    )
    votes = paragraphs(
        "Votes and politics. Castra Solis holds 17 votes, with the Praeco's "
        "and the Presiding Quaesitor's besides. The Coenobium is its firm "
        "ally, and together they can carry almost anything, though both know "
        "the smaller covenants must not be driven to walk out. Bellaquin "
        "counts it a staunch friend, Stella Durus usually follows Renaud's "
        "lead toward it, Ara Maxima Nova follows it or abstains, and "
        "the Ostal des Exiles thinks it misguided; Aedes Mercurii hates it "
        "and works against it at every turn. In private its magi think Aedes "
        "Mercurii a liability too big to fight openly but apt to wreck "
        "itself. At the 1221 Tribunal the faidits and refugees will seek the "
        "approval and backing of Garus and his milites.",
        "The milites are Flambeau, mostly Hoplites, who stayed at Castra "
        "Solis after each war and have sworn a chivalric oath of service "
        "before Garus; under him they see themselves as knights serving a "
        "liege. The Mithraians of the House are mostly Christian; some have "
        "fought in the Reconquista in secret. They are split over the "
        "milites but united in contempt for the Mercurian Flambeau and their "
        "pretensions; the pious here think the Mercurian flamen at "
        "Tribunal blasphemous.",
    )
    hidden = [
        titled(
            "The true mithraeum",
            "The mithraeum under Castra Solis is Kaeso's copy; the true temple "
            "lies secret under Bordeaux.",
        ),
        titled(
            "Who killed the Presiding Quaesitors",
            "Dama, the Praeco, killed the Presiding Quaesitors Senex (1210) and "
            "Tibaut (1219).",
        ),
        titled(
            "Dama's familiar",
            "Dama's familiar Maju is becoming a demon.",
        ),
        titled(
            "Tibaut's lab notes",
            "Tibaut's lab notes on Senex's last inquiry are in his sanctum at "
            "Castra Solis; Senex told no one where he went.",
        ),
        titled(
            "The Praeco's bargain",
            "Dama won the Chief Redcap Alazais's tacit support by secretly "
            "making a Longevity Ritual for her mundane companion, and counts on "
            "Castra Solis's weight to bury any motion against her.",
        ),
        titled(
            "Storyguide Notes",
            "For Dama and Maju see her sheet and the Serpent's Venom.",
        ),
    ]
    castra = b.covenant(
        "Castra Solis",
        tribunal=tribunal,
        founded=850,
        place=provence.places["castra_solis_site"],
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(votes),
        secrets=hidden,
        aura=3,
        unnamed_magi=11,
        season="Summer",
    )
    provence.covenants["castra_solis"] = castra
    _castra_solis_magi(provence, b, castra)
    b.book(
        castra,
        "The library of Castra Solis",
        "Other",
        description=(
            "The domus magna's library, strong in military subjects: the "
            "warfare of magi, Hoplite tactics, and the lore of the House's "
            "many wars. Faith & Flame names none of its books (Houses of "
            "Hermes: Societates describes it). Hidden stairs lead from it to "
            "the chambers behind the mithraeum."
        ),
    )


def _castra_solis_magi(provence: Provence, b: Builder, castra: Covenant) -> None:
    m = provence.magi
    m["garus"] = b.magus(
        "Garus",
        covenant=castra,
        house=FLAMBEAU,
        age=135,
        summary=paragraphs(
            "Primus of House Flambeau, very old and frail, looking about "
            "eighty. English by birth and training, he crossed to Gascony in "
            "1155 straight after Henry married Eleanor of Aquitaine. When "
            "Primus Vancasitum vanished late in the twelfth century, Garus "
            "won the primacy chiefly through the milites, the Flambeau "
            "Hoplites who stayed on at Castra Solis after each war; under "
            "him they came to see themselves as knights serving a liege, and "
            "his long rule has turned the House toward politics. He has "
            "always cared about the politics of the region, more than about "
            "the Legion of Mithras, whose inner circle he never joined. He "
            "keeps one of the old Redcap lanterns that light the way to "
            "Val-Negra. Everyone expects him to die soon, himself included, "
            "and Flammarcus of Aedes Mercurii waits for the day.",
        ),
        traits={"Political": 3, "Steadfast": 2, "Mentoring": 1},
    )
    m["marcus_minor"] = b.magus(
        "Marcus Minor",
        covenant=castra,
        house=FLAMBEAU,
        age=119,
        summary=paragraphs(
            "The covenant's second most senior magus, looking about sixty, "
            "named Minor because an elder Marcus, Marcus Major, once lived "
            "here too. Pious and magnetic, he is the chief mystagogue of the "
            "Legion of Mithras at Castra Solis, and insiders know that he "
            "and his followers are the covenant's real leaders. He keeps the "
            "Legion's Christian bent, and through him the warrior magi have "
            "come to feel like brothers of a holy order of knights.",
        ),
        traits={"Pious": 3, "Charismatic": 3, "Crafty": 2},
    )
    m["troya"] = b.magus(
        "Troya",
        covenant=castra,
        house=FLAMBEAU,
        age=53,
        summary=paragraphs(
            "An established maga, looking about forty, who has given her life "
            "to magical mounts, horses above all. Her stable is bred and "
            "trained to bear Gifted riders, by methods she shares by letter "
            "with like-minded magi in Hibernia, and her horses learn charges, "
            "leaps and other moves useful to a magus in battle: dashing in "
            "to cast a Touch spell or snatch a hair for an Arcane Connection, "
            "then away. Many of her spells change horse and rider together. "
            "Her horses are said to descend from the stock of Bayard, the "
            "magic horse Maugris gave his cousin Renaud de Montauban four "
            "centuries ago.",
        ),
        traits={"Bold": 3, "Considerate of horses": 3, "Proud": 2, "Curious": 1},
    )
    m["marie"] = b.magus(
        "Marie of Merinita",
        covenant=castra,
        house=MERINITA,
        age=113,
        summary=paragraphs(
            "Filia of Dama, who trained her as her only apprentice about "
            "a century ago; she looks about forty-five, and sometimes "
            "calls herself Marie of France. A famous figure in her "
            "House, headstrong and independent, she lives in a manor "
            "near Poitiers counted part of Castra Solis though it stands "
            "in Normandy's lands, attends the Provençal Tribunal, and "
            "works to bring all Aquitaine into it by spreading the "
            "language and culture of the south.",
            "She escaped her mater's grip mostly through her devotion to "
            "Eleanor of Aquitaine, whom she sees as her twin or her "
            "mundane counterpart. She says she rode with Eleanor on the "
            "Second Crusade in her bare-breasted Amazon procession, "
            "guarding her with her Parma; came home with her after the "
            "annulment; followed her to Henry's English court; and wrote "
            "romances and fables for its nobles. Since Eleanor died she "
            "has come back to Poitou to grieve and turned to Hermetic "
            "politics. She has Faerie Blood and the second degree of the "
            "Matres and Matrones, which lets her initiate others and lead "
            "rites, though she seldom does; she has trained several "
            "apprentices, all gone abroad. She says Eleanor was a folk "
            "witch who brought secrets home from her uncle's court in the "
            "Holy Land. Dama wants her to become a Matron, but Marie "
            "thinks of her as a harsh taskmistress; they are cold to each "
            "other, and Marie honours Eleanor far more.",
        ),
        secrets=[
            titled(
                "Eleanor's faerie double",
                "Perhaps none of it happened: Marie may instead have trailed "
                "after an Arcadian faerie queen who looks like Eleanor and feeds "
                "on the stories told of her.",
            ),
            titled(
                "Why Dama drove Marie away",
                "Dama drove her away by putting the cult first and refusing the "
                "rites Marie said Eleanor taught her.",
            ),
        ],
        traits={"Unaging": 3, "Political": 3, "Artistic": 2},
    )
    m["beatrice"] = b.magus(
        "Beatrice of Guernicus",
        covenant=castra,
        house=GUERNICUS,
        age=None,
        summary=paragraphs(
            "Filia of the late Presiding Quaesitor Tibaut, acting in his "
            "office and presumed to succeed him at the Tribunal of 1221, "
            "though that may be contested and is the first business of "
            "the meeting. A troubled woman, she truly means to do right, "
            "but amid the crusade and the Tribunal's feuds she is no "
            "longer sure what right is. She is young for the office, has "
            "won little respect from the factions yet, and would likely "
            "hand it to another of her House if a better one came "
            "forward. Registered at Castra Solis, she spends all her time "
            "in the Arelat, living as the Coenobium's guest at the ruins "
            "of Glanum, where she studies the Roman shrines of the cults "
            "that flourished there; some say she has fallen out with "
            "Garus, others with one of the societies based in the "
            "Arelat. She is thought to sympathise with the Matres and "
            "Matrones.",
        ),
        secrets=[
            titled(
                "Tibaut's letters",
                "Tibaut told her he believed Senex dead, and sent her sealed "
                "letters by an Iberian Redcap who was ambushed by crusader "
                "camp followers and died in the wilds by the Via Domitia; "
                "the letter is still in his satchel.",
            ),
            titled(
                "How Beatrice came to the office",
                "When Tibaut missed their meeting she took her fears to Dama, "
                "who calmly suggested she hold the office until the Tribunal; "
                "honoured, she agreed.",
            ),
            titled(
                "Dama's hopes for Beatrice",
                "Dama believes Beatrice will not pursue her pater's inquiry and "
                "has all but drawn her into the cult.",
            ),
        ],
    )
    _mimizan_magi(provence, b, castra)


def _mimizan_magi(provence: Provence, b: Builder, castra: Covenant) -> None:
    m = provence.magi
    m["dama"] = b.magus(
        "Dama of Merinita",
        covenant=castra,
        house=MERINITA,
        age=1220 - 993,
        summary=paragraphs(
            "The Praeco of the Tribunal, by custom its eldest magus, born "
            "in 993. Twilight has shattered her early memories: she may "
            "have been the child of a Basque folk witch and a Viking "
            "raider. Her mater was a Greek Merinita and former Thessalian "
            "witch who had learned the Hoplite's trade at Val-Negra and "
            "Castra Solis and was versed in her House's symbolic and sympathetic "
            "mysteries. Dama became her apprentice in 1001, just before "
            "the Schism War, and the two hid as guests at the court of "
            "Oriande la Fée. Gauntleted in 1016, Dama took the whole "
            "path of Story Magic and unwisely swore herself to Oriande's "
            "court.",
            "In 1061 her risks threw her into Twilight. Nineteen years "
            "later something came back that a Quaesitor confirmed as "
            "Dama, though it was more a husk woven of patchwork memory, "
            "ambition and desire, glowing faintly like the Virgin in "
            "the painted images, with auburn hair and ruddy skin. Her "
            "fey oath ran for her natural life, and a faerie prophecy "
            "said she would die at seventy, so she came back free of it. "
            "A very old man who called himself a childhood friend made "
            "her take a farewell gift, a green-black stone the size of "
            "a hen's egg he called a baetylus, and charged her to carry "
            "it far from the castle and keep it from the one who craved "
            "it: it would give Dama vigour, but Oriande would use it as "
            "an Orphic Egg for a great apotheosis. Oriande was "
            "displeased but could do nothing.",
            "Resolved to leave a legacy of her own rather than her "
            "House's, she trained one apprentice, Marie; founded "
            "Mimizan; bound Maju, a faerie of the lake, as her familiar "
            "with her House's spell; and founded a mystery cult, the "
            "Matres and Matrones, devoted to raising up women, which she "
            "leads as mystagogue. The cult is obscure but not secret, and "
            "a little digging shows she is at its heart. She favours "
            "female magi and is a true friend to women. She is openly "
            "pagan, which leaves the pious of Castra Solis uneasy about "
            "her and gives Aedes Mercurii hope she is fair; even the "
            "Mercurians heed her when she speaks. She dislikes visitors, "
            "and has grown more secretive, paranoid and ambitious.",
            "She looks an older, handsome Basque woman in rich court "
            "dress, silver hair with a trace of auburn pulled into a bun "
            "under a Basque shawl, with a fine dagger, gold rings on her "
            "fingers and the stone hung from a gold chain, leaning on a walking "
            "stick; her faint amber glow shows most at evening, when she "
            "seems almost a ghost. A scent of lilies attends her magic. "
            "Her voting sigil is an ivory dragon's head gilded in red "
            "gold, her father's gift and the only thing she has from "
            "before her apprenticeship.",
        ),
        secrets=[
            titled(
                "What Maju is",
                "Maju is not what it seems. Worshipped by the Gauls as "
                "Teutates, who drowned captives for it at the lake's black "
                "rock, it later wore the mask of Sugaar among the Basques, "
                "then returned to play in Oriande's court, where Dama first "
                "saw it.",
            ),
            titled(
                "Maju's hold on Dama",
                "Maju has bound her spirit as she bound it, and its counsel "
                "led her into sin and blasphemy and to the edge of "
                "infernalism.",
            ),
            titled(
                "The cult's upper levels",
                "Maju had her build the chthonic sorginak into her cult under "
                "the guise of the Black Madonna, so that at its upper levels "
                "the Matres and Matrones are a coven of tainted witches close "
                "to demonic corruption.",
            ),
            titled(
                "Maju becoming a demon",
                "Through the Matres and Matrones Maju sets women against men "
                "and against Christ, and the sins it spreads will soon make it "
                "a demon outright; it already hides the Infernal aura at "
                "Mimizan.",
            ),
            titled(
                "Maju's shapes",
                "Maju appears as a winged sprite, a hare, a dove or, in "
                "private, a snake that coils round her throat.",
            ),
            titled(
                "The death of Senex",
                "In 1210 Senex, Presiding Quaesitor, came to suspect her "
                "cult. While she was away at an akelarre he slipped into "
                "Mimizan; she came back early and found him in her sanctum. "
                "The Aegis, Revoke the Protection of Bonisagus and Maju's "
                "viper venom killed him; she stripped his goods and Maju, as "
                "a drake, ate the body.",
            ),
            titled(
                "Whether Senex's killing was lawful",
                "Having entered her sanctum uninvited Senex had forfeited his "
                "immunity, so the killing was lawful, but she told no one to "
                "keep the cult unseen.",
            ),
            titled(
                "Tibaut's inquiry",
                "Senex's successor Tibaut found the thread in Senex's notes, "
                "began probing the Tribunal's cults in 1217, and pressed Luc "
                "of Ara Maxima Nova about clergy and pilgrims on the Via "
                "Domitia.",
            ),
            titled(
                "Luc's warning",
                "Luc of Ara Maxima Nova lost a Certamen to Tibaut and told "
                "Dama which Arts to avoid.",
            ),
            titled(
                "The death of Tibaut",
                "In 1219 she lured Tibaut into an abandoned house near the road "
                "to Foix, broke his Parma, and set Maju on him; he staggered "
                "into the road and collapsed, and crusader knights, Divinely "
                "blessed and proof against her magic, carried him to the "
                "Abbey of Saint Hilaire, where he died of the poison. They "
                "later took him for a Cathar and raided the abbey.",
            ),
            titled(
                "Tibaut's grave",
                "Tibaut lies in the cemetery of the Abbey of Saint Hilaire; his "
                "belongings sit locked in a chest in the abbot's office.",
            ),
            titled(
                "What Tibaut may have told",
                "Dama does not know whether Tibaut told the knights or the "
                "monks anything.",
            ),
            titled(
                "Dama and Beatrice",
                "She has never killed a woman. She worries a little that "
                "Beatrice is a woman, but thinks Beatrice will not follow her "
                "pater's trail and has nearly won her for the cult.",
            ),
            titled(
                "The Coenobium's support",
                "She bought the tacit support of Alazais and the Coenobium by "
                "secretly making a Longevity Ritual for Alazais's mundane "
                "companion.",
            ),
            titled(
                "Dama's failing ritual",
                "Her own Longevity Ritual is failing: she must renew it before "
                "1232, may sacrifice Maju for its vis, and feels her legacy "
                "slipping away.",
            ),
            titled(
                "Maju's urging",
                "Maju urges her to draw more sorginak in and bend their faith "
                "in Mari and Sugaar, and needles her about Marie and about "
                "Mimizan's smallness beside Rosefleur.",
            ),
            titled(
                "No more apprentices",
                "She has taken no more apprentices, as Maju thinks it too risky.",
            ),
            titled(
                "Dama's soul",
                "If she is shown what her familiar truly is, she may yet be "
                "saved; if she falls, Maju means to carry her soul to Hell.",
            ),
            titled(
                "The baetylus",
                "The baetylus holds a shard of the beginning of Creation, "
                "perhaps of Sol Invictus or of Cronus.",
            ),
            titled(
                "The baetylus's gifts",
                "Touching the baetylus guards her against aging; it purifies "
                "her and all she touches or eats, so poison cannot harm her; "
                "and it gives her visions of danger to herself or the stone, "
                "which feed her paranoia.",
            ),
            titled(
                "The tale of the baetylus",
                "The tale she believes says the baetylus fell into the lake of "
                "Toulouse and was raised by pagan wizards who later became "
                "Diedne, and that Maugris kept it, long-lived by its power, "
                "hid with it at Oriande's court in the Schism War, and gave "
                "it to her so that he could at last die and so that Oriande, "
                "whom he foresaw it would corrupt, would never have it.",
            ),
            titled(
                "Storyguide Notes",
                paragraphs(
                    "Maju as a demon: Infernal Might 45, a Duke of False Gods. "
                    "See the Serpent's Venom.",
                    "Touching the baetylus she adds 5 to her aging rolls and "
                    "suffers no aging crises; it purifies as the Greater "
                    "Purifying Touch.",
                ),
            ),
        ],
        traits={"Driven": 4, "Proud": 3, "Optimistic": 2},
    )
    m["rebecca"] = b.magus(
        "Rebecca",
        covenant=castra,
        house=EX_MISC,
        age=32,
        summary=paragraphs(
            "A Basque sorgina of House Ex Miscellanea, a folk witch who "
            "has sworn the Oath, and the only other resident of Mimizan. "
            "Her father found a hoard of Roman gold in their village and "
            "spent it quietly on her comfort and schooling, grooming her "
            "to marry one of the region's lesser knights; but Dama's "
            "coven found her, talked several of her suitors into going "
            "on crusade, and took her in. After her apprenticeship she "
            "became Dama's chief helper, and she serves her as envoy, "
            "messenger and spy, flying and changing shape to travel fast "
            "and unseen. She often goes home to fly over the whalers as "
            "an albatross, and they follow her gladly as a good omen. She "
            "nurses young mothers through childbirth with potions and "
            "takes the afterbirth as her fee, rendering it each spring "
            "equinox at an old hillside shrine for 5 pawns of Corpus "
            "vis, her own source.",
            "She still hopes to find a husband, ideally a young magus of "
            "good breeding and character, and would welcome a quick "
            "romance and a quicker marriage, for she wants a child soon; "
            "a mundane knight or ship's captain might do, but her "
            "upbringing, growing power and pride set the bar high. Close "
            "to pagan, she sees nothing wrong in the Matres and "
            "Matrones: does not all mortal life come from women? She is "
            "teaching an apprentice, young Alexa, who helps Dama while "
            "Rebecca is away and means to be initiated into Intuition "
            "when she joins the cult. Rebecca's voting sigil is a wolf "
            "fetish she took in a fight from a rival sorgina.",
        ),
        secrets=[
            titled(
                "Rebecca and the cult",
                "She is one of the sorginak Maju is working to corrupt through "
                "Dama's cult.",
            ),
        ],
        traits={"Optimistic": 2},
    )


# ------------------------------------------------------------- Tres' Band


def _tres_band(provence: Provence, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "A roving covenant in all but name: the notorious rusticanus Tres Ex "
        "Miscellanea, his two filii, also rusticani, and their custodes, gone "
        "to ground in the moors and woods near Bazas since the Tribunal of "
        "1214. Tres leads a ragtag following of outcasts and opportunist "
        "routiers from the northern armies, and came back to the Tribunal of "
        "his birth seeking vengeance.",
        "In the winter of 1209 he declared Wizard's War on every magus of "
        "Mistridge, the famed tower on a precipice in the Val du Bosque; some "
        "say to avenge Windgraven, others that its proud magi had refused him "
        "hospitality and treated him as a hedge wizard. With his two fellow "
        "rusticani, a host of mercenaries carrying magic weapons of his own "
        "making, and magical siege engines, he levelled the conjured tower "
        "and killed its defenders. At the Tribunal of 1214 he was charged "
        "with arming hirelings and calling them grogs; many deplored it, but "
        "the war was justly declared and no ruling barred grogs from it, so "
        "the vote went narrowly his way. He wisely vanished before Mistridge's "
        "friends could take revenge.",
        "The band holds three votes it never casts: it does not attend "
        "Tribunal and opposes nearly everything the Order does. It is aloof "
        "toward new covenants at first, and over many seasons comes to hate "
        "those that lord it over the mundanes around them, which it sets out "
        "to dissuade; it would rather not teach the lesson of Mistridge again "
        "but would not shrink from it.",
    )
    what_matters = joined_lines(
        "Votes: 3, never used; the band does not attend Tribunal",
        "Craft: Tres's magic weapons and siege engines; some think one of them struck down Simon de Montfort at Toulouse in 1218",
        "Boon: Hedge Tradition (the rusticani, an Ex Miscellanea tradition of craft magic)",
        "Hook: Constantly Mobile; Infamous (Mistridge); Hermetic Politics",
        "Tension: the friends of Mistridge want revenge; the Ostal des Exiles, made of Mistridge's survivors, has not forgiven Tres",
        "Tension: hostile to any covenant that makes itself a ruling class over the peasantry",
    )
    tres_band = b.covenant(
        "Tres' Band",
        tribunal=tribunal,
        founded=None,
        place=provence.places["bazas_landes"],
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(
            "The book gives no founding year, aura or season for the band; "
            "the section the Tribunal chapter points to for Tres is missing "
            "from Faith & Flame. Its two other magi are unnamed.",
        ),
        unnamed_magi=2,
        season="Summer",
    )
    provence.covenants["tres_band"] = tres_band
    provence.magi["tres"] = b.magus(
        "Tres",
        covenant=tres_band,
        house=EX_MISC,
        age=None,
        summary=paragraphs(
            "An infamous rusticanus of House Ex Miscellanea, a craft magus "
            "born in the Tribunal who came home for revenge, leading two "
            "filii and a rabble of outcasts and routiers. He destroyed "
            "Mistridge in a Wizard's War in 1209 with magic-armed mercenaries "
            "and siege engines of his own making, was narrowly acquitted at "
            "the Tribunal of 1214 because grogs may lawfully fight in a "
            "Wizard's War, and went into hiding near Bazas. Some suspect the "
            "stone that killed Simon de Montfort at Toulouse came from one of "
            "his engines.",
        ),
    )
    b.book(
        tres_band,
        "The library of Tres' Band",
        "Other",
        description=(
            "Whatever books the band keeps travel with it or lie in its "
            "scattered sancta; the book names none. The rusticani are a "
            "craft tradition, and their lore of magical weapons and siege "
            "engines is their treasure."
        ),
    )


# -------------------------------------------------------------- the lords


def _lords(provence: Provence, b: Builder) -> None:
    w = provence.world
    region = provence.places["gascony"]
    w["henry_iii"] = b.lord(
        "Henry III, King of England and Duke of Aquitaine",
        title="duke",
        wealth="Wealthy",
        manors=40,
        seat="Bordeaux",
        place=region,
        summary=paragraphs(
            "The boy king of England, fourteen in 1220, whose crown has held "
            "Gascony firmly since Richard the Lionheart. The dukes rule from "
            "Bordeaux and leave the rest alone, but for the odd show of force "
            "down the Garonne. Henry visits his mother Isabella nearby, likes "
            "to lodge at Belin, and has made Archbishop Guillaume Amanieu his "
            "Seneschal and Guardian of his lands overseas.",
        ),
    )
    w["hugh_lusignan"] = b.lord(
        "Hugh X of Lusignan, Count of Angoulême",
        title="count",
        wealth="Wealthy",
        manors=12,
        seat="Angoulême",
        place=region,
        summary=paragraphs(
            "Count of Angoulême by his marriage to Isabella of Angoulême, "
            "King John's widow and Henry III's mother, and overlord of Blaye "
            "(see The Lion and the Lily). Isabella, wed first at twelve, "
            "Eleanor of Aquitaine's choice for John and called Messalina, a "
            "siren and the Helen of Gaul by the English, married him without "
            "waiting for the English council's leave, which a queen dowager "
            "must have; the council seized her dower and stopped her pension, "
            "and the pair answered by threatening to keep Henry's ten-year-"
            "old sister Joan, promised to Alexander II of Scotland, in France, "
            "perhaps at Castle Rudel. She will bear Hugh nine more children "
            "and her beauty never fades: faerie blood, a bargain with "
            "Oriande la Fée, or a pact with Ducaru of Stella Durus?",
        ),
    )
    w["geoffrey_rudel"] = b.lord(
        "Geoffrey I, Lord of Blaye",
        title="landed",
        wealth="Wealthy",
        manors=3,
        seat="Castle Rudel, Blaye",
        answers_to=w["hugh_lusignan"],
        place=region,
        summary=paragraphs(
            "Castellan of the rich port of Blaye from Castle Rudel, beside "
            "the basilica, for the counts of Angoulême. His family has held "
            "the post for generations at the counts' pleasure, and Hugh X has "
            "lately confirmed him in it.",
        ),
    )
    w["lord_blanquefort"] = b.lord(
        "The Lord of Blanquefort",
        title="landed",
        manors=2,
        seat="Blanquefort",
        answers_to=w["henry_iii"],
        place=provence.places["medoc"],
        summary=(
            "Keeper of the white limestone castle in the Médoc that guards "
            "the Levade and the Channel Soulac, charged with taking the toll "
            "from travellers on the road."
        ),
    )
    w["baron_la_motte"] = b.lord(
        "The Baron de La Motte",
        title="baron",
        wealth="Wealthy",
        manors=5,
        seat="Roquetaillade Castle",
        answers_to=w["henry_iii"],
        place=region,
        summary="Lord of Roquetaillade near Langon, said to be the first castle "
        "Charlemagne built, a square stronghold with four towers that "
        "each lord of the line has made grander.",
        secrets=[
            titled(
                "The masons' pact",
                "The faerie masons of the nearby caves build for each new lord "
                "under a family pact passed from father to son on the deathbed.",
            ),
        ],
    )
    w["count_armagnac"] = b.lord(
        "Pierre-Gerald, Count of Armagnac",
        title="count",
        manors=10,
        seat="Auch",
        place=region,
        summary=(
            "Ruler of Auch on the Gers. He dislikes the crusading archbishop "
            "Garsie de Lhort, an old enmity rooted in the crusade: his father, "
            "the late count, loved the trobairitz Lombarda, whom he met in "
            "Toulouse and wrote to all through the war without their love "
            "ever being fulfilled, and died in 1219 before they could meet "
            "again; the son blames the archbishop's support of the crusade."
        ),
    )
    w["count_astarac"] = b.lord(
        "Centule, Count of Astarac",
        title="count",
        manors=6,
        seat="Astarac",
        place=region,
        summary=(
            "A Gascon count who led Prince Louis's crusaders to the siege of "
            "Marmande just after Christmas 1218 and held it nine months, "
            "until the garrison surrendered and the town was massacred."
        ),
    )
    w["count_bearn"] = b.lord(
        "William Raymond, Count of Béarn",
        title="count",
        manors=10,
        seat="Tarbes",
        place=region,
        summary=paragraphs(
            "An aged count who governs from Tarbes, leaving Pau to his son "
            "William. Béarn lies at the foot of the Pyrenees, caught between the "
            "crown of Aragon and the crusade on its doorstep; it is no "
            "Cathar stronghold, but the late count helped Toulouse and Foix "
            "more than once and its knights have no love for crusaders. "
            "William Raymond looks to Aragon; his son leans to the English "
            "in Aquitaine. His rights to Pau are contested, since his "
            "brother's widow Petronilla of Bigorre married Guy de Montfort.",
            "If the saga follows history, he dies in 1223 and William turns "
            "to Aragon and tries to take Cerdagne.",
        ),
    )
    w["william_bearn"] = b.lord(
        "William of Béarn",
        title="landed",
        manors=2,
        seat="Pau",
        answers_to=w["count_bearn"],
        place=region,
        summary=(
            "Heir of Béarn, who holds Pau and its ford for his father and "
            "favours the English. He might grant magi the towers above the "
            "ford in return for guarding the crossing and taking fair tolls."
        ),
    )
    w["guy_montfort"] = b.lord(
        "Guy de Montfort, Count of Bigorre",
        title="count",
        manors=6,
        seat="Tarbes",
        place=region,
        summary=paragraphs(
            "Simon de Montfort's son, count of Bigorre by marriage to "
            "Petronilla of Bigorre. He is away with the crusade and Petronilla "
            "lives at Poitiers out of reach of reprisals, so Tarbes has no "
            "seneschal and its towns keep order as best they can with the "
            "bishop and clergy. Bigorre's capital at Lourdes, with its salt "
            "valleys, matters more to the crusade than Tarbes.",
            "If the saga follows history, he is killed in April 1220 in a "
            "skirmish with the count of Toulouse's men near Castelnaudary.",
        ),
    )
    w["count_labourd"] = b.lord(
        "The Count of Labourd",
        title="count",
        manors=5,
        seat="Ustaritz",
        answers_to=w["henry_iii"],
        place=region,
        summary=(
            "A Basque lord who has lived at Ustaritz, ten miles east of "
            "Bayonne, since Richard the Lionheart crushed the local barons in "
            "1177 for rising against King Henry and held Bayonne himself until "
            "1199. Bayonne's charter of 1215 freed the city from his "
            "authority."
        ),
    )


# ------------------------------------------------------------ the Church


def _churches(provence: Provence, b: Builder) -> None:
    w = provence.world
    region = provence.places["gascony"]
    w["bordeaux_cathedral"] = b.church(
        "Bordeaux Cathedral",
        church="Archbishop's cathedral",
        ruler="Archbishop Guillaume Amanieu",
        founded=1096,
        place=region,
        summary=paragraphs(
            "The archbishop's seat, consecrated by Urban II in 1096. Its "
            "archbishops are often open agents of English policy, and "
            "Guillaume Amanieu is no exception: Henry III has named him "
            "Seneschal and Guardian of all his lands overseas. No meek "
            "scholar, he has fought in the Reconquista and the Albigensian "
            "Crusade, and quarrels often with Simon de Sully, archbishop of "
            "Bourges.",
            "The city's other great churches are the basilicas of St Seurin "
            "and of St Michel, the latter outside the walls; Roland's broken "
            "horn, the Olifant, is said to rest in St Seurin.",
        ),
    )
    w["sainte_croix"] = b.church(
        "The Abbey of Sainte-Croix de Bordeaux",
        church="Monastery or nunnery",
        order="Benedictine",
        place=region,
        summary=(
            "A powerful Benedictine abbey of Bordeaux, with a small daughter "
            "house north-west of Soulac, the first monastery in the area."
        ),
    )
    w["belin_church"] = b.church(
        "The Church of Belin",
        church="Parish church",
        place=provence.places["belin"],
        summary=(
            "The tomb church of Olivier de Viennes, Ogier the Dane and other "
            "Peers of Charlemagne, Divine aura 4, its air sweet with a "
            "healing scent; its Creo vis is described with Belin."
        ),
    )
    w["bazas_cathedral"] = b.church(
        "The Cathedral of St John the Baptist, Bazas",
        church="Bishop's cathedral",
        place=region,
        summary=(
            "The bishop's church of Bazas, where pilgrims on the Limoges road "
            "pray before going on to Ostabat. St Veronica built its oratory, "
            "and its altar holds a relic of the Baptist's blood that Urban II "
            "declared genuine in 1092; he came back in 1096 to preach the "
            "Crusade here. Divine aura 5, 6 on 29 August, the feast of the "
            "Baptist's beheading."
        ),
    )
    w["bazas_templars"] = b.church(
        "The Templar Hospital of Bazas",
        church="Hospital",
        order="Knights Templar",
        place=region,
        summary="A hospital the Templars keep in Bazas for pilgrims on the Way.",
    )
    w["saint_romain"] = b.church(
        "The Basilica of Saint-Romain, Blaye",
        church="Large urban church",
        place=region,
        summary=paragraphs(
            "A basilica over the Gironde estuary, a favourite stop on the "
            "Way: pilgrims pray at its crypt and altar before taking the "
            "ferry. In the crypt Charibert, the old king of Aquitaine, and "
            "Roland, Charlemagne's greatest paladin, lie in white marble "
            "tombs. Divine aura 4, rising to 5 on 15 August, the day Roland "
            "died, and on St Romain's day, 24 November. A hospice of St "
            "Nicholas beside it cares for pilgrims.",
            "Roland's relic-filled sword Durendal and his horn, the Olifant, "
            "carved from a unicorn's horn and split by his last blast, are "
            "not here. The horn is said to be in St Seurin at Bordeaux. "
            "Durendal's golden hilt is said to hold a tooth of St Peter, "
            "blood of St Basil, a lock of St Denis's hair and a scrap of the "
            "Virgin's clothing, a mighty weapon against demons and harmful "
            "magic; the Confraternity of Roland says it was the work of "
            "Wayland Smith and Verditius together. Roland is said to have cut the Brèche de "
            "Roland with it and flung it away; a sword stuck in the cliff "
            "under the abbey of Rocamadour may be it, unless Charlemagne "
            "took it and Roscius of Verditius later stole it away to Verdi.",
        ),
    )
    w["blanquefort_church"] = b.church(
        "The Church of St Martin, Blanquefort",
        church="Parish church",
        place=provence.places["medoc"],
        summary=(
            "A white limestone church whose crypt holds a great marble "
            "sarcophagus, perhaps the tomb of one of Charlemagne's Peers."
        ),
    )
    w["soulac_basilica"] = b.church(
        "Notre-Dame de la Fin des Terres, Soulac",
        church="Large urban church",
        place=provence.places["medoc"],
        summary=(
            "The church where many English pilgrims begin the Way, rich in "
            "relics: a candle from the Nativity, palm leaves strewn before "
            "Christ in Jerusalem, and above all drops of the Virgin's milk. "
            "Divine aura 4. The Hospitallers keep a hospice in the town."
        ),
    )
    w["auch_cathedral"] = b.church(
        "The Cathedral of St Thomas, Auch",
        church="Archbishop's cathedral",
        ruler="Archbishop Garsie de Lhort",
        place=region,
        summary=paragraphs(
            "The seat of an archdiocese since 879, when it moved from Eauze. "
            "The cathedral burned in 1170, and rebuilding has gone no further "
            "than clearing the rubble and raising a few stretches of wall; it "
            "has no Divine aura. Its relics travel with the archbishop, "
            "Garsie de Lhort, since 1214, who usually rides with Prince "
            "Louis's crusaders and was at the massacre of Marmande. The count "
            "of Armagnac loathes him.",
            "If the saga follows history, nobody tries to rebuild until 1310.",
        ),
    )
    w["saint_caprasius"] = b.church(
        "The Church of Saint Caprasius, Agen",
        church="Parish church",
        place=region,
        summary=(
            "Agen's church, where the Valerenes light candles each midsummer "
            "before walking to Limoges."
        ),
    )
    w["bayonne_cathedral"] = b.church(
        "The Cathedral of St Mary, Bayonne",
        church="Bishop's cathedral",
        place=region,
        summary=(
            "A great cathedral begun in 1213 and still building; its finished "
            "crypts hold the relics of the city's patron, Leon de Carentan, "
            "whom Vikings beheaded in the ninth century. Divine aura 2, "
            "rising to 3 on his feast, 1 March."
        ),
    )
    w["tarbes_cathedral"] = b.church(
        "The Bishop's Palace and Cathedral of Tarbes",
        church="Bishop's cathedral",
        place=region,
        summary=paragraphs(
            "The cathedral and bishop's palace at the heart of Tarbes, "
            "ringed by the town's six walled villages; with no seneschal, "
            "the bishop and clergy help the towns keep order. Legend says "
            "Tharbis, the Cushite queen of Ethiopia whom Moses spurned, "
            "founded the town. Two heirlooms pass from bishop to bishop: "
            "a polished walking staff of African moringa wood, which the "
            "bishop keeps in his office unused, and a plain gold ring set "
            "with amber in a soapstone box.",
        ),
        secrets=[
            titled(
                "The bishop's ring",
                "Whoever is given the bishops' gold ring and told to think of a "
                "subject slowly forgets it.",
            ),
            titled(
                "What the ring holds",
                "The bishops' gold ring holds 4 pawns of Mentem vis and is an "
                "Arcane Connection to the spirit of Tharbis.",
            ),
            titled(
                "How the ring's power was forgotten",
                "The power of the bishops' gold ring was forgotten when a dying "
                "bishop gave it to his successor and told him never to forget "
                "it.",
            ),
            titled(
                "Storyguide Notes",
                "The ring's forgetting: an Intelligence roll each full moon "
                "against 7, plus 1 for each failure, and after five failures "
                "the subject is gone. The effect is not Hermetic (a season and "
                "an InMe Lab Total of 30 to work out).",
            ),
        ],
    )
    w["saint_savin"] = b.church(
        "The Abbey of Saint-Savin",
        church="Monastery or nunnery",
        place=region,
        summary="An abbey and convent south of Lourdes. Roland lodged here while "
        "Charlemagne besieged Lourdes and repaid the monks by killing the "
        "giants Passamont and Alabaster, who lived near their priory and "
        "ate their flocks.",
        secrets=[
            titled(
                "What became of the giants",
                "The giants were faeries and did not die: their essence passed "
                "into the skull fetishes Roland left behind, and they now dwell "
                "deeper in the Pyrenees, behind tales of savage brutes haunting "
                "the high pastures and passes.",
            ),
        ],
    )
    w["bessaut"] = b.church(
        "The Bessaut Commandery",
        church="Hospital",
        order="Order of Santiago",
        ruler="Juan Marcos Correa",
        founded=1219,
        place=region,
        summary=(
            "The Order of Santiago's chief house in the Tribunal, with the "
            "new hospital of Our Lady Mary Magdalene, built on a gift from "
            "Guilhem de Mazerolles in 1219. Eight knights, their households "
            "and forty men-at-arms serve here, apart from any town. The "
            "Knight Commander, Juan Marcos Correa, is a cheerful veteran of "
            "the Reconquista on good terms with the other orders' houses; his "
            "brother is also of the Order in Iberia."
        ),
    )


# ---------------------------------------------------------------- towns


def _towns(provence: Provence, b: Builder) -> None:
    w = provence.world
    region = provence.places["gascony"]
    w["bordeaux"] = b.town(
        "Bordeaux",
        charter="Noble lord",
        ruler="Henry III, as Duke of Aquitaine",
        answers_to=w["henry_iii"],
        place=region,
        summary=paragraphs(
            "The great port on the Garonne and the stronghold of English "
            "power in the region since Eleanor of Aquitaine's marriage to "
            "Louis was annulled. It trades briskly in tin and lead from "
            "southern England, passing the metal on to France and beyond, "
            "and is a major stop on the Way of St James. Cenodoxus "
            "Superbia and Julian the Tempter hunt its crowds.",
        ),
        secrets=[
            titled(
                "Kaeso's true mithraeum",
                "Kaeso's true mithraeum lies in a cavern under Bordeaux's "
                "southern quarter.",
            ),
        ],
    )
    w["blaye"] = b.town(
        "Blaye",
        charter="Noble lord",
        ruler="Geoffrey I",
        answers_to=w["geoffrey_rudel"],
        place=region,
        summary=(
            "An ancient, prosperous port on the Gironde, older than Caesar's "
            "conquest and a bulwark of Charlemagne's against the Saracens, "
            "where pilgrims take the ferry across the estuary; Julian the "
            "Tempter haunts the crossing."
        ),
    )
    w["soulac"] = b.town(
        "Soulac",
        charter="Noble lord",
        place=provence.places["medoc"],
        summary=(
            "A small town at the tip of the Médoc where many English pilgrims "
            "start the Way, with a Hospitaller hospice and the basilica of "
            "Notre-Dame de la Fin des Terres."
        ),
    )
    w["langon"] = b.town(
        "Langon",
        charter="Noble lord",
        place=region,
        summary=(
            "A trading port on the left bank of the Garonne and a stop on the "
            "Way before Bazas, near Roquetaillade Castle."
        ),
    )
    w["bazas"] = b.town(
        "Bazas",
        charter="Church",
        place=region,
        summary=(
            "A walled cathedral city on the edge of the Landes where the "
            "Garonne meets the Brion, a regular stop on the Limoges road of "
            "the Way, with a Templar hospital and the cathedral of St John "
            "the Baptist."
        ),
    )
    w["auch"] = b.town(
        "Auch",
        charter="Noble lord",
        ruler="Pierre-Gerald of Armagnac",
        answers_to=w["count_armagnac"],
        place=region,
        summary=(
            "The archbishop's town on the Gers, ruled by the count of "
            "Armagnac, with its burnt-out cathedral and the mithraea beneath."
        ),
    )
    # Toulousain makes Agen; Gascony adds the Valerenes to it.
    w["agen"].summary += "\n\n" + paragraphs(
        "An unremarkable town on the Way, home to a small Christian sect, "
        "the Valerenes, who say they descend from a Diedne magus who "
        "slipped away from the Order by giving up his magic and turning "
        "hermit some years before the Schism War. Devoted to St Valerie "
        "of Limoges, whom he was said to have known in life, he is "
        "remembered by his followers, who each midsummer light candles "
        "at Saint Caprasius and then walk to her bones at Limoges and at "
        "the Benedictine house of Chambon-sur-Voueize. They live apart "
        "in the Gascon wilds, at their founder's old covenant (Bachlach's "
        "Hermitage), looking for plain signs of the Divine in nature, and "
        "are eager for news of the unicorns of Bazas. They have shown "
        "powers of Intervention and Purity, Saint's Aid and Wilderness "
        "Sense; their rites are secret, and some say they act out "
        "Valerie's beheading. They help the larger Valerene cult of "
        "Limoges with great initiations, and both want the ring of "
        "Valerie, called so at Richard I's investiture as prince of "
        "Aquitaine in 1172 and given back to the bishop of Limoges when "
        "Richard took the cross: her refused wedding ring.",
    )

    w["la_romieu"] = b.town(
        "La Romieu",
        charter="Noble lord",
        place=region,
        summary=paragraphs(
            "A small village about a mile from the ruins of Nemetannais, a "
            "Diedne covenant. The country round it teems with matagots "
            "(Magic Might 15, Animal): big dark calico cats flecked with "
            "gold, with tufted ears and cruel eyes. A matagot serves whoever "
            "first feeds it until that person dies or lets it go, conjures a "
            "hidden hoard of coins worth some twenty pounds and pays it out "
            "when its family pleases it, and racks with pain anyone who will "
            "not release it. Three pawns of Animal vis lie in its tail.",
        ),
    )
    w["bayonne"] = b.town(
        "Bayonne",
        charter="Commune",
        place=region,
        summary=paragraphs(
            "A great shipbuilding and whaling port, rebuilt by Basques and "
            "Viking settlers in the mid-tenth century. King John's charter of "
            "1215 gave it a mayor, jurors, councillors and advisers and freed "
            "it from the count of Labourd. Its whalers are a skilled, "
            "well-ordered community of fine shipwrights and sailors who have "
            "hunted the sarda for nearly two hundred years. About nine Gifted "
            "sorginak live in and around it; Cenodoxus and Julian prey on its "
            "crowds. The ruins of Lapurdum, a Flambeau mithraeum abandoned to "
            "the Vikings, lie within the city.",
        ),
    )
    w["ostabat"] = b.town(
        "Ostabat",
        charter="Noble lord",
        place=region,
        summary=(
            "The Basque town where four routes of the Way meet before "
            "Roncevaux: two hotels, two hospitals and over two dozen hostels, "
            "with more than five thousand palmers a week passing toward the "
            "rough stone tunnel into Iberia, inside which an inn shelters "
            "travellers and their mounts from storm and snow. Drakes and "
            "worms are worst here."
        ),
    )
    w["pau"] = b.town(
        "Pau",
        charter="Noble lord",
        ruler="William of Béarn",
        answers_to=w["william_bearn"],
        place=region,
        summary=(
            "A town the count of Béarn founded in the eleventh century on the "
            "north bank of the Gave de Pau to guard its ford, which two large "
            "square towers overlook."
        ),
    )
    w["tarbes"] = b.town(
        "Tarbes",
        charter="Church",
        ruler="Guy de Montfort, in name",
        answers_to=w["guy_montfort"],
        place=region,
        summary=(
            "The capital of Bigorre, on the left bank of the Adour: six "
            "walled villages round the bishop's palace and cathedral. Its "
            "oldest ruins are Roman. With Guy de Montfort at war and no "
            "seneschal, the towns and the bishop keep order."
        ),
    )
    w["lourdes"] = b.town(
        "Lourdes",
        charter="Noble lord",
        place=region,
        summary=(
            "A walled town on the Gave de Pau among caves and quarries, with "
            "the old seat of the counts of Bigorre, on Roman footings, on a "
            "rock east of it: a great square tower the crusaders think more "
            "vital than Tarbes, since it commands the salt mines of the "
            "valleys. Nearby Bagnères-de-Bigorre has Roman baths."
        ),
    )
    w["mimizan_village"] = b.town(
        "Mimizan",
        charter="Noble lord",
        place=region,
        summary=(
            "A coastal village by a lake in the Landes. Its folk fear the "
            "marsh on the lake's north side and the trail into it, and tell "
            "ghost stories about what lives there: Dama's tower."
        ),
    )


# -------------------------------------------------------------- factions


def _factions(provence: Provence, b: Builder) -> None:
    w = provence.world
    region = provence.places["gascony"]
    w["court_of_rosefleur"] = b.faction(
        "The Court of Rosefleur",
        faction="Faerie court",
        decides="Its leader",
        ruler="Oriande la Fée",
        realm="Faerie",
        place=provence.places["rosefleur"],
        summary=(
            "Oriande la Fée's court and the Dames Blanches who own her as "
            "queen, from the Gironde to the Pyrenees and east to the "
            "Camargue: courtly fae, nymphs, sirens, trolls and fauns who live "
            "in the Médoc's dolmens and torment pilgrims on the Way."
        ),
        wants="Stories: knights and pilgrims forced into quests, ransoms and errands",
        offers="Shelter for refugees, vassals and allies, as Maugris and Dama had; Oriande's glass dagger to a favoured knight",
    )
    b.link(
        w["court_of_rosefleur"],
        "characters",
        provence.magi["dama"],
        "Spent long years at the court; once sworn to Oriande",
    )
    w["bayonne_whalers"] = b.faction(
        "The Whalers of Bayonne",
        faction="Gild",
        decides="A council",
        place=region,
        summary=(
            "The Basque whalers of Bayonne and its coast, who keep watch from "
            "the vigias and hunt the sarda in fleets of small boats with "
            "harpoons and spears, second to none at their craft."
        ),
        wants="Whales, and safe return",
        offers="Whale meat and goods; the bones and baleen of Whales of Virtue hold Animal and Aquam vis",
    )
    w["templars"] = b.faction(
        "The Knights Templar in Provence",
        faction="Military order",
        decides="Its leader",
        ruler="Grand Master Peter de Montaigu",
        members=100,
        place=region,
        summary=paragraphs(
            "The largest knightly order, exempt by papal bull from local law "
            "and taxes. Its commanderies, each with a commander's house, "
            "quarters, pilgrim lodging, farm, mill, chapel and graveyard "
            "inside a wall, raise men and money for the Holy Land; six to "
            "fifty brother knights, as many sergeants and a chaplain hold "
            "each, under a commander elected by the brothers. The Tribunal "
            "has a hundred: 27 in the Arelat, 20 in Gascony, 14 in the "
            "Narbonnais and 29 in the Toulousain, with ten of Auvergne's "
            "seventeen inside its bounds, and none in Andorra or the "
            "Pyrenees. Those of Gascony and the Toulousain guard the Way and "
            "support the Fifth Crusade and the Reconquista. Montsaunès, fifty "
            "miles south-west of Toulouse, oversees St Marcet, Boudrac and "
            "smaller houses and holdings across the district.",
            "Grand Master Peter de Montaigu of Auvergne, whose brother Guerrin "
            "leads the Hospitallers, holds that the only true crusade is "
            "against the Saracens, and the Templars would not join the war "
            "on the Cathars; Grand Master Bertrand de Blanchefort had Cathar "
            "blood, and his kin in the Razès fought for the Cathars. Houses "
            "close to Cathar communities have hidden perfecti for short "
            "spells. Of the Tribunal's three masters, Giraud Brochard is "
            "master of Aquitaine and Guillaume d'Ailly master of Spain and "
            "Provence; the third, over Provence's province and bailiwick, died in "
            "1219, and the post stays empty until 1229 if the saga follows "
            "history.",
        ),
    )
    w["hospitallers"] = b.faction(
        "The Knights Hospitaller in Provence",
        faction="Military order",
        decides="Its leader",
        ruler="Grand Master Guerrin de Montaigu",
        members=81,
        place=region,
        summary=(
            "The Order of St John of Jerusalem, strong in Provence, which "
            "supports pilgrims on the Way and raises revenue for the Levant. "
            "Its chief preceptory at Saint-Gilles near Nîmes runs 53 of its "
            "81 holdings across the Arelat, Gascony, the Narbonnais and the "
            "Toulousain; the preceptory of Toulouse runs the other 28. It "
            "keeps a hospice at Soulac."
        ),
    )
    w["order_of_santiago"] = b.faction(
        "The Order of Santiago",
        faction="Military order",
        decides="Its leader",
        ruler="Grand Master Martín Peláez Barragán, in Castile",
        place=region,
        summary=(
            "The Knights of St James of the Sword, an Iberian order with only "
            "a few houses in Provence, all on the Way and mostly in Gascony, "
            "there only to guard and help pilgrims. The chief one is the "
            "Bessaut Commandery."
        ),
    )


# --------------------------------------------------------- printed stats


DAMA: StatBlock = {
    "characteristics": {
        "intelligence": 3,
        "perception": 0,
        "presence": 2,
        "communication": 1,
        "strength": -2,
        "stamina": 1,
        "dexterity": -2,
        "quickness": -1,
    },
    "aging_points": {"strength": 1},
    "size": 0,
    "confidence": (1, 5),
    "decrepitude": (1, 8),
    "warping": (8, 9),
    "apparent_age": 60,
    "virtues_flaws": [
        "The Gift",
        "Charm Magic",
        "Chthonic Magic",
        "Feminine Ceremony",
        "The Feminine Gift",
        ("Major Magical Focus", {"focus": "controlling human beings"}),
        "Story Magic",
        ("Affinity with {art}", {"art": "rego"}),
        "Arcane Lore",
        "Dark Magic",
        "Faerie Magic",
        "Skilled Parens",
        "Venus' Blessing",
        "Driven (Major)",
        "Evil Destiny",
        "Favors",
        "Proud (Major)",
        "Twilight Prone",
        "Fear",
        "Weakness (Minor)",
    ],
    "traits": {"Driven": 4, "Proud": 3, "Optimistic": 2},
    "reputations": {
        "Ambitious (Hermetic)": 3,
        "Ancient (Hermetic)": 3,
        "Pagan (Hermetic)": 2,
        "Reclusive (Hermetic)": 2,
        "Secretive (Hermetic)": 2,
        "Possible Diedne Maga or Sympathizer (Hermetic)": 1,
    },
    "abilities": [
        ("Area Lore: Provence", 4, "vis sites"),
        ("Area Lore: Pyrenees", 3, "vis sites"),
        ("Artes Liberales", 3, "astronomy"),
        ("Athletics", 1, "hiking"),
        ("Awareness", 3, "observation"),
        ("Bargain", 3, "faeries"),
        ("Brawl", 2, "dodge"),
        ("Carouse", 1, "recovery"),
        ("Charm", 4, "women"),
        ("Code of Hermes", 4, "Tribunal procedure"),
        ("Concentration", 6, "comprehending Twilight"),
        ("Craft: Weaving", 2, "wool"),
        ("Chthonic Magic", 5, "using Infernal vis"),
        ("Dead Language: Latin", 5, "Hermetic terms"),
        ("Divine Lore", 1, "female beings"),
        ("Etiquette", 3, "faeries"),
        ("Faerie Lore", 4, "female beings"),
        ("Faerie Magic", 7, "experimentation"),
        ("Feminine Ceremony", 4, "group casting"),
        ("Finesse", 5, "Rego"),
        ("Folk Ken", 3, "women"),
        ("Guile", 3, "women"),
        ("Infernal Lore", 3, "female beings"),
        ("Intrigue", 4, "long-term plans"),
        ("Leadership", 4, "inspiration"),
        ("Living Language: Basque", 4, "conversation"),
        ("Living Language: Danish", 5, "descriptions"),
        ("Living Language: French", 4, "conversation"),
        ("Living Language: Greek", 4, "conversation"),
        ("Living Language: Occitan", 4, "conversation"),
        ("Magic Lore", 3, "female beings"),
        ("Magic Theory", 10, "experimentation"),
        ("Organization Lore: Folk Witches", 3, "Basque covens"),
        ("Organization Lore: Matres and Matrones", 8, "initiations"),
        ("Organization Lore: Merinita Cult", 5, "initiations"),
        ("Organization Lore: Order of Hermes", 4, "Tribunal members"),
        ("Parma Magica", 7, "Mentem"),
        ("Penetration", 3, "Vim"),
        ("Philosophiae", 2, "ceremonial magic"),
        ("Stealth", 1, "remaining hidden"),
        ("Survival", 1, "Gascony"),
        ("Swim", 1, "rivers"),
        ("Teaching", 3, "single student"),
    ],
    "arts": {
        "Creo": 21,
        "Intellego": 14,
        "Muto": 14,
        "Perdo": 16,
        "Rego": 20,
        "Animal": 13,
        "Aquam": 15,
        "Auram": 13,
        "Corpus": 20,
        "Herbam": 15,
        "Ignem": 12,
        "Imaginem": 13,
        "Mentem": 17,
        "Terram": 11,
        "Vim": 17,
    },
    "spells": [
        ("Mighty Torrent of Water", "CrAq", 20, 0),
        ("Circling Winds of Protection", "CrAu", 20, 0),
        ("The Incantation of Lightning", "CrAu", 35, 0),
        ("True Sight of the Air", "InAu", 15, 0),
        ("Purification of the Festering Wounds", "CrCo", 20, 0),
        ("Restoration of the Defiled Body", "CrCo", 25, 0),
        ("Cheating the Reaper", "CrCo", 30, 0),
        ("Curse of the Unruly Tongue", "ReCo", 5, 0),
        ("Lifting the Dangling Puppet", "ReCo", 15, 0),
        ("Seven-League Stride", "ReCo", 30, 0),
        ("The Leap of Homecoming", "ReCo", 35, 0),
        ("Trap of the Entwining Vines", "CrHe", 15, 0),
        ("Repel the Wooden Shafts", "ReHe", 10, 0),
        ("Pilum of Fire", "CrIg", 20, 0),
        ("Ward Against Heat and Flames", "ReIg", 25, 0),
        ("Veil of Invisibility", "PeIm", 20, 0),
        ("Image from the Wizard Torn", "ReIm", 30, 0),
        ("Wizard's Sidestep", "ReIm", 10, 0),
        ("Weight of a Thousand Hells", "CrMe", 25, 0),
        ("Frosty Breath of the Spoken Lie", "InMe", 20, 0),
        ("Coerce the Spirits of the Night", "ReMe", 25, 0),
        ("Veil of Haunting Terror", "ReMe", 35, 0),
        ("Wall of Protecting Stone", "CrTe", 25, 0),
        ("The Earth Split Asunder", "ReTe", 30, 0),
        ("Piercing the Faerie Veil", "InVi", 20, 0),
        ("Enigma's Caress", "CrVi", 20, 0),
        ("Sight of the Active Magics", "InVi", 40, 0),
        ("Demon's Eternal Oblivion", "PeVi", 15, 1),
        ("Faerie Scourged from Memory", "PeVi", 15, 1),
        ("Revoke the Protection of Bonisagus", "PeVi", 20, 1),
        ("Gather the Essence of the Beast", "ReVi", 15, 0),
        ("Circular Ward Against Faeries", "ReVi", 20, 0),
        ("Aegis of the Hearth", "ReVi", 35, 1),
        ("Faerie Chains of the Familiar Slave", "ReVi", 45, 0),
    ],
    "masteries": {
        "Demon's Eternal Oblivion": ["Multiple Casting"],
        "Faerie Scourged from Memory": ["Multiple Casting"],
        "Revoke the Protection of Bonisagus": ["Magic Resistance"],
        "Aegis of the Hearth": ["Magic Resistance"],
    },
    "notes": paragraphs(
        "Stat block printed in Faith & Flame (as 'The Guide'). Its age line "
        "reads 193 (apparent 60), which leaves out her 34 years in Twilight; "
        "she was born in 993. Longevity Ritual modifier 23 (ritual 15, "
        "baetylus 5, living conditions 3); her ritual is failing and must be "
        "renewed before 1232. Strength has 1 aging point; Stamina and "
        "Quickness have each lost a point to Decrepitude. Soak +5.",
        "Virtues and Flaws the catalog lacks, left off the sheet: the "
        "Mystery Virtue Sympathetic Magic and the Flaw Oath (protect "
        "women). The Feminine Gift, Venus' Blessing and Dark Magic are "
        "Twilight Virtues. Her Driven is to leave a legacy, her Favors are "
        "owed to Oriande la Fée, her Fear is of spiders and her Weakness is "
        "for women in need. Story Magic, Charm Magic, Sympathetic Magic, her "
        "Major Magical Focus (in controlling people), Driven, Favors, Fear "
        "and Oath came by Mystery Initiation and Ordeal; Faerie Magic is "
        "her House Virtue. The book calls Chthonic Magic 'Cthonic Magic'.",
        "Twilight Scars: three comprehended Twilights before 1061 gave her "
        "the Feminine Gift, Venus' Blessing and Dark Magic; her nineteen-year "
        "Twilight erased most of her memories before 1001; two later ones, "
        "of six and nine years, left her like the popular image of the "
        "Virgin, faintly glowing, with auburn hair and ruddy skin.",
        "Spells: she also knows Demon's Eternal Oblivion at level 10. "
        "Enigma's Caress is Enigma's Gift but inflicts two Warping Points. "
        "Faerie Scourged from Memory is Demon's Eternal Oblivion against "
        "Faerie beings. Veil of Haunting Terror is laid along Mimizan's game "
        "trail. Faerie Chains of the Familiar Slave (the book calls it "
        "Familiar Chains of the Faerie Slave) is her House's spell, by "
        "which she bound Maju.",
        "Familiar: Maju, a faerie of the lake at Mimizan (see the Secrets in "
        "her summary). Vis: 15 pawns of Faerie Vim in three gold rings, and "
        "25 more within a week through her cult. Equipment: courtier's "
        "finery, dagger, four gold rings, the baetylus on a pendant chain, "
        "good boots, a walking stick used as a club. Casting sigil: a faint "
        "scent of lilies. Voting sigil: an ivory dragon's head gilded in red "
        "gold.",
        "Her xp, as the book designed her: 5615, of which 1960 in Arts and "
        "795 in spells; seasons went to a talisman she later sacrificed, "
        "three Longevity Rituals, one for Alazais's companion, Mimizan, her "
        "apprentice and her Initiation scripts.",
    ),
}

REBECCA: StatBlock = {
    "characteristics": {
        "intelligence": 1,
        "perception": 0,
        "presence": 2,
        "communication": 1,
        "strength": -2,
        "stamina": 3,
        "dexterity": 1,
        "quickness": 1,
    },
    "size": -1,
    "confidence": (1, 3),
    "decrepitude": (0, 0),
    "warping": (1, 7),
    "apparent_age": 32,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Wealthy",
        "The Feminine Gift",
        "Good Teacher",
        "Improved Characteristics",
        "Personal Vis Source",
        "Privileged Upbringing",
        "Venus' Blessing",
        "Proud (Major)",
        "Waster of Vis",
        "Cabal Legacy",
        "Close Family Ties",
        ("Flawed Parma Magica", {"form": "animal"}),
        "Optimistic (Minor)",
        "Small Frame",
        "Susceptibility to Divine Power",
    ],
    "traits": {"Optimistic": 2},
    "reputations": {"Pragmatic": 3, "Well-informed": 2},
    "abilities": [
        ("Animal Handling", 2, "birds"),
        ("Area Lore: Gascony", 3, "vis sites"),
        ("Artes Liberales", 1, "astronomy"),
        ("Athletics", 1, "hiking"),
        ("Awareness", 2, "observation"),
        ("Brawl", 1, "dodge"),
        ("Carouse", 1, "staying sober"),
        ("Charm", 2, "men"),
        ("Concentration", 2, "flight"),
        ("Craft: Weaving", 2, "wool"),
        ("Cursing", 3, "men"),
        ("Dead Language: Latin", 4, "Hermetic terms"),
        ("Dowsing", 3, "in bog"),
        ("Flight", 3, "at night"),
        ("Folk Ken", 2, "men"),
        ("Folk Witch Magic Theory", 3, "vis extraction"),
        ("Guile", 2, "men"),
        ("Healing", 3, "sword wounds"),
        ("Living Language: Euskara", 5, "description"),
        ("Living Language: Occitan", 4, "conversation"),
        ("Organization Lore: Order of Hermes", 1, "Tribunal members"),
        ("Organization Lore: Folk Witches", 3, "sorginak covens"),
        ("Organization Lore: Matres and Matrones", 3, "Initiations"),
        ("Parma Magica", 3, "Mentem"),
        ("Penetration", 3, "Cursing"),
        ("Second Sight", 1, "seeing invisible creatures"),
        ("Shapeshifter", 5, "birds"),
        ("Stealth", 2, "remaining hidden"),
        ("Survival", 2, "Gascony"),
        ("Teaching", 1, "folk witches"),
    ],
    "arts": {},
    "spells": [],
    "notes": paragraphs(
        "Stat block printed in Faith & Flame, built with the folk witch rules "
        "of Hedge Magic as an Ex Miscellanea sorgina. Age 32 (apparent 32). "
        "Soak +2.",
        "Virtues and Flaws the catalog lacks, left off the sheet: "
        "Well-Trained Folk Witch and the Flaw Flawed Folk "
        "Witch Gift Opening (Animal Ken). The Feminine Gift, Good Teacher "
        "and Venus' Blessing came by Mystery Initiation through her Cabal "
        "Legacy; her Proud Flaw by the cult's Initiations. Her Flawed Parma "
        "Magica is against Animal. Her folk witch Abilities (Cursing, "
        "Dowsing, Flight, Healing, Shapeshifting, Folk Witch Magic Theory) "
        "are entered by the book's names; the book calls Shapeshifter "
        "'Shapeshifting'. Sorginak powers are not modelled.",
        "Witch Moon Scar: 5 xp in Cursing. Vis: 15 pawns of Corpus in a "
        "string of animal skulls, and her personal source of 5 Corpus a "
        "year from afterbirth rendered each spring equinox at a hillside "
        "shrine. Equipment: bear, hare, raven, stag and wolf fetishes, "
        "clothing, a dagger, pots and gear for brewing potions. Voting "
        "sigil: the wolf fetish, won in a fight from a rival sorgina. She "
        "dresses as a Basque wise woman, in dark wool with a bright, wide "
        "sash, her hair under a shawl.",
    ),
}


# ------------------------------------------------------- generated stats


P = Profile
OCCITAN = "Occitan"


#: Each sketched magus's profile, by key in provence.magi.
PROFILES: dict[str, Profile] = {
    "garus": P(
        strong="int pre com",
        weak="dex qik",
        arts={"Cr": 6, "Ig": 6, "Re": 5, "Pe": 4, "Me": 4, "Vi": 4, "In": 3},
        abilities={
            "Intrigue": (4, "Tribunal politics"),
            "Leadership": (4, "milites"),
            "Etiquette": (3, "nobles"),
            "Organization Lore: House Flambeau": 3,
            "Area Lore: Provence": 2,
            "Single Weapon": 2,
        },
        virtues=[
            "Hermetic Prestige",
            vf_art("Affinity with {art}", "ignem"),
            vf_ability("Puissant {ability}", "intrigue"),
            "Enemies",
            "Dutybound",
        ],
        reputations={"Primus of House Flambeau (Hermetic)": 6},
        native="English",
    ),
    "marcus_minor": P(
        strong="pre com int",
        arts={"Cr": 5, "Ig": 6, "Re": 4, "Me": 5, "Vi": 4, "Co": 3},
        abilities={
            "Leadership": (4, "initiates"),
            "Charm": (3, "the faithful"),
            "Theology: Christian": 3,
            "Organization Lore: Legion of Mithras": 4,
            "Guile": 2,
        },
        virtues=[
            vf_ability("Puissant {ability}", "leadership"),
            vf_art("Affinity with {art}", "ignem"),
            "Pious (Minor)",
            "Dark Secret",
        ],
        reputations={"Mystagogue of the Legion of Mithras (Hermetic)": 3},
        native=OCCITAN,
    ),
    "troya": P(
        strong="pre sta dex",
        arts={"An": 7, "Mu": 6, "Co": 5, "Re": 4, "Cr": 3, "Ig": 3},
        abilities={
            "Ride": (4, "battle manoeuvres"),
            "Animal Handling": (4, "horses"),
            "Animal Ken": 2,
            "Single Weapon": 2,
        },
        virtues=[
            vf_focus("Minor Magical Focus", "horses"),
            vf_art("Affinity with {art}", "animal"),
            "Proud (Minor)",
            "Compassionate (Minor)",
        ],
        native=OCCITAN,
    ),
    "marie": P(
        strong="pre com int",
        arts={"Im": 6, "Me": 6, "Cr": 4, "Mu": 4, "Re": 4, "He": 3, "Vi": 3},
        abilities={
            "Charm": (3, "nobles"),
            "Etiquette": (3, "courts"),
            "Profession: Storyteller": (4, "romances"),
            "Faerie Lore": 3,
            "Intrigue": (3, "Tribunal border"),
            "Organization Lore: Matres and Matrones": 3,
            "Living Language: Occitan": 3,
        },
        virtues=[
            "Faerie Blood",
            "Faerie Magic",
            "Good Teacher",
            "Venus' Blessing",
            "Driven (Major)",
            "Lost Love",
            "Weakness (Minor)",
        ],
        reputations={"Marie of France (Hermetic)": 3},
        native="French",
    ),
    "beatrice": P(
        strong="int per com",
        arts={"In": 7, "Me": 6, "Re": 4, "Vi": 4, "Cr": 3, "Co": 3},
        abilities={
            "Code of Hermes": (5, "Peripheral Code"),
            "Intrigue": (2, "Tribunal politics"),
            "Folk Ken": (3, "magi"),
            "Organization Lore: Order of Hermes": 3,
            "Area Lore: Provence": 2,
        },
        virtues=[
            vf_art("Affinity with {art}", "intellego"),
            "Clear Thinker",
            "Dutybound",
            "Heir",
        ],
        age=45,
        native=OCCITAN,
    ),
    "tres": P(
        strong="int dex sta",
        weak="pre",
        arts={"Re": 6, "Te": 6, "Mu": 5, "Cr": 4, "Ig": 3, "He": 3, "Vi": 3},
        abilities={
            "Craft: Siege Engines": (4, "magical engines"),
            "Craft: Weaponsmith": (4, "enchanted weapons"),
            "Leadership": (3, "mercenaries"),
            "Survival": (2, "Gascony"),
            "Area Lore: Provence": 2,
        },
        virtues=[
            "Inventive Genius",
            vf_art("Affinity with {art}", "terram"),
            "Infamous",
            "Enemies",
        ],
        age=60,
        native=OCCITAN,
    ),
}


def stats(provence: Provence) -> None:
    """Dama's and Rebecca's printed stat blocks, then generated stats for
    the other magi of Gascony."""
    b = provence.b
    b.stats(provence.magi["dama"], DAMA)
    b.stats(provence.magi["rebecca"], REBECCA)
    for key, profile in PROFILES.items():
        apply(b, provence.magi[key], profile)
