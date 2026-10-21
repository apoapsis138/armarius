"""The saga's stories, in paraphrase: each a threat whose stages lay out
how it unfolds if the troupe ignores, stops or turns it.

Under way in 1220: the Dragon War, the book's great saga (chapter 8),
from the spark that breaks the Pax Draconis through the war's
escalating situations to a climax the troupe brings about. The book
offers several sparks and several endings, so the first stage lists the
sparks and the last the endings, each paired with its cause.

Dormant until the storyguide begins them: the Teutonic Knights'
expulsion (dated stages in 1222 and 1225), the Mongols, the Bosnian
crusade, the Valley of the Thracian Kings, the return of Zalmoxis, the
Székely taltós, Poena's succession and the papal legate. Where the book
says what history does next, the stages follow it and are marked as
what happens if history holds.

`finish` puts each story inside the place where it plays out, ties it
to the oppida, magi, creatures and places the other parts made (found
by key or by name), puts the faction behind it as the one it answers
to, adds chapter 10's horror seeds to the places and oppida they use,
and closes the Tribunal's summary with a word on the stories."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...threats import DORMANT
from ..builder import Builder, paragraphs

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Transylvania

S = Builder.stage
DATED = "Fixed dates"
HISTORY = "If history holds, "


def build(transylvania: Transylvania) -> None:
    _dragon_war(transylvania)
    _teutonic(transylvania)
    _mongols(transylvania)
    _bosnian_crusade(transylvania)
    _thracian_valley(transylvania)
    _zalmoxis(transylvania)
    _taltos(transylvania)
    _succession(transylvania)
    _legate(transylvania)


def _dormant(threat: Neighbour) -> Neighbour:
    """Mark a threat as not yet begun: More, Begin This Story starts it."""
    threat.details[DORMANT] = True
    return threat


# -- the main saga --


def _dragon_war(transylvania: Transylvania) -> None:
    b = transylvania.b
    transylvania.world["threat_dragon_war"] = b.threat(
        "The Dragon War",
        summary=paragraphs(
            "Hundreds of dragons, perhaps thousands, lair in the "
            "Tribunal's mountains, gorges, lakes and forests. They are "
            "of two kinds that hate each other: the aždaje, Infernal "
            "beasts that plunder for the joy of harm and rank "
            "themselves by force, and the zmajevi, Magic dragons that "
            "covet wives and gold as much but hardly notice the misery "
            "they cause, and rank themselves by remembered favours and "
            "slights. Intellego Vim tells the two apart, one realm at "
            "a time.",
            "Since the second century they have been held to the Pax "
            "Draconis, the treaty of Fetillusclaviceps, a Roman dragon "
            "who beat the twelve-headed zmaj Abur-ciocîrlie in a duel "
            "and brought the aždaje to heel by helping Slomljenakrila "
            "kill the oath-breaking Britvazub. Under its terms dragons "
            "do not league against one another, keep their quarrels "
            "local, defer to the stronger and leave men alone unless "
            "attacked; a wife may be taken only with a superior's "
            "leave, and a dragon that takes one without it is outlawed "
            "and may be hunted for its hoard. The peace holds only "
            "while its keeper is feared, and Fetillusclaviceps has not "
            "been seen for fifty years. Early in the ninth century "
            "Tremere himself put down a rising of raiders while wearing "
            "the Roman dragon's shape, and some Tremere wonder whether "
            "later sightings were their own sodales doing the same.",
            "If the peace fails, every dragon settles old scores and "
            "seizes what it can, raiding towns for gold and slaves. "
            "Dragons of one kind may band together, rarely with the "
            "other. House Tremere, the Order's self-appointed soldiers, "
            "would see in such a war both a catastrophe and its chance "
            "to prove itself to the whole Order.",
            "A saga frame, not a single story: choose the spark that "
            "suits the troupe (best of all one the player characters "
            "struck themselves, perhaps with charges laid against them "
            "for it), escalate through situations that come ever "
            "closer to what they hold dear, and let them make the "
            "ending. A peasant legend that a devil's wizard from the "
            "Scholomance rides an aždaja and makes the storms can be "
            "woven in: a storm wizard, a shapechanged magus, or a "
            "magus corrupted to lead the Infernal dragons.",
        ),
        secrets=paragraphs(
            "Who keeps the peace: one ending the book offers is that a "
            "renowned Flambeau hunter tracked Fetillusclaviceps to its "
            "lair and killed it about a century ago, then, seeing that "
            "the peace died with it, has played the Roman dragon ever "
            "since rather than confess. If the troupe uncovers this, "
            "continuing the pretence is probably a breach of the Code, "
            "since it means dealing with Infernal beasts, and House "
            "Tremere's good name rides on whether a substitute keeper "
            "can be found.",
            "Another: the stone column where Leontine of Old Histria "
            "argues ethics with an ancient zmaj was taken by Dominic "
            "of Tytalus, aedile of Coeris, perhaps to test his protégé "
            "and perhaps to start the war on purpose. Dominic then "
            "vanishes, dead or in hiding, and the column may lie "
            "somewhere within Coeris's defences.",
            "Sebastian, the ageless caretaker of the Scholomance, may "
            "be the seven-headed zmaj king Aževastjepan, who rules the "
            "Carpathian dragons and has banished aždaje from his realm.",
        ),
        antagonist="The dragons of the Tribunal, once the Pax Draconis fails",
        realm="Magic",
        stages=[
            S(
                "The spark",
                at=1,
                clues=(
                    "Choose one, or let the player characters strike it. "
                    "Veles wakes as the Slavs return to Perun, and drives "
                    "his dragons to war (zmajevi if he is of Magic, aždaje "
                    "if he is a demon). Abur-ciocîrlie leaves his castle and "
                    "persuades other zmajevi that the magi serve the Roman "
                    "dragon, perhaps killing a zmaj and leaving its hoard "
                    "in an abandoned Kezdö Válasz fort. Dragons find the "
                    "lost treasury of Decebalus and fight over it. The "
                    "aždaja Rabidanadas, seeing Akgah's success in Thebes, "
                    "leads a band against Bulgaria. Dragons or magi learn "
                    "that the Roman dragon has long been a magus in "
                    "disguise. Leontine of Old Histria quarrels with her "
                    "zmaj partner over the Golden Mean, their column goes "
                    "missing, and the zmaj's kin fall on Old Histria. Or "
                    "magi rescue a boyar's stolen daughter, or drive a zmaj "
                    "from a regio they covet, and the dragon they humbled "
                    "rouses others."
                ),
                ignored=(
                    "One band breaks the peace; others test their bounds, "
                    "and raids become war."
                ),
                stopped=(
                    "The quarrel is mended, the hoard shared out or the "
                    "rumour quashed before a second dragon joins in."
                ),
                turned=(
                    "The troupe learns early who struck the spark, the key "
                    "to the ending."
                ),
            ),
            S(
                "Sound the alarm",
                at=2,
                clues=(
                    "Word must go to the five legal covenants and from them "
                    "to every oppidum, to the Prima, the Quaesitors, the "
                    "Redcaps and the hoplites. Messengers cross the worst "
                    "country in the Tribunal, hunt for absent magi, and "
                    "convince doubting elders that this is more than one "
                    "dragon's raid."
                ),
                ignored="The Tribunal is caught unready when the first blows fall.",
                stopped="The Tribunal mobilises in good time.",
                turned=(
                    "The bearers of the news win the Prima's ear and a "
                    "place in the councils of war."
                ),
            ),
            S(
                "Rush to the front",
                at=3,
                clues=(
                    "House Tremere moves while other Houses debate. Orders "
                    "go out according to rank and privilege, forces are "
                    "mustered and the site of the first fighting is "
                    "searched. The dragons fly, so the front is hard to "
                    "find; they favour the mountains, and the defences of "
                    "Laniena, the Scholomance, Coeris and Lycaneon are seen "
                    "to first."
                ),
                ignored="The mountain oppida stand alone.",
                stopped="The oppida's defences are readied in time.",
                turned=(
                    "Player magi take command of a sector of the war, or "
                    "of its supplies."
                ),
            ),
            S(
                "The first assault",
                at=4,
                clues=(
                    "The Scholomance closes its classes and sends its "
                    "apprentices and mundane scholars south through the "
                    "Bran Pass into Bulgaria in the troupe's care. On the "
                    "road, aždaje fall on a smaller band of zmajevi in the "
                    "sky and the fight comes down around the column."
                ),
                ignored="Scholars die, and with them the school's future agents.",
                stopped="The column reaches safety unseen.",
                turned=(
                    "Magi who can tell the two kinds apart help the "
                    "zmajevi, and win Magic dragons as allies."
                ),
            ),
            S(
                "Consequences",
                at=5,
                clues=(
                    "The war tears through the Tribunal's other "
                    "supernatural folk, killing faeries and driving others "
                    "from their homes. Three enraged giants wreck a crowded "
                    "village."
                ),
                ignored="The giants' rampage spreads.",
                stopped="The giants are slain.",
                turned=(
                    "The giants are calmed or resettled, perhaps with the "
                    "help of storm wizards who know their kind."
                ),
            ),
            S(
                "A city in flames",
                at=6,
                clues=(
                    "A flight of zmajevi comes to burn Veszprém, home of "
                    "the college library many magi have quietly read and "
                    "borrowed from."
                ),
                ignored="The city and its library burn, a loss to Hermetic scholars.",
                stopped="The dragons are driven off.",
                turned=(
                    "Saving the city wins the bishop's gratitude, and in "
                    "time the king's."
                ),
            ),
            S(
                "The first to fall",
                at=7,
                clues=(
                    "An oppidum is lost, best of all one the troupe cares "
                    "for. For example, an aždaja finds Laniena and is beaten "
                    "back, but kills several hunters; hours after the "
                    "troupe arrives, twenty-five aždaje fill the sky, and "
                    "Lexander resolves to abandon the caves and save what "
                    "he can."
                ),
                ignored="The oppidum and its people are lost.",
                stopped=(
                    "The evacuation saves its magi, books and vis, though "
                    "the site is gone."
                ),
                turned=(
                    "The troupe earns the gratitude of the oppidum's "
                    "survivors, and perhaps the right to rebuild it."
                ),
            ),
            S(
                "Returning the blow",
                at=8,
                clues=(
                    "A mountain nest is found where more than fifty "
                    "zmajevi rest between raids, and there is time to "
                    "gather the Tribunal's forces against it."
                ),
                ignored="The nest keeps feeding the raids.",
                stopped="The Tribunal's strike scatters the nest.",
                turned=(
                    "The troupe plans and leads the blow, and its names go "
                    "into the Tribunal's chronicle."
                ),
            ),
            S(
                "Containing the fire",
                at=9,
                clues=(
                    "The war threatens to spill into the Greater Alps, "
                    "Novgorod, Thebes and Rome. House Tremere has staked "
                    "its standing, perhaps its existence, on keeping it "
                    "inside the ring of mountains."
                ),
                ignored=(
                    "The war reaches other Tribunals, and the Order holds "
                    "House Tremere to account."
                ),
                stopped="The dragons are held within the Tribunal's mountains.",
                turned="The House's credit across the Order rises.",
            ),
            S(
                "The climax",
                at=10,
                clues=(
                    "Each ending answers a spark. Destroy Veles, first "
                    "quelling Perun's revived worship, by knights or by "
                    "magi turned missionaries. Prove Abur-ciocîrlie a liar "
                    "and beat him in a duel, or find Fetillusclaviceps to "
                    "fight him. Share Decebalus's gold out among the "
                    "zmajevi by rank and enforce the share, perhaps "
                    "destroying every aždaja beside them. Go to Thebes and "
                    "destroy Akgah, without which Rabidanadas cannot be "
                    "beaten. Unmask the magus who plays the Roman dragon "
                    "and find a true keeper for the peace. Or recover the "
                    "stolen column so Leontine and her zmaj can make peace."
                ),
                ignored=(
                    "The dragons level cities and topple kingdoms; rivers "
                    "boil dry and the face of the Tribunal is changed for "
                    "ever."
                ),
                stopped="A new peace binds the dragons, or the aždaje are destroyed.",
                turned=(
                    "Ending the war through Thebes could heal the old wound "
                    "between the two Tribunals and clear House Tremere's "
                    "name at last."
                ),
            ),
        ],
    )


# -- the dormant stories --


def _teutonic(transylvania: Transylvania) -> None:
    b = transylvania.b
    transylvania.world["threat_teutonic"] = _dormant(
        b.threat(
            "The Teutonic Expulsion",
            summary=paragraphs(
                "In 1211 King Andrew II granted the Burzenland to the "
                "Teutonic Knights, free of taxes and dues though he "
                "kept the coinage and half the gold and silver mined, "
                "to hold the Carpathian passes against the Cumans. "
                "Brother Theoderich runs the mission almost alone while "
                "the hochmeister, Hermann von Salza, divides his time "
                "between the Holy Land and Egypt. In nine years the "
                "knights have built forts and are finishing five "
                "castles around Kronstadt, settled Saxons to feed them, "
                "quarrelled with the local bishop over his rights, and "
                "courted the pope to slip free of Hungary. They mean to "
                "push down the Danube to the Black Sea and reopen the "
                "land road to Constantinople.",
                "House Tremere has forbidden formal contact with the "
                "knights. The pope has charged them to root out heresy "
                "and diabolism, and the Tremere fear they will count "
                "the Order of Hermes among the pagans and idolaters; "
                "the knights have also heard of the Scholomance. The "
                "Order cannot stay hidden from them much longer. An "
                "isolated order with few friends among the Hungarians "
                "might accept a hand held out, but the Code makes such "
                "friendship delicate.",
            ),
            secrets="The book offers three Teutonic Orders. One is pious and "
            "mundane. A holier one makes Dominion auras of a brave "
            "temper on the land it conquers and keeps an inner circle "
            "of Divine wonder-workers. A profane one serves Hell: its "
            "leaders are goetic sorcerers, its knights take part in "
            "infernal rites, it seizes shamans, witches and taltós for "
            "their lore, and its favoured knights carry great swords "
            "with a demon bound inside that whispers in their dreams.",
            antagonist="The Teutonic Knights under Brother Theoderich",
            realm="",
            moves=DATED,
            stages=[
                S(
                    "The captured hedge wizard",
                    year=1220,
                    clues=(
                        "A pagan hedge wizard with a grudge against the "
                        "Order of Hermes falls into a garrison's hands and "
                        "tells the knights all he knows of magi, and more. "
                        "Soon the garrison chooses Hermetic targets."
                    ),
                    ignored=(
                        "The knights move against the Order as heretics, "
                        "and the secret is out."
                    ),
                    stopped=(
                        "The troupe deals with the garrison, revealing as "
                        "little as it can or leaving no witnesses, and "
                        "answers for breaking the Tremere edict either way."
                    ),
                    turned=(
                        "The troupe sets the knights' errors right with "
                        "care, and opens a quiet channel to the order."
                    ),
                ),
                S(
                    "The Golden Bull",
                    year=1222,
                    clues=(
                        HISTORY + "the nobles, restless since Andrew II came "
                        "home from crusade in 1218, force on him the Golden "
                        "Bull, which lets them check the king's acts. He "
                        "still refuses to take back the Burzenland."
                    ),
                    ignored="The nobles' grudge against the knights deepens.",
                    stopped="The king revokes the grant while there is still peace.",
                    turned=(
                        "Magi who can sway the barons decide which way the "
                        "Burzenland goes."
                    ),
                ),
                S(
                    "A fief of the Holy See",
                    year=1225,
                    clues=(
                        HISTORY + "Hermann von Salza uses his credit with "
                        "the pope to make the Burzenland a papal fief. The "
                        "king cannot lose the land; the knights demand a "
                        "second hearing and will not go."
                    ),
                    ignored=(
                        "Royal troops drive the knights out by force, and "
                        "their castles stand empty."
                    ),
                    stopped="The knights stay in Hungary on new terms.",
                    turned=(
                        "The troupe claims a castle site, or a grateful "
                        "knight's friendship, from the wreck."
                    ),
                ),
                S(
                    "The Cumans return",
                    year=1225,
                    clues=(
                        HISTORY + "with the passes unguarded the Cumans pour "
                        "into the Danube basin, pressed from the east by "
                        "the Great Khan's horde."
                    ),
                    ignored="The Cumans trouble Hungary for the rest of the century.",
                    stopped="The passes are held by other hands.",
                    turned="Magi who befriend the Cumans gain allies on the frontier.",
                ),
            ],
        )
    )


def _mongols(transylvania: Transylvania) -> None:
    b = transylvania.b
    transylvania.world["threat_mongols"] = _dormant(
        b.threat(
            "The Mongols",
            summary=paragraphs(
                "Beyond the Cuman steppe a greater power is stirring. "
                "If history holds, the Mongols come west in waves "
                "through the middle of the century, first breaking the "
                "Cumans, then driving whole peoples before them, and at "
                "last falling on Hungary itself. To the Tribunal's "
                "people they will seem as alien as any monster, a "
                "horde no one can defeat and few escape, which makes "
                "them the natural foe of a horror story.",
                "Tablinum is rumoured to hide the Refuge, a network of "
                "regiones stocked with laboratories where House Tremere "
                "could outlast any calamity. True or not, desperate "
                "magi will flock there if the horde comes.",
            ),
            secrets="",
            antagonist="The Mongol horde",
            moves=DATED,
            stages=[
                S(
                    "The Kalka",
                    year=1223,
                    clues=(
                        HISTORY + "the Mongols shatter the Cuman confederacy "
                        "at the Kalka. Twenty thousand Cuman families enter "
                        "Hungary, promising to be baptised and to fight the "
                        "Mongols if they come back; other Cumans are "
                        "swallowed by the Golden Horde."
                    ),
                    ignored="Hungary fills with uneasy pagan settlers.",
                    stopped="The Cumans are turned away, and the border burns.",
                    turned=(
                        "Magi win the newcomers' shamans as friends, and "
                        "news of the enemy beyond them."
                    ),
                ),
                S(
                    "Thrace emptied",
                    year=1237,
                    clues=(
                        HISTORY + "a vast migration lays Thrace waste, and "
                        "ten thousand Cuman families take service with the "
                        "Nicene emperor for land."
                    ),
                    ignored="The south fills with refugees and raiders.",
                    stopped="The Tribunal's frontier oppida stand firm.",
                    turned="The troupe learns how the horde fights, before it arrives.",
                ),
                S(
                    "The invasion",
                    year=1241,
                    clues=(
                        HISTORY + "the horde falls on Hungary and its "
                        "neighbours, ending the Bosnian war and every other "
                        "quarrel."
                    ),
                    ignored=(
                        "Towns burn and oppida are overrun; magi run for the "
                        "Refuge, if it exists."
                    ),
                    stopped="The horde is turned back or passes by.",
                    turned=(
                        "The troupe shelters the realm's survivors and "
                        "shapes what rises from the ashes."
                    ),
                ),
            ],
        )
    )


def _bosnian_crusade(transylvania: Transylvania) -> None:
    b = transylvania.b
    transylvania.world["threat_bosnia"] = _dormant(
        b.threat(
            "The Bosnian Crusade",
            summary=paragraphs(
                "The Bosnian Church, heir to the Bogomils who survived "
                "Stefan Nemanja's purge, calls its faithful Patarians "
                "and keeps to itself. The King of Hungary has written "
                "ordering it to purge them; it answers that Bosnia has "
                "no heretics. Pope Honorius III has sent a legate to "
                "urge Andrew II on, clerics preach against the "
                "Patarians, and Hungarian knights are gathering.",
                "House Tremere has not decided what to do. The Oath "
                "forbids meddling with mundanes, yet a crusade could "
                "remake the Tribunal, and the House remembers how the "
                "Fourth Crusade broke Thebes. Several of its leaders "
                "know Hungarians, Bosnians and Patarians personally, "
                "and the House watches the border for the small "
                "incident that could set it alight. In Vrhbosna the "
                "Mercere keep one of their oldest mansiones, a "
                "quarrelsome place where a brawl ended in murder a year "
                "ago.",
            ),
            secrets="Some suspect an Infernal aura has grown in the Vrhbosna "
            "mansio; none has been detected yet.",
            antagonist="The crusaders of Hungary and Croatia",
            realm="Divine",
            moves=DATED,
            stages=[
                S(
                    "The legate's sermons",
                    year=1220,
                    clues=(
                        "Warriors muster across the Tribunal and preachers "
                        "denounce the heretics; rumours of a crusade are "
                        "easily believed."
                    ),
                    ignored="The muster goes on, and the House stays undecided.",
                    stopped=(
                        "The troupe quietly takes the heat out of the border "
                        "quarrels, within the Code."
                    ),
                    turned="Magi with friends on both sides become the House's go-betweens.",
                ),
                S(
                    "The crusade",
                    year=1237,
                    clues=(
                        HISTORY
                        + "after a dozen quiet years Pope Gregory IX persuades the Duke of "
                        "Croatia to take the cross against Bosnia. The "
                        "crusade loses its purpose and becomes a war "
                        "between Bosnia and Hungary."
                    ),
                    ignored=(
                        "Villages burn far from any heretic, and the war drags on."
                    ),
                    stopped="The crusade is turned aside before it reaches Bosnia.",
                    turned="The troupe protects what the House values in its path.",
                ),
                S(
                    "Ended by the horde",
                    year=1241,
                    clues=(
                        HISTORY + "the Mongol invasion turns every ruler's "
                        "eyes elsewhere, and the war ends."
                    ),
                    ignored="Bosnia is left exhausted.",
                    stopped="The war ends sooner.",
                    turned="The Bosnian Church survives, owing the troupe a debt.",
                ),
            ],
        )
    )


def _thracian_valley(transylvania: Transylvania) -> None:
    b = transylvania.b
    transylvania.world["threat_thracian_valley"] = _dormant(
        b.threat(
            "The Valley of the Thracian Kings",
            summary=paragraphs(
                "Four years ago a Tremere necromancer, then a hoplite, "
                "found the burial ground of the ancient Thracian kings "
                "near Seuthopolis, their old capital. The House's "
                "necromancers are delighted, and House Verditius wants "
                "a dig too, since the Thracians worshipped smith-gods. "
                "Benilda, who never trusts a cheerful necromancer, is "
                "blocking access for now, but she knows the Tremere "
                "will win in the end and hopes to look first or to "
                "choose who digs and why.",
                "Seuthopolis itself began as a covenant of Verditius "
                "magi of the Cabeiri cult; House Guernicus now forbids "
                "its members to worship the old chthonic gods, and has "
                "removed three from office for irrationality that "
                "looked like the cult's hubris.",
            ),
            secrets="",
            antagonist="The magician-kings of Thrace and their guardians",
            realm="Magic",
            stages=[
                S(
                    "Benilda's survey",
                    at=1,
                    clues=(
                        "Benilda quietly asks trusted magi to look over the "
                        "valley before the Tremere can force the matter."
                    ),
                    ignored="The Tremere win access on their own terms.",
                    stopped="The valley stays closed a while longer.",
                    turned=(
                        "The troupe's report decides who leads the dig, and "
                        "Benilda owes it."
                    ),
                ),
                S(
                    "The dig",
                    at=2,
                    clues=(
                        "The excavation begins and must be hidden from "
                        "mundanes; the tombs are cunningly trapped."
                    ),
                    ignored="Diggers die and the locals talk.",
                    stopped="The dig is halted.",
                    turned="The troupe brings out grave goods intact.",
                ),
                S(
                    "The guardians loosed",
                    at=3,
                    clues=(
                        "Spirits the magician-kings set to guard their "
                        "tombs wake when the robbers break in."
                    ),
                    ignored="The guardians haunt Seuthopolis and the pass.",
                    stopped="The spirits are laid or bound.",
                    turned="The guardians are pacified and their lore learned.",
                ),
                S(
                    "The Cabeiri",
                    at=4,
                    clues=(
                        "The recovered items need assessing, and may serve "
                        "Original Research. The trail leads to the "
                        "Cabeiri, the Thracians' gods, perhaps through "
                        "journeys into the Magic or Faerie realms, or to "
                        "initiations in their Mystery."
                    ),
                    ignored="The Cabeiri's hubris spreads among the Quaesitors.",
                    stopped="The cult stays buried.",
                    turned=(
                        "The troupe gains a breakthrough, or an initiation, "
                        "from the kings' legacy."
                    ),
                ),
            ],
        )
    )


def _zalmoxis(transylvania: Transylvania) -> None:
    b = transylvania.b
    transylvania.world["threat_zalmoxis"] = _dormant(
        b.threat(
            "The Return of Zalmoxis",
            summary=paragraphs(
                "The Geto-Dacians worshipped Zalmoxis before Christ, "
                "and his rich, secretive cult went into hiding in the "
                "Carpathians as the people converted. The cult says he "
                "learned magic from Pythagoras on Samos and the secrets "
                "of immortality in Egypt, then spent three years in a "
                "cave on holy Kogaionon and came out to teach that the "
                "soul does not die. Every five years it sends a "
                "messenger to its god by throwing him onto spear "
                "points: if he dies, the god has accepted him.",
                "In the southern mountains around Maramures several "
                "groups of cultists each follow a vrajitoarea, a Vlach "
                "folk witch. One of them has the Gift and is slowly "
                "drawing the others to him, though his Gift keeps them "
                "at a distance. Then he learns that a wizard called "
                "Zalmoxis lives in the hollow mountain nearby.",
            ),
            secrets="Archmagus Zalmoxis of Verditius, Lycaneon's longevity "
            "specialist, is only named after the god and has nothing "
            "to do with the cult, and the magi of Lycaneon know "
            "nothing of what is brewing. The vrajitoarele belong to "
            "the Magic realm; none of their powers is Infernal.",
            antagonist="A Gifted vrajitoarea of the Cult of Zalmoxis",
            realm="Magic",
            stages=[
                S(
                    "The cults unite",
                    at=1,
                    clues=(
                        "The Gifted witch proclaims that the god has risen "
                        "again and is held prisoner by the other wizards of "
                        "the mountain, and the scattered cults rally to him."
                    ),
                    ignored="The cult grows bold and numerous.",
                    stopped="The cults stay divided.",
                    turned="The troupe learns of the cult before Lycaneon does.",
                ),
                S(
                    "Pilgrims at the mountain",
                    at=2,
                    clues=(
                        "Strangers watch Lycaneon's approaches, ask after "
                        "the old wizard among its servants and miners, and "
                        "a messenger is sent to the spears."
                    ),
                    ignored="The cult finds a way in.",
                    stopped="The watchers are caught and questioned.",
                    turned=(
                        "Zalmoxis himself, vain as he is, may be persuaded "
                        "to play the god and send the faithful home."
                    ),
                ),
                S(
                    "The rescue",
                    at=3,
                    clues=(
                        "The faithful try to free their god by force or "
                        "guile, with folk witchcraft and the Gifted leader's "
                        "spells."
                    ),
                    ignored=(
                        "Blood is spilt at the House's manufactory, and the "
                        "Tribunal's secrecy suffers."
                    ),
                    stopped="The cult is broken.",
                    turned="The witches become the Order's allies, or its informants.",
                ),
            ],
        )
    )


def _taltos(transylvania: Transylvania) -> None:
    b = transylvania.b
    transylvania.world["threat_taltos"] = _dormant(
        b.threat(
            "The Székely Taltós",
            summary=paragraphs(
                "Serb and Croat legend says a hermit taltós of "
                "matchless power led the Slavs south from beyond the "
                "Carpathians, and that in hard times another will come "
                "to free the people from their masters. The tale is "
                "loved most in the poor communities of the forest "
                "glens and the upper Danube.",
                "The Székely, Magyars thought lesser by their kin, were "
                "settled on the kingdom's eastern edge to hold off "
                "Cuman and Mongol raiders. They are reckoned the "
                "fiercest warriors in the Tribunal and once followed "
                "shape-changing taltós into battle. Now a mysterious "
                "man preaches in their villages, and the Székely have "
                "turned on their Vlach and Saxon neighbours. The Vlachs "
                "say a Magyar taltós has won back his tradition's old "
                "power, called lesser taltós to him and is building an "
                "empire. House Tremere ought to look into it.",
                "The true taltós destroyed one another a thousand years "
                "ago, so a taltós of real power would be a marvel. "
                "Laniena trains its Fectores with initiation scripts "
                "taken from a taltós clan, and Tatiana, the Prima's "
                "spymistress, was born a Szekler.",
            ),
            secrets="",
            antagonist="A taltós preacher among the Székely",
            realm="Magic",
            stages=[
                S(
                    "The preacher",
                    at=1,
                    clues=(
                        "Border raids by the Székely rise; a stranger "
                        "preaches deliverance from village to village."
                    ),
                    ignored="The Székely find a common voice.",
                    stopped="The preacher is discredited or vanishes.",
                    turned="The troupe meets him and learns what he wants.",
                ),
                S(
                    "The lesser taltós",
                    at=2,
                    clues=(
                        "Hedge wizards gather to him; spirit battles and "
                        "shapechangers are reported along the frontier."
                    ),
                    ignored="A hedge tradition of power reborn on the Order's doorstep.",
                    stopped="The gathering breaks apart, or joins the Order.",
                    turned="The Fectores or the troupe win the taltós' lore.",
                ),
                S(
                    "A new power",
                    at=3,
                    clues=(
                        "The Székely rise against their neighbours and their "
                        "king under the taltós' banner."
                    ),
                    ignored=(
                        "A new and volatile power stands in the east, and "
                        "the frontier against the Cumans and Mongols cracks."
                    ),
                    stopped="The rising fails.",
                    turned=(
                        "The taltós becomes a ruler who owes his throne to the troupe."
                    ),
                ),
            ],
        )
    )


def _succession(transylvania: Transylvania) -> None:
    b = transylvania.b
    transylvania.world["threat_succession"] = _dormant(
        b.threat(
            "Poena's Succession",
            summary=paragraphs(
                "House Tremere's leader is chosen by appointment and "
                "certamen, a quick and plain method that does not stop "
                "magi from trying to sway it. Poena has been Prima for "
                "two years. Her legata, Monica Ierne, is her heir: if "
                "Poena dies or is unfit, Monica acts as Prima until an "
                "emergency council meets. Monica does not want the "
                "office and would take it only to keep out someone "
                "odious; as Prima she would push for the leader to be "
                "chosen by a duel of champions, then resign. Horatius, "
                "who helped Poena to power, would make a good "
                "compromise if the House split, and would plant oppida "
                "round the Black Sea. Janus will never stand, for fear "
                "of what would come out.",
                "The previous Primus nominally leads the Burning Acorns "
                "hunt for Diedne survivors. The House has lost touch "
                "with him deep in the Novgorod Tribunal, and he knows "
                "the House's structure and Coeris's defences.",
            ),
            secrets="Janus is a lycanthrope, which is why he will never seek the office.",
            antagonist="The House's rival candidates",
            stages=[
                S(
                    "The illness",
                    at=1,
                    clues=(
                        "Poena learns she has an illness that will weaken "
                        "her and may cloud her judgement. Without alarming "
                        "the House she sends envoys to size up possible "
                        "successors, meaning to choose and train one for a "
                        "deciding certamen at the next Decennial."
                    ),
                    ignored="The envoys' reports decide the House's future unseen.",
                    stopped="A cure is found, and the matter is shelved.",
                    turned="The troupe's candidate becomes Poena's choice.",
                ),
                S(
                    "The lost Primus",
                    at=2,
                    clues=(
                        "Word comes that the past Primus is missing in "
                        "Novgorod; what he knows of Coeris would be priceless "
                        "to an enemy or a rival."
                    ),
                    ignored="His knowledge falls into other hands.",
                    stopped="He is found and brought home.",
                    turned="He backs the troupe's candidate.",
                ),
                S(
                    "Failing strength",
                    at=3,
                    clues=(
                        "Poena weakens faster than she planned. Those who "
                        "know can conceal it, so the House's rivals stay "
                        "busy with their own work, or give her away and "
                        "let a stronger hand take the House at once."
                    ),
                    ignored="Rumour spreads and the councilors begin to manoeuvre.",
                    stopped="The secret is kept until the Decennial.",
                    turned="The troupe chooses when the House learns of it.",
                ),
                S(
                    "Prima pro tempore",
                    at=4,
                    clues=(
                        "Poena dies and Monica acts as Prima. The troupe is "
                        "sent to summon the councilors and gauge each one's "
                        "ambitions, policies and support; Monica uses the "
                        "interval to finish Poena's plans and rush through "
                        "a few of her own."
                    ),
                    ignored=(
                        "The succession is settled by certamen among whoever "
                        "pushes hardest."
                    ),
                    stopped="A worthy successor is agreed before the duel.",
                    turned=(
                        "Loyal servants of Poena get to pitch their wildest "
                        "schemes to a sympathetic Prima."
                    ),
                ),
            ],
        )
    )


def _legate(transylvania: Transylvania) -> None:
    b = transylvania.b
    transylvania.world["threat_legate"] = _dormant(
        b.threat(
            "The Papal Legate",
            summary=paragraphs(
                "Across the Balkans and as far as the Emperor's court, "
                "people tell of the Devil's school in the mountains, "
                "whose ten pupils learn every secret of nature and "
                "magic in seven years, and one of whom the Devil keeps. "
                "In truth it is the Scholomance, an oppidum's school "
                "for agents, companions, future Redcaps and "
                "apprentices. The Church has sent a papal legate to "
                "look into it. He lodges with the Teutonic Knights while "
                "he builds his case, and has found only hearsay, since "
                "the only people who know anything are magi or their "
                "former pupils.",
                "The school no longer wipes its mundane pupils' "
                "memories as it once did: its policy now is to make "
                "friends for the Order, neither boasting of its masters "
                "nor denying them. That leaves many former pupils who "
                "could talk.",
            ),
            secrets="Sebastian, the school's ageless caretaker, may be the "
            "zmaj king Aževastjepan; a legate who found him would find "
            "more than he bargained for.",
            antagonist="The papal legate, lodged with the Teutonic Knights",
            realm="Divine",
            stages=[
                S(
                    "Hearsay",
                    at=1,
                    clues=(
                        "The legate questions travellers, priests and "
                        "nobles about the Devil's school; the knights, who "
                        "have heard the same tale, help him."
                    ),
                    ignored="His questions draw nearer to former pupils.",
                    stopped="He is satisfied the school is a legend.",
                    turned="The troupe feeds him a harmless trail.",
                ),
                S(
                    "A witness",
                    at=2,
                    clues=(
                        "A former mundane pupil, a bishop or a nobleman "
                        "perhaps, is pressed to say what he learned in the "
                        "mountains."
                    ),
                    ignored="The legate gains a sworn witness.",
                    stopped="The witness keeps faith with his school.",
                    turned="The witness becomes the troupe's man in the legate's household.",
                ),
                S(
                    "The castle in the storm",
                    at=3,
                    clues=(
                        "The legate goes into the mountains south of "
                        "Hermannstadt in search of the tower that shows "
                        "itself only in storms."
                    ),
                    ignored=(
                        "He finds the school, or something worse, and the "
                        "knights learn where the Order lives."
                    ),
                    stopped="He goes home with nothing.",
                    turned=(
                        "The school is shown to him in its best light, and "
                        "he reports a harmless academy to Rome."
                    ),
                ),
            ],
        )
    )


# -- tying the stories to the other parts' records --


def _key(name: str) -> str:
    """A name compared loosely: case and a leading 'The' set aside."""
    out = name.casefold().strip()
    out = out.removeprefix("the ")
    return out.replace("-", " ").replace("’", "'")


def _find(records: list[Any], *names: str) -> Any | None:
    """The first record whose name is one of `names`, or failing that
    whose name starts with one of them as a whole word, loosely
    compared."""
    wanted = [_key(n) for n in names]
    for record in records:
        if _key(record.name) in wanted:
            return record
    for record in records:
        name = _key(record.name)
        if any(name.startswith(n + " ") for n in wanted):
            return record
    return None


def _add_to(record: Any, more: str, hidden: str = "", attr: str = "summary") -> None:
    """Add a paragraph to a record's summary (or notes), and `hidden` to
    its secrets."""
    setattr(record, attr, paragraphs(getattr(record, attr) or "", more))
    if hidden:
        record.secrets = paragraphs(record.secrets, hidden)


def _place(transylvania: Transylvania, places: list[Any], *keys: str) -> Any | None:
    """A place by one of the region parts' keys, or by one of its names."""
    for key in keys:
        if key in transylvania.places:
            return transylvania.places[key]
    return _find(places, *keys)


