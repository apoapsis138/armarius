"""Arelat, the Provençal Tribunal's eastern march, as of 1220: the Rhone
valley from Lyonnais to the sea and the coast of Provence to the
Maritime Alps; the Coenobium Rhodanien, its four chapters and its magi;
the secret Fraxinetum Redux on the Hyères islands; Aucassin of Tytalus
under Beaucaire; the region's auras, regiones, unclaimed vis and
creatures; and the King of Arles, the Count of Provence, the Baux, the
river communes and the Church, in paraphrase of Faith & Flame chapter
eight (with chapter three for votes and politics).

The ruined covenants of Arelat (Barbegal, Castra Peccaius, the Birds of
Camargue, Elisii Campi, Fraxinetum, Telo Martius, Turris Mascis, Portus
Cottiae, Portus Termini, Yf) are tribunal.py's; the places they lie in
are here for it to put them in; Glanum, where the 1221 Tribunal meets,
is tribunal.py's places["ruin_glanum"]. Creatures (the drac, the Tarasque's kin, the ogre
of Pont Flavian, the golden goat, Ventoux and the Mistrau) are described
in the summaries of the places they haunt, since there is no bestiary
yet. Keys: the region is places["arelat"]; the Coenobium's chapters are
places["coenobium_avignon"], ["coenobium_arles"], ["coenobium_factory"]
and ["coenobium_toulon"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...arms import Arms
from ..builder import Builder, joined_lines, paragraphs, titled, vf_art
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from . import Provence

BJORNAER = "house_bjornaer"
BONISAGUS = "house_bonisagus"
EX_MISC = "house_ex_miscellanea"
GUERNICUS = "house_guernicus"
JERBITON = "house_jerbiton"
MERCERE = "house_mercere"
TYTALUS = "house_tytalus"

#: The lead line of a covenant's notes, before its secrets.
KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}


def _add(provence: Provence, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = provence.b.place(name, **kw)
    provence.places[key] = place
    return place


def build(provence: Provence) -> None:
    b = provence.b
    tribunal = provence.tribunal
    assert tribunal is not None
    _region(provence)
    _rhone(provence)
    _arles_country(provence)
    _east(provence)
    _north(provence)
    _coenobium(provence, b, tribunal)
    _fraxinetum_redux(provence, b, tribunal)
    _loose_magi(provence, b)
    _lords(provence, b)
    _churches(provence, b)
    _towns(provence, b)
    _factions(provence, b)


# ------------------------------------------------------------- the region


def _region(provence: Provence) -> None:
    _add(
        provence,
        "arelat",
        "Arelat",
        summary=paragraphs(
            "The Tribunal's eastern march: the lands of the old Kingdom "
            "of Lower Burgundy, bounded on the west by the Rhone (save "
            "the little County of Viviers, Beaucaire and the Lyonnais, "
            "which lie across it) and running east along the "
            "Mediterranean shore to the Maritime Alps a little past "
            "Nice. Its north-eastern edge is vague, somewhere beyond the "
            "Grande Chartreuse where the Viennois meets Savoy and the "
            "Greater Alps; by custom the Tropaeum Alpium marks its "
            "eastern limit. Rome settled here before anywhere else "
            "outside Italy, and the churches and towns of the Middle "
            "Ages stand on a carpet of Roman and Gallic ruins. Franks, "
            "Lombards and Saracens came in turn until Charles Martel "
            "conquered it; in 1220 it is calmer, and a heartland of the "
            "troubadours.",
            "The country is hot and poor, scoured by the Mistral, and "
            "known for wine, honey, limes and olives. Frederick II, the "
            "Emperor, is nominally King of Arles but acts only through "
            "his viceroy at Arles; the strongest magnate is the Catalan "
            "Ramon Berenguer V, Count of Provence and now of Forcalquier, "
            "back from captivity in Aragon since 1219; and the young "
            "Count of Toulouse still claims the March of Provence, which "
            "its lords honour when it suits them. Much of the land "
            "answers to petty lords or to chartered towns, above all "
            "Arles and Avignon, the great communes of the river. The Albigensian "
            "Crusade has not ravaged it, though some communes, and "
            "perhaps some magi, have quietly helped both sides.",
            "This was once part of the Lotharingian Tribunal; when the "
            "Grand Tribunal of 898 sent its northern covenants to "
            "Normandy and the Rhine, the remnant along the Rhone and in "
            "the Toulousain became the Provençal Tribunal. Proud heirs of "
            "the Roman Provincia, its first covenants kept their Latin "
            "names for every official document, a custom still followed. "
            "Its early magi left many ruins, monuments to how hard "
            "Hermetic cooperation can be, until the heirs of the fallen "
            "covenants pooled their holdings in the Coenobium, which now "
            "has a grip on nearly every easily reached magical resource "
            "in the region and dominates its hedge wizards. Its magi care "
            "little for the Rhine's Lotharingian Movement.",
            "Unclaimed or contested vis in Arelat (each described in its "
            "place): the yew of the Isle d'Yf (Intellego, with the ruin of Yf), the monthly "
            "almond blossom of Ste Marguerite at Lérins (Mentem, "
            "Divine-tainted), the blood-red ford of St Gilles (Corpus, "
            "Infernal-tainted), the golden goat's wool in the Alpilles "
            "(Imaginem), the field of the Golden Court of 1174 (Faerie "
            "vis, suspected), the Source du Groseau below Ventoux "
            "(Aquam), and the ruined mills of Barbegal north of Arles, "
            "with a Magic aura of 5 and three magical wheels still lost.",
        ),
        secrets=[
            titled(
                "Fraxinetum Redux",
                "Fraxinetum Redux, heirs of the raider covenant the Coenobium "
                "destroyed, keep a hidden base on the Hyères islands.",
            ),
            titled(
                "The eremite under Beaucaire",
                "A Tytalus eremite, Aucassin, lives in a regio under Beaucaire.",
            ),
            titled(
                "Tytali against the Coenobium",
                "Individual Tytali may have reason to work their way into the "
                "Coenobium and undermine it, which could set off a conflict "
                "across the Order.",
            ),
        ],
        **KNOWN_ORDER,
    )


# ------------------------------------------------------- the Rhone valley


def _rhone(provence: Provence) -> None:
    region = provence.places["arelat"]
    _add(
        provence,
        "rhone",
        "The Rhone",
        inside=region,
        summary=paragraphs(
            "'The Bruiser' to its boatmen: a river of fierce currents, "
            "shoals and spring floods, navigable by barge up to about "
            "Macon. Joined by the Saone at Lyon, it runs down the great "
            "trench between the Massif Central and the Alpine foothills "
            "and is the south-western frontier of the Empire. Only four "
            "bridges cross it: Lyon's ancient bridge on oak piles, "
            "Vienne's Roman one of stone, Avignon's newer Pont "
            "St Bénezet, and a lesser wooden bridge at Arles "
            "to Trinquetaille. Going down from Macon to Arles takes about "
            "three weeks, and the trip back a week or two longer, the "
            "barges hauled by horse teams or helped by magic; at Arles "
            "cargoes go onto small sailing barges for the sea.",
            "Barge trains of five to seven craft, towed by fifty or more "
            "horses along the banks, carry the bulk goods; nobles ride "
            "the water coaches, under sail or drawn by horses, which "
            "Jerbiton magi prefer to magic. Boats bear crosses and holy "
            "signs against harm, and many magi hide small wards in the "
            "designs.",
            "Lesser drac haunt the darker reaches of its tributaries: "
            "young Faerie drakes (Faerie Might 15, rising by 10 at their "
            "place of power), greenish-black, long-bodied, with webbed "
            "legs like a flamingo's and lacy blue fins for wings. They "
            "lure washerwomen, children and vagrants to watery lairs "
            "with illusions, can take human size, and let anyone they "
            "grapple breathe underwater; they feed on the fear their "
            "stories spread, and some live among people disguised as "
            "boatmen, laundresses or merchants. Each carries 3 pawns of "
            "Imaginem vis in its eyes. A human can hold a drac's jaws "
            "shut, since the muscles that open them are weak.",
            "Gervase of Tilbury's Otia imperialia, an encyclopedia of "
            "myth and marvels written at Arles between 1210 and 1214, "
            "tells of the drac's recent return and names two ways into "
            "its lair, a pool outside the north gate of Arles and a well "
            "at Beaucaire; it serves as four tractatus of Quality 6 "
            "(Provençal Lore, Faerie Lore, Infernal Lore and Magic Lore). "
            "The Redcaps think a further entrance lies in some Magic "
            "aura on a lonelier stretch of the river, and that all of "
            "them open on a great web of regiones under the valley, "
            "which might serve as a magical road; those who walk it hear "
            "inhuman breathing and feel hunted.",
        ),
        secrets=[
            titled(
                "The Coenobium's barge",
                "The Coenobium keeps at least one barge as a floating "
                "laboratory, moored along the banks or tributaries of the Rhone "
                "wherever a good Magic aura lies.",
            ),
        ],
        **KNOWN_TRIBUNAL,
    )
    _add(
        provence,
        "pont_saint_benezet",
        "Pont Saint-Bénezet",
        inside=region,
        realm="Divine",
        aura=4,
        summary=paragraphs(
            "Avignon's bridge: twenty-two stone arches across the low Isle "
            "de Barthelasse in midstream, unpaved but sound, with a "
            "drawbridge at the eastern end to keep the Porte du Rhone shut "
            "and a great gatehouse still unfinished. Over the third pier "
            "from the east bank is a small chapel of St Nicholas of Myra "
            "holding St Bénezet's body and relics, beloved of the Rhone "
            "boatmen; its Divine aura of 4 covers only the first few piers. "
            "Its doorkeeper, Jorin, a former boatman and retired Redcap, "
            "reports to the Coenobium.",
            "Under the first arch, the only one on the eastern shore, is a "
            "piece of Roman temple said to have been set there by the saint: "
            "a small Magic lacuna of 4, smothered by the chapel's aura by "
            "day but felt at night. Past the chapel the bridge is beyond the "
            "Divine aura of 3 thrown by the city and the abbey across the "
            "river, and the bound spirits of the Rhone flowing under its "
            "arches raise a weak Magic aura of 2 there.",
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "drac_well",
        "The Drac's Well at Beaucaire",
        inside=region,
        summary=paragraphs(
            "A disused well in Beaucaire's old marketplace, with a weak "
            "Magic aura (the book gives no strength). Local legend tells "
            "of the Drac, a cruel sorcerer-dragon of the river older than "
            "the Order, who drew mothers and little children to his lair "
            "beneath the water, walked unseen among the townsfolk, and "
            "is blamed for some three thousand dead knights and "
            "villagers. No tale says he was slain, so he was thought to "
            "have died of age, until a run of disappearances about ten "
            "years ago; none have been reported for some years, and "
            "folk are forgetting, but the well is still said to reach "
            "his lair.",
            "Nicolette, a young woman of the town, tells anyone who will "
            "listen her dreams of dragons and drowned kingdoms. Old folk "
            "say she once vanished for seven years and came back "
            "remembering nothing, not even the baby son she left; her "
            "husband and grown boy turn the talk when strangers press.",
        ),
        secrets=[
            titled(
                "The regio beneath the well",
                "Beneath the Drac's Well opens the underwater regio web that "
                "runs under the Rhone and the Drac river, with a powerful Magic "
                "aura.",
            ),
            titled(
                "Aucassin's sanctum",
                "Aucassin of Tytalus has his sanctum in the regio beneath the "
                "Drac's Well and revived the Drac legend to cover his "
                "kidnappings.",
            ),
            titled(
                "The cave paintings",
                "Cave paintings within the regio beneath the Drac's Well, with "
                "the regio itself, make up a Mystery Initiation Script to mature "
                "a human heir of the Drac into a true elder drac.",
            ),
            titled(
                "The deeper level",
                "A deeper level of the regio beneath the Drac's Well, aligned to "
                "Imaginem, opens on the Magic Realm, where a sleeping dragon "
                "Vestige like a giant drac guards the far side. Aucassin has "
                "taken some odd vis from beyond it but dares not face the "
                "Vestige yet.",
            ),
            titled(
                "Aucassin's captives",
                "Living under compulsion in the caves are Aucassin's "
                "abducted servants, among them a lavender-seller as wet "
                "nurse and a young scribe once used by Alazais, made to "
                "teach his sickly Gifted captive, 'Le Petit', Latin and the "
                "liberal arts.",
            ),
            titled(
                "Who Nicolette is",
                "Nicolette may be a former drac bride freed to spread tales, or "
                "one of Aucassin's escaped grogs.",
            ),
        ],
        **RUMOURED,
    )
    _add(
        provence,
        "golden_court",
        "The Field of the Golden Court",
        inside=region,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "Meadows just north of Beaucaire where Henry II, then Count of "
            "Provence, held a court in 1174 to mark Narbonne's "
            "reconciliation with the King of Aragon, and where (by Abbot "
            "Geoffrey of Vigeois's flattering chronicle) a hundred thousand "
            "knights gathered. Most were faeries reveling in the foudat, the "
            "deliberate folly that troubadour culture breeds: thirty "
            "thousand gold sous of glamour were ploughed into the ground, "
            "and herds of faerie cattle roasted over costly wax and "
            "pitch-pine torches. The faeries crowned Guilhem Mita 'King of "
            "the Minstrels' with a gold crown sent by Sorgest, the "
            "faerie-blooded Countess of Urgell.",
            "Each anniversary, faeries in the likeness of the troubadours "
            "and nobles of that day replay the feast and try to pull "
            "mortals into new versions of it. The Faerie aura of 3 rises to "
            "5 on the anniversary. Minor demons of envy, greed and lust, "
            "shed from the crusading army's wake, have lately settled round "
            "about. The Coenobium suspects the field could yield plentiful, "
            "renewable Faerie-tainted vis, and may send would-be members to "
            "look into it.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "tarasque_lair",
        "The Tarasque's Lair",
        inside=region,
        aura=2,
        summary=paragraphs(
            "A cave in the hills outside Tarascon where the Tarasque laired: "
            "a six-legged amphibious beast that St Martha tamed and the "
            "villagers of Nerluc then slew in cowardly fashion in AD 48. Its "
            "remains are long scattered, but the cave runs down into "
            "flooded passages that may join others in the region. The "
            "residual Magic aura is 2, with stronger regiones believed to "
            "lie deeper.",
            "Lesser kin of the beast may lurk there. A small tarasque "
            "(Magic Might 20) is a winged, scaly ox with a lizard-like lion's "
            "head, six taloned legs, a tortoise's shell and a leathery tail, "
            "about fifteen paces long, smoke curling from its jaws: it flies "
            "though its wings should not carry it, breathes a long gout of "
            "fire, cannot be harmed by fire or want, and is cowed by sincere "
            "holy display, as hymns once mesmerised its ancestor. Its shell "
            "holds 4 pawns of Animal vis.",
            "Just north of the town, by a small island, Hannibal fought the "
            "Volcae at the Rhone crossing; on clear moonlit nights boatmen "
            "see giant elephant skeletons on the riverbed and huge ghostly "
            "beasts marching under the current.",
        ),
        **KNOWN_LOCALLY,
    )


# --------------------------------------------- Arles, the Crau and Camargue


def _arles_country(provence: Provence) -> None:
    region = provence.places["arelat"]
    _add(
        provence,
        "alyscamps",
        "The Alyscamps",
        inside=region,
        summary=paragraphs(
            "The old Roman necropolis of Arles along the road east, famous "
            "for its crypts and tombs; coffins once floated down the Rhone "
            "from all over Europe, steered by boatmen who did not always "
            "deliver the valuables with them. Its glory faded when the "
            "relics of St Trophimus went to the cathedral in 1152, and "
            "townsfolk now take its stones for building while the council "
            "gives sarcophagi away to honoured visitors.",
            "The spirit masters of Elisii Campi lived in its crypts in the "
            "tenth century, hid through the Schism War, and were driven out "
            "when the Coenobium stirred up the townsfolk with rumours of "
            "diabolists under the necropolis. Many sarcophagi still hold "
            "their enchantments and traps; one that falls into a "
            "covenant's hands could lead to a hidden covenant in the Verdon "
            "Gorge, or to blood on the Coenobium's past.",
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "pont_flavian",
        "Pont Flavian",
        inside=region,
        summary=paragraphs(
            "A single-arched Roman bridge between two triumphal arches, "
            "carrying the Via Julia Augusta over the Touloubre near "
            "St Chamas. It has stood over a thousand years partly thanks to "
            "the faerie ogre living under it (Faerie Might 20, 30 at his "
            "best), who takes a toll of sheep and beer, or wine and a sheep "
            "a wagon, or a sack of coin, and eats those who sneak across or "
            "damage the bridge. He is a huge boar-headed brute with clawed "
            "hands and amber tusks, clubbing with a root-spiked tree stump, "
            "throwing stones he pulls from the earth, moving soundlessly, "
            "and able to seem a standing stone; heads hang at his belt, "
            "among them a skull in a net that holds 4 pawns of Corpus vis "
            "and makes its bearer Tough. He claims to be cousin to the Boar "
            "King of Normandy.",
            "He lately caught a lost Redcap, who promised a ransom from "
            "the magi; the ogre hid him in an oubliette only he can open "
            "and sent a shepherd boy for the wizards, eating a sheep for "
            "each day past the fourth. If the ogre dies first, the Redcap "
            "rots unfound.",
        ),
        **KNOWN_LOCALLY,
    )
    alpilles = _add(
        provence,
        "alpilles",
        "The Alpilles",
        inside=region,
        summary=paragraphs(
            "A range of limestone teeth at the northern edge of the Crau, so "
            "like the Alps in little that locals call them the Alps' "
            "children. Wild and untouched, they rise above St-Rémy and hold "
            "both Magic and Faerie auras with their creatures.",
            "Here roams le Chèvre d'Or, the Golden Goat, said to guard the "
            "treasure cave of the first Caliph of Cordoba, Abd al-Rahman "
            "III, whose daughter she is: a goat with a fiery golden coat and a gold coronet "
            "on ebony horns, who seems trapped and begs, in Arabic and then "
            "Occitan, to be freed, and if ignored becomes a beautiful "
            "Saracen princess promising her treasure. She is a powerful "
            "nymph (or, if the storyguide prefers, a Spirit of Deceit) who "
            "keeps the way into a treasure regio, perhaps at the foot of the "
            "Garagai, in the Val d'Enfer, or in any gully of the Provençal "
            "foothills; it lets people in but not out, and without Second "
            "Sight a lover may wander its layers for ever. The few youths "
            "who escape lose their wits or souls, or come back as "
            "impostors.",
            "Shepherds find strands of her golden wool on the bushes: "
            "accrued Imaginem vis, unclaimed, which an aesthete of the "
            "Coenobium might set a would-be member to gather.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "val_denfer",
        "The Val d'Enfer",
        inside=alpilles,
        realm="Infernal",
        aura=2,
        summary=paragraphs(
            "A rocky valley under the plateau of Les Baux, lined with "
            "sinister caves, under an Infernal aura of 2. The caves lead "
            "into a Tartaran regio where lesser demons of pride and "
            "ambition dwell, the ones that drove the lords of Baux into "
            "their wars over the centuries. The Golden Goat's treasure "
            "regio may open here.",
            "Carved into the rock below the valley is the Tremais, a rough "
            "sculpture of three figures most take for Lazarus, Mary "
            "Magdalene and Martha: a minor pilgrimage shrine with a Divine "
            "aura of 4, set inside a wider Faerie aura of 2, for the "
            "carving first honoured the Roman general Marius, his wife and "
            "his Syrian sibyl Martha before missionaries claimed it.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "camargue",
        "The Camargue",
        inside=region,
        summary=paragraphs(
            "The marshy triangle between the Rhone's two last branches, "
            "entered from Trinquetaille, Arles's unwalled suburb on the "
            "right bank, where the Coenobium's Factory stands. The Bjornaer "
            "of the Birds of Camargue lived here until they joined the "
            "Coenobium in 970.",
            "Two Bjornaer, nominally the Coenobium's guests, live on the "
            "edge of Trinquetaille and spend most of their time in the "
            "marsh: little Bubulcus, usually an egret, riding his bull, and "
            "Elornis One-Leg, a greater flamingo. Both know of the "
            "legendary horses of the Camargue and the Great Stallion who "
            "leads them, but have little to do with them.",
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "st_gilles_ford",
        "The Ford of St Gilles",
        inside=region,
        realm="Infernal",
        aura=3,
        summary=paragraphs(
            "A ford on the Rhone just outside St Gilles where the papal "
            "legate Peter of Castelnau was killed in 1208, by a demon or by "
            "one of Raimond VI's men. It is stained by an Infernal aura of "
            "3. On the anniversary the river runs red as blood, and small "
            "skull-shaped pebbles yield several pawns of Corpus vis, always "
            "Infernally tainted. Unclaimed.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "arch_of_orange",
        "The Arch of Orange",
        inside=region,
        aura=2,
        summary=paragraphs(
            "Tiberius's triumphal arch, now built into Orange's walls as "
            "its north gate astride the old Via Agrippa. A Magic aura of 2 "
            "flickers up at night when the Divine aura fades. Some magi "
            "think it may keep secrets of the Mercurians' old road magic, "
            "and Neo-Mercurians and members of the Cult of Mercury quietly "
            "study its inscriptions and stones. Nearby, the ruins of one of "
            "the finest Roman theatres outside Italy, shut by the "
            "Christians in 391, lie as the barbarians left them.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        provence,
        "crau",
        "The Plaine de la Crau",
        inside=region,
        summary=paragraphs(
            "A stony plain on the Via Domitia, of great interest to Ara "
            "Maxima Nova: legend says Heracles, driving Geryon's cattle "
            "home, was set on here by the giants Bergion and Ligur, sons of "
            "Poseidon, and when he prayed to Zeus the plain rained the "
            "rocks he hurled to beat them. Its round stones make good sling "
            "and catapult shot.",
            "Among them, now and then, is a perfectly round sling stone "
            "that is Terram vis. The Coenobium's grogs gather a handful "
            "each year with minor enchanted devices under apprentices' "
            "eyes, a tedious chore kept for troublemakers and idlers.",
        ),
        **KNOWN_REGION,
    )


# ------------------------------------------------------- eastern Provence


def _east(provence: Provence) -> None:
    region = provence.places["arelat"]
    _add(
        provence,
        "frioul",
        "The Frioul Islands",
        inside=region,
        summary=paragraphs(
            "Four small, uninhabited islands off Marseille. Smugglers, "
            "pirates and Saracen raiders from their nest in the Hyères "
            "moor at Pomègues and Ratonneau, the two largest; Tiboulen "
            "is the tiniest. The fourth, the Isle d'Yf, with its old yew "
            "grove and the ruins of the Diedne covenant of Yf, is "
            "described with that ruin.",
        ),
        secrets=[
            titled(
                "Vis on the islands",
                "The magi of Fraxinetum Redux harvest vis on the small islands "
                "of the coast, Yf among them.",
            ),
        ],
        **KNOWN_REGION,
    )
    _add(
        provence,
        "maures",
        "The Massif des Maures",
        inside=region,
        summary=paragraphs(
            "A granite upland between Hyères and Fréjus, strange among "
            "Provence's limestone hills and dark with forests, named for "
            "the Saracen privateers who held the coast and the Alpine "
            "passes from the eighth to the tenth century. Above St Tropez, "
            "almost unreachable among its crystalline peaks, lies La "
            "Garde-Freinet, the razed site of Fraxinetum amid cork, oak and "
            "chestnut woods, still with a Magic aura of 4 and the ruins of "
            "the covenant fort. A palisade of close-set ash trees planted "
            "by its Herbam masters rings the grounds, and the remnants of "
            "their defensive rituals make the bigger ashes beat back "
            "intruders, so peasants call the place haunted and leave it "
            "unlooted.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        provence,
        "hyeres",
        "The Hyères Islands",
        inside=region,
        summary=paragraphs(
            "The Stoechades of Pliny and the Greeks, opposite old Olbia, "
            "known for slopes covered in lavender. A monastery holds the "
            "big eastern island, the Ile du Levant, while pirates haunt "
            "the quiet coves of Port-Cros and Porquerolles; the Giens "
            "peninsula to the west is cut off except at the lowest tides, "
            "a fourth island most of the year. Charlemagne brought the "
            "lavender (stoechas) to the mainland, and it is now in every "
            "monastic physic garden and in the folk magic of the "
            "south-east (+3 to cleansing, purifying or healing, +5 "
            "against evil spirits).",
            "Lavender of Virtue holds a pawn of Rego vis a bunch. Dried "
            "in an open barn through the winter Mistral, tied in a posy "
            "and steeped a season in asp venom, it becomes an amulet "
            "that gives a wearer without Magic Resistance Greater "
            "Immunity to one major disease while its scent can be "
            "smelled; it lasts a year and warps its wearer as a constant "
            "low-power effect, and hung over a lintel it protects the "
            "sick recovering in the room beyond. Unclaimed.",
        ),
        secrets=[
            titled(
                "The heirs of Fraxinetum",
                "The heirs of Fraxinetum keep their base on the Hyères Islands, "
                "among the lavender of the pirate isles.",
            ),
            titled(
                "Who backs the raids",
                "The heirs of Fraxinetum sponsor raids on the coast and on "
                "Catalan and Genoese shipping.",
            ),
        ],
        **KNOWN_REGION,
    )
    ventoux = _add(
        provence,
        "ventoux",
        "Mount Ventoux",
        inside=region,
        aura=7,
        levels=[
            Builder.level(
                "The Home of the Winds",
                9,
                notes=(
                    "Above the gravelly summit, where the wind never stops: "
                    "the realm of many air spirits ruled by the great daimon "
                    "Ventoux, now sealed by the Mistrau with Calais of "
                    "Bonisagus inside."
                ),
            )
        ],
        summary=paragraphs(
            "'The Home of the Winds', the bald mountain at Provence's "
            "northern edge, long feared as the source of the Mistral. "
            "Chapels stand on its lower slopes, among them two chapels "
            "and a watchtower at Beaumont-du-Ventoux and the great "
            "monastery of Notre-Dame-du-Groseau. The upper slopes have "
            "a Magic aura of 7, rising to a regio of 9 near the summit, "
            "where the endless gale lets nothing grow. There dwell air "
            "spirits of many strengths under a great daimon called "
            "Ventoux, who now and then lets his lesser kin loose on the "
            "country below.",
            "Calais filius Septentrio of Bonisagus, a Rhine magus "
            "staying with the Coenobium who calls himself Master of the "
            "Winds, made a sanctum in a cave just below the summit to "
            "win the daimon over as its Spirit Votary. That angered the "
            "Mistrau ('the Master'), an ancient Faerie lord who embodies "
            "every Provençal tale of the mistral: he has sealed the "
            "spirits' regio, which has made this season unusually mild, "
            "and Calais is trapped inside fighting Ventoux's angry "
            "servants. His hosts expected him back last season. To get "
            "in, one must beat one of the Mistrau's champions at "
            "catching two fleeting things out of Arcadia: winter's dying "
            "breath and spring's first sigh.",
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "The storyguide may make the daimon or the Mistrau an Infernal "
                "spirit of the Order of Aerial Powers posing as Faerie, hoping "
                "by a pact to spread corruption through every elementalist "
                "tradition in the Order; the prayers of the monks of "
                "Notre-Dame-du-Groseau have partly held it in.",
            ),
        ],
        **KNOWN_REGION,
    )
    _add(
        provence,
        "source_du_groseau",
        "The Source du Groseau",
        inside=ventoux,
        summary=(
            "A magical spring gushing from a cliff north of Ventoux, sacred "
            "to the Celtic spring god Groselos, and a possible source of "
            "Aquam vis. Unclaimed."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "garagai",
        "The Garagai Gorge",
        inside=region,
        realm="Infernal",
        aura=2,
        summary=paragraphs(
            "A chasm near Montagne Sainte-Victoire, outside Aix. After "
            "Marius crushed the Teutones there in 102 BC, so many that the "
            "Campi Putridi were fattened for years, legend says three "
            "hundred captive chieftains were driven into the gorge at the "
            "urging of his Syrian sibyl Martha, and each anniversary their "
            "spirits rise from the floor to relive the defeat. The lip has "
            "an Infernal aura of 2, stronger lower down, where unexplored "
            "Tartaran regiones lead, some say, to a mouth of Hell at the "
            "very bottom. Some tales put the Golden Goat's treasure cave "
            "here.",
            "The ghosts are not Infernal but Magic, Teutonic kin of House "
            "Tremere's ghostly soldiers; questioned, they might reveal the "
            "lost tradition of Martha, who may have been of a lineage like "
            "the Canaanite necromancers. Even before the slaughter, "
            "prophetic spirits were said to rise from the depths, best "
            "treated as Spirits of Deceit, and local masques or "
            "necromantic magi may still call them.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "lerins",
        "The Sanctuary of Venus on Ste Marguerite",
        inside=region,
        aura=2,
        summary=paragraphs(
            "The Iles de Lérins have been a land of monks since "
            "St Honoratus drove off their venomous snakes in the fifth "
            "century; the snakes never returned, but the Saracens did, "
            "killing Abbot St Porcarius in the eighth. On the smaller "
            "island, under the sister convent of Ste Marguerite, a cave "
            "network hides a little sanctuary of Venus that the "
            "fourteenth abbot, St Nazarius, failed to destroy; it keeps a "
            "weak Magic aura of 2.",
            "Also on the island is an almond tree that flowers every month: "
            "its crushed blossoms give 1 pawn of Mentem vis a month, "
            "Divinely tainted. Unclaimed.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "tropaeum",
        "The Tropaeum Alpium",
        inside=region,
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "The Trophy of Augustus at La Turbie: a round arcaded monument "
            "to Rome's defeat of the Gaulish tribes, once the edge of Roman "
            "Italy on the Via Julia Augusta, later a fortress and refuge. By "
            "tradition it marks the Tribunal's easternmost limit, though "
            "the town is under Genoa and counted part of Liguria in speech "
            "and politics. Christian mobs, taking it for a pagan temple, "
            "smashed most of the statue of Augustus inside, and villagers "
            "have carried off its stones; whatever magic they hold is "
            "drowned by the Divine aura of 3 of the nearby church of "
            "St Michael.",
            "The mostly Mercurian magi of short-lived Turris Mascis, the "
            "Tower of the Masques, studied the monument, but what they "
            "learned is lost.",
        ),
        **KNOWN_TRIBUNAL,
    )


# ---------------------------------------------------------- Lower Burgundy


def _north(provence: Provence) -> None:
    region = provence.places["arelat"]
    burgundy = _add(
        provence,
        "lower_burgundy",
        "Lower Burgundy",
        inside=region,
        summary=paragraphs(
            "The north of Arelat: part of the Kingdom of Lower Burgundy "
            "(Cisjurania) that Boso of Provence proclaimed at Arles in 879, "
            "then of the reunited Kingdom of Arelat from 933, and under the "
            "Emperor Conrad II from 1032, though it slips ever further from "
            "imperial control. Like the Duchy of Burgundy in the Normandy "
            "Tribunal, it is known more for cathedrals, monasteries and "
            "pilgrimages than for trade. It is quite apart from the old "
            "Kingdom of Upper Burgundy north of the Jura and the Free County "
            "of Burgundy, which lie in the Tribunal of the Greater Alps. "
            "Beatrice of Albon, Dauphine of Viennois, rules here, while the "
            "prince-archbishop of Vienne disputes the land with her line.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        provence,
        "notre_dame_de_vie",
        "Notre Dame de Vie at Vienne",
        inside=burgundy,
        aura=3,
        summary=paragraphs(
            "A church at Vienne that hides the colonnaded Temple of "
            "Augustus and Livia, with a Magic aura of 3, thought once to "
            "have been an important Mercurian site. Nearby a truncated "
            "pyramid called Pilate's Tomb is said to mark where Pilate's "
            "body was sunk in the river, until it stirred up evil spirits in "
            "the water and was taken out. A Roman theatre lies on Mont "
            "Pipet to the east, and old roads and aqueducts run on the "
            "city's edge.",
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "grande_chartreuse",
        "The Grande Chartreuse",
        inside=burgundy,
        realm="Divine",
        aura=7,
        summary=paragraphs(
            "The Carthusians' motherhouse in the mountains above "
            "Grenoble: a cloister of separate cells, each a two-storey "
            "hermitage with its own walled garden off a long corridor. "
            "The monks' simple devotion gives the motherhouse a Divine "
            "aura of 7; the valley has 3. Several choir monks are "
            "unGifted Ascetics of a Holy Tradition; the prior and at "
            "least one other have True Faith, two elder brothers are "
            "skilled mythic herbalists, and the old hunchbacked "
            "cellarer, Salvatore, has the Blatant Gift.",
            "Its newest retreatant is Romualdus, once a Jerbiton magus, "
            "now the novice Brother Thomas, who has cut himself off "
            "from his old sodales.",
        ),
        secrets=[
            titled(
                "Brother Jude",
                "Romualdus has found that Brother Jude, a shy, clumsy young "
                "novice, holds True Faith as well as the Gift.",
            ),
            titled(
                "Romualdus and Jude",
                "Romualdus has befriended Brother Jude and fears the boy will be "
                "claimed as a Hermetic apprentice if word gets out.",
            ),
            titled(
                "Storyguide Notes",
                "Romualdus might seek a Bonisagus to intervene and then help train "
                "Jude himself, at the cost of his new vows.",
            ),
        ],
        **KNOWN_REGION,
    )
    _add(
        provence,
        "lac_du_bourget",
        "The Lac du Bourget",
        inside=burgundy,
        summary=paragraphs(
            "A beautiful lake just north of Aix-les-Bains, the Roman spa "
            "whose hot springs in the foothills of the Jura and the Alps "
            "still draw travellers. Fed by the Leysse, it is said to be the "
            "largest and deepest lake of the area, with an Aquam regio deep "
            "in its waters. Some magi report the elemental Men of the Lake "
            "here, unconfirmed.",
        ),
        **RUMOURED,
    )


# ----------------------------------------------------- the Coenobium


def _coenobium(provence: Provence, b: Builder, tribunal: Tribunal) -> None:
    region = provence.places["arelat"]
    p = provence.places
    p["coenobium_avignon"] = b.place(
        "The Coenobium's Avignon chapter (Sub Pontem)",
        inside=region,
        aura=3,
        summary=paragraphs(
            "The heart of the covenant, the old Sub Pontem: council rooms "
            "and guest quarters dug under the lightly wooded Isle de "
            "Barthelasse, the shifting midstream island above the Pont "
            "St Bénezet. The island is in effect a great lacuna in the "
            "city's Dominion, with a Magic aura of 2, which is 3 at the "
            "island's northern end, where most of the visiting magi's laboratories "
            "lie underground; the Rhone's floods sometimes make that hard. "
            "Only this northern site has an Aegis of the Hearth, renewed at "
            "the summer solstice rather than in winter.",
            "Nicodemus's underground laboratory opens under the bridge's "
            "second pier; the magi of old Sub Pontem still work their urban "
            "magic on the arches beyond the chapel, and one of the "
            "covenant's laboratory barges usually lies moored below a "
            "western pier. The consuls' townhouses in and around Avignon "
            "sit in the city's small lacunae and rely on weaker wards. "
            "Patrons have transport magic tied by Arcane Connection to the "
            "main council chamber, to come to a meeting at short notice.",
        ),
        **KNOWN_TRIBUNAL,
    )
    p["coenobium_arles"] = b.place(
        "The Coenobium's Arles chapter (St Cyprian's)",
        inside=region,
        summary=paragraphs(
            "The Mercer House of the Tribunal, in Les Arènes: the Roman "
            "arena of Arles, stripped for building stone and now a maze of "
            "hovels, churches and illicit trades that respectable folk "
            "avoid after dark. It passes for a pilgrims' inn of St Cyprian "
            "and is in truth a brothel, nominally owned by Alazais; the "
            "covenant's Redcaps and Jerbiton magi meet here and often stay "
            "for its earthier pleasures. Below the inn and the client rooms, "
            "chambers serve more discreet business. The city's Divine aura "
            "keeps any Magic aura from forming, so there is no Aegis; an "
            "archway carved with magical inscriptions links one chamber to "
            "the rooms under the Isle de Barthelasse.",
        ),
        **KNOWN_TRIBUNAL,
    )
    p["coenobium_factory"] = b.place(
        "The Coenobium's Trinquetaille chapter (the Factory)",
        inside=p["camargue"],
        summary=paragraphs(
            "A great warehouse at Trinquetaille, at the gate of the "
            "Camargue, holding the covenant's mundane wealth behind what "
            "look like ordinary merchants' stores. It runs several levels "
            "underground, with a heavily warded area inside a second Aegis "
            "for dangerous and exotic goods and captive creatures. Only "
            "patrons join its Aegis ritual, and the First Consul keeps a "
            "close hand on its few tokens each year. The heavier processes "
            "behind the covenant's wealth are worked here, magic helping or "
            "replacing the usual methods, hidden by subtle wards and by "
            "traps that wipe memories.",
        ),
        **KNOWN_TRIBUNAL,
    )
    p["coenobium_toulon"] = b.place(
        "The Coenobium's Toulon chapter",
        inside=region,
        summary=paragraphs(
            "A small chapter house below Mount Faron at Toulon, on the site "
            "of the old Flambeau covenant of Telo Martius. Toulon has made "
            "dyes since the Phoenicians: its beaches are among the few "
            "sources of the murex shellfish for imperial purple, and the "
            "hillside oaks keep the kermes beetle for a crimson nearly as "
            "precious. Aloysius Porphyri, a retired Redcap and unGifted "
            "alchemist, runs the chapter, oversees both harvests and one of "
            "the dye works of the covenant's factory outside the town.",
            "Purple once went only to the Byzantine emperors; now only part "
            "goes east, the covenant keeping some for magic (purple: +10 "
            "royalty, +7 rule and authority, +5 controlling people). The "
            "crimson is sold widely and loved by hoplites and Flambeau "
            "(+7 violence, +4 courage and martyrdom, +3 sin). Magic makes "
            "the extraction cheaper than any rival's, but the covenant "
            "takes care not to flood the market. A rare shell or beetle "
            "holds a little Imaginem vis.",
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "The largest covenant of the Tribunal, depending on how many "
        "visitors are in at once: a chain of chapter houses along the lower "
        "Rhone and east along the coast of Provence, called in the Redcap "
        "rolls Mascum Sub Pontem after its original main site, and by most "
        "Provençal magi just the Coenobium (Normandy's magi say Coenobium "
        "Rhodanien, to tell it from their own small unofficial coenobia). "
        "Its device is an arched bridge, and its motto 'Together we rule, "
        "divided we fall'.",
        "Late in the tenth century, against Fraxinetum's raids, the heirs of "
        "several Provençal covenants and some eremites bound themselves "
        "together. Mostly Jerbiton, they used their families and friends "
        "among the nobles and the Church to raise William I of Provence's "
        "army, which broke the Saracens at Tourtour and took their base in "
        "the Maures; they narrowly escaped the Quaesitores' wrath for "
        "destroying Fraxinetum, and found the league too useful to "
        "dissolve. The Birds of Camargue joined in 970, Barbegal's and Yf's "
        "survivors came too, and Anaïs of Jerbiton, last of Portus Cottiae, "
        "was among the loudest for a Hermetic hegemony. Since then, by "
        "cooperation and nepotism, its magi have gained control of or "
        "influence over most magical and mundane resources in the County "
        "of Provence, which they justify as insurance against ever again "
        "being caught unready by Hermetic aggression.",
        "The heart is urban, at Avignon, with holdings at Arles, at the "
        "edge of the Camargue, across southern Provence and as far north as "
        "Grenoble; in truth the whole Rhone sustains it, in magic and in "
        "trade. Two or more magi are always travelling the river in great "
        "barges made by the resident boatwright, smaller boats carry "
        "Redcaps on errands, and many of its standing enchantments cover "
        "the whole river or work as long as one is afloat on it or a major "
        "tributary. Few magi are ever in one place at once, which perhaps "
        "helps them tolerate one another.",
        "Over two dozen magi, mostly Jerbiton, are consuls, its voting "
        "members; nearly a dozen others are permanent guests, and up to six "
        "Redcaps may be staying. Jerbiton and Mercere dominate, but there "
        "are Bonisagus (especially Trianomae), Ex Miscellanea, Verditius "
        "and even Flambeau; as most belong to loose Societates, Alazais "
        "cares less for a magus's House than for an agreeable manner and "
        "commitment to the covenant. It is led, unusually, by the unGifted "
        "Chief Redcap, Alazais of Mercere, as First Consul, both autocrat "
        "and leader, leaving most magi free for their own pursuits much of "
        "the year. Its Jerbiton care little for magical power and much for "
        "worldly pursuits, with views of Beauty that differ from their "
        "housemates' elsewhere.",
        "The covenant fosters rather than supplants the region's masques: "
        "witches, cunning men and women, herbalists and faerie doctors "
        "who get its protection from the authorities and from other magi, and in "
        "return serve as unGifted agents and informants along the coast and "
        "the Alpine foothills, harvest and guard vis, make charms for its "
        "people, and spread its sway, while the magi keep to the letter of "
        "the Code. It welcomes visitors and specialists warmly (see the "
        "notes for its toll and code), and would welcome allied chapter "
        "houses elsewhere in the Tribunal, but its help comes with the "
        "hint of later annexation, and no independent covenant has "
        "flourished in southern Provence in over a century.",
    )
    what_matters = joined_lines(
        "Vis: Castra Peccaius salt, from a brackish pond in the ruins on the Petit Rhone; 1 to 3 pawns of Corpus a year, dedicated to longevity (+2 to a Longevity Ritual's Creo Corpus total, one pawn a ritual); the land is leased from the Abbey of Psalmody through dependants",
        "Vis: the round sling stones of the Crau, a handful of Terram pawns a year, gathered by grogs as a punishment",
        "Vis: Imaginem in rare murex shells and kermes beetles at Toulon, taken by Aloysius Porphyri",
        "Vis: the Hermetic toll, a silver florin holding a pawn of vis from each visitor to Avignon, which pays the non-Jerbiton specialists",
        "Vis: most vis sources in the region are held by the covenant or guarded by its hedge allies",
        "Trade: the salt vis goes to a research covenant of the Greater Alps for favours to its elders",
        "Income: the Factory at Trinquetaille, magically worked trades, Rhone shipping, and the purple and crimson dyes of Toulon",
        "Library: no books named; each consul keeps his own, with the Mercer House's records",
        "Allies: the masques of the Coenobium, led for it by Lavandarius; the Chief Redcap's network of Redcaps, retired Redcaps and their kin",
        "Allies: the abbot of St André, secretly; Hugh III of Baux through his cousin Marcus; Castra Solis in Tribunal",
        "Boon: Urban; Mercer House; Wealth; Secondary Income; Regional Produce; Informants; Hedge Tradition; Mystical Portal (the arch from Arles to Avignon)",
        "Hook: Hermetic Politics; Contested Resource (the salt pond); Weak Aura (its town sites lie in small lacunae)",
        "Tension: other Jerbiton find its magical grip on nobles, resources and hedge wizards distasteful",
        "Tension: its hegemony unsettles even old allies; some fear it means to dominate the Tribunal after the crusade",
        "Tension: it wants the lost Alpine sites and Barbegal reclaimed, and its few strong auras make it hungry for them",
        "Tension: threaten its salt and the politically aloof magi will hit back hard",
        "Hook: it seeks specialists in wards, transport and weather magic, a non-Tremere certamen champion, and teachers for its apprentices",
        "Hook: a magus who founds a chapter under a consul's patronage may petition for membership, or later declare independence",
    )
    toll = paragraphs(
        "The Hermetic toll. Every magus visiting Avignon openly is asked to "
        "call at the covenant and say why he has come and how long he will "
        "stay, under the rules of hospitality House Jerbiton promotes. The "
        "Tribunal's Redcaps, at Alazais's urging, let it be known that a "
        "silver florin holding a pawn of vis is expected as a goodwill "
        "gift. Those who pay are given a consul as guide, answerable for "
        "their conduct in the town, which some visitors find a meddling "
        "minder. Those who decline are thought ill-bred and watched by the "
        "covenfolk; a guest who flaunts himself or works magic on the "
        "townsfolk draws Xiphos or the covenant's hedge allies, and though "
        "the Coenobium stops short of Wizard's War, it obstructs such a "
        "magus patiently for years, even trumping up charges at Tribunal.",
        "The visitor's code. Guests are offered food, lodging and a "
        "laboratory, and the consuls choose a patron for each, usually a "
        "Jerbiton. In return a visitor is to: introduce himself properly, "
        "ideally sending word ahead by Redcap; bring a small gift, by "
        "custom a silver florin holding a pawn of vis; say why he has come "
        "and for how long, and tell his patron when he leaves; behave with "
        "decorum and restraint, helping his patron if asked; and go at once "
        "if asked to. The patron explains these rules, answers for the "
        "guest, shields him from harm and inconvenience, and gives him a "
        "token gift at parting; the duty is honoured more than rewarded, "
        "and a patron may call on other members for help or be let off a "
        "season of service.",
        "Membership. Consuls vote; up to a dozen visitors and independent "
        "magi are linked to the covenant at any time, among them up to six "
        "new Jerbiton resting between stages of their Itinerarium. Guests "
        "do not vote, but if they behave well they may ask to use the "
        "covenant's resources with the approval of their patron and two "
        "other consuls, much as at many Autumn covenants. The First Consul "
        "may ask any magus there for help with his resources, though he "
        "need not agree. There is no roster of covenfolk: each consul keeps "
        "his own servants, kin, grogs, artists and troubadours.",
        "Votes: about 20 at Tribunal, the largest bloc.",
        "Founded: the book gives no year, only the late tenth century, "
        "about two centuries ago; it already existed when the Birds of "
        "Camargue joined it in 970.",
    )
    hidden = [
        titled(
            "Who steers the council",
            "Alazais never seems to vote in council but pulls the strings "
            "behind it, steering the covenant to her own ends.",
        ),
        titled(
            "The Praeco's bargain",
            "Dama made a Longevity Ritual for Alazais's lover, a folk witch; "
            "that bought the Praeco the Coenobium's tacit support, which she "
            "means to spend to bury any inquiry into the Presiding Quaesitors' "
            "deaths.",
        ),
        titled(
            "The fall of Elisii Campi",
            "The Coenobium drove Elisii Campi from the Alyscamps by spreading "
            "rumours of diabolists; many suspect hoplites it sponsored hunted "
            "down the survivors at Portus Termini.",
        ),
        titled(
            "The Balthazarine magi",
            "The Coenobium may use its Balthazarine magi as decoys and "
            "scapegoats, and it feeds the nobles' stories of the Baux line's "
            "descent from Balthazar.",
        ),
        titled(
            "The humiliated Redcap",
            "Aucassin's thugs in the boatmen's guild lately humiliated a Redcap "
            "carrying a private message to one of the Coenobium's magi; the "
            "Coenobium wants the utricularii taught to cooperate.",
        ),
        titled(
            "Calais overdue",
            "Calais of Bonisagus, a valued guest of the Coenobium, is trapped in "
            "Ventoux's regio and overdue.",
        ),
    ]
    coenobium = b.covenant(
        "The Coenobium Rhodanien",
        tribunal=tribunal,
        founded=970,
        place=p["coenobium_avignon"],
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(toll),
        secrets=hidden,
        unnamed_magi=17,
        season="Autumn",
    )
    provence.covenants["coenobium"] = coenobium
    _coenobium_magi(provence, b, coenobium)
    b.book(
        coenobium,
        "The libraries of the Coenobium",
        "Other",
        description=(
            "The book names no books. With no shared roster or common "
            "household, each consul keeps his own collection in his "
            "townhouse or sanctum, and the Mercer House at Arles holds the "
            "Redcaps' records; a lost Merinita trove of Faerie books lies at "
            "Caturigomagus among the ruins of Portus Cottiae, and the "
            "covenant would sponsor its recovery."
        ),
    )


def _coenobium_magi(provence: Provence, b: Builder, home: Covenant) -> None:
    m = provence.magi
    m["alazais"] = b.magus(
        "Alazais of Mercere",
        covenant=home,
        house=MERCERE,
        age=59,
        summary=paragraphs(
            "The Coenobium's First Consul and the Provençal Chief "
            "Redcap, unGifted, looking about twenty-seven thanks to a "
            "lasting Longevity Ritual. She claims descent from Helen of "
            "Troy, and from Mercere himself through his granddaughter, "
            "which wins her respect among Redcaps and Jerbiton alike. She "
            "wears a classical actor's tragic mask and takes it off only "
            "before magi or her lover, an unGifted folk witch allied to "
            "the covenant; rumour, which no magus confirms or denies, "
            "says a spurned suitor scarred her face with acid.",
            "Under her the Coenobium has taken in more non-Jerbiton "
            "magi as long-term guests and adopted lesser hedge wizards "
            "as nominal Redcaps. She plays the humble manager, urging "
            "the Jerbiton to chase beauty and leave the running of the "
            "covenant to supposed inferiors. In 1214 she helped avert "
            "the Tribunal's collapse by threatening to suspend every "
            "Redcap service. She is rumoured to belong to the Matres and "
            "Matrones. She owns the inn of St Cyprian at Arles.",
        ),
        secrets=[
            titled(
                "Her lover's longevity",
                "Her lover's longevity was Dama's work, done at great cost, "
                "and it ties Alazais to the Praeco.",
            ),
            titled(
                "Alazais in council",
                "She quietly steers every vote of the council while seeming "
                "never to cast one.",
            ),
        ],
        traits={"Ambitious": 6, "Wily": 3, "Patient": 2},
    )
    m["nicodemus"] = b.magus(
        "Nicodemus Ex Miscellanea",
        covenant=home,
        house=EX_MISC,
        age=102,
        summary=paragraphs(
            "A senior magus who looks sixty-three, once a Jerbiton "
            "enchanted by the beauty of Roman waterworks, until Twilight "
            "scars in his youth left him with a Blatant Gift. Obsessed with "
            "Aquam magic, unable to live the tasteful life among mundanes, "
            "and estranged from his gently Gifted colleagues, he "
            "reluctantly moved to House Ex Miscellanea; he is still a "
            "nominal consul, though most find his ways unbecoming. River "
            "folk and Redcaps respect him warily and know him as a hermit "
            "on the shore under the Pont St Bénezet, where his laboratory "
            "opens below the second pier.",
            "He is working to fold the Atlantean magic of his lineage into "
            "standard Hermetic theory. Alazais sees him caring less and "
            "less for what his housemates expect, and suspects Warping from "
            "his experiments is wearing down his sanity.",
        ),
        traits={"Absent-Minded": 6, "Reclusive": 3},
    )
    m["marcus_baux"] = b.magus(
        "Marcus d'Les Baux, the Balthazar",
        covenant=home,
        house=TYTALUS,
        age=42,
        summary=paragraphs(
            "An aggressive young scion of the lords of Baux, looking "
            "thirty-five, known in his family as the wizard Balthazar and "
            "the current Hermetic heir of the Balthazarine line, which "
            "claims descent from the wise king. His sigil includes the "
            "Christmas star of his family's arms. The book names him of "
            "House Tytalus, the House that Baux scions of poor taste often "
            "end in after a Jerbiton apprenticeship.",
            "The late Chief Quaesitor warned him for meddling openly in "
            "mundane affairs for his family and his friends in the Church, "
            "above all the abbot of St André. He keeps his seat as consul "
            "but may not act as a patron until he shows he can be more "
            "discreet about his nepotism. His cousin Hugh III of Baux, "
            "Viscount of Marseille, deals with the Coenobium through him. "
            "At least two younger Balthazarine magi of junior branches "
            "exist, and Marcus may see any of them as rivals.",
        ),
        traits={"Loyal": 3, "Sly": 2},
    )
    m["pola"] = b.magus(
        "Pola the Sophist",
        covenant=home,
        house=JERBITON,
        age=81,
        summary=paragraphs(
            "A maga who looks about fifty, of a lineage begun by a Jerbiton "
            "who had been a Gorgiastic, one of those who left House Criamon "
            "rejecting its teaching on the Enigma; over time the line "
            "became a wandering tradition of rhetoricians and advocates "
            "schooled in Gorgias and the Sophists, and some of its younger "
            "members have been taken into House Tytalus on merit. A fine "
            "speaker, she holds debate an expression of beauty and pushes "
            "it as a better way to settle disputes than certamen or "
            "Wizard's War.",
            "Of all the consuls she is the likeliest patron for a visitor. "
            "Nominally in charge of the Avignon holdings, she oversees the "
            "Jerbiton apprentices passing through on their Itinerarium to "
            "or from Eboris in Paris.",
        ),
        traits={"Precise": 3, "Impatient": 2, "Haughty": 1},
    )
    m["xiphos"] = b.magus(
        "Xiphos filia Damocles",
        covenant=home,
        house=JERBITON,
        age=73,
        summary=paragraphs(
            "A disgraced master hoplite of Terram from beyond the "
            "Tribunal, looking about fifty-four, expelled from House "
            "Guernicus for repeated conduct unworthy of a hoplite. At "
            "Primus Andru's unexpected insistence House Jerbiton "
            "grudgingly took her in and gave her a chance to reform, on "
            "terms that seem to bind her to use her talents to keep the "
            "Coenobium stable; thanks to her, her gentler housemates "
            "pursue Beauty and Taste with little trouble from magical "
            "threats. She claims descent from a legendary Guernicus "
            "Terrae-magus, Adamantius, and has nearly total mastery of "
            "metal and blades.",
            "Her parens Damocles, a disgraced magus, killed Argentius in "
            "a mundane duel when he was Auriel Blake; she and Argentius "
            "are now unlikely friends. Chapter three's list of possible "
            "parentes calls her line 'Damocles of the Coenobium, raised "
            "Guernicus, now Jerbiton'.",
        ),
        secrets=[
            titled("Her pardon", "The exact terms of her pardon are unknown."),
        ],
        traits={"Ill-tempered": 3, "Intolerant": 2, "Cruel": 2},
    )
    m["lavandarius"] = b.magus(
        "Lavandarius the Pralician",
        covenant=home,
        house=EX_MISC,
        age=67,
        summary=paragraphs(
            "The covenant's go-between with its hedge wizard allies, "
            "looking thirty-eight: a Gifted student of a local herbalist "
            "tradition taken as second apprentice by his Pralician mater. "
            "His lineage brought the region's hedge wizards into the "
            "covenant, with Alazais's backing, a policy the northern "
            "Tribunals, Normandy and the Rhine above all, think wildly "
            "unorthodox. One of the few non-Jerbiton consuls, he is never "
            "made a visitor's patron but answers for the stronger hedge "
            "magicians who come to the Coenobium's towns.",
            "He carries on his mater's slow work to bring herbalists' folk "
            "practice into standard Hermetic theory. His familiar is a "
            "common asp he found among the Hyères lavender.",
        ),
        traits={"Cautious": 3, "Diplomatic": 2, "Charming": 2},
    )
    m["argentius"] = b.magus(
        "Argentius of Mercere",
        covenant=home,
        house=MERCERE,
        age=49,
        summary=paragraphs(
            "The Invited Redcap, looking forty-one, living a second life. As "
            "Auriel Blake, weapon-master of Valnastium, he seemed killed by "
            "the disgraced magus Damocles in a mundane duel, then was "
            "brought back by a miracle of the greater relic of St Michael in "
            "his sword's pommel. Alazais took him in as a Redcap of the "
            "Coenobium. Still coming to terms with his return, he keeps "
            "apart from covenfolk who hold him in awe and fear, and has "
            "struck up an odd friendship with his killer's former "
            "apprentice, Xiphos.",
            "His resurrection woke the latent powers of his Heroes' "
            "Birthright, giving him remarkable command of swords and other "
            "blades, and magi cannot decide whether he counts as a hedge "
            "magician or a true Redcap, however odd. He believes, "
            "perhaps rightly, that his sword is the Sword of Ares that "
            "Attila bore as the Scourge of God, and lets no one examine it.",
        ),
        traits={"Wrathful": 3, "Gloomy": 2, "Pious": 2},
    )
    m["bubulcus"] = b.magus(
        "Bubulcus",
        covenant=home,
        house=BJORNAER,
        age=None,
        summary=(
            "A diminutive Bjornaer, nominally a guest of the Coenobium, who "
            "lives on the edge of Trinquetaille but spends most of his time "
            "roaming the Camargue on his bull, his animal companion, "
            "usually in his egret heartbeast form. The more sociable of its "
            "two Bjornaer; he knows of the Great Stallion and the wild "
            "horses but seldom deals with them. A possible parens for "
            "Bjornaer characters."
        ),
    )
    m["elornis"] = b.magus(
        "Elornis One-Leg",
        covenant=home,
        house=BJORNAER,
        age=None,
        summary=(
            "A Bjornaer guest of the Coenobium living on the edge of "
            "Trinquetaille, of a line of African diviners, whose heartbeast "
            "is a greater flamingo. He spends at least a season a year in "
            "his North African homeland or travelling through dreams, and "
            "has little contact with the horses of the Camargue. A possible "
            "parens for Bjornaer characters."
        ),
    )
    m["calais"] = b.magus(
        "Calais filius Septentrio",
        covenant=home,
        house=BONISAGUS,
        age=None,
        summary="A Bonisagus of the Rhine, guest of the Coenobium, who "
        "calls himself Master of the Winds, one of the specialists in narrow, "
        "powerful magic the covenant invites. Drawn by Ventoux's "
        "spirits, he made a sanctum in a cave just below the summit to "
        "persuade the daimon there to take him as its Spirit Votary.",
        secrets=[
            titled(
                "Calais in Ventoux's regio",
                "The Faerie lord Mistrau has sealed the spirits' regio with "
                "Calais inside, still fighting Ventoux's furious servants; his "
                "hosts expected him back last season and are growing worried.",
            ),
        ],
    )
    m["aloysius"] = b.magus(
        "Aloysius Porphyri",
        covenant=home,
        house=MERCERE,
        age=None,
        summary=(
            "A retired Redcap and unGifted alchemist who runs the Toulon "
            "chapter on the site of old Telo Martius, oversees the harvest "
            "of murex and kermes, runs one of the dye works of the factory "
            "outside the town, and takes the rare Imaginem vis from the "
            "shells and beetles."
        ),
    )
    m["jorin"] = b.magus(
        "Jorin",
        covenant=home,
        house=MERCERE,
        age=None,
        summary=(
            "A retired Redcap and former Rhone boatman who keeps the door "
            "of the chapel of St Nicholas on the Pont St Bénezet, where "
            "St Bénezet lies, and reports to the Coenobium."
        ),
    )


# ------------------------------------------------------ Fraxinetum Redux


def _fraxinetum_redux(provence: Provence, b: Builder, tribunal: Tribunal) -> None:
    summary = "A covenant the Tribunal does not know of."
    hidden = [
        titled(
            "Where the heirs of Fraxinetum live",
            "The heirs of Fraxinetum, the raider covenant of Sayyid Shajarat "
            "al-Darda and his Tytalan lieutenant Nasr ibn Amaf that the "
            "Coenobium destroyed in 975, no longer live in the ash forest of "
            "the Maures but on the Hyères islands.",
        ),
        titled(
            "The raids of Fraxinetum Redux",
            "The heirs of Fraxinetum still back mundane raids on the coastal "
            "towns of Provence and harry Catalan and Genoese shipping, though "
            "Ahmad's ships strike only non-Hermetic vessels and rely on "
            "well-placed spies to keep clear of the Coenobium's fleet.",
        ),
        titled(
            "The magi of Fraxinetum Redux",
            "Two Moorish magi of Fraxinetum Redux live at the pirates' main "
            "base among the lavender, and a third has a sanctum aboard one of "
            "the larger ships of their shady associates.",
        ),
        titled(
            "Vis on the islands",
            "The magi of Fraxinetum Redux harvest vis scattered over the small "
            "islands of the coast, the deserted Diedne site at Yf among them.",
        ),
        titled(
            "Never declared",
            "The magi of Fraxinetum Redux have never declared themselves at "
            "Tribunal for fear their ancestors' shadow would bring a Wizard's "
            "War down on them: the Tribunal does not know the covenant exists, "
            "and it has never voted.",
        ),
        titled(
            "What they would oppose",
            "Fraxinetum Redux will not oppose new covenants unless someone "
            "builds another sea stronghold or takes an island off the south "
            "coast.",
        ),
    ]
    what_matters = joined_lines(
        "Vis: scattered sources on the small islands of the south coast, the deserted Diedne site of Yf among them",
        "Income: a share of the pirates' raids on the coast and on Catalan and Genoese shipping",
        "Allies: the corsairs of the Hyères and their spies ashore",
        "Boon: Island; Hunters or Sailors; Spies",
        "Hook: Dark Secret (an undeclared covenant of the raiders' heirs); Rival (the Coenobium)",
        "Tension: discovery could bring the Wizard's War their ancestors suffered",
    )
    redux = b.covenant(
        "Fraxinetum Redux",
        tribunal=tribunal,
        founded=None,
        place=provence.places["hyeres"],
        summary=summary,
        what_matters=what_matters,
        secrets=[
            *hidden,
            titled(
                "Storyguide Notes",
                joined_lines(
                    "Votes: 3 if it ever declared itself, unused.",
                    "Founded: the book gives no year; its magi descend from Fraxinetum (889-975).",
                ),
            ),
        ],
        unnamed_magi=2,
        season="Summer",
    )
    provence.covenants["fraxinetum_redux"] = redux
    provence.magi["ahmad"] = b.magus(
        "Ahmad ibn Nasr",
        covenant=redux,
        house=TYTALUS,
        age=68,
        summary="A Tytalus magus the Tribunal does not know of.",
        secrets=[
            titled(
                "Ahmad of Fraxinetum Redux",
                "Leader of the pirates of Fraxinetum Redux, looking "
                "forty-three, a direct descendant of the raider covenant's "
                "founder, and a master of sea magic, jinn and water "
                "elementals.",
            ),
            titled(
                "Ahmad's teachers",
                "He may have been partly taught by a Hermetic sahir of "
                "al-Andalus and learned non-Hermetic mysteries from faerie jinn.",
            ),
            titled(
                "Ahmad's familiar",
                "His familiar is a mighty sea-dwelling 'afrit who claims to be a "
                "prince of an undersea jinn tribe near Gibraltar, defeated by "
                "Ahmad in his self-taught initiation script.",
            ),
        ],
        traits={"Carefree": 3, "Brave": 2},
    )


# ---------------------------------------------- magi with no covenant here


def _loose_magi(provence: Provence, b: Builder) -> None:
    m = provence.magi
    m["aucassin"] = b.magus(
        "Aucassin of Tytalus",
        covenant=None,
        house=TYTALUS,
        age=None,
        summary="A Tytalus magus, an orphan raised by a peregrinator of the "
        "Rhine and born at Beaucaire, who does not come to Tribunal and "
        "is thought by many to have vanished, perhaps after training an "
        "apprentice.",
        secrets=[
            titled(
                "Aucassin's sanctum",
                "Back in his birthplace after his Gauntlet, he was drawn to "
                "a weak Magic aura round a disused well in the old market of "
                "Beaucaire and found beneath it the underwater regio web "
                "under the Rhone and the Drac, where he built his sanctum.",
            ),
            titled(
                "Aucassin le Draconnet",
                "Styling himself 'Aucassin le Draconnet', he revived the "
                "Drac legend to cover his search for an apprentice and his "
                "forcible recruitment of servants.",
            ),
            titled(
                "Rene of Dragonianum",
                "For years he has kept up a Persona as Rene of Dragonianum, a "
                "prosperous merchant boss of Beaucaire, steering its council "
                "with craft and low-level Mentem magic, dealing as Rene with "
                "the Coenobium's Redcaps and hedge allies but never meeting a "
                "Gifted magus, and never working open magic in town.",
            ),
            titled(
                "Aucassin's blood",
                "Over twenty years he has learned that his blood comes from "
                "the Drac of old, and the cave paintings of his regio make up "
                "a Mystery script to turn him into a true elder drac.",
            ),
            titled(
                "The dragon Vestige",
                "Beyond a portal in Aucassin's regio to the Magic Realm, "
                "aligned to Imaginem, sleeps the dragon Vestige whose legacy "
                "he would claim when he understands the rites better.",
            ),
            titled(
                "Le Petit",
                "About ten years ago he kidnapped children round Beaucaire and "
                "kept a sickly Gifted boy who seems to share his blood, 'Le "
                "Petit', whom he trains as an apprentice.",
            ),
            titled(
                "Le Petit's illness",
                "Le Petit is wasting from a magical illness Aucassin cannot "
                "heal, and Aucassin may come to magi disguised as a poor "
                "washerwoman to beg a cure.",
            ),
            titled(
                "Aucassin's boatmen",
                "His agents in the boatmen's guild of Beaucaire and Arles spy "
                "and enforce for him and keep the ferry's toll steep.",
            ),
            titled(
                "Aucassin and the Redcaps",
                "He leaves Redcaps alone, though one of his thugs lately "
                "humiliated a messenger of the Coenobium.",
            ),
            titled(
                "Storyguide Notes",
                "His blood from the Drac of old is Mythic Blood.",
            ),
        ],
    )
    m["romualdus"] = b.magus(
        "Romualdus",
        covenant=None,
        house=JERBITON,
        age=None,
        summary="A former Jerbiton magus, now Brother Thomas, a novice at the "
        "Grande Chartreuse. Repelled by the pagan remnants and decaying "
        "culture of the Order, he has given up active Hermetic life and "
        "shuns his former sodales. He no longer works ordinary Hermetic "
        "magic and seeks God through a more ascetic use of his Gift, "
        "hoping to found a new, prayer-based tradition of holy magic.",
        secrets=[
            titled(
                "Brother Jude",
                "He has found that Brother Jude, a young novice, holds True "
                "Faith and the Gift, and fears the Order will claim him.",
            ),
        ],
    )
    m["fraxinus"] = b.magus(
        "Fraxinus of Portus Termini",
        covenant=None,
        house=GUERNICUS,
        age=None,
        summary=(
            "A Guernicus magus the book names only among possible parentes, "
            "of Portus Termini: the hidden covenant in the caves of the "
            "Verdon Gorge that the spirit masters of Elisii Campi tried to "
            "found after the Coenobium drove them from the Alyscamps. It "
            "failed before the next Tribunal and was never registered, and "
            "contact was lost soon after. Where he lives now is unknown."
        ),
    )


# ------------------------------------------------------- the mundane world


def _lords(provence: Provence, b: Builder) -> None:
    w = provence.world
    p = provence.places
    region = p["arelat"]
    w["king_of_arles"] = b.lord(
        "King of Arles",
        title="duke",
        wealth="Wealthy",
        ruler="Frederick II, Holy Roman Emperor",
        place=region,
        summary=(
            "Frederick II, the Emperor, holds the rather hollow title of King "
            "of Arles, ruling the kingdom of Arelat and Provence in name. "
            "In practice he has little sway there, exercised through his "
            "viceroy at Arles, the young Prince of Orange. Lower Burgundy "
            "grows ever more independent of him, and the Rhone's "
            "boatmen and the Coenobium's servants count themselves part of "
            "no distant Empire."
        ),
    )
    king = w["king_of_arles"]
    w["count_of_provence"] = b.lord(
        "Count of Provence",
        title="count",
        wealth="Wealthy",
        seat="Aix",
        ruler="Ramon Berenguer V",
        answers_to=king,
        place=region,
        summary=(
            "Ramon Berenguer V, a Catalan of the house of Barcelona, Count of "
            "Provence and now of Forcalquier too, the region's strongest "
            "magnate; he was freed in 1219 from imprisonment in Aragon. His "
            "mother Garsenda's marriage to Alfonso in 1209 brought him the "
            "wide Forcalquier inheritance. Aix, the old Roman Aquae Sextiae "
            "by its thermal spring, is his recently chosen capital, and his "
            "house's backing made Marseille a great port again. Avignon "
            "owes him no allegiance."
        ),
    )
    count = w["count_of_provence"]
    w["forcalquier"] = b.lord(
        "Countess of Forcalquier",
        title="count",
        seat="Forcalquier",
        ruler="Countess Garsenda, regent",
        answers_to=count,
        place=region,
        summary="Countess Garsenda governs the county along the Durance from "
        "the citadel on its steep conical hill, as regent; her marriage "
        "to Alfonso in 1209 added her inheritance to her son's lands as "
        "Count of Provence. A trobairitz in her own right and a famous "
        "patron of troubadours across the south, she is said to have "
        "powers beyond the ordinary troubadour's gift of inspiring song.",
        secrets=[
            titled(
                "The countess's lovers",
                "Among her rumoured lovers is at least one Jerbiton magus of "
                "the Coenobium.",
            ),
        ],
    )
    w["prince_of_orange"] = b.lord(
        "Prince of Orange",
        title="count",
        seat="Orange",
        ruler="Raymond I of Baux",
        answers_to=king,
        place=region,
        summary=(
            "Raymond I of Baux, young prince of Orange, a Celtic oppidum "
            "and then a colony of Caesar's veterans that the Baux have held "
            "since the Kingdom of Arles broke up in 1033; Frederick I raised "
            "the county to a little principality in 1163. Raymond acts as "
            "the Emperor's viceroy at Arles and still claims that office, "
            "which his father William, a troubadour, held until he died in "
            "an Avignon prison in 1218; but the town's commune limits his "
            "power sharply."
        ),
    )
    w["lord_of_baux"] = b.lord(
        "Lord of Baux",
        title="landed",
        wealth="Wealthy",
        seat="Marseille",
        ruler="Hugh III of Baux",
        answers_to=king,
        place=p["alpilles"],
        arms=Arms("Gules", charge="Star", charge_tincture="Argent"),
        summary=paragraphs(
            "Hugh III, son of Bertrand, Seigneur of Baux, whose fortress "
            "was razed in 1162 at the end of the Baussenque Wars against "
            "the Catalan counts. He lives mostly in bustling Marseille, "
            "which he holds as viscount for the Emperor. His kin include "
            "the Prince of Orange and much of Provence's lesser nobility, "
            "and his younger cousin Marcus is the wizard Balthazar of "
            "the Coenobium, through whom Hugh keeps close ties to the "
            "covenant; his young son Barral deeply distrusts his "
            "father's dealings with wizards.",
            "The Baux claim descent from Balthazar, one of the three "
            "wise kings, and bear the Star of Bethlehem; their deeds "
            "have been less than Christian. The shield shown follows the "
            "later blazon, gules a star argent (of sixteen rays, which "
            "the app draws as a plain star).",
        ),
        secrets=[
            titled(
                "The Gift in the Baux line",
                "The Gift turns up unusually often in the family of the lords of Baux.",
            ),
            titled(
                "The Balthazar legend",
                "The Coenobium encourages the Balthazar legend among the nobles "
                "to its own ends.",
            ),
        ],
    )
    w["dauphine"] = b.lord(
        "Dauphine of Viennois",
        title="count",
        ruler="Beatrice of Albon",
        answers_to=king,
        place=p["lower_burgundy"],
        summary=(
            "Beatrice of Albon, Dauphine of Viennois and Countess of Albon, "
            "whose grandson Hugh IV, aged eight, is Duke of Burgundy in "
            "the Normandy Tribunal. The dauphins keep challenging the "
            "prince-archbishop of Vienne for control of the region; it has "
            "not yet come to blows, but threatens to."
        ),
    )


def _churches(provence: Provence, b: Builder) -> None:
    w = provence.world
    p = provence.places
    region = p["arelat"]
    burgundy = p["lower_burgundy"]
    w["archbishop_vienne"] = b.church(
        "Archbishopric of Vienne",
        church="Archbishop's cathedral",
        ruler="Jean de Bernin, prince-archbishop",
        place=burgundy,
        summary=(
            "Vienne, once capital of the Allobroges and a great Roman "
            "colony, is the seat of the archbishop of northern Arelat. Jean "
            "de Bernin, its prince-archbishop, is lawful count of the area "
            "for the Emperor but is constantly challenged by the dauphins."
        ),
    )
    w["st_trophime"] = b.church(
        "Cathedral of St Trophime, Arles",
        church="Archbishop's cathedral",
        place=region,
        summary=(
            "The cathedral of Arles, which has held the relics of "
            "St Trophimus since they were taken from the Alyscamps in "
            "1152, draining the old necropolis of its importance. The "
            "city's Divine aura is why the Coenobium's Mercer House can "
            "raise no Aegis."
        ),
    )
    w["st_andre"] = b.church(
        "Abbey of St André",
        church="Monastery or nunnery",
        ruler="The abbot of St André",
        place=region,
        summary="A prosperous abbey-town on Mont Andaon at the western end of "
        "Avignon's bridge, commanding the road to the commune and "
        "lodging pilgrims bound for Santiago. It keeps the relics of "
        "St Casarie, a Visigothic princess who lived as a hermit in the "
        "sixth century, under "
        "a strong Divine aura of 4. The abbot, a distant kinsman of the "
        "Baux and one of the greatest landowners nearby, is more open "
        "than most churchmen and sometimes receives the more "
        "respectable hedge wizards. Magi who refuse the Coenobium's "
        "hospitality may ask him for lodging in the aptly named Tower "
        "of Sorcerers, discreetly, or risk the bishop's anger and the "
        "Coenobium's interest.",
        secrets=[
            titled(
                "The abbot and the Coenobium",
                "The abbot of St André secretly keeps on good terms with the "
                "Coenobium, and Marcus d'Les Baux has meddled on his behalf.",
            ),
        ],
    )
    w["st_ruf"] = b.church(
        "Abbey of St Ruf",
        church="Monastery or nunnery",
        order="Canons of St Rufus",
        place=region,
        summary=(
            "The canons of St Rufus, Avignon's patron saint, keep an abbey, "
            "church and hospice just outside the town near the Rhone; its "
            "grounds have a Divine aura of 3."
        ),
    )
    w["st_gilles"] = b.church(
        "Abbey of St Gilles",
        church="Monastery or nunnery",
        order="Benedictine",
        place=region,
        summary=(
            "A Benedictine house grown from the seventh-century hermitage "
            "of St Giles, the first halt on the Via Tolosana from Arles and "
            "a day's walk on the Way of St James; abbey and town are a "
            "pilgrimage in their own right, and the birthplace and family "
            "lands of the recent counts of Toulouse. Barren women come to "
            "the saint's crypt to pray for children, and cripples on his "
            "feast, the first of September."
        ),
    )
    w["psalmody"] = b.church(
        "Abbey of Psalmody",
        church="Monastery or nunnery",
        place=region,
        summary=(
            "The abbey near the Petit Rhone that owns the land of the ruins "
            "of Castra Peccaius, which the Coenobium leases through its "
            "dependants for the salt pond inside. If history runs its "
            "course the monks will sell it to King Louis to found Aigues-"
            "Mortes for his crusade, and corrupt captains may then grab the "
            "salt pans, and the vis."
        ),
    )
    w["lerins_abbey"] = b.church(
        "Abbey of Lérins",
        church="Monastery or nunnery",
        place=region,
        summary=(
            "The fortified monastery on the Ile St-Honorat, which the book "
            "calls Cistercian, ruling the walled town on the mainland under "
            "the watchtower on the Suquet. Pilgrims flock to St Honoratus: "
            "some count the journey equal to one to the Holy Land, and it "
            "has trained remarkable clerics, perhaps St Patrick. Its sister "
            "convent of Ste Marguerite stands on the smaller island."
        ),
    )
    w["groseau"] = b.church(
        "Notre-Dame-du-Groseau",
        church="Monastery or nunnery",
        place=p["ventoux"],
        summary=(
            "The large monastery on Ventoux's lower slopes, whose prayers "
            "and hymns, if the mountain's powers are Infernal, have partly "
            "held them in."
        ),
    )
    w["chartreuse"] = b.church(
        "Order of the Carthusians",
        church="Monastery or nunnery",
        order="Carthusian",
        ruler="The prior of the Grande Chartreuse",
        place=p["grande_chartreuse"],
        founded=1084,
        summary=(
            "Founded in 1084 by the hermit St Bruno of Cologne under its own "
            "statutes, motto 'the Cross stands firm while the world turns'. "
            "Shunning the worldliness of Benedictines and Cistercians, its "
            "monks live in solitude and silence within the Chartreuse "
            "massif, with no ministry but prayer, and seldom take "
            "retreatants. They avoid needless speech but may talk on their "
            "weekly four-hour walk in the woods, changing partners each half "
            "hour; only the prior speaks to would-be retreatants and "
            "outsiders. Lay brothers in a dormitory at the valley's foot do "
            "the labour, manage supplies and turn visitors away."
        ),
    )
    w["st_apollinaris"] = b.church(
        "Cathedral of St Apollinaris",
        church="Bishop's cathedral",
        place=region,
        summary=(
            "A cathedral rebuilt in the Cluniac Romanesque style and "
            "reconsecrated by Pope Urban II in 1095. Set into a column of "
            "its ambulatory is a milestone of the Via Agrippa whose Latin "
            "inscription names its sponsor, Florentius Niger, a senator "
            "thought to have been a priest of Mercury; it reeks of "
            "non-Hermetic magic and may hold an Insight into the old "
            "Mercurian road magic, or a clue to a lost temple. Studying it "
            "in place is hard, and taking it out would bring the clergy "
            "hunting the thief."
        ),
    )
    w["st_michael_turbie"] = b.church(
        "Church of St Michael, La Turbie",
        church="Parish church",
        place=p["tropaeum"],
        summary=(
            "The church beside the Tropaeum Alpium whose Divine aura of 3 "
            "smothers whatever magic the monument's scattered stones hold."
        ),
    )


def _towns(provence: Provence, b: Builder) -> None:
    w = provence.world
    p = provence.places
    region = p["arelat"]
    king, count = w["king_of_arles"], w["count_of_provence"]

    def town(key: str, name: str, summary: str, **kw: Any) -> None:
        w[key] = b.town(name, summary=summary, **kw)

    town(
        "avignon",
        "Avignon",
        "The commune that has dominated southern Provence since 1129, "
        "half free of the Empire and owing nothing to the Catalan count. "
        "Its bridge, the Pont St Bénezet, and the Isle de Barthelasse are "
        "the heart of the Coenobium, and the city's Divine aura is 3. "
        "Magi visiting openly are expected to call on the covenant and pay "
        "its toll.",
        charter="Commune",
        place=region,
    )
    town(
        "arles",
        "Arles",
        "A free commune on the pattern of the Italian city-states, ruled "
        "since 1132 by an elected podestà from outside, who names the other "
        "consuls. A busy seaport where northern crusaders and pilgrims take "
        "ship for the Holy Land, where the Rhone barges hand cargo to sea "
        "craft, and where most of the Rhone boatmen live. The Coenobium's "
        "Mercer House hides in the old arena, the Factory stands across the "
        "wooden bridge at Trinquetaille, and the drac's lair is said to open "
        "from a pool outside the north gate.",
        charter="Commune",
        answers_to=king,
        place=region,
    )
    town(
        "beaucaire",
        "Beaucaire",
        "'Beautiful rock', on the Languedoc bank facing Tarascon, nominally "
        "the Count of Toulouse's; he took it back from Simon de Montfort's "
        "men after a short siege in 1216. The utricularii of the boatmen's "
        "guild rule the wharves under the cliff, the guildsmen guard the "
        "ferry to Tarascon jealously and charge dearly, and the Coenobium, "
        "unusually, keeps no one here, though rumours of the Drac's return "
        "may draw it.",
        charter="Noble lord",
        ruler="The Count of Toulouse",
        place=region,
    )
    town(
        "tarascon",
        "Tarascon",
        "The imperial town facing Beaucaire across the Rhone, with its own "
        "legend of an amphibious dragon, the Tarasque, whose lair lies in "
        "the hills outside.",
        charter="Noble lord",
        answers_to=count,
        place=region,
    )
    town(
        "marseille",
        "Marseille",
        "Massalia of the Phocaean Greeks, above the mouth of the Lacydon; "
        "Caesar slighted it for Arles after it backed Pompey, and Saracen "
        "raids wasted it, but with the Catalan counts' support it is again "
        "an important port. Pilgrim and crusader ships sail now and then, "
        "though Genoa holds most of the Levant trade. Hugh III of Baux holds "
        "it as viscount for the Emperor.",
        charter="Noble lord",
        ruler="Hugh III of Baux, viscount",
        answers_to=w["lord_of_baux"],
        place=region,
    )
    town(
        "orange",
        "Orange",
        "A town of the Baux princes with a strong commune that curbs them, "
        "its north gate Tiberius's arch, its great Roman theatre in ruins.",
        charter="Noble lord",
        answers_to=w["prince_of_orange"],
        place=region,
    )
    town(
        "aix",
        "Aix",
        "The Count of Provence's new capital, grown from the Celtic hill "
        "fort of Entremont and the Roman camp of Aquae Sextiae by its hot "
        "spring. Marius beat the Teutones nearby at Montagne Sainte-"
        "Victoire, and the Garagai Gorge lies close.",
        charter="Noble lord",
        answers_to=count,
        place=region,
    )
    town(
        "toulon",
        "Toulon",
        "A dyers' town under Mount Faron since Phoenician times, with murex "
        "on its beaches and kermes oaks on its hills; the Coenobium has a "
        "chapter house and a dye works here.",
        charter="Noble lord",
        answers_to=count,
        place=region,
    )
    town(
        "st_remy",
        "St-Rémy",
        "A medieval town under the Alpilles, with the ruins of Glanum just "
        "to the south, where the Tribunal meets in summer 1221.",
        charter="Noble lord",
        answers_to=count,
        place=region,
    )
    town(
        "vienne",
        "Vienne",
        "Capital of the Allobroges and a great Roman colony, now the seat "
        "of the prince-archbishop of northern Arelat, with its Roman stone "
        "bridge over the Rhone.",
        charter="Church",
        answers_to=w["archbishop_vienne"],
        place=p["lower_burgundy"],
    )


def _factions(provence: Provence, b: Builder) -> None:
    w = provence.world
    p = provence.places
    region = p["arelat"]
    w["utricularii"] = b.faction(
        "The Utricularii",
        faction="Gild",
        decides="A council",
        place=p["rhone"],
        wants="Control of every cargo and crossing on the Rhone",
        offers="Passage, barges, river news",
        summary="The boatmen of the Rhone, a powerful guild that controls the "
        "river's trade. Nominally based at Beaucaire, where they hold "
        "the wharves and the ferry, they are most numerous at Arles, "
        "where cargoes pass to sea-going ships. Many venerate "
        "St Bénezet at his chapel on Avignon's bridge, and they respect "
        "Nicodemus warily.",
        secrets=[
            titled(
                "Aucassin's agents",
                "Aucassin of Tytalus has agents among the utricularii at "
                "Beaucaire and Arles who spy and enforce for him and keep the "
                "ferry toll high.",
            ),
            titled(
                "The humiliated Redcap",
                "One of Aucassin's agents among the utricularii lately "
                "humiliated a Redcap of the Coenobium.",
            ),
        ],
    )
    w["masques"] = b.faction(
        "The Masques of the Coenobium",
        faction="Hedge coven",
        decides="Its leader",
        ruler="Lavandarius the Pralician, for the Coenobium",
        place=region,
        wants="Protection from the authorities and from other magi",
        offers="UnGifted agents and informants, vis harvesting and guarding, charms and amulets, sway over common folk",
        rules="The Hermetic magi remain the senior partners",
        summary=(
            "The witches, cunning folk, herbalists and faerie doctors "
            "of the southern coast and Alpine foothills, allied "
            "to the Coenobium for two centuries: it shelters them, and they "
            "watch over its mundane interests and let its magi keep within "
            "the letter of the Code. Some have been adopted as nominal "
            "Redcaps; Alazais's lover is one of them. The Coenobium suits a "
            "troupe wanting a non-Hermetic saga."
        ),
    )
    w["house_of_baux"] = b.faction(
        "The House of Baux",
        faction="Family",
        decides="Its leader",
        ruler="Hugh III of Baux",
        place=p["alpilles"],
        arms=Arms("Gules", charge="Star", charge_tincture="Argent"),
        wants="Advancement, lands and the favour of Emperor and Church",
        summary=paragraphs(
            "Lords of Baux, Orange and much of Provence's petty nobility, who "
            "claim descent from Balthazar and bear the Star of Bethlehem. "
            "The Gift appears strangely often among them, lending weight to "
            "their talk of magical blood. House Jerbiton has long recruited "
            "their less warlike sons, but these seldom have the Gentle Gift "
            "and tend to nepotism and self-advancement, and often to a "
            "coarse taste in beauty; several have gone over to Tytalus and "
            "a few warlike ones to Flambeau. Balthazarine magi have the "
            "Mythic Blood (Balthazarine) Virtue. Marcus d'Les Baux is the "
            "current Hermetic heir, with at least two younger Balthazarine "
            "magi of junior branches.",
        ),
    )
    w["corsairs"] = b.faction(
        "The Corsairs of the Hyères",
        faction="Brigands and mercenaries",
        decides="Its leader",
        ruler="Ahmad ibn Nasr (secretly)",
        place=p["hyeres"],
        wants="Plunder from the coast and its shipping",
        summary="Pirates and Saracen raiders who haunt the coves of Port-Cros "
        "and Porquerolles and moor at the Frioul islands off Marseille, "
        "raiding the towns of the coast and Catalan and Genoese ships.",
        secrets=[
            titled(
                "Whom the corsairs serve",
                "The Corsairs of the Hyères are the mundane arm of Fraxinetum "
                "Redux, led by Ahmad ibn Nasr.",
            ),
            titled(
                "The corsairs' quarry",
                "Ahmad ibn Nasr keeps the Corsairs of the Hyères off Hermetic "
                "shipping and away from the Coenobium's fleet with spies ashore.",
            ),
        ],
    )


# ------------------------------------------------------------- finishing


def finish(provence: Provence) -> None:
    """Tie Alazais to the Praeco once gascony.py has made her."""
    b = provence.b
    by_name = {c.name: c for c in b.saga.characters}
    dama = next((c for name, c in by_name.items() if name.startswith("Dama")), None)
    if dama is not None:
        b.link(
            provence.magi["alazais"],
            "characters",
            dama,
            "Made the Longevity Ritual of Alazais's lover",
        )


# --------------------------------------------------------------- stats

P = Profile
OCCITAN = "Occitan"
PROVENCE = "Area Lore: Provençal Tribunal"


#: Each magus the book sketches without a stat block, by character key.
PROFILES: dict[str, Profile] = {
    "alazais": P(
        gifted=False,
        strong="com pre int",
        native=OCCITAN,
        abilities={
            "Intrigue": (5, "the Coenobium"),
            "Leadership": (4, "Redcaps"),
            PROVENCE: (4, "covenants"),
            "Area Lore: Rhine Tribunal": 0,
            "Organization Lore: Order of Hermes": 3,
            "Etiquette": 3,
            "Guile": 3,
            "Ride": 2,
            "Code of Hermes": 2,
            "Dead Language: Latin": 3,
        },
        virtues=["Redcap", "Ambitious (Major)", "Dutybound"],
        reputations={"Chief Redcap of Provence (Hermetic)": 5},
    ),
    "nicodemus": P(
        strong="int sta per",
        weak="pre com",
        arts={"Aq": 8, "Re": 5, "Cr": 4, "Mu": 3, "Te": 3, "Vi": 2},
        abilities={
            "Magic Theory": (5, "Aquam"),
            "Craft: Engineer": (3, "waterworks"),
            "Area Lore: Rhone": 3,
        },
        virtues=[
            "Atlantean Magic",
            vf_art("Affinity with {art}", "aquam"),
            "Blatant Gift",
            "Reclusive",
            "Warped by Magic",
        ],
        native=OCCITAN,
    ),
    "marcus_baux": P(
        strong="pre com int",
        arts={"Re": 5, "Me": 5, "Cr": 3, "Im": 3, "In": 2},
        abilities={
            "Intrigue": (4, "Provençal nobility"),
            "Etiquette": (3, "nobles"),
            "Leadership": (2, "intimidation"),
            "Charm": 2,
            PROVENCE: 2,
        },
        virtues=[
            "Mythic Blood (Balthazarine)",
            ("Social Contacts", {"group": "the nobility of Provence"}),
            "Meddler (Major)",
            "Close Family Ties",
            "Proud (Minor)",
        ],
        native=OCCITAN,
    ),
    "pola": P(
        strong="com int pre",
        arts={"Me": 6, "Im": 4, "In": 4, "Cr": 3, "Re": 3},
        abilities={
            "Artes Liberales": (4, "rhetoric"),
            "Code of Hermes": (4, "advocacy"),
            "Etiquette": 3,
            "Intrigue": 3,
            "Teaching": 2,
            "Philosophiae": 2,
        },
        virtues=["Gorgiastic", "Good Teacher", "Proud (Minor)", "Driven (Minor)"],
        native=OCCITAN,
    ),
    "xiphos": P(
        strong="sta str int",
        weak="pre com",
        arts={"Te": 9, "Re": 5, "Pe": 5, "Mu": 4, "Cr": 3, "Co": 2},
        abilities={
            "Single Weapon": (4, "sword"),
            "Penetration": (4, "Terram"),
            "Code of Hermes": (3, "hoplites"),
            "Awareness": 2,
            "Hunt": 2,
        },
        virtues=[
            vf_art("Affinity with {art}", "terram"),
            vf_art("Puissant {art}", "terram"),
            ("Minor Magical Focus", {"focus": "metal and blades"}),
            "Wrathful (Minor)",
            "Infamous",
            "Dutybound",
            "Proud (Minor)",
        ],
        native="French",
    ),
    "lavandarius": P(
        strong="pre com per",
        arts={"He": 7, "Co": 5, "Cr": 4, "Vi": 3, "In": 3},
        abilities={
            "Herbalism": 3,
            "Folk Ken": (3, "hedge wizards"),
            "Charm": 3,
            "Magic Lore": (2, "hedge traditions"),
            "Etiquette": 2,
        },
        virtues=[
            "Herbalism",
            ("Social Contacts", {"group": "the hedge wizards of Provence"}),
            "Dutybound",
            "Driven (Minor)",
        ],
        native=OCCITAN,
    ),
    "argentius": P(
        gifted=False,
        strong="str sta dex",
        native="High German",
        abilities={
            "Single Weapon": (6, "sword"),
            "Ride": (3, "long journeys"),
            "Area Lore: Rhine Tribunal": 2,
            PROVENCE: 2,
            "Dead Language: Latin": 3,
            "Code of Hermes": 2,
            "Awareness": 3,
        },
        virtues=[
            "Redcap",
            "Heroes' Birthright",
            "Pious (Minor)",
            "Wrathful (Minor)",
            "Dark Secret",
        ],
    ),
    "bubulcus": P(
        strong="per sta dex",
        arts={"An": 7, "Mu": 6, "Co": 4, "Aq": 3, "In": 3},
        abilities={
            "Animal Ken": (3, "bulls"),
            "Survival": (3, "marshes"),
            "Area Lore: Camargue": 3,
        },
        virtues=["Animal Companion", "Small Frame"],
        native=OCCITAN,
    ),
    "elornis": P(
        strong="per int sta",
        arts={"In": 6, "Mu": 5, "An": 5, "Me": 4, "Im": 3},
        abilities={
            "Awareness": (3, "omens"),
            "Magic Lore": (2, "dreams"),
            "Survival": 2,
        },
        virtues=["Premonitions", "Visions", "Lame"],
        native="Arabic",
    ),
    "calais": P(
        strong="int sta pre",
        arts={"Au": 9, "Vi": 6, "Re": 5, "Cr": 4, "In": 3},
        abilities={
            "Magic Lore": (4, "spirits of the air"),
            "Penetration": (3, "Auram"),
            "Area Lore: Rhine Tribunal": 2,
        },
        virtues=[
            vf_art("Affinity with {art}", "auram"),
            "Driven (Minor)",
            "Overconfident (Minor)",
        ],
        native="High German",
    ),
    "aloysius": P(
        gifted=False,
        strong="int per dex",
        native=OCCITAN,
        abilities={
            "Philosophiae": (4, "alchemy"),
            "Craft: Dyer": (4, "purple"),
            "Bargain": 3,
            "Ride": 2,
            "Area Lore: Rhine Tribunal": 0,
            PROVENCE: 3,
            "Dead Language: Latin": 3,
        },
        virtues=["Redcap", "Dutybound", "Busybody", "Obsessed (Minor)"],
    ),
    "jorin": P(
        gifted=False,
        strong="sta str per",
        native=OCCITAN,
        abilities={
            "Profession: Boatman": (4, "the Rhone"),
            "Area Lore: Rhone": (4, "currents"),
            "Awareness": 3,
            "Ride": 1,
            "Area Lore: Rhine Tribunal": 0,
            PROVENCE: 2,
            "Dead Language: Latin": 2,
        },
        virtues=["Redcap", "Dutybound", "Pious (Minor)", "Busybody"],
    ),
    "ahmad": P(
        strong="pre sta int",
        arts={"Aq": 8, "Au": 6, "Re": 6, "Vi": 5, "Cr": 3},
        abilities={
            "Profession: Sailor": (4, "galleys"),
            "Magic Lore": (4, "jinn"),
            "Leadership": (3, "pirates"),
            "Area Lore: Provençal coast": 3,
        },
        virtues=[
            "Spirit Familiar",
            vf_art("Affinity with {art}", "aquam"),
            "Educated (Islamic)",
            "Dark Secret",
            "Reckless (Minor)",
        ],
        native="Arabic",
    ),
    "aucassin": P(
        strong="int com pre",
        arts={"Me": 6, "Im": 6, "Aq": 5, "Mu": 4, "Re": 4, "An": 3},
        abilities={
            "Guile": (4, "Rene of Dragonianum"),
            "Bargain": (3, "trade"),
            "Intrigue": (3, "Beaucaire's council"),
            "Magic Lore": (3, "dragons"),
        },
        virtues=["Mythic Blood", "Persona", "Dark Secret", "Driven (Major)"],
        native=OCCITAN,
    ),
    "romualdus": P(
        strong="int com per",
        arts={"Me": 4, "In": 4, "Co": 3, "He": 3},
        abilities={
            "Theology": (3, "contemplation"),
            "Etiquette": 2,
            "Artes Liberales": 2,
        },
        virtues=["Monastic Vows (Hermetic)", "Pious (Minor)"],
        native=OCCITAN,
    ),
    "fraxinus": P(
        strong="int per com",
        arts={"In": 6, "Me": 5, "Vi": 4, "Re": 3},
        abilities={"Code of Hermes": (4, "investigation"), "Magic Lore": 2},
        native=OCCITAN,
    ),
}


def stats(provence: Provence) -> None:
    """Generated stats for the magi of Arelat, none of whom has a printed
    stat block."""
    b = provence.b
    for key, profile in PROFILES.items():
        apply(b, provence.magi[key], profile)
