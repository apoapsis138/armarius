"""The Greater Alps' regions and places (ch09, and the covenant
chapters), as of 1220.

places["alps"] is the Tribunal's region, and inside it
places["western_alps"], ["bavaria"] and ["eastern_marches"], the book's
three parts. The covenants' sites: places["axis_magica"] (the Cave of
Twisting Shadows' nine-level regio, Magic 5 rising a level at a time,
inferred), ["mont_joux"] (Journeys End's Faerie 8 regio, with the
Arcadian gate on the peak), ["sinews_falls"] (Magic 7 at the
laboratories), ["tarragon_hill"], ["valnastium_valley"] (Magic 3) with
["saint_cyprian"] (Divine 6) inside it, and ["icy_north_hill"] (Magic 6).
The chapters (A9) are places of their covenants, named "... Chapter".

The places the book describes with an aura, a regio, vis, a creature or
a story: the Aare Gorge, Baden, Vindonissa, Botzberg, the Cirque
d'Annibal, the Domleschg grove, Pierres de Niton, Pfeffers' springs,
Heiligenblut, Lukerbad, Martigny, Mount Pilatus and the Temple of
Mercury, the Righi, Saint Beatus' Cave, the Saint Bernard and Saint
Gotthard passes, Saint Pierre's column, the Rosegarten, Val Fanes,
Vorarlberg's dragons, the Danube, Mittenwald, the Augsburg tunnels,
the Trivia statue at Eisenstadt, Dachstein's giants, the Dolomites'
lunar aura, Klagenfurt's lindworm skull, the lost Habach mine, Saint
Wolfgang, Schwyz, Staubbach Fall, Werfen's ice caves and the drowned
Wörthsee. Auras the book doesn't number follow DE p. 418 (a place of
worship Divine 4, a cathedral or major monastery's church 5, a town 3);
an unnumbered magic site is Magic 3, inferred (A20 as amended)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import paragraphs
from .state import KNOWN_ORDER, KNOWN_TRIBUNAL

if TYPE_CHECKING:
    from ...models import Neighbour
    from .state import Alps


def _place(alps: Alps, key: str, name: str, region: str, **kw: Any) -> Neighbour:
    inside = alps.places.get(region)
    place = alps.b.place(name, inside=inside, **kw)
    alps.places[key] = place
    return place


def build(alps: Alps) -> None:
    _regions(alps)
    _covenant_sites(alps)
    _western(alps)
    _bavaria(alps)
    _eastern(alps)


# -- the regions --


def _regions(alps: Alps) -> None:
    b = alps.b
    alps.places["alps"] = alps_region = b.place(
        "The Greater Alps",
        known="In the Order",
        summary=paragraphs(
            "Europe's largest labyrinth: ranges of mountains cut by valleys "
            "that join into passes, the roads of settlement, war and trade. "
            "Those who hold the passes hold the land. The roads are mostly "
            "too steep for carts, so goods go by horse and mule, or by "
            "water: the lakes are crossroads, and the lake towns are some of "
            "the oldest and richest in the region, though the rivers run to "
            "rapids where they fall steeply. Wheat grows in the lower and "
            "warmer passes, rye in most places, and most mountain villages "
            "have as many mouths as their land can feed.",
            "Nobles here build castles and towns in a frenzy, following the "
            "now-extinct Zähringers; the book puts some of the blame on the "
            "folly spirits, which lay their eggs in new buildings and breed "
            "paranoia in the castles they inhabit, so that many Alpine "
            "castles hold weak magic auras that suit magi. Most great lords "
            "are absentees, and lesser lords style themselves counts. "
            "Towns and lords band together in peace alliances "
            "(landfriedensbund).",
        ),
    )
    for key, name, summary in (
        (
            "western_alps",
            "The Western Alps",
            "From Savoy and the Jura to Lake Constance and Rhaetia: the "
            "Oberland plateau between the Jura and the Alps is the "
            "breadbasket, the most densely peopled land. The Little and "
            "Great Saint Bernard have been the great passes until now; "
            "around 1220 the Saint Gotthard opens a quicker road from the "
            "Italian trading cities to the north, and wealth begins to "
            "shift to the towns on the new route. Saint Gallen's lowland "
            "exports wheat, and the southern foothills grow Mediterranean "
            "crops. The Zähringers died out in 1217 with Berthold V, and "
            "their lands passed to the Kyburgs; Zurich and Lucerne are "
            "imperial cities, Berne the Emperor's since 1218.",
        ),
        (
            "bavaria",
            "Bavaria",
            "A broad plateau ringed and pierced by mountains, divided north "
            "and south by the Danube, whose valley and tributaries carry "
            "its trade and hold most of its people. Its wealth is trade, "
            "timber and farming; apart from Augsburg it has little mineral "
            "wealth, and its wilder parts are heavily forested. The ducal "
            "seat is Regensburg. The Wittelsbachs have ruled it since 1180 "
            "and gained the Rhenish Palatinate in 1214.",
        ),
        (
            "eastern_marches",
            "The Eastern Marches",
            "Austria, Styria, Carinthia and Salzburg: here the Alps grow "
            "harsher and split into three parallel ranges, east to west, "
            "each broken by passes, so the east is mountainous but easy to "
            "cross. The people live mostly in the eastern foothills, where "
            "the soil is richer, before the plains at the Tribunal's edge. "
            "The Brenner, in use since Roman times, is the great pass. "
            "The Babenbergs hold Austria and Styria; the duke's seat is "
            "Vienna, and the archbishop of Salzburg opposes him.",
        ),
    ):
        alps.places[key] = b.place(
            name, inside=alps_region, summary=summary, known="In the Order"
        )


# -- the covenants' sites --


def _covenant_sites(alps: Alps) -> None:
    b = alps.b
    _place(
        alps,
        "axis_magica",
        "The Axis Magica",
        "eastern_marches",
        aura=0,
        levels=[
            b.level(
                f"The {ordinal} level",
                4 + number,
                notes=note,
            )
            for number, (ordinal, note) in enumerate(
                (
                    (
                        "first",
                        "Servants, stores, and the central cave as a mess hall; no visitor goes higher unless asked to a ritual.",
                    ),
                    ("second", ""),
                    ("third", ""),
                    ("fourth", ""),
                    ("fifth", ""),
                    ("sixth", "The library's cave."),
                    ("seventh", ""),
                    (
                        "eighth",
                        "Where Sanctuary of Ice has a Primus slain and the past Primi summoned; Houses of Hermes: Mystery Cults moves the slaying to the ninth.",
                    ),
                    (
                        "ninth",
                        "The Hypostasis's threshold: no laboratory can work here; the Prima is slain and her successor chosen here (HoH:MC p. 55).",
                    ),
                ),
                start=1,
            )
        ],
        summary=paragraphs(
            "A mountainside honeycombed with looping tunnels, repeated on "
            "nine levels of regio, around a natural cave that runs through "
            "every level and opens into the Magic realm. House Criamon "
            "calls it the Axis Magica, the pivot about which the world's "
            "tides of magic wash, its world's navel and stairway to a finer "
            "existence. On the mundane level there is no sign of anyone "
            "living there. Things that turn up are mostly minor spirits "
            "rather than people, and the regio can be assailed from every "
            "direction from the Magic realm. Its highest level holds "
            "mind-traps, enchanted tunnels that catch airy spirits and "
            "abstractions.",
            "Magic items kept long in the upper levels bleed their power "
            "into the Axis, so the covenant has none and no laboratory "
            "there can be bettered beyond +1; Enigmatic Wisdom rolls in the "
            "regio gain +2. The book numbers no level's aura: Magic 5 on "
            "the first, rising one a level to 13 on the ninth, is inferred "
            "(A10).",
        ),
        **KNOWN_ORDER,
    )
    _place(
        alps,
        "icy_north_hill",
        "The Motherhouse of the Icy North",
        "bavaria",
        aura=6,
        summary=paragraphs(
            "Once the site of the covenant of Highest Aspiration, destroyed "
            "in the Sundering of Tremere. Its main building is a broad cone, "
            "tilted slightly north, with a stair winding round it to the "
            "top; it is older than its present use. A crenellated wall and "
            "watchtowers enclose the magi's and specialists' quarters, and "
            "a second wall the fairground and two great barracks used only "
            "in summer. Moderate slopes on every side, a road to the front "
            "gate, and about a visitor a day. A small town, which governs "
            "itself by a show of men's hands, rings the covenant. Magic "
            "aura 6.",
        ),
        **KNOWN_ORDER,
    )
    _place(
        alps,
        "mont_joux",
        "Mont Joux",
        "western_alps",
        realm="Faerie",
        levels=[
            b.level(
                "The Covenant Where Journeys End",
                8,
                "Faerie",
                enter="A gateway hidden by illusion under an icy lake on the mountain.",
                notes="Bitterly cold, from below freezing at the summit to "
                "sharply cool at its edges. On the peak is a gate to "
                "Arcadia that lets travellers go far in minutes of mortal "
                "time and has no real guardian. The stat block gives "
                "Faerie 8; the text says 6 (A11).",
            )
        ],
        summary=paragraphs(
            "The highest peak in Europe, which later ages will call Mont "
            "Blanc: the tallest of a ridge of three. The Romans named it "
            "Mons Iovis for Jupiter Pennius, Peonn, the Celtic god of Alpine "
            "storms. No one has climbed it, and the priests say it is "
            "unlucky to try. In the eleventh century the blessed Bernard of "
            'Menthon chained the "demon" worshipped as Jupiter on the '
            "second peak, or drove it off a cliff, and that peak is now "
            "Mont Maudit, the Accursed Mountain.",
            "Rock quartz, which needs great cold, and fluorite, which needs "
            "great heat, grow embedded in each other here, a contradiction "
            "of the natural order; the book gives them shape and material "
            "bonuses for enchanting, which stay in the book.",
        ),
        **KNOWN_ORDER,
    )
    _place(
        alps,
        "sinews_falls",
        "The Falls of Sinews of Knowledge",
        "bavaria",
        aura=7,
        summary=paragraphs(
            "A minor waterfall on a tributary of the Danube in the Bavarian "
            "Alps, behind which runs a mostly artificial cave system whose "
            "plan, skilled vivisectionists say, is disturbingly like the "
            "blood vessels about a liver. A misplaced Great Bear is carved "
            "on the tunnel ceilings and enchanted to give light; no one knows "
            "its first purpose. An overshot wheel turns invisibly in the "
            "falls. A village lies at their foot, where merchants come in "
            "groups to trade. Magic 7 on the level of the magi's "
            "laboratories; deeper levels are higher and dangerously "
            "unstable.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _place(
        alps,
        "tarragon_hill",
        "Tarragon Vale's Hill",
        "western_alps",
        aura=3,
        summary=paragraphs(
            "A misty hilltop in Unterwalden. Tarragon Vale's long, barn-like "
            "stone hall stands three storeys high inside, mostly open, with "
            "rooms round the eaves; its many basements are sealed by the "
            "Quaesitores' wards, and its wooden outbuildings have rotted to "
            "compost. The Quaesitores keep up its Aegis and a Shrouded Glen. "
            "The book gives no aura; Magic 3 is inferred.",
        ),
        **KNOWN_TRIBUNAL,
    )
    valley = _place(
        alps,
        "valnastium_valley",
        "Valnastium",
        "eastern_marches",
        aura=3,
        summary=paragraphs(
            "A valley of the Dolomites, the family land of the Founder "
            "Jerbiton, whose ancestor was a Roman soldier settled here. Its "
            "entrance is hidden, its weather ruled by magic, its mouth "
            "barred by fortifications from the Schism War, and mountains "
            "overlook it on three sides, the river running through on the "
            "fourth. Almost a thousand people live in its villages and in "
            "the town round Jerbiton's villa, speaking a Rhaetian of their "
            "own; they call themselves the Ierbii. Its library is a true "
            "Temple of the Muses moved stone by stone from Greece, which "
            "the Founder brought for its aura.",
            "Magic 3 over most of it; the church of Saint Cyprian has kept "
            "it from rising further, and much of the valley is Divine 2, "
            "rising to 6 at the church (Houses of Hermes: Societates p. 53).",
        ),
        **KNOWN_ORDER,
    )
    alps.places["saint_cyprian"] = alps.b.place(
        "The Church of Saint Cyprian",
        inside=valley,
        realm="Divine",
        aura=6,
        summary=paragraphs(
            "The valley's main church, raised with Hermetic magic and "
            "dedicated to Saint Cyprian, the magus who became a saint, "
            "though visitors take it for Cyprian of Carthage. Jerbiton knew "
            "closed communities draw diabolists, and his heirs have kept "
            "the sacraments regular here. Divine 6.",
        ),
        **KNOWN_TRIBUNAL,
    )


# -- the Western Alps --


def _western(alps: Alps) -> None:
    for key, name, kw in WESTERN:
        _place(alps, key, name, "western_alps", **kw)


WESTERN: tuple[tuple[str, str, dict[str, Any]], ...] = (
    (
        "aare_gorge",
        "The Aare Gorge",
        {
            "summary": "A deep crevasse near Meiringen, the lair of the "
            "Tatzelwurmli, a monstrous limbless land dragon, a kind of "
            "well worm. No covenant has claimed its vis, since none has "
            "shown it can harvest from the worm's lair.",
        },
    ),
    (
        "baden",
        "Baden",
        {
            "realm": "Divine",
            "aura": 3,
            "summary": "A town whose sulphur springs have been visited for "
            "their healing since Roman times: good for joints, heart and "
            "lungs, baldness and the heartsickness of failed love. Taking "
            "the cure, a month at a spa famed for the malady, lets a minor "
            "affliction be ignored for three years, though it heals "
            "nothing. Divine 3 (a town, DE p. 418).",
        },
    ),
    (
        "vindonissa",
        "Vindonissa",
        {
            "summary": "The ruins of the Roman fortress between Baden and "
            "Basel that guarded Helvetia from the Germans across the Rhine. "
            "Inside its fallen walls is Hapsburg castle, built by Bishop "
            "Werner of Strasbourg in the eleventh century, where a lesser "
            "scion of the Hapsburgs lives and his ancestors are buried.",
        },
    ),
    (
        "botzberg",
        "Botzberg",
        {
            "summary": paragraphs(
                "Mons Vocetius, the field of the battle of AD 69 that ended "
                "Helvetian freedom from Rome. It is not haunted as such, "
                "but its remains can raise the ghosts of the fallen, who "
                "say priests, sounding like primitive magi, died in the "
                "battle; magi dig here now and then for those wizards' "
                "skulls.",
                "Staying long, and sleeping there above all, rouses the "
                "field's spirits to fight the battle again, with any magi "
                "cast as the slain Roman priests. A survivor would know "
                "where his skull lies; every party that has tried has died "
                "and been dumped at the field's edge.",
            ),
        },
    ),
    (
        "cirque_d_annibal",
        "The Cirque d'Annibal",
        {
            "summary": "A field near the Little Saint Bernard with a vast "
            "circle of ten rough monoliths, where Hannibal waited for his "
            "stragglers and held his council of war. Magi call it "
            "ill-omened, full perhaps of the spirits of those who died on "
            "the march from Carthage, angered by Rome's heirs; the "
            "wilder tales have its shadows fuse into a demon, part bronze, "
            "part man and mostly elephant.",
        },
    ),
    (
        "domleschg",
        "The Domleschg",
        {
            "summary": paragraphs(
                "A valley of twenty-one castles in every state of use and "
                "ruin. Legend says fifteen druids lived here in the Order's "
                "early years and fought Diedne and her followers, believing "
                "a woman Archdruid would cut them off from their "
                "mysteries.",
                "The victors raised a grove of oaks over the battlefield, "
                "each grown by magic from an acorn planted in a dead man's "
                "mouth. The motherhouse of the Icy North claims it as a "
                "source of Rego vis.",
            ),
        },
    ),
    (
        "pierres_de_niton",
        "The Pierres de Niton",
        {
            "summary": "Two large flat rocks in Lake Léman south-east of "
            "Geneva. Hermetic tales say House Diedne made human sacrifices "
            "on them, perhaps a garbled memory of Romans sacrificing to "
            "Neptune; the giant Gargantua is said to have thrown the larger "
            "into the lake, and to have dug the lake itself.",
        },
    ),
    (
        "pfeffers",
        "Pfeffers",
        {
            "realm": "Divine",
            "aura": 5,
            "summary": "A Benedictine monastery founded in 713, by hot "
            "springs set in a crevice, into which patients are lowered on "
            "long ropes and left for a week at a time, food let down to "
            "them. Divine 5 at its church (a major monastery, DE p. 418).",
        },
    ),
    (
        "heiligenblut",
        "Heiligenblut",
        {
            "realm": "Divine",
            "aura": 6,
            "summary": "A village named for the vial of Christ's blood in "
            "its church, brought by a Byzantine general who died of "
            "exposure here on campaign. A Tremere was Marched two centuries "
            "ago for trying to steal it. The book gives no aura; Divine 6 "
            "for the chapel of a most important relic (DE p. 418) is "
            "inferred.",
        },
    ),
    (
        "lukerbad",
        "Lukerbad",
        {
            "summary": "The hottest springs in Europe, at Leuk, where a "
            "cure takes three weeks of ever longer bathing. Sabina, a "
            "powerful Flambeau maga, lived here last century and vanished; "
            "her laboratory has never been found, and some suspect her of "
            "unsavoury theurgy, living so near sulphurous wells.",
        },
    ),
    (
        "martigny",
        "Martigny",
        {
            "summary": "Roman since AD 15, with a festival kept since then "
            "in which cows fight to be Queen of the Herd. Some magi think it "
            "once summoned a protective faerie spirit into the Queen to "
            "watch the herds, and that it may be tied to the Mithraic "
            "religion; the Legion of Mithras's Alpine meeting place, in sagas "
            "that use it, is here.",
        },
    ),
    (
        "pilatus",
        "Mount Pilatus",
        {
            "aura": 3,
            "summary": paragraphs(
                "A centre of Alpine myth, so crowded with strange "
                "inhabitants that some magi think a cluster of regiones "
                "opens on its slopes at random: lair of dragons, home of "
                "the barbegazi, eyrie of a witch and haunt of a sinner "
                "cursed by God. However well it is surveyed, there is "
                "always something new on it, in it or terrorising the "
                "villages below; it may open into Arcadia, the Magic realm "
                "or both. Locals avoid it and punish anyone who climbs it, "
                "and magi who settled there would know no peace.",
                "Pontius Pilate's ghost gives it its name. Climbers anger "
                "him, and he sends weather that ruins Lucerne's crops and "
                "closes the lake; even priests may not climb, for few "
                "think they can exorcise a spirit God is justly punishing. "
                "His body lies incorrupt in an icy pool, and once a year he "
                "comes down to wash his hands in the lake, which turns to "
                "blood. Harvesting vis from him is forbidden by the Code. "
                "The book gives no aura; Magic 3 is inferred.",
            ),
        },
    ),
    (
        "temple_of_mercury",
        "The Temple of Mercury",
        {
            "aura": 3,
            "summary": "A ruined Roman temple near Mount Pilatus that "
            "Hermetic historians try to tie to the three Founders whose "
            "domus magnae border the Alps. The Tribunal met here before the "
            "Midsummer Fair drew it to the Icy North. Devices that make "
            "illusions still hide it; no magi live there, and it would make "
            "an excellent chapter. The book gives no aura; Magic 3 is "
            "inferred.",
        },
    ),
    (
        "righi",
        "The Righi",
        {
            "summary": "A mountain between Schwyz and Lucerne that peasants "
            "call the home of giants. Vast shadows with rainbow edges are "
            "cast on its fog: at best, magi know, the ghosts of giants. The "
            "death of its last giant set the Tribunal on limiting its own "
            "numbers. Journeys End owns it in the Hermetic sense, and hopes "
            "giants will settle it again.",
        },
    ),
    (
        "st_beatus_cave",
        "Saint Beatus' Cave",
        {
            "summary": "Caves in the Jungfrau country lived in by ancient "
            "people, said to have been the retreat of a British saint who "
            "converted the region and drove out the cave's last tenant, a "
            "dragon.",
        },
    ),
    (
        "great_st_bernard",
        "The Hospice of Saint Bernard",
        {
            "realm": "Divine",
            "aura": 5,
            "summary": paragraphs(
                "The Benedictine hospice on the Great Saint Bernard pass, "
                "founded in 962 by Bernard of Menthon, who led it for forty "
                "years and was made a saint; he founded a second house on "
                "the Little Saint Bernard. Saracens razed it late in the "
                "eleventh century; refounded in 1123, it took his name. "
                "Before it stood a temple of the Celtic mountain god, then "
                "of Roman Jupiter, and the monks gather the relics of it "
                "that surface. Its monks rescue lost travellers, with the "
                "great dogs bred from Roman war hounds, and their presence "
                "guards the passes from the blizzard demons.",
                "The Code protects it. House Jerbiton helps it name the "
                "dead; House Mercere's merchant house funds it at times, and "
                "its merchants find it an essential waypoint. Divine 5 (a "
                "major monastery, DE p. 418).",
            ),
        },
    ),
    (
        "st_gotthard",
        "The Saint Gotthard Pass",
        {
            "summary": "Opened to travellers on foot around 1220, the most "
            "direct road from Basel and Zurich to Italy, and being made "
            "ready for pack animals; it will drain trade from the other "
            "passes. Its Devil's Bridge was built by the Devil, locals say, "
            "and they show the boulders he threw when cheated of his price; "
            "the abbot of Einsiedeln says he paid for it. Redcaps used the "
            "pass long before mundanes did.",
        },
    ),
    (
        "saint_pierre",
        "Saint Pierre",
        {
            "summary": "A tiny village with a column Constantine raised in "
            "339 at the top of the Saint Bernard pass, in place of a statue "
            "of Jupiter Penninus he had destroyed.",
        },
    ),
    (
        "rosegarten",
        "The Rosegarten",
        {
            "realm": "Faerie",
            "aura": 3,
            "summary": "The still-open regio of Laurens, the dwarf king of "
            "a land of roses in the Catinaccio of the Val Gardena. He stole "
            "a faerie princess, was followed home by her kin along the path "
            "of roses, and was taken prisoner; escaping, he cursed the roses "
            "to look like stone by day and by night. At dusk, when the sun "
            "lies low, they show, wreathing the mountains red. The book "
            "gives no aura; Faerie 3 is inferred.",
        },
    ),
    (
        "val_fanes",
        "Val Fanes",
        {
            "realm": "Faerie",
            "aura": 3,
            "summary": "A valley where the Fanes, a kind of faerie, once "
            "ruled a mighty kingdom before humans conquered them in "
            "ancient times; they hide, awaiting their revenge and the "
            "rebuilding of their palaces. Chapels on their places of power "
            "have bottled many of them up, leaving other sites unguarded "
            "and harvestable, so Valnastium favours priests. Andru's war on "
            "one of their kings was pardoned in 1194, and gossip says he "
            "took a summer prince's crown. The book gives no aura; Faerie 3 "
            "is inferred.",
        },
    ),
    (
        "vorarlberg",
        "Vorarlberg",
        {
            "realm": "Faerie",
            "aura": 3,
            "summary": paragraphs(
                "A small land on the upper Rhine's flood plain round "
                "Bregenz, the old Roman fortress, notable for its isolated "
                'villages and high faerie auras; Venedigers, "men from '
                'Venice", are a kind of faerie here.',
                "Its dragons belong to storms and avalanches, not fire, "
                "and wandering scholars deal with them: a beggar wrecked a "
                "farm at Bezau with a dragon on a red rope; Lake Sonderdach's "
                "dragon warns swimmers off; a dragon guards a scholar's "
                "hoard in a cave of the Vale Galina; a Venetian rode one "
                "away from Sontag; and at Brand a scholar's storm buried "
                "another under the rubble called the Grave of the Dragon. "
                "The book gives no aura; Faerie 3 is inferred.",
            ),
        },
    ),
)


# -- Bavaria --


def _bavaria(alps: Alps) -> None:
    for key, name, kw in BAVARIA:
        _place(alps, key, name, "bavaria", **kw)


BAVARIA: tuple[tuple[str, str, dict[str, Any]], ...] = (
    (
        "danube",
        "The Danube",
        {
            "summary": paragraphs(
                "Rising in the Black Forest and fed by the Alps, it flows "
                "south-east past Regensburg and Vienna and out of the "
                "Tribunal toward the Black Sea, navigable nearly all its "
                "length though it floods, runs low and freezes in parts. "
                "Goods are still portaged to the Main as the Romans did; "
                "Mercere magi like Charlemagne's idea of a canal, but see no "
                "way to help it without breaching the Code. Sinews of "
                "Knowledge lies behind a cataract that feeds it.",
                "It is Danu's river: the goddess of a web of rivers across "
                "Europe, faded with the old powers, whose nymphs keep "
                "jewelled regiones in her waters and whose springs open on "
                "ways to Arcadia and its great River. She is beyond "
                "statistics and no longer deals with mortals.",
            ),
        },
    ),
    (
        "mittenwald",
        "Mittenwald",
        {
            "summary": "Home of a master carver of the finest instruments. "
            "When he dies, another of the village's instrument makers "
            "becomes the master within a day, inheriting even some of his "
            "memories, his debts and unfinished commissions: atavism, one of "
            "the oldest forms of magic. His technique itself is quite "
            "mundane.",
        },
    ),
    (
        "augsburg_tunnels",
        "The Augsburg Tunnels",
        {
            "summary": "Secret tunnels under Augsburg joining two churches "
            "on either side of the city, whose walls mix Hermetic symbols "
            "with sacred images: the home, the Quaesitores and Jerbiton and "
            "Criamon magi think, of a religious magus whose name and fate "
            "are unknown. No covenant claims them; the city's Dominion has "
            "put off would-be chapters.",
        },
    ),
)


# -- the Eastern Marches --


def _eastern(alps: Alps) -> None:
    for key, name, kw in EASTERN:
        _place(alps, key, name, "eastern_marches", **kw)


EASTERN: tuple[tuple[str, str, dict[str, Any]], ...] = (
    (
        "trivia_statue",
        "The Statue of Trivia",
        {
            "aura": 3,
            "summary": "A small regio west of Eisenstadt, where the "
            "Burgenland marks the border with Transylvania, holding a "
            "marble statue of Trivia, the threefold goddess of the roads. "
            "The Redcaps use it to exchange messages. The book gives no "
            "aura; Magic 3 is inferred.",
        },
    ),
    (
        "dachstein",
        "Dachstein",
        {
            "realm": "Magic",
            "levels": [
                {
                    "name": "The giants' regio",
                    "realm": "Magic",
                    "aura": 3,
                    "see": "",
                    "enter": "Through the ice caves near Dachstein.",
                    "notes": "The book gives no aura; Magic 3 is inferred.",
                }
            ],
            "summary": paragraphs(
                "Ice caves near Dachstein lead into a regio where a "
                "community of giants lives: a dull majority ruled by a "
                "small caste of devious magic-weavers who sometimes play "
                "simple. They forage in Arcadia, but their gate opens on "
                "the Summer lands; they say they are a raiding party driven "
                "out by Summer faeries, with an ancestral home on the edge "
                "of Arcadian Winter where giants are larger and wiser.",
                "They are allies of Journeys End and trade with it. They "
                "value iron, which they use to poison their enemies, and "
                "want above all the Banner of Winter, which would let them "
                "stay long in the hot Summer lands.",
            ),
        },
    ),
    (
        "dolomites",
        "The Dolomites",
        {
            "realm": "Faerie",
            "aura": 1,
            "summary": paragraphs(
                "Pale limestone mountains in the Tribunal's south-east, "
                "worn into stark shapes like single great rocks, that blaze "
                "at dawn and dusk and glow white by day. Folk say the "
                "Salvani gnomes wove moonlight into them so that a prince's "
                "bride from the Moon would not pine.",
                "Most nights a faerie aura rises in their wild places by "
                "the Moon: 1, 2 at the full, none when there is no Moon; "
                "where a Bright faerie aura is already, it adds to it. "
                "Coral is found in the rocks of the highest peaks. "
                "Valnastium and Journeys End each suspect the other of "
                "keeping the way to the Lunar Faerie realm to itself.",
            ),
        },
    ),
    (
        "klagenfurt",
        "Klagenfurt",
        {
            "summary": "A Carinthian town refounded in 1161, where the "
            "villagers could not drain the marshes for the lindworm, a "
            "dragon fond of virgins, until Herakles passed by and killed "
            "it. They keep its skull still.",
        },
    ),
    (
        "habach",
        "The Habach Emerald Mine",
        {
            "status": "Rumoured",
            "summary": "Europe's only real source of emeralds, worked by the "
            "Romans in the Habach valley near Salzburg; no one knows where "
            "it is. Some say faeries took the stones, others that an "
            "ancient magus hid it and his defences may yet wear away.",
        },
    ),
    (
        "st_wolfgang",
        "Saint Wolfgang",
        {
            "realm": "Divine",
            "aura": 4,
            "summary": "A church in the Abersee valley, where in 976 the "
            "priest Wolfgang threw his axe and built where it fell, then "
            "beat the Devil so that he could never harm it. It is a "
            "pilgrimage site, and the demon-haunted retire here: one of its "
            "monks may be a mighty magus hiding from the servants of demons "
            "he banished. Divine 4 (a place of worship, DE p. 418).",
        },
    ),
    (
        "schwyz",
        "Schwyz",
        {
            "summary": "Just before 1200 the monks of Einsiedeln were given "
            "the lands round Schwyz as empty waste. The Schwytzers, who "
            "disagreed, fell on the abbey's tenants and have since joined "
            "the coalitions against the Emperor; Frederick II, now Emperor, "
            "is their ally. That a whole people could be overlooked "
            "amazes even magi, and many tie their sudden appearance to the "
            "Vanishing Away at nearby Tarragon Vale.",
        },
    ),
    (
        "staubbach",
        "Staubbach Fall",
        {
            "aura": 3,
            "summary": "The Dust Fall near Lauterbrunnen, so high and thin "
            "that its water turns to mist before it lands, like a veil in "
            "the wind; in winter a vast upturned icicle rises halfway up "
            "it. It is a public vis source of Imaginem in the Code, whose "
            "harvesting right is traded among the Tribunal's magi as a "
            "costly barter good: Paxon of Verditius holds it now, finds it "
            "far from home, and would sell for an intriguing offer. The book "
            "gives neither its aura nor its yield; Magic 3 is inferred.",
        },
    ),
    (
        "werfen",
        "The Werfen Ice Caves",
        {
            "aura": 4,
            "summary": paragraphs(
                "A maze of ice caves near Werfen, reached only on foot over "
                "hard ground, with a magic aura of 4 and a fountain that "
                "pours out 30 pawns of Imaginem vis a year. The Code "
                "mentions them more than once; no covenant can claim the "
                "source, as none can show it can use it steadily. It lies "
                "near Salzburg and the trade road from the Brenner, and "
                "Werfen village could supply covenfolk.",
                "Two chapters have been tried here. One failed from bad "
                "planning; the members of the other were found dead without "
                "a wound, some having cut syllables of gibberish into the "
                "ice. The common guess is a lucifugus; others think of a "
                "delirium-bringing spirit of disease or a monster that "
                "sleeps between meals, like an ice wyrm.",
            ),
        },
    ),
    (
        "worthsee",
        "The Wörthsee",
        {
            "summary": "A Carinthian lake over a drowned town of sinners: a "
            "tiny man with a tiny keg, an agent of God's wrath, warned the "
            "inn to mend its ways, was mocked, and pulled the bung. Sailors "
            "at night still hear the church bells under the water.",
        },
    ),
)