def _character(transylvania: Transylvania, *names: str) -> Any | None:
    for name in names:
        found = transylvania.magi.get(name)
        if found is not None:
            return found
    return _find(transylvania.b.saga.characters, *names)


def _covenant(transylvania: Transylvania, *names: str) -> Any | None:
    for name in names:
        found = transylvania.covenants.get(name)
        if found is not None:
            return found
    return _find(transylvania.b.saga.covenants, *names)


#: The links `finish` makes where the other parts made the target:
#: (story, link kind, the target's possible keys or names, note).
LINKS: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    ("threat_dragon_war", "creatures", ("Danaslepih",), "A zmaj of the war"),
    ("threat_dragon_war", "creatures", ("Upokorituma",), "An aždaja of the war"),
    (
        "threat_dragon_war",
        "creatures",
        ("Georghe and Ladislau", "Georghe"),
        "Giants the war could drive to rampage",
    ),
    ("threat_dragon_war", "characters", ("leontine",), "Argues with an old zmaj"),
    ("threat_dragon_war", "characters", ("dominic",), "Took the column"),
    ("threat_dragon_war", "characters", ("lexander",), "Abandons Laniena"),
    ("threat_dragon_war", "characters", ("poena",), "Must be warned"),
    ("threat_dragon_war", "characters", ("monica",), "The House's field commander"),
    ("threat_dragon_war", "characters", ("Sebastian",), "Perhaps the dragon king"),
    ("threat_dragon_war", "covenants", ("old_histria",), "Leontine's zmaj attacks it"),
    ("threat_dragon_war", "covenants", ("laniena",), "The first to fall"),
    ("threat_dragon_war", "covenants", ("scholomance",), "Its pupils sent south"),
    ("threat_dragon_war", "covenants", ("coeris",), "Where the column may lie"),
    ("threat_dragon_war", "covenants", ("lycaneon",), "A mountain oppidum to defend"),
    (
        "threat_dragon_war",
        "covenants",
        ("kezdo_valasz",),
        "Its old forts could be used to frame it",
    ),
    ("threat_dragon_war", "places", ("veszprem", "Veszprém"), "The city in flames"),
    (
        "threat_dragon_war",
        "places",
        ("bran_pass", "The Bran Pass"),
        "The scholars' road",
    ),
    (
        "threat_teutonic",
        "places",
        ("burzenland", "The Burzenland"),
        "The knights' grant",
    ),
    ("threat_teutonic", "places", ("kronstadt", "Kronstadt"), "Their central castle"),
    ("threat_mongols", "covenants", ("tablinum",), "Said to hide the Refuge"),
    ("threat_mongols", "places", ("hungary",), "The horde's target"),
    ("threat_bosnia", "places", ("vrhbosna", "Vrhbosna"), "The Mercere mansio"),
    ("threat_bosnia", "places", ("bosnia", "Bosnia"), "The Patarians' land"),
    (
        "threat_thracian_valley",
        "places",
        (
            "thracian_valley",
            "valley_of_the_thracian_kings",
            "The Valley of the Thracian Kings",
        ),
        "The burial ground",
    ),
    ("threat_thracian_valley", "covenants", ("seuthopolis",), "Guards the valley"),
    ("threat_thracian_valley", "characters", ("benilda",), "Blocks the dig"),
    ("threat_zalmoxis", "covenants", ("lycaneon",), "The hollow mountain"),
    ("threat_zalmoxis", "characters", ("zalmoxis",), "Taken for the god"),
    ("threat_zalmoxis", "places", ("maramures", "Maramures"), "The cults' mountains"),
    ("threat_taltos", "characters", ("tatiana",), "Born a Szekler"),
    ("threat_taltos", "covenants", ("laniena",), "Holds taltós initiation scripts"),
    ("threat_succession", "characters", ("poena",), "The Prima"),
    ("threat_succession", "characters", ("monica",), "The legata and heir"),
    ("threat_succession", "characters", ("horatius",), "A compromise candidate"),
    ("threat_succession", "characters", ("janus",), "Will never stand"),
    ("threat_succession", "covenants", ("coeris",), "The Prima's seat"),
    ("threat_legate", "covenants", ("scholomance",), "The school he hunts"),
    ("threat_legate", "characters", ("simium",), "The headmaster"),
    ("threat_legate", "characters", ("Sebastian",), "The caretaker"),
    ("threat_legate", "places", ("burzenland", "The Burzenland"), "Where he lodges"),
)

