"""The Slav lands of the Transylvanian Tribunal, as of 1220: Serbia,
Bosnia, Croatia, Istria and the Adriatic coast; the Mercere oppida Old
Histria and Shrouded Bay and their magi; the Redcap families and the
register of vis sales; the old faith of Perun and Veles; the Kingdom of
Serbia under Stefan the First-Crowned, Archbishop Sava and Studenica;
Bosnia's Patarians and the school at Mostre; Croatia, Knin, and Zadar,
Dubrovnik and Cres under Venice; and the places, auras and vis of the
region, in paraphrase of Against the Dark chapter five (with chapter two
for the vis register and the Venice portal, chapter six for Mostre and
chapter eight for Stefan's dragon shape and Istria's dragons).

Leviathan and the lost zenodochium of Zadar are fortresses.py's; the
Székely taltós, the Bosnian crusade and the Dragon War are stories.py's
threats; the creatures (strigons, votaress snakes, building faeries, the
dragons) are the Bestiary's and only named here. Keys: the region is
places["slavs"], its parts places["serbia"], ["bosnia"], ["croatia"] and
["istria"]; the dragon's ruin is places["diocletians_palace"]; Perun's
stones lie in places["pirin_mountains"], moved into Bulgaria in
finish."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.world import FULL
from ..builder import Builder, joined_lines, paragraphs, titled, vf_art
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Neighbour, Tribunal
    from . import Transylvania

MERCERE = "house_mercere"
TREMERE = "house_tremere"
TYTALUS = "house_tytalus"
VERDITIUS = "house_verditius"

#: The lead line of an oppidum's notes, before its secrets.
KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}


def _add(transylvania: Transylvania, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = transylvania.b.place(name, **kw)
    transylvania.places[key] = place
    return place


def build(transylvania: Transylvania) -> None:
    b = transylvania.b
    _region(transylvania)
    _serbia(transylvania)
    _bosnia(transylvania)
    _croatia(transylvania)
    _istria(transylvania)
    _lords(transylvania, b)
    _churches(transylvania, b)
    _towns(transylvania, b)
    _factions(transylvania, b)
    tribunal = transylvania.tribunal or next(iter(b.saga.tribunals), None)
    if tribunal is None:
        # The oppida need the Tribunal record tribunal.py makes first.
        return
    _old_histria(transylvania, b, tribunal)
    _shrouded_bay(transylvania, b, tribunal)
    _histrian_magi(transylvania, b)


# ------------------------------------------------------------- the region


def _region(transylvania: Transylvania) -> None:
    _add(
        transylvania,
        "slavs",
        "The Slav Lands",
        summary=paragraphs(
            "The Tribunal's south-western quarter: Serbia, Bosnia and "
            "Croatia, with the Istrian peninsula and the Adriatic shore "
            "beyond the Dinaric Alps. The Slavs came south over the "
            "Danube in the sixth and seventh centuries, from a homeland no "
            "chronicle can place; by 1220 they are too many tribes to "
            "list, and only the Serbs, the Bosniaks (Bošnjanin) and the "
            "Croats have become powers. Smaller groups live among their "
            "neighbours: the Krashovani by the Timok, the Šokci on the "
            "Sava, the Gorani on the edge of Epiros, the Montenegrins of "
            "Zeta, and the Székely in the eastern Carpathians.",
            "A Slav household is a zadruga, an extended family under its "
            "patriarch, living in a knot of half-sunken log huts; herders "
            "and farmers, a clan can load its goods and drive its beasts "
            "away overnight when danger comes. Most villages lie open by "
            "rivers and lakes, though a few north of the Danube shelter "
            "the chieftain's kin behind an earth bank and palisade ringed "
            "with hidden wolf-pits. Every Slav offers a stranger a meal "
            "and a seat at his table, and many still burn their dead on a "
            "pyre with their goods, which the clergy condemn and the "
            "townsfolk are giving up. Few are professional soldiers; a "
            "spear and a small wooden shield are the usual arms, and the "
            "Serbs fight in the Byzantine manner they have absorbed.",
            "The Old Ways. Every Slav tribe is Christian now, but many "
            "simply gave their old high god, Perun the Thunderer, the "
            "name God and kept the rest; priests call this double faith, "
            "dvoeverie, and find it strongest north of the Danube. Perun "
            "rules the sky and guards the World Tree, forever hunting "
            "Veles, a dragon of the underworld, trickery and magic, who "
            "steals his cattle, is slain, sinks below and returns; some "
            "still hear their fight in every thunderstorm. Pilgrims seek "
            "the old holy places, fenced clearings in deep woods or on "
            "lonely heights with many-headed idols of Perun, watched over "
            "by werewolves. Many such sites carry Magic auras, not "
            "Faerie, so Hermetic theorists suspect Perun and Veles were "
            "titans of the Magic realm and that lost magical traditions "
            "wait to be found there; the Order holds several, Rügen, the "
            "Bjornaer domus magna, among them.",
            "Perun's golden apples, thrown skyward to burst into a storm "
            "of lightning (a Serbian tale has one killing six hundred), "
            "are his mightiest weapon. Several Tremere would dearly like "
            "one for the House's arsenal; none has ever been found.",
            "Vis in the region (each in its place): Perun's stones and "
            "arrows in the Pirin Mountains (Auram), and, held by the "
            "Histrian oppida, Old Histria's mercury pool (Terram), the "
            "Istrian truffles (Herbam), the Strange Vis of the roof tar "
            "(Creo), Cres's blood well (Corpus) and storm beach (Rego); "
            "also the amphorae of Pula's temple, and the blood in a "
            "destroyed strigon's grave.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        transylvania,
        "sacred_glens",
        "The Sacred Glens of Perun",
        inside=transylvania.places["slavs"],
        aura=0,
        summary=paragraphs(
            "The holy places of the old Slav faith, spread through the "
            "forests and mountains of the Slav lands: clearings closed by "
            "a wooden fence, some with a carved idol of Perun in wood or "
            "stone showing several heads, and guarded, the old writings "
            "say, by werewolves. Pagan pilgrims still come. Where magi "
            "have looked, the auras are often Magic (of no stated "
            "strength), which is why some think Perun and Veles were "
            "titans, and a seeker might find a lost tradition among those "
            "who keep only the old religion.",
        ),
        **RUMOURED,
    )
    _add(
        transylvania,
        "pirin_mountains",
        "The Pirin Mountains",
        inside=transylvania.places["slavs"],
        realm="Magic",
        summary=paragraphs(
            "A mountain range where lightning has fused the soil into "
            "Perun's stones, fulgurites: hollow tubes of natural glass two "
            "or three inches across and up to several feet long, most "
            "holding a pawn or two of Auram vis, found by travellers "
            "across the range.",
            "Longer ones, Perun's arrows, turn up only in Magic auras. "
            "Their vis is spell-like: hurled like a javelin, one becomes "
            "a bolt of lightning before it strikes (a CrAu 25 effect, "
            "+30 damage on a hit, Initiative -1 and Attack +1 as a "
            "thrown weapon). Not yet in the item catalog.",
        ),
        **KNOWN_REGION,
    )


# ------------------------------------------------------------------ Serbia


def _serbia(transylvania: Transylvania) -> None:
    region = transylvania.places["slavs"]
    serbia = _add(
        transylvania,
        "serbia",
        "Serbia",
        inside=region,
        summary=paragraphs(
            "The western edge of the Tribunal, where the Balkans meet "
            "eastern Mythic Europe: first settled between the Sava and "
            "Danube to the north, the Morava to the east and the Adriatic "
            "to the south-west. Mountains, broken hills and plains, cut "
            "by many rivers, with the foothills of the Balkan range, the "
            "Carpathians and the Alps all reaching in, and the Dinaric "
            "Alps walling the coast off from the interior; the coast is "
            "Mediterranean, the inland weather much like Hungary's. Most "
            "people live in the fertile river valleys along the trade "
            "routes.",
            "Serb legend says a great anchorite led them south at the "
            "bidding of Emperor Heraclius, to serve as Roman mercenaries, "
            "only for the emperor to bar them from the richest land. Each "
            "clan (župa) belongs to a district (župaija) under a chieftain, "
            "the župan; the župan of Raška, on the Bulgarian border, rose "
            "to be grand župan, and his line has ruled since, keeping the "
            "realm whole by playing Bulgaria and Byzantium off against "
            "each other.",
            "The line between the pope's flock and the patriarch's runs "
            "through Serbia: Croatia is Roman, Bosnia goes its own way, "
            "and most Serbian dioceses took the Western rite when the "
            "papal legate crowned Stefan, though Kotor Bay and Ston keep "
            "the Greek one. Serbs are unusually easy about such "
            "differences; the strain lies between priests who cannot say "
            "the Latin rite and the superiors who demand it, which Rome "
            "tolerates for now.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "studenica",
        "Studenica",
        inside=serbia,
        realm="Divine",
        aura=8,
        summary=paragraphs(
            "The white marble monastery at the head of the Raška, some "
            "fifteen miles north of Ras: the royal foundation that is the "
            "heart of the Serbian Church and Archbishop Sava's seat, and "
            "the holiest place in Serbia, with a Divine aura of 8. Inside "
            "its walls stand two churches, the Virgin's and the King's, "
            "both raised by Stefan Nemanja, blending Italian "
            "and Byzantine building into something admired on both sides.",
            "The newly painted frescoes of the four portals hold a mythic "
            "artist's small wonders (Art & Academe): the sky behind the "
            "Crucifixion is blue by day, gold at sunset and black by "
            "night. Inside, one fresco shows Nemanja and the Virgin "
            "presenting a little model of the church to Christ.",
            "St Stefan Nemanja's relics were brought here from Mount "
            "Athos in 1206, and his tomb has wept holy oil ever since, "
            "earning him the name Myrrh-flowing: enough each day to fill "
            "a small vial, and all day on his feast, 13 February. "
            "Anointing someone with a vial works one of a saint's "
            "miracles costing 1 Divine Might (Realms of Power: The "
            "Divine). The saint, of Divine Might 50, takes a close "
            "interest in his family and his church.",
        ),
        **KNOWN_REGION,
    )
    _add(
        transylvania,
        "mount_hum",
        "Mount Hum",
        inside=serbia,
        realm="Faerie",
        summary=paragraphs(
            "A mountain of gentle slopes in the north of Zachlumia, on "
            "the Adriatic shore, the favourite hunting ground of King "
            "Stefan's eldest sons, Radoslav (28) and Vladislav (26), "
            "children of the queen he drove out for adultery in 1200, "
            "Eudocia Angelina. Since Serbian tales so often star a "
            "prince, the local faeries see the pair as perfect sources of "
            "vitality and keep dragging them into faerie adventures, "
            "which the princes, keener on game than on faeries, have no "
            "idea how to escape.",
            "A few of the Tribunal's magi know of this and quietly help "
            "the princes out, anonymously where they can, careful neither "
            "to harm the faeries much nor to meddle visibly in mundane "
            "affairs. The book gives no aura.",
        ),
        **RUMOURED,
    )


# ------------------------------------------------------------------ Bosnia


def _bosnia(transylvania: Transylvania) -> None:
    region = transylvania.places["slavs"]
    bosnia = _add(
        transylvania,
        "bosnia",
        "Bosnia",
        inside=region,
        summary=paragraphs(
            "A landlocked banate on the Dinaric Alps, with Hungary to "
            "the north, Croatia westward and Serbia on its southern and "
            "eastern sides, its northern edge reaching down into the Pannonian "
            "basin as far as the Sava and the Danube. Mostly hills and "
            "mountains; seven great rivers run off to the Adriatic, the "
            "Neretva, which divides Bosnia from Serbia and lower down "
            "Serbia from Croatia, the greatest of them. Settlements "
            "follow the rivers: Vrhbosna, the ban's seat and the heart of "
            "its church, Banja Luka in the north-west and Zenica on the "
            "Bosna.",
            "Its own church, the Bosnian Church of the Patarians, is "
            "Bogomil in all but name, and the King of Hungary demands it "
            "be purged; following history, a Hungarian invasion is "
            "coming (see the Bosnian crusade among the threats).",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "vrhbosna_mansio",
        "The Mansio of Vrhbosna",
        inside=bosnia,
        summary=paragraphs(
            "One of House Mercere's oldest mansiones, a half-public "
            "trading post in Vrhbosna with a name for trouble: "
            "quarrels every day and frequent brawls. Last year two "
            "local merchants came to blows there and one died; no "
            "visiting magus or servant was involved.",
        ),
        secrets=[
            titled(
                "An aura in the mansio",
                "Some suspect an Infernal aura has grown in the mansio of "
                "Vrhbosna; none has yet been detected.",
            ),
        ],
        **KNOWN_TRIBUNAL,
    )


# ----------------------------------------------------------------- Croatia


def _croatia(transylvania: Transylvania) -> None:
    region = transylvania.places["slavs"]
    croatia = _add(
        transylvania,
        "croatia",
        "Croatia",
        inside=region,
        summary=paragraphs(
            "The border of west and east: the Italian communes on one "
            "side, Serbs, Bosniaks and Magyars on the other. The Alpine "
            "foothills reach its west, the green Pannonian valleys lie to "
            "the north, the wooded Dinaric Alps close the east, and the "
            "rocky Adriatic shore runs along the south, most of it paying "
            "tribute to Venice.",
            "The Croats came south with the other Slavs and settled as two "
            "duchies, Pannonia in the north and Littoral Croatia on the "
            "coast; Frankish rule in the eighth century taught them "
            "feudal ways early, and their own kings ruled from the tenth "
            "century until the Trpimirović line ended in a feud between "
            "brothers in 1091. The northern nobles then offered the crown "
            "to Ladislaus I of Hungary, and Croatia has been a Hungarian "
            "vassal ever since.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "zadar_regiones",
        "The Night Streets of Zadar",
        inside=croatia,
        realm="Infernal",
        summary=paragraphs(
            "Years of murder on Zadar's docks and back alleys have "
            "raised Infernal auras in the city, and over the worst "
            "killings Infernal regiones have formed. Greed, bloodshed and "
            "resentment draw demons, and some magi fear the city will "
            "become a centre of their work unless the tension eases; "
            "would-be demon hunters among the young magi boast of "
            "stalking its empty streets after dark. The book gives no "
            "aura strengths.",
            "The zenodochium the Tremere hid here after 1203, and lost, "
            "is the hidden fortresses' (see the zenodochia).",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "diocletians_palace",
        "Diocletian's Palace",
        inside=croatia,
        realm="Magic",
        summary=paragraphs(
            "The vast limestone palace the emperor Diocletian built "
            "near Salona, where he was born, and retired to; later "
            "governments used it as offices, and refugees and the "
            "persecuted long sought shelter in it. Legend says Cyril "
            "and Methodius devised the Glagolitic letters in one of "
            "its halls to put the Gospels into Old Slavonic. In 1220 "
            "it is a ruin, but not an empty one: Salona's monks dig "
            "for martyrs' relics, and treasure hunters roam the "
            "unexplored rooms after the emperor's gold.",
            "Tremere magi now and then come looking for the dragon "
            "said to lie inside, coiled round a hoard of Roman gold. "
            "The current guess is that it lives in a regio; no one "
            "knows whether it is a Magic beast or an Infernal one, so "
            "the Magic 3 here is the pack's choice, not the book's.",
        ),
        secrets="",
        **RUMOURED,
    )


# ------------------------------------------------------------------ Istria


def _istria(transylvania: Transylvania) -> None:
    region = transylvania.places["slavs"]
    istria = _add(
        transylvania,
        "istria",
        "Istria",
        inside=region,
        summary=paragraphs(
            "The large peninsula at the head of the Adriatic, with its "
            "islands, claimed by the Histrian oppida; it takes its name, "
            "through the Romans, from the tribe that held it when Rome "
            "came. The coasts are Mediterranean; to the north-west the "
            "land climbs through wooded hills of pine and oak into low "
            "mountains. Many faeries live here, some very powerful.",
            "Istria's vampire is the strigon, which roams the streets "
            "after midnight knocking on doors to foretell a death, lies "
            "with widows and drinks children's blood. It is hard to "
            "destroy unless caught at rest in a grave that is itself hard "
            "to find; dug up and staked through the belly, it leaves its "
            "grave full of blood rich in vis, more the older it was. "
            "Redcaps who travel by night loathe strigons, which attack "
            "them or get them chased by mobs as suspects, and the Mercere "
            "often ask Pahniro to deal with one (see the Bestiary).",
            "A race of wise, friendly dragons, zmajevi, lives in Istria "
            "too, and the Histrian magi deal with them often (see the "
            "Bestiary and the Dragon War).",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "old_histria_fortress",
        "The Fortress of Old Histria",
        inside=istria,
        aura=7,
        summary=paragraphs(
            "A hill fort older than Rome on a mountain north-east of "
            "Pazin, its ditches and walls rebuilt again and again over "
            "the centuries into deep layers of defence against any "
            "mundane assault, and guarded by potent enchanted items: the "
            "oppidum of Old Histria. Its Magic aura is 7.",
            "In its grounds lies a pool of magical mercury, a rich source "
            "of Terram vis. A child dipped in it gains the Visions Flaw, "
            "and often worse Flaws besides, so it is seldom done.",
            "The site is bleak in winter, cold and wet, which drives many "
            "of its magi to Cres for the season.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        transylvania,
        "truffle_woods",
        "The Truffle Woods of Northern Istria",
        inside=istria,
        summary=paragraphs(
            "Pine and oak forests rich in truffles, which are Herbam vis "
            "as well as a delicacy; magi think they grow best where "
            "lightning has struck, and pay their weight in gold for "
            "them. They are gathered by night by odd, silent men in dark "
            "cloaks with clever dogs. Faeries crave truffles and pester "
            "anyone who finds them, unless the finder knows the right "
            "propitiations.",
        ),
        **KNOWN_REGION,
    )
    _add(
        transylvania,
        "mirna_valley",
        "The Mirna Valley",
        inside=istria,
        summary=(
            "A river valley of Istria where giants lived in ancient "
            "times; they are rare on the peninsula now. (The source text "
            "breaks off here.)"
        ),
        **RUMOURED,
    )
    _add(
        transylvania,
        "pula_arena",
        "The Arena of Pula",
        inside=istria,
        realm="Faerie",
        aura=6,
        summary=paragraphs(
            "Pula's amphitheatre, which magi credit to Rome and the town's "
            "faeries to themselves: building faeries raised it in a "
            "single night and fled at a muddled cock's crow before the "
            "roof was on, leaving a trail of huge stones dropped on the "
            "way from their far-off quarry. It stands open to the sky "
            "with a Faerie aura of 6, rising to 8 on certain nights; "
            "players who perform there then may cross into another world, "
            "or win favours from the unseen watchers beyond the back "
            "rows.",
            "Those who have slipped into its regio tell of a faerie town "
            "beneath, Diviægrad, whose folk answer a visitor's needs or "
            "mock mortal life; magi hope the strange symbolism behind "
            "their games preserves something of Pula's founders, the "
            "Colchian war band sent after the Golden Fleece, ruled by a "
            "family of sorcerers, one of whom could turn back age.",
            "The building faeries (Diviæe, see the Bestiary) are small "
            "and weak alone but achieve wonders together; given stone "
            "and a good reason they can raise a hall overnight, and what "
            "they build has a useful aura. Attempts to tame and spread "
            "them had mixed results and have stopped. The surest, and "
            "most perilous, way to their help is to go down into their "
            "town and find their rulers, or to bargain with the watchers "
            "at a play on an auspicious night.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "temple_of_augustus",
        "The Temple of Augustus, Pula",
        inside=istria,
        aura=5,
        summary=paragraphs(
            "A temple to the goddess Roma in the middle of Pula, with a "
            "Magic aura of 5; Seekers are sure it was once a place of "
            "power of the Cult of Mercury, but the town around it makes "
            "quiet study hard. Old amphorae keep working up out of the "
            "ground nearby, to be knocked by gardeners and passers-by; "
            "they hold vis but are awkward to gather.",
            "King Solomon of Hungary, a folk hero rumoured to have "
            "founded the Scholomance, is buried in Pula.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "mount_klek",
        "Mount Klek",
        inside=istria,
        realm="Infernal",
        summary=paragraphs(
            "A mountain east of the Histrian lands, where witches and "
            "corrupted elves dance to demonic music. Its summit has a "
            "strong Infernal aura (no number is given) and perhaps a "
            "gate into Hell; witches are common all round it.",
            "Local lore: a dust devil spinning up at a crossroads by "
            "night is two witches fighting, tearing at each other's hair, "
            "and a traveller must not walk through it; whoever has, comes "
            "back next morning and lays a stone on the spot to give away "
            "any curse he took.",
        ),
        **KNOWN_REGION,
    )
    cres = _add(
        transylvania,
        "cres",
        "Cres",
        inside=istria,
        aura=1,
        summary=paragraphs(
            "An island ruled by Venice, one of a chain that folklore says "
            "the enchantress Medea made from the torn body of her brother "
            "Aspytrus, sent after the Golden Fleece and her lover; its "
            "faeries swear the tale is true, and the faint Magic aura of "
            "1 over most of the island seems to bear it out.",
            "Rego vis is cast up on one beach after storms, among ships' "
            "flotsam, building up through the year rather than coming "
            "once; a well of blood gives a large Corpus source. Both are "
            "Shrouded Bay's.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "shrouded_bay_villa",
        "The Villa of Shrouded Bay",
        inside=cres,
        aura=6,
        summary=(
            "The Histrian magi's large villa on Cres, hidden by The "
            "Shrouded Glen, in a Magic aura of 6: the oppidum of Shrouded "
            "Bay, pleasanter than Old Histria and the favourite winter "
            "home of its magi, with the Tremere and Mercere fleets' "
            "support works in the bay."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "grave_of_aspytrus",
        "The Grave of Aspytrus",
        inside=cres,
        summary=paragraphs(
            "The palatial tomb where Medea laid her brother after "
            "raising Cres on his body as the focus of her spell. His "
            "servants, too frightened of her father to go home to "
            "Colchis, founded a city near Pula; when Jason cast her "
            "off she lived among them a while, and rid them of a "
            "plague of magical serpents by shutting the snakes into "
            "the tomb.",
            "The magi of Cres leave it alone: Medea's curses may "
            "still guard it, and the serpents inside may be orms, "
            "wingless and legless dragons, or votaress snakes "
            "(zmije zatocnice), clever, vicious faerie snakes sworn "
            "not to sleep through winter until they have killed a man "
            "(see the Bestiary). Loosing a swarm of them just to see "
            "what they guard seems excessive.",
        ),
        secrets=[
            titled(
                "What Medea made of Aspytrus",
                "Some Seekers think Medea made her brother Aspytrus an airy "
                "spirit fit to be patron of a mystery cult, the serpents at "
                "his grave perhaps part of its Ordeals.",
            ),
            titled(
                "The wards on the grave",
                "A few magi desperate for Medea's secret of regeneration have "
                "died to strong wards trying to break into the Grave of "
                "Aspytrus; whether Medea, the Histrians or a cult already "
                "serving Aspytrus set them is unknown.",
            ),
        ],
        **RUMOURED,
    )


# ------------------------------------------------------------- Old Histria


def _old_histria(transylvania: Transylvania, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "The elder of the two Mercere oppida of Istria, and the "
        "Tribunal's Mercere House: its gatekeeper to the west, its chief "
        "negotiator with foreigners, and a recruiting ground, school and "
        "market for the Redcap families. It sits in a much-rebuilt hill "
        "fort above Pazin in a Magic aura of 7. House Tremere bases its "
        "merchant navy and the Tribunal's diplomats here and at Shrouded "
        "Bay; some say the House's spies in the Roman Tribunal are run "
        "from here too, which the Tremere deny.",
        "Histria was a covenant of the Roman Tribunal, claiming the whole "
        "peninsula through its name. Worn down by that Tribunal's endless "
        "politics, its magi came over to Transylvania as foederati, "
        "bringing their outpost on Cres with them. The Tribunal has since "
        "made the camp, where socii now dominate, the place of record for "
        "every sale of vis and enchanted items.",
        "Its members are the same as Shrouded Bay's: eight Gifted magi "
        "between the two, three more who live at the chapter house in "
        "Venice, and many unGifted Redcaps, who are full members and vote "
        "in the oppidum's own ballots. Magi of the two camps often add "
        "Adiran, of the Adriatic, to their names, which the swarm of "
        "same-named Redcaps makes useful.",
        "It is roomy enough for formal gatherings and for the Redcap "
        "families' many projects, but cold and stormy in winter; the "
        "strong aura is what keeps researchers there through the sleet.",
    )
    what_matters = joined_lines(
        "Vis: the mercury pool, a rich Terram source (a child dipped in it gains Visions and often worse Flaws)",
        "Vis: the truffles of the northern Istrian woods (Herbam), sought by faeries, worth their weight in gold",
        "Vis: the Strange Vis, a little Creo in the roof tar of the four corner houses of random villages on Saint John's Eve, collected Tribunal-wide",
        "Register: the place of record for all sales of vis and magic items in the Tribunal, with the master of vis trading's list of promissory notes",
        "Laboratory: Accursius's suite and excellent laboratory, used by Volante",
        "Library: no books named; the Mercere House's records",
        "Items: the House's cache of magic items, and the potent items guarding the fort",
        "Boon: Aura (Magic 7); Fortified site (a layered hill fort)",
        "Hook: Hermetic Services (the Mercere House: Redcaps, the vis register, the Tribunal's envoys)",
        "Hook: Harsh winters",
        "Tension: Harco recognises few of the Tribunal's Redcaps, and none who are vampire-blooded",
        "Tension: the proposed Mercere's Portal to the Venice chapter house",
    )
    notes = paragraphs(
        "Origins. The Incantation of Lightning, usually thought Druidic, "
        "was in fact invented here, as a tool for farming.",
        "The Strange Vis. Folk witches break fevers with a potion of the "
        "roof tar of a village's four outermost houses. Hermetic scholars "
        "found that on Saint John's Eve the tar of the corner houses of "
        "seemingly random villages takes on a little Creo vis, so the tar "
        "of many villages is gathered and tested every year. Odd enough "
        "that it forms only in the Dominion, and only when the four "
        "houses' tar is kept unmixed and complete; odder still, it began "
        "to appear in Istrian villages once Histria joined, as if it "
        "spreads with the Tribunal. Some magi think whatever makes it "
        "knows the Tribunal's border; others scoff.",
        "The vis register. Most Transylvanian magi may not sell vis or "
        "enchanted items abroad; only the socii, the Praeco, the "
        "Tremere Primus, and those acting for them may. Sales need not pass through Old "
        "Histria: matching letters, notarised by a Quaesitor, suffice. "
        "The Praeco's agents may bid for anything of interest to the "
        "Tribunal, which can raise sellers' prices and hurts buyers of "
        "rarities, while buyers of common vis can compare the "
        "speculative promissory notes on file with Old "
        "Histria's vis-trading master. The same bar on sales covers many magical beasts, "
        "letting House Tremere, always after breeding stock for war, "
        "buy exports first and bid on imports.",
        "Mansiones. Mercere rest houses, a day apart on the main roads "
        "between oppida, some secret and for the Order alone, others "
        "half-public and open to merchants and clergy. They are not "
        "oppida, having no resident cives. Small towns of the founders' "
        "descendants have grown round the biggest; since their holders "
        "owe the King of Hungary no fealty this is no trouble yet, but "
        "some heirs are marrying into the lesser nobility.",
        "The Redcap families. Only Gifted Mercere vote in this Tribunal; "
        "in return the Redcaps have been let multiply. An oppidum can "
        "have a 'Redcap' each week if it likes; whole families tour as "
        "players, carrying messages and swaying the common folk with "
        "their plays; retired Redcaps keep businesses in most towns; "
        "magi's spouses are sometimes named Redcaps to give them rights "
        "under Hermetic law. They think of themselves as one big, fond, "
        "odd family of near-magicians, and call each other cousin. House "
        "Mercere formally counts only fifteen Redcaps in Transylvania; "
        "the Tremere reckon about forty-five are needed (two for each "
        "major oppidum, the House's staff, and the retired, trainees and "
        "honorary members). The children of several kinds of local "
        "vampire make good Redcaps, and the House seeks them out; those "
        "not taken become grogs.",
        "Harco. House Mercere has only some 150 members, and the "
        "Tremere wish to add thirty-five Transylvanian Redcaps looks to "
        "Harco like a lever on the House. The local Mercere side with the "
        "Prima, see no reason their children should not all be Redcaps, "
        "and are unmoved by a recluse in Piedmont. The present truce: "
        "Harco accepts the heads of the Redcap families as members, and "
        "the rest as the House's agents, whom Transylvanian magi treat "
        "and call Redcaps. The Roman Mercere find the vampire-blooded "
        "ones creepy and recognise none of them, and Redcaps proud of "
        "heroic blood despise them, though the bloodcaps of the Celtic "
        "lands, faerie-blooded themselves, get on with them. If someone "
        "on the Roman side pushes for control the truce may fail; player "
        "magi could broker a new one.",
        "Stories. The Mercere House's duties are the usual ones "
        "(recruiting, training, supporting and rescuing Redcaps), but at "
        "this scale whole troupes of players or shiploads of messengers "
        "vanish, and every oppidum then gets a formal plea for help that "
        "it would be shameful to ignore. New coloniae in interesting "
        "country may find a small Mercere school bolted on; trainee "
        "Redcaps are always trouble. Histrian magi are the usual envoys "
        "to the domus magnae of the west (Harco, Magvillis, Valnastium, "
        "the Cave of Twisting Shadows), always at least two, one Tremere "
        "and one not; a saga of envoys reaches Autumn covenants, royal "
        "courts and Arab, Cuman and Hebrew sorcerers.",
        "The Venice lodging. Three Gifted members live at the chapter "
        "house in Venice, in the Roman Tribunal, Merit of Tremere among "
        "them; a Mercere's Portal from Old Histria to it has been mooted "
        "for years (see the Tribunal's docket).",
        "Vigilia of Seuthopolis may not be given cases touching the "
        "Histrian oppida, after her censure. The book gives no founding "
        "year and no season. Of the unnamed magi, one is Gifted and in "
        "Istria and two are in Venice.",
    )
    hidden = [
        titled(
            "Pahniro's frailty",
            "Pahniro's frailty is an act: he was a hoplite for twenty years and has killed three magi in single combat.",
        ),
        titled(
            "Pahniro the spymaster",
            "Pahniro may well be the House's spymaster for the Roman Tribunal.",
        ),
    ]
    covenant = b.covenant(
        "Old Histria",
        tribunal=tribunal,
        founded=None,
        place=transylvania.places["old_histria_fortress"],
        aura=7,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        unnamed_magi=3,
        detail=FULL,
        season="Autumn",
    )
    transylvania.covenants["old_histria"] = covenant
    b.book(
        covenant,
        "The library of Old Histria",
        "Other",
        description=(
            "No books are named. The Mercere House keeps the records of "
            "the Redcap families and their messages, and the Histrians' "
            "own working books; the spell Incantation of Lightning was "
            "first written here."
        ),
    )
    b.book(
        covenant,
        "The Register of Vis Sales",
        "Other",
        description=(
            "The Tribunal's record of every sale of vis and magic items "
            "by its magi, kept at Old Histria, with the notarised matching "
            "letters of sales made elsewhere and the master of vis "
            "trading's list of promissory notes on offer."
        ),
    )


# ------------------------------------------------------------ Shrouded Bay


def _shrouded_bay(transylvania: Transylvania, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "The younger Histrian oppidum, a large villa on the Venetian "
        "island of Cres, hidden by The Shrouded Glen in a Magic aura of 6. "
        "Old Histria's magi set up a chapter house here to guard the "
        "island's storm-washed Rego vis, too far from the fort to protect, "
        "against raids by Transylvanian Tremere; when Histria joined the "
        "Tribunal, the settlement became an oppidum too. In law it stands "
        "alone, but the two camps share their members and are close "
        "allies.",
        "Most Histrian magi like it better than Old Histria, above all in "
        "winter, and Accursius, the chief Mercere, lives here. It holds "
        "the support works for the small Mercere and Tremere trading "
        "fleets, and its aedile, Placido, runs the Tremere fleet from it.",
    )
    what_matters = joined_lines(
        "Vis: the well of blood, a major Corpus source, used for the Redcaps' longevity rituals",
        "Vis: Rego washed up on one beach after storms among ships' wreckage, accruing through the year",
        "Laboratory: Accursius's, less good than his suite at Old Histria",
        "Library: no books named",
        "Fleet: the support base of the Mercere and Tremere trading fleets",
        "Boon: Aura (Magic 6); Hidden (The Shrouded Glen)",
        "Hook: Ruled by Venice",
        "Tension: Leviathan, the secret base in the southern Dalmatian isles, is to be opened if Shrouded Bay seems unsafe in war",
        "Tension: the Grave of Aspytrus and its serpents, on the island",
    )
    notes = paragraphs(
        "Naval stories. The Adriatic is the safer of the Tribunal's two "
        "coasts and one of the world's busiest trade lanes. The fleets "
        "have their works here and in a hidden cache somewhere in the "
        "southern Dalmatian isles, Leviathan in the Tremere plans (see "
        "the hidden fortresses). Trade, piracy and salvage stories can "
        "draw on City & Guild. Phillip of Lycaneon, who builds naval "
        "parts, is often here tinkering.",
        "The book gives no founding year and no season. One Gifted member is unnamed.",
    )
    covenant = b.covenant(
        "Shrouded Bay",
        tribunal=tribunal,
        founded=None,
        place=transylvania.places["shrouded_bay_villa"],
        aura=6,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        unnamed_magi=1,
        detail=FULL,
        season="Summer",
    )
    transylvania.covenants["shrouded_bay"] = covenant
    b.book(
        covenant,
        "The library of Shrouded Bay",
        "Other",
        description=(
            "No books are named; the villa holds the working books of the "
            "magi who winter there and of Accursius's laboratory."
        ),
    )


# -------------------------------------------------------- the Histrian magi


def _histrian_magi(transylvania: Transylvania, b: Builder) -> None:
    old = transylvania.covenants["old_histria"]
    bay = transylvania.covenants["shrouded_bay"]
    m = transylvania.magi
    p = transylvania.privileges
    m["accursius"] = b.magus(
        "Accursius Adiran",
        covenant=bay,
        house=MERCERE,
        age=90,
        summary=paragraphs(
            "The chief Mercere: an aged magus who leads the Histrian magi "
            "and the Tribunal's Redcaps after a fashion. He has great "
            "standing and decides which Redcaps get longevity rituals, "
            "but cannot really make the sprawling family obey; long since "
            "reconciled to that, he steers it through yearly meetings of "
            "the heads of the main families. He works at craftwork and "
            "illusion.",
            "Too old to travel without magic, he keeps to his laboratory, "
            "at Shrouded Bay because it is nicer, though his lab there is "
            "worse than the one he leaves to Volante. He can send Redcap "
            "families to help, make weak longevity rituals fit for young "
            "magi, open the House's cache of items, and he collects "
            "favours to spend when a Redcap's trouble goes beyond what the "
            "Code obliges magi to fix.",
            "Every few years the lab-bound life gets too much and he takes "
            "a holiday, famous for embarrassment, scrapes and scandal; "
            "when he vanishes, word goes round the Redcaps to watch for the "
            "Old Man and keep things quiet. He may turn up on one of these "
            "jaunts in a town near the players' oppidum.",
        ),
        traits={"Dutiful": 3, "Finicky": 2},
    )
    p["accursius"] = ("socii", "chief Mercere")
    m["leontine"] = b.magus(
        "Leontine Adiran",
        covenant=old,
        house=TYTALUS,
        age=30,
        summary=paragraphs(
            "The Tribunal's chief negotiator: only thirty, yet one of the "
            "finest communicators in Mythic Europe, encouraged to grow "
            "her gift for diplomacy at the cost of her magic, a bargain "
            "she accepts gladly for now. She works in espionage, and "
            "usually travels with Merit of Tremere. Her task is to "
            "threaten, bribe and persuade, so she seeks out magi with "
            "narrow Affinities for help, and pays in introductions to "
            "the most powerful magi in this and the neighbouring "
            "Tribunals, or in the name of exactly the right person.",
            "She is not Dominic of Tytalus's apprentice but his protégée; "
            "rumour, knowing the Tytalus, invents a passionate affair "
            "seasoned with murder attempts. In truth he enjoys a sharp, "
            "amusing pupil and she a wily mentor and something of a "
            "father. She also sharpens her wits arguing ethics with an "
            "ancient zmaj of Istria.",
        ),
        traits={"Intrigued by other magi": 3, "Loves practical jokes": 1},
    )
    p["leontine"] = ("hospites", "chief negotiator of the Tribunal")
    m["pahniro"] = b.magus(
        "Pahniro Adiran",
        covenant=old,
        house=TREMERE,
        age=110,
        summary=paragraphs(
            "The aedile of Old Histria, an old Tremere near Twilight "
            "given the post as a useful retirement, since few in the "
            "House expect trouble at Histria; he is the House's eyes "
            "on this western gate. He equips mundane spies, is "
            "rumoured to run the House's agents in the Roman "
            "Tribunal, and laughs that off: surely a spymaster would "
            "live in Venice? He says he is only an old man finishing "
            "his talisman as a legacy, with Placido as his lab "
            "assistant.",
            "Anyone breaking the Code nearby may meet him first, "
            "sizing things up before he calls the hoplites and "
            "Quaesitors. A prolific letter writer, he asks Tremere for "
            "help when he wants to look into something without "
            "alarming the Redcaps, and trades news with others for "
            "favours; coloniae often owe senior Tremere aid by their "
            "terms, so players may be bound to serve his whims. The "
            "Mercere often send him after strigons, which he passes "
            "to younger magi.",
        ),
        secrets=[
            titled(
                "Pahniro's frailty",
                "His doddering is misdirection: he served twenty years as a "
                "hoplite and has killed three magi in single combat.",
            ),
        ],
        traits={
            "Brave": 4,
            "Likes fooling people with his old codger act": 3,
            "Dedicated": 3,
        },
    )
    p["pahniro"] = ("cives", "")
    m["placido"] = b.magus(
        "Placido Adiran",
        covenant=bay,
        house=TREMERE,
        age=32,
        summary=paragraphs(
            "The aedile of Shrouded Bay, a young Tremere with an Affinity "
            "for Aquam who runs the House's trading fleet, keeps it ready "
            "for war, and specialises in battle magic at sea. Lately "
            "taken with naval sabotage, he has money to try new ways of "
            "fighting ships and wants partners; keeping even a small navy "
            "supplied means endless dealing with suppliers, their rivals "
            "and the local nobles, so he calls on coloniae with strategic "
            "land or odd faerie resources and on anyone with useful "
            "skills when new ports open.",
            "He loathes pirates with startling zeal. At heart he loves "
            "fights to the death for the thrill, but will not see himself "
            "as a murderer, so he turns the urge on people everyone agrees "
            "deserve it, and invites players with a gift for mayhem or "
            "swift travel to clear pirate nests with him. He is also "
            "Pahniro's lab assistant on his talisman, a service other "
            "Houses think beneath a magus but the Tremere do not.",
        ),
        traits={
            "Hates pirates": 6,
            "Wants to be virtuous": 3,
            "Enjoys killing people": 2,
        },
    )
    p["placido"] = ("cives", "")
    m["priscilla"] = b.magus(
        "Priscilla of Verditius",
        covenant=old,
        house=VERDITIUS,
        age=40,
        summary=paragraphs(
            "A maga of middle years who spends most of her time at Old "
            "Histria brewing longevity potions for the unGifted, a waste "
            "of her talent, she thinks. She has quarrelled with her "
            "teacher, yet has neither the wish to join a frontier "
            "oppidum nor the political skill to win better terms; she "
            "will not call herself Adiran, feeling she does not belong, "
            "and longs for a workshop to make magical puppets in peace.",
            "She hates discussing her rote work, but is a treasure for "
            "anyone founding a colonia: she knows the local law and "
            "custom, the sites of local legend, and the promising places "
            "the Tribunal's survey has marked for settlement, and though "
            "her ties to senior magi are weak, she knows whom to ask.",
        ),
        traits={"Wants to do her own thing": 3, "Proud": 1, "Tentative": 1},
    )
    p["priscilla"] = ("hospites", "")
    m["volante"] = b.magus(
        "Volante Adiran",
        covenant=old,
        house=MERCERE,
        age=60,
        summary=paragraphs(
            "A Gifted Mercere from Italy, likely to follow Accursius when "
            "he dies or fades into Twilight, though she has even less hold "
            "on the local family than he does. Her recent marriage to a "
            "man of an old Redcap line made her less of a stranger, but "
            "pulls her from her work of putting right what goes wrong for "
            "the family; the couple live in Accursius's fine suite and "
            "laboratory at Old Histria. She is skilled in travel and "
            "flying magic, though politics has cut into her studies.",
            "When a Redcap is hurt or killed, she is the one who comes, "
            "and the one to report to. She effectively commands the small "
            "fighting part of the Redcap fleet and lends items that help "
            "Redcaps force a way through hard country. The senior Redcaps "
            "want her to raise an heir or two so the family gets leaders "
            "who know local ways rather than a new magus from Harco each "
            "generation; she will not take apprentices yet, which may "
            "cause friction when she succeeds. She seeks favours for her "
            "House, and a magical bird as her familiar.",
        ),
        traits={"Happy": 3, "Amused by people": 2, "Fierce defender of her family": 2},
    )
    p["volante"] = ("socii", "")
    m["merit"] = b.magus(
        "Merit",
        covenant=old,
        house=TREMERE,
        age=None,
        summary=paragraphs(
            "An older Tremere, shaven-headed and heavily muscled, with a "
            "stare that could split masonry, who lives at the Histrian "
            "chapter house in Venice and usually goes with Leontine on her "
            "missions as the Tremere half of the Tribunal's envoys.",
            "A member of Old Histria lodged in Venice, in the Roman "
            "Tribunal; the book gives no age or privilege.",
        ),
    )
    p["merit"] = ("", "")
    transylvania.aediles["old_histria"] = ["pahniro"]
    transylvania.aediles["shrouded_bay"] = ["placido"]


# ------------------------------------------------------------- mundane world


def _lords(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    p = transylvania.places
    w["serbia_kingdom"] = b.lord(
        "Kingdom of Serbia",
        title="duke",
        wealth="Average",
        seat="Ras",
        ruler="King Stefan II the First-Crowned",
        place=p["serbia"],
        summary=paragraphs(
            "The strongest of the Slav realms, ruled by the Nemanja line, "
            "the grand župans of Raška. Stefan Nemanja, of modest birth, "
            "rose as a Byzantine vassal, fought Hungary for the emperor in "
            "1164, then rebelled and beat a Byzantine army at Pantino; his "
            "1171 league with Venice, Hungary and German princes against "
            "Byzantium fell apart in Serbian feuds, Venetian mutiny and "
            "plague, and Manuel Komnenos besieged Ras and took him to "
            "Constantinople in chains. Oddly, the two became friends, and "
            "Nemanja came home the emperor's strategos and the Serbs' only "
            "lawful ruler. He gave up the throne in 1195, died in 1199 and "
            "was made a saint in 1200, a staunch Orthodox builder of "
            "churches and hammer of the Bogomils.",
            "He passed over his eldest, Vukan, for his second son Stefan, "
            "and Vukan's anger brought civil war in 1204, the year the "
            "Latins took Constantinople. Stefan won, but too weakened to "
            "grab any lost Byzantine land, he bound the Serbian "
            "principalities into one kingdom instead, and in 1217 a papal "
            "legate crowned him king and autocrat of all the Serbian and "
            "coastal lands, the equal of Hungary's and Bulgaria's kings. "
            "His first wife, Eudocia Angelina, the emperor Alexios's "
            "daughter and mother of five of his children, he drove out "
            "for adultery in 1200; his second is Ana Dandolo, the doge "
            "Enrico Dandolo's daughter. With Stefan on the throne and his "
            "brother Sava over the Church, the Nemanjas hold the realm "
            "together, though Serbia's wealth and arms are a shadow of "
            "Hungary's or Bulgaria's, and Hungarian backing for Bosnia and "
            "Croatia, and Serbian feuding, keep Stefan from taking them.",
            "Crowned by both Churches' representatives, Stefan has a Magic "
            "Resistance of 10 and, as a king of Slav blood, the Divine "
            "Shapeshifter Virtue: he can become a wolf, a lion, or even a "
            "dragon, as he pleases.",
            "Two custos envoys of Kezdö Válasz attend his court with the "
            "Tribunal's leave, reporting to Essedarius and Leona: never "
            "advisers, never threats, they simply keep the Order in the "
            "king's mind and let slip, over dinner, the news of Hungary, "
            "Bulgaria, Latins and Greeks, giants, vampires and stirring "
            "dragons. Their careful reports go to Kezdö Válasz and on to "
            "Coeris, often carried by young Tremere. A seed: the pair are "
            "framed for some crime and await execution in Stefan's "
            "dungeon, their reports seized; the players must find who "
            "framed them and why.",
        ),
    )
    w["bosnia_banate"] = b.lord(
        "Banate of Bosnia",
        title="duke",
        wealth="Poor",
        seat="Vrhbosna",
        ruler="The Ban of Bosnia",
        place=p["bosnia"],
        summary=paragraphs(
            "A frontier province ruled by a ban, a rank like a duke's or "
            "a Serbian grand župan's; the present ban, whom the book does "
            "not name, is the King of Hungary's vassal, and the king holds "
            "the real power. Bosnia is weaker than Serbia, and Hungary "
            "keeps Stefan from swallowing it.",
            "The king's letters order Bosnia's church to purge its "
            "Patarians; it answers that there are no heretics in Bosnia. "
            "The pope (Honorius III; the book says Honorius II) has sent "
            "a legate urging Andrew II to crusade, knights are mustering "
            "and preachers denounce the heretics, and House Tremere, "
            "barred from meddling yet sure a crusade could remake the "
            "Tribunal, cannot decide what to do (see the Bosnian crusade "
            "among the threats). In history nothing comes of it until "
            "1237.",
        ),
    )
    w["croatia_banate"] = b.lord(
        "Banate of Croatia",
        title="duke",
        wealth="Average",
        seat="Knin",
        ruler="The Ban of Croatia and his twelve deputies",
        place=p["croatia"],
        summary=paragraphs(
            "Croatia under the Árpád kings of Hungary since 1091: the "
            "Croats run their own affairs within the limits of vassalage, "
            "through a ban and twelve deputies who govern and lead the "
            "army. They insist the King of Hungary has no say unless he "
            "stands on Croatian soil and that no Hungarian may settle "
            "there, claims that are more story than truth. To Hungary it "
            "is a buffer in the west against the grasping Italian "
            "provinces and the Empire. Most of its coast pays tribute to "
            "Venice, and the nobles of Knin do nothing about it.",
        ),
    )
    w["venice"] = b.lord(
        "Republic of Venice",
        title="duke",
        wealth="Wealthy",
        seat="Venice",
        ruler="The Doge of Venice",
        place=p["slavs"],
        summary=paragraphs(
            "The merchant republic across the Adriatic, outside the "
            "Tribunal, which holds much of its coast: Zadar since 1202 "
            "(by a sham treaty since 1205), Dubrovnik since 1205, and the "
            "island of Cres, where Shrouded Bay stands. Most of the "
            "Croatian shore pays it tribute, and Dubrovnik is a base for "
            "its war galleys. The Histrian oppida keep a chapter house in "
            "the city.",
        ),
    )


def _churches(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    p = transylvania.places
    w["studenica_monastery"] = b.church(
        "Studenica Monastery",
        church="Monastery or nunnery",
        order="Orthodox",
        ruler="Archbishop Sava Nemanja",
        answers_to=w["serbia_kingdom"],
        place=p["studenica"],
        summary=paragraphs(
            "The royal monastery at the head of the Raška, centre of the "
            "Serbian Church and seat of its archbishop, holding St Stefan "
            "Nemanja's oil-weeping tomb (see the place).",
            "Sava, born Rastko, Nemanja's youngest son, matters to the "
            "Serbs perhaps more than his royal brother. He fled his "
            "family's quarrels to the monks of Mount Athos, came back to "
            "Studenica in 1208 to build up the Serbian Church, and in 1219 "
            "won from the Greek patriarch its independence, the right to "
            "choose its own bishops, and was himself consecrated its "
            "archbishop. He wrote the Nomocanon, the great book of church "
            "law every Slavic church uses. Blessed by God, he has the "
            "Holy Method Invocation, with Wonders, Blessing and "
            "Adjuration among his Holy Powers (see Realms of Power: The "
            "Divine).",
        ),
    )
    w["mostre_school"] = b.university(
        "The Cathedral School of Mostre",
        school="Cathedral school",
        place=p["bosnia"],
        summary=(
            "The cathedral school of the Bosnian Church at Mostre, with "
            "Veszprém's the nearest thing the region has to a university: "
            "it teaches theology, cosmology, ethics and medicine."
        ),
    )


def _towns(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    p = transylvania.places
    serbia, venice = w["serbia_kingdom"], w["venice"]
    bosnia, croatia = w["bosnia_banate"], w["croatia_banate"]

    def town(key: str, name: str, summary: str, **kw: Any) -> None:
        w[key] = b.town(name, summary=summary, **kw)

    town(
        "ras",
        "Ras",
        "Serbia's capital, in the middle of Raška, the Nemanja family's "
        "own district. Serbian troops took it from Byzantium in the "
        "Hungarian-Byzantine war of 1127 to 1129; burnt and rebuilt, it "
        "keeps little of the old town. New stone walls crown a gorge "
        "above the crossing of the main roads east-west and north-south. "
        "Smaller than Hungary's or Bulgaria's capitals, Ras with Novi "
        "Pazar is still the kingdom's political, cultural and religious "
        "centre.",
        charter="Noble lord",
        ruler="King Stefan II the First-Crowned",
        answers_to=serbia,
        place=p["serbia"],
    )
    town(
        "novi_pazar",
        "Novi Pazar",
        "The 'new bazaar', a young trading town at the crossroads below "
        "Ras, which merchants prefer to the fortress: the royal market, "
        "though Ras's walls far above do not shelter it. The king's law "
        "holds, but trade is freer than elsewhere, so goods and people "
        "of every sort mix there. A backwater with few foreigners, it is "
        "where news is swapped and tales told, and a favourite spot for "
        "magi to meet agents and companions discreetly.",
        charter="Noble lord",
        answers_to=serbia,
        place=p["serbia"],
    )
    town(
        "dubrovnik",
        "Dubrovnik",
        "Ragusa to the Italians: a lovely Adriatic port living on sea "
        "trade, walled in stone from its Byzantine days with double "
        "walls, round and square towers and attached forts, a wonder of "
        "the age. It once rivalled Venice, Genoa and Amalfi, and its "
        "riches undid it: Venice took it in 1205, and it now pays "
        "tribute and harbours Venetian galleys. Natives and occupiers "
        "dislike each other, down to the city's very name; some look to "
        "the Nemanjas for help, others to Byzantium. No blood has been "
        "shed yet, unlike Zadar, but House Tremere watches it closely.",
        charter="Commune",
        answers_to=venice,
        place=p["serbia"],
    )
    town(
        "vrhbosna",
        "Vrhbosna",
        "Bosnia's chief town, the forerunner of Sarajevo: seat of the "
        "ruling family and centre of the Bosnian Church, with one of "
        "House Mercere's oldest mansiones (see the place).",
        charter="Noble lord",
        ruler="The Ban of Bosnia",
        answers_to=bosnia,
        place=p["bosnia"],
    )
    town(
        "banja_luka",
        "Banja Luka",
        "The 'duke's meadow', one of Bosnia's largest settlements, in the north-west.",
        charter="Noble lord",
        answers_to=bosnia,
        place=p["bosnia"],
    )
    town(
        "zenica",
        "Zenica",
        "One of Bosnia's largest settlements, on the River Bosna.",
        charter="Noble lord",
        answers_to=bosnia,
        place=p["bosnia"],
    )
    town(
        "knin",
        "Knin",
        "The old royal capital of Croatia, at the source of the Krka on "
        "the site of the Roman camp of Burnum, under a mighty fortress. "
        "It stands for Croatian unity on a coast Venice dominates and is "
        "counted the steadying hand of the Croatian shore, yet it shows "
        "Croatia's weakness too: the coast pays Venice tribute and Knin's "
        "nobles sit still.",
        charter="Noble lord",
        answers_to=croatia,
        place=p["croatia"],
    )
    town(
        "zadar",
        "Zadar",
        "Zara to the Italians, the richest port of the Croatian coast "
        "and the King of Hungary's by right. Crusaders sacked it in "
        "1202 and Hungary did little to dislodge the Venetians; a loyal "
        "Croatian noble won it back two years later, but within a year "
        "Venice held it again, this time by a treaty with the city "
        "council making them overseers instead of occupiers. Everyone "
        "knows the treaty is a sham: the wealth has only changed hands, "
        "which galls the locals more, and violence flares nightly on the "
        "docks and in the alleys, breeding Infernal auras (see the night "
        "streets). In history the risings go on for two centuries, until "
        "Venice gives the city back in 1358.",
        charter="Commune",
        answers_to=venice,
        place=p["croatia"],
    )
    town(
        "pula",
        "Pula",
        "An old Roman town of the Istrian coast, founded (its faeries "
        "say) by the Colchians who came after the Golden Fleece, over "
        "the faerie town of Diviægrad. It has the faeries' roofless "
        "arena and the Temple of Augustus, and King Solomon of Hungary "
        "lies buried there.",
        charter="Commune",
        place=p["istria"],
    )


def _factions(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    p = transylvania.places
    w["bosnian_church"] = b.faction(
        "The Bosnian Church (the Patarians)",
        faction="Faith or sect",
        decides="A council",
        ruler="The djed",
        place=p["bosnia"],
        rules="Bogomil doctrine; a loose network of monastic houses",
        wants="To be left alone between Rome and Constantinople",
        offers="Burials, and a school at Mostre",
        summary=paragraphs(
            "Bosnia's own church, formed from the Bogomils who lived "
            "through Stefan Nemanja's purge late in the last century, "
            "holding its own ground between the Roman and Greek Churches. "
            "Its people call themselves Patarians and keep the Bogomil "
            "teaching. A bishop, the djed, leads it with a council of "
            "twelve, the strojnici; it is a loose web of monastic houses "
            "(hiža), each under a gost with his own strojnici. It keeps out "
            "of politics and, beyond burials, has little to do with the "
            "Bosniaks.",
            "Serbs and Croats put up with it as they put up with each "
            "other's rites, but Hungary does not, and a crusade is "
            "gathering against it.",
        ),
    )
    w["redcap_families"] = b.faction(
        "The Redcap Families",
        faction="Family",
        decides="A council",
        ruler="Accursius Adiran",
        place=p["istria"],
        members=15,
        rules="Heads of the main families meet yearly under the chief Mercere; members call each other cousin",
        wants="Recognition by Harco of all their kin as Redcaps",
        offers="Messages every week, travelling players, news, propaganda, guides in war",
        summary=paragraphs(
            "The Tribunal's sprawling Redcap clans, centred on Old "
            "Histria: messengers, touring players who carry letters and "
            "plays that sway the common folk, retired Redcaps keeping "
            "shops in most towns, and magi's spouses named Redcaps for "
            "the rights it gives them. Harco counts only fifteen proper "
            "Redcaps in Transylvania, the heads of families among them; "
            "the rest serve as the House's agents. Children of the local "
            "vampires, with their small useful powers, are sought out as "
            "recruits, and Harco will not accept those.",
            "Whole families travel together, so when trouble strikes a "
            "whole troupe or a whole ship can vanish, and every oppidum is "
            "then formally asked for help.",
        ),
    )


# ------------------------------------------------------------- finishing


def _lord_named(transylvania: Transylvania, *words: str) -> Neighbour | None:
    """The lord another part made whose name holds all `words`."""
    for neighbour in transylvania.b.saga.neighbours:
        if neighbour.kind == "lord" and all(
            word.casefold() in neighbour.name.casefold() for word in words
        ):
            return neighbour
    return None


def finish(transylvania: Transylvania) -> None:
    """Make the Bosnian and Croatian bans (and Serbia) Hungary's vassals
    once hungary.py has made the kingdom, and put the Pirin Mountains in
    Bulgaria once bulgaria.py has made it."""
    hungary = _lord_named(transylvania, "Hungary")
    if hungary is not None:
        for key in ("bosnia_banate", "croatia_banate"):
            transylvania.world[key].answers_to = hungary.id
    bulgaria = transylvania.places.get("bulgaria")
    if bulgaria is not None:
        transylvania.places["pirin_mountains"].place_id = bulgaria.id


# --------------------------------------------------------------- stats

P = Profile
CROATIAN = "Croatian"
ITALIAN = "Italian"
TRANSYLVANIA = "Area Lore: Transylvanian Tribunal"


#: Each Histrian magus the book sketches without a stat block.
PROFILES: dict[str, Profile] = {
    "accursius": P(
        strong="int per dex",
        weak="qik str",
        arts={"Im": 8, "Cr": 7, "Co": 6, "Mu": 5, "Re": 4, "Vi": 3},
        abilities={
            "Magic Theory": (6, "longevity rituals"),
            "Leadership": (4, "Redcap families"),
            "Craft: Goldsmith": (3, "fine work"),
            "Bargain": 2,
            "Carouse": 2,
            TRANSYLVANIA: 3,
        },
        virtues=[
            vf_art("Affinity with {art}", "imaginem"),
            "Social Contacts",
            "Dutybound",
            "Fragile Constitution",
        ],
        native=ITALIAN,
    ),
    "leontine": P(
        strong="com pre int",
        weak="str sta",
        arts={"Me": 8, "In": 5, "Im": 4, "Re": 3},
        abilities={
            "Charm": (5, "magi"),
            "Etiquette": (4, "magi"),
            "Folk Ken": (4, "magi"),
            "Intrigue": (4, "negotiation"),
            "Guile": 3,
            TRANSYLVANIA: 2,
        },
        virtues=[
            "Gentle Gift",
            "Mentor",
            "Poor Formulaic Magic",
            "Busybody",
            "Dutybound",
            "Overconfident (Minor)",
        ],
        native=CROATIAN,
    ),
    "pahniro": P(
        strong="int pre sta",
        arts={"Me": 9, "Im": 6, "In": 6, "Pe": 6, "Re": 5, "Co": 4, "Vi": 4},
        abilities={
            "Intrigue": (5, "spies"),
            "Guile": (4, "playing the old codger"),
            "Penetration": (4, "Mentem"),
            "Code of Hermes": 4,
            "Single Weapon": 3,
            TRANSYLVANIA: 3,
        },
        virtues=[
            vf_art("Affinity with {art}", "mentem"),
            "Social Contacts",
            "Hermetic Prestige",
            "Twilight Prone",
        ],
        native=CROATIAN,
    ),
    "placido": P(
        strong="sta dex qik",
        weak="com",
        arts={"Aq": 9, "Pe": 6, "Re": 6, "Ig": 3, "Cr": 3},
        abilities={
            "Profession: Sailor": (3, "warships"),
            "Leadership": (3, "sailors"),
            "Bargain": (2, "naval stores"),
            "Single Weapon": 2,
            "Penetration": 3,
        },
        virtues=[
            vf_art("Affinity with {art}", "aquam"),
            "Hatred",
        ],
        native=CROATIAN,
    ),
    "priscilla": P(
        strong="int dex per",
        weak="pre",
        arts={"Cr": 8, "Co": 7, "Vi": 4, "Mu": 4, "Te": 3, "He": 3},
        abilities={
            "Magic Theory": (5, "longevity rituals"),
            "Medicine": (3, "longevity"),
            "Craft: Woodcarving": (3, "puppets"),
            TRANSYLVANIA: (3, "sites for coloniae"),
            "Code of Hermes": (2, "Transylvanian custom"),
        },
        virtues=["Inventive Genius", "Proud (Minor)"],
        native=ITALIAN,
    ),
    "volante": P(
        strong="pre com sta",
        arts={"Re": 7, "Au": 6, "Mu": 6, "An": 4, "Co": 4},
        abilities={
            "Leadership": (3, "Redcaps"),
            "Folk Ken": (3, "Redcaps"),
            "Intrigue": (3, "House politics"),
            "Ride": 2,
            TRANSYLVANIA: 2,
        },
        virtues=["Well-Traveled", "Close Family Ties"],
        native=ITALIAN,
    ),
    "merit": P(
        strong="sta str pre",
        weak="com",
        arts={"Pe": 7, "Me": 6, "Re": 5, "Co": 5, "Ig": 4},
        abilities={
            "Leadership": (3, "intimidation"),
            "Brawl": 3,
            "Single Weapon": 3,
            "Folk Ken": 2,
            "Etiquette": 2,
        },
        virtues=["Piercing Gaze", "Dutybound"],
        age=70,
        native=ITALIAN,
    ),
}


def stats(transylvania: Transylvania) -> None:
    """Generated stats for the Histrian magi, none of whom has a printed
    stat block."""
    b = transylvania.b
    for key, profile in PROFILES.items():
        character = transylvania.magi.get(key)
        if character is not None:
            apply(b, character, profile)