#: Each story's place: oppida whose place to use, then place keys and
#: names to try, then the region's key as the fallback.
PLACES: dict[str, tuple[tuple[str, ...], tuple[str, ...], str]] = {
    "threat_dragon_war": ((), ("carpathians", "The Carpathians"), "transylvania"),
    "threat_teutonic": ((), ("burzenland", "The Burzenland"), "transylvania"),
    "threat_mongols": ((), (), "hungary"),
    "threat_bosnia": ((), ("bosnia", "Bosnia", "vrhbosna", "Vrhbosna"), "slavs"),
    "threat_thracian_valley": (
        (),
        (
            "thracian_valley",
            "valley_of_the_thracian_kings",
            "The Valley of the Thracian Kings",
        ),
        "bulgaria",
    ),
    "threat_zalmoxis": (("lycaneon",), ("maramures", "Maramures"), "transylvania"),
    "threat_taltos": ((), ("szeklerland", "Szeklerland"), "transylvania"),
    "threat_succession": (("coeris",), (), "transylvania"),
    "threat_legate": (("scholomance",), ("burzenland",), "transylvania"),
}

#: Factions other parts may make that stand behind a story.
BEHIND: dict[str, tuple[str, ...]] = {
    "threat_teutonic": ("Teutonic Knights", "Teutonic Order", "The Teutonic Order"),
    "threat_bosnia": ("Kingdom of Hungary", "Andrew II", "King Andrew II"),
    "threat_zalmoxis": ("Cult of Zalmoxis", "The Cult of Zalmoxis"),
    "threat_taltos": ("Szeklers", "Székely", "The Szeklers", "The Székely"),
    "threat_legate": ("Teutonic Knights", "Teutonic Order", "The Teutonic Order"),
}

#: Chapter 10's horror seeds, each added to the places or oppida it
#: uses: (place keys and names, or an oppidum's key with "covenant:",
#: the paragraph).
HORROR: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("transylvania",),
        "Horror seeds. This is the land of the book's horror stories. A "
        "vampire wearing the face of a dead friend or foe makes a fine "
        "nemesis; werewolves are common in places; vampire hunters serve "
        "as the savant who alone can beat the monster, or become monsters "
        "themselves, since a dhampir rises as a vampire when he dies, and "
        "a hunter whose own parent is the vampire has a ready-made "
        "tragedy. Giants make good brutes, with storm wizards, who hunt "
        "them, as the savant. The empty wilderness can drive the stoutest "
        "grog to frenzy, and a story locked into one regio, one storm or "
        "one night keeps the dread tight.",
    ),
    (
        ("carpathians", "The Carpathians", "transylvania"),
        "Horror seed: the mountains' dragons, hundreds or thousands of "
        "them, can come as a single monster or as a horde (see the Dragon "
        "War).",
    ),
    (
        ("hungary",),
        "Horror seed: if history holds, the Mongols come in waves in the "
        "middle of the century, a horde that can only be fled, not beaten "
        "(see The Mongols).",
    ),
    (
        ("burzenland", "The Burzenland"),
        "Horror seed: the Teutonic Knights can be the savants of a horror "
        "story, the hidden hand of a conspiracy, or, as a small band gone "
        "mad or bad, its psychopaths.",
    ),
    (
        ("covenant:coeris",),
        "Horror seed: magi make savants, but also nemeses, psychopaths "
        "and conspirators, and House Tremere itself is the Tribunal's "
        "largest possible conspiracy, with mystery cults, Diedne "
        "survivors and infernalists close behind. Magi conspirators strike "
        "from a distance, since the Order is good at tracing a sigil, and "
        "that only feeds the victims' paranoia.",
    ),
)

STORIES = paragraphs(
    "Stories. The Dragon War is the saga's great frame: the Pax Draconis "
    "hangs on a dragon unseen for fifty years, and any spark could set "
    "the Tribunal's dragons on each other and on men. Others wait for the "
    "storyguide to begin them: the Teutonic Knights' fall in 1222 and "
    "1225, the Mongols, the Bosnian crusade, the Valley of the Thracian "
    "Kings, the return of Zalmoxis, the Székely taltós, Poena's "
    "succession and the papal legate hunting the Scholomance. The "
    "Tribunal also suits horror: monster against savant, the psychopath, "
    "the horde, the conspiracy, the madness of the frontier, the changing "
    "body, nature's revenge and the cycle that repeats; the seeds sit on "
    "the places they use.",
)


def finish(transylvania: Transylvania) -> None:
    saga, world = transylvania.b.saga, transylvania.world
    places = [n for n in saga.neighbours if n.kind == "place"]
    factions = [n for n in saga.neighbours if n.kind == "faction"]
    for key, kind, names, note in LINKS:
        if kind == "characters":
            target = _character(transylvania, *names)
        elif kind == "covenants":
            target = _covenant(transylvania, *names)
        elif kind == "creatures":
            target = _find(saga.creatures, *names)
        else:
            target = _place(transylvania, places, *names)
        if target is not None:
            Builder.link(world[key], kind, target, note)
    for key, (covenants, names, region) in PLACES.items():
        place_id = None
        for name in covenants:
            covenant = _covenant(transylvania, name)
            if covenant is not None and covenant.place_id:
                place_id = covenant.place_id
                break
        if place_id is None:
            place = _place(transylvania, places, *names) if names else None
            place = place or transylvania.places.get(region)
            place_id = place.id if place is not None else None
        if place_id is not None:
            world[key].place_id = place_id
    for key, names in BEHIND.items():
        faction = _find(factions, *names)
        if faction is not None:
            world[key].answers_to = faction.id
    _horror(transylvania, places)
    tribunal = transylvania.tribunal or next(iter(saga.tribunals), None)
    if tribunal is not None:
        _add_to(tribunal, STORIES)


def _horror(transylvania: Transylvania, places: list[Any]) -> None:
    """Each horror seed on the first of its places that exists; one with
    no place found is left out."""
    for names, text in HORROR:
        if names[0].startswith("covenant:"):
            covenant = _covenant(transylvania, names[0].removeprefix("covenant:"))
            if covenant is not None:
                _add_to(covenant, text, attr="notes")
            continue
        place = _place(transylvania, places, *names)
        if place is not None:
            _add_to(place, text)
