"""The Tribunal's two networks of hidden fortresses, as of 1220: the
oppidum of Kezdö Válasz, whose magi are pledged to answer any threat
first, with its permanent fort at Sarmizegethusa, Leona's fort in the
Prokletije and the forts it has left behind, its four named magi and
the treasure of Decebalus; and the zenodochia, the Tribunal's hidden
roadside hospitals for magi, as one sketch covenant with their
hospitals as places (the Bran Pass, a plague house, and the lost one at
Zadar), their items and their Curantis; with Leviathan, House Tremere's
mothballed naval cache, as a sketch, and Gigas, a Theban covenant the
Tremere use as a cat's paw, as a place with notes. In paraphrase of
Against the Dark chapter seven (with chapter five for Zadar and
Leviathan, chapter four for Gigas and chapter six for the Bran Pass).

Keys: covenants["kezdo_valasz"], ["zenodochia"] and ["leviathan"];
magi["essedarius"], ["leona"], ["adulio"] and ["neculai"]; places
["sarmizegethusa"], ["prokletije_fort"], ["old_forts"], ["iron_gate"],
["vargyas"], ["bran_zenodochium"], ["plague_house"],
["zadar_zenodochium"], ["leviathan"] and ["gigas"]. The places are made
without a region and put in theirs in `finish`, once the region parts
have built."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models import InstilledEffect
from ...models.world import FULL
from ..builder import joined_lines, paragraphs, vf_art
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from ..builder import Builder
    from . import Transylvania

BJORNAER = "house_bjornaer"
TREMERE = "house_tremere"

#: The lead line of an oppidum's notes, before its secrets.
KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}

#: Each place's region (a key of places), and the names of a place
#: another part may have made there to stand inside instead.
REGIONS: dict[str, tuple[str, tuple[str, ...]]] = {
    "sarmizegethusa": ("transylvania", ()),
    "prokletije_fort": ("slavs", ("Prokletije",)),
    "old_forts": ("transylvania", ()),
    "iron_gate": ("transylvania", ("Iron Gate",)),
    "vargyas": ("transylvania", ()),
    "bran_zenodochium": ("transylvania", ("Bran Pass",)),
    "plague_house": ("transylvania", ()),
    "zadar_zenodochium": ("slavs", ("Zadar",)),
    "leviathan": ("slavs", ()),
    "gigas": ("bulgaria", ()),
}


def _add(transylvania: Transylvania, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = transylvania.b.place(name, **kw)
    transylvania.places[key] = place
    return place


def build(transylvania: Transylvania) -> None:
    b = transylvania.b
    tribunal = transylvania.tribunal
    if tribunal is None:
        tribunal = next(iter(b.saga.tribunals), None)
    assert tribunal is not None, "tribunal.py builds the Tribunal first"
    _fort_places(transylvania)
    _kezdo_valasz(transylvania, b, tribunal)
    _zenodochium_places(transylvania)
    _zenodochia(transylvania, b, tribunal)
    _leviathan(transylvania, b, tribunal)
    _gigas(transylvania)


# ---------------------------------------------------------- the forts


def _fort_places(transylvania: Transylvania) -> None:
    _add(
        transylvania,
        "sarmizegethusa",
        "Sarmizegethusa Fort",
        aura=3,
        summary=paragraphs(
            "The first fort Norsius built, raised in the ruins of "
            "Sarmizegethusa, the palace of the Dacian king Decebalus in "
            "the second century, near the heart of the Tribunal. It is "
            "Kezdö Válasz's one fixed home and the only fort never "
            "abandoned at the seven-year move: it keeps a standing staff, "
            "two laboratories traditionally the leader's and his "
            "partner's (often empty, since both have other labs where "
            "their sanctum markers hang), and the oppidum's casting "
            "tablets, vis stores and spare gear. The magi gather here "
            "every 12 August.",
            "Like every Kezdö fort it is a two-storey stone block with one "
            "door, slit windows and a taller watchtower at one corner: a "
            "kitchen and great hall below, and stairs in the thickness of "
            "the walls, one up to the upper floor and the tower, one down "
            "to the cellars. Forts are always set in a Magic aura; the "
            "book gives no strength (5 is the pack's).",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "prokletije_fort",
        "The Prokletije Fort",
        aura=3,
        summary=paragraphs(
            "Leona's new fort in the Prokletije, the 'Accursed Mountains' "
            "of southern Serbia at the far end of the Dinaric Alps, near "
            "the source of the Erenick River, where Macrobius was killed "
            "by a griffin. Remote and hard to reach, it is her base for "
            "hunting griffins; her sodales grumble that it wastes the "
            "oppidum's casting tablets and vis, and Essedarius promises "
            "it will be given up once her anger cools. Neculai has been "
            "sent to call on her. Magic aura, strength not given (4 is "
            "the pack's).",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        transylvania,
        "old_forts",
        "The Abandoned Forts of Kezdö Válasz",
        ruined=True,
        summary=paragraphs(
            "Forts Kezdö Válasz has left behind in the seven-yearly "
            "moves, scattered across the Tribunal in places that no "
            "longer interest it. A fort that drew mundane notice is "
            "cleared away, and one that drew supernatural notice is "
            "destroyed, by casting tablets made for the purpose; "
            "others are left standing for later use, or simply "
            "because the tablet to destroy them was not to hand. "
            "Abandoned forts are usually left empty. All were built in "
            "Magic auras, but auras change: some are still Magic, a "
            "few are now Faerie, and one or two Infernal. The book "
            "dates none of them.",
            "Story seeds: wandering coloniae who know the oppidum's "
            "ways may squat in one, and if a powerful one settles in a "
            "fort the oppidum wants back, the youngest members are "
            "sent to deal with it; giants looking for a home near a "
            "village, a magical dragon in a mountain fort, or knights "
            "or bandits looking for a refuge may move in too.",
        ),
        secrets="Whether a fort left standing still belongs to Kezdö Válasz "
        "once its magi have gone is an open question.",
        **KNOWN_LOCALLY,
    )
    _add(
        transylvania,
        "iron_gate",
        "The Iron Gate",
        summary=paragraphs(
            "The gorge where the Danube cuts between the Carpathian and "
            "Balkan mountains, dividing its upper and lower valleys; one "
            "of the places Kezdö Válasz might build a fort. Remnants of "
            "the Bridge of Apollodorus, built under Trajan and broken a "
            "century later, still stand, and ghostly legionaries are said "
            "to march across it under the full moon.",
            "Story seed: fearing war between Hungary and the Bošnjanin, "
            "Essedarius gives young magi vis and casting tablets to raise "
            "a fort here, and wonders whether a regio still holds a "
            "magical copy of the bridge, which would account for the "
            "ghosts.",
        ),
        **RUMOURED,
    )
    _add(
        transylvania,
        "vargyas",
        "The Vargyas River",
        summary=paragraphs(
            "A small river running off the western slopes of the "
            "Hargitta mountains, which might be the lost Sargetias. "
            "When Trajan marched on Dacia in 105, Decebalus had "
            "captive Romans turn the Sargetias aside, sealed his and "
            "his nobles' gold and silver into its bed under stones, "
            "let the water back, hid more in caves along its banks, "
            "and killed the workmen. Captured Dacian nobles betrayed "
            "the secret, but a Byzantine official's report says the "
            "hoard was never recovered and says nothing of the caves. "
            "Neither river nor caves has been found.",
            "Kezdö Válasz has not looked for it: the hoard is small beside Lycaneon's.",
        ),
        secrets="Slavonic dragons line their lairs with gold and silver, and a "
        "treasure this size has very probably drawn one.",
        **RUMOURED,
    )


def _kezdo_valasz(transylvania: Transylvania, b: Builder, tribunal: Tribunal) -> None:
    fort = transylvania.places["sarmizegethusa"]
    summary = paragraphs(
        "Less a place than a vow: its members swear to be first to meet "
        "any threat to the Tribunal and to drop their lab work and study "
        "the moment they are called. It is a chain of forts, not one "
        "site. Every member is a cives (of Coeris), foreign magi too who "
        "would otherwise be foederati, so joining is a quick road to "
        "citizenship though no sure one: Tremere keep the privilege for "
        "good, but magi of other Houses must bargain for it again if "
        "they leave.",
        "The Tremere Norsius founded it in 1008, in the Schism War, as "
        "Primum Responsans, 'first answer', to guard the borders; it is "
        "better known by its Hungarian name. A historian more than a "
        "soldier, he took Trajan's Wall as his model: since no wall could "
        "ring the Tribunal, he built a few forts in Magic auras near the "
        "frontier, each with two magi ready to ride out while they got "
        "on with their own work. The Schism War never reached "
        "Transylvania, and the forts were never tested. His filius "
        "Gasparus spread them across the whole Tribunal as the Balkan "
        "kingdoms rose, and had each pair move to a new fort after every "
        "Tribunal meeting, every seven years, taking their sanctum "
        "markers and labs; old forts are left, reused or torn down. The "
        "leader traditionally lives in the first fort.",
        "Four forts are active, two magi in each, with about a dozen "
        "staff per fort (men-at-arms, cooks, grooms, servants, craftsmen "
        "and an autocrat), who move the gear when the magi move; a move "
        "takes one or two seasons. Families were once barred and are now "
        "allowed. The oppidum has about 55 grogs in all, many living "
        "apart as agents in courts, towns and churches who report "
        "regularly. Each magus hands his agents rings, bracelets and "
        "charms that, when used, give him a small sign through his Parma "
        "(Essedarius's ring turns his left thumbnail blue when his agent "
        "in Niš calls), and all work on spells and devices for speaking "
        "and travelling at a distance: the oppidum owns devices that "
        "carry a magus instantly to places it holds Arcane Connections "
        "to, and members are urged to learn Rego Corpus spells that do "
        "the same. Horses are a tradition, not a necessity: Norsius made "
        "charms so horses would bear the Gifted, the leader always rides, "
        "and the younger members love the saddle.",
        "Every 12 August, the founding day, the members meet at "
        "Sarmizegethusa for about a week to share news, introduce new "
        "members and assign them forts; with an odd number one fort "
        "holds three, its meeting room made a third lab. Magi who want "
        "to form a vexillation say so there. It is one of the easiest "
        "oppida to join, takes young Tremere and foreigners gladly, and "
        "pairs newcomers with each other or with elders; new members "
        "share its privileges and duties but must follow Essedarius, "
        "who never runs short of errands for them.",
    )
    what_matters = joined_lines(
        "Vis: the oppidum's stockpile at Sarmizegethusa (the book names no source)",
        "Library: casting tablets for the ritual that raises a fort, for generic laboratories, and for one that destroys a fort (Destroy the Fort)",
        "Enchantments: devices that carry a magus at once to places the oppidum holds Arcane Connections to, and the signal charms its agents carry",
        "Boon: Informants (about 55 grogs, many of them agents in courts, cities and churches)",
        "Hook: Dedicated Covenant (sworn to be first against any threat to the Tribunal)",
        "Hook: Tribunal Border (founded to guard the frontiers)",
        "Tension: Leona's Prokletije fort, which her sodales think a waste",
        "Tension: Neculai's reports to Clan Sirnas on House Tremere",
        "Tension: Adulio's eagerness for war, censured twice",
    )
    notes = paragraphs(
        "The forts. Besides Sarmizegethusa and Leona's Prokletije fort, "
        "two more are active, their magi left for the troupe to make. A "
        "fort can stand anywhere a story needs one, since magic raises "
        "and razes them easily; the book suggests the Bran Pass, the "
        "Madara Plateau, the Black Sea coast north of Varna, the "
        "Adriatic coast where Serbia meets the Despotate of Epirus, the "
        "Iron Gate on the Danube, the steppe beyond the Carpathians where "
        "Cuman war bands gather, and the Bulgarian-Byzantine border north "
        "of Adrianople. After each Tribunal the magi choose new sites "
        "and build a fort where none stands; a magus moves his own "
        "specialised lab, and an ordinary one is simply made anew.",
        "Two custos envoys of the oppidum attend King Stefan of Serbia's "
        "court with the Tribunal's leave, reporting to Essedarius and "
        "Leona; their records go to Coeris.",
        "Founded 12 August 1008 (the season given is that of the "
        "founding day). Four of its eight magi are unnamed.",
        "Story seeds: a zmaj breaks into 'The Bones of the Founders', one "
        "of Tablinum's hidden exhibits, and the Curator calls for help, "
        "telling the magi to kill it and look at nothing; Adulio asks "
        "the characters to catch 'Golden Sunshine', a faerie horse seen "
        "on the plain of horses by the upper Danube, privately to see "
        "what trouble such a steed brings before he owns it; and the "
        "treasure of Decebalus may lie in the Vargyas River.",
    )
    kezdo = b.covenant(
        "Kezdö Válasz",
        tribunal=tribunal,
        founded=1008,
        place=fort,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        unnamed_magi=4,
        detail=FULL,
        season="Summer",
    )
    transylvania.covenants["kezdo_valasz"] = kezdo
    b.book(
        kezdo,
        "The casting tablets of Kezdö Válasz",
        "Other",
        language="Latin",
        description=(
            "No books are named. The oppidum keeps many casting tablets at "
            "Sarmizegethusa: several of the ritual that raises a fort, "
            "others that make an ordinary laboratory, and others that "
            "bring a fort down to rubble (Destroy the Fort), with Norsius's "
            "old spells for calming horses under a Gifted rider."
        ),
    )
    m = transylvania.magi
    m["essedarius"] = b.magus(
        "Essedarius",
        covenant=kezdo,
        house=TREMERE,
        age=85,
        summary=paragraphs(
            "Leader of Kezdö Válasz since 1215 and the fourth in its "
            "history, filius of Macrobius, filius of Gasparus, filius of "
            "the founder Norsius; a cives (of Coeris). Tall, thickset and "
            "bald, with brown eyes, he looks thirty-eight and at ease, "
            "wears dark clothes for the saddle, and never goes without "
            "his talisman, an enchanted sword holding several powers to wound "
            "and to act at a distance. A Corpus specialist, he has not "
            "aged a day since his first longevity ritual.",
            "Born in the Order, son of a warrior of Laniena, schooled at "
            "the Scholomance, he has known no life outside House Tremere; "
            "a steady rather than a brilliant pupil, he was picked as "
            "Macrobius's apprentice. When an angry griffin met by chance "
            "tore Macrobius apart in 1215, he took the lead.",
            "Untested so far, he watches the growing quarrel between "
            "Bosnia and Hungary and dreads the slaughter a crusade would "
            "bring; he knows the Hungarian knights who cross the border to "
            "kill Patarians, tells his agents to keep clear of them, and "
            "will protect his Bosnian spies. To show his commitment he "
            "lives in the field, in a camp with six armed grogs, rather "
            "than in his fort; some say he should be in his lab instead. "
            "He has given Adulio a magic bridle that calms a horse so it "
            "will carry a magus.",
        ),
        traits={"Steadfast": 3, "Thoughtful": 2, "Cheerful": 1},
    )
    m["leona"] = b.magus(
        "Leona",
        covenant=kezdo,
        house=TREMERE,
        age=106,
        summary=paragraphs(
            "Essedarius's partner, who took the place of her old partner "
            "Macrobius; a cives (of Coeris), looking fifty-six. Of middle "
            "height and stout, in riding clothes like most of her "
            "sodales, she is a master of Herbam who learns what she needs "
            "by questioning the trees and bushes wherever she goes; her "
            "sigil is a scent of lilac, stronger the greater the spell. "
            "People take her for slow and heavy, but she is quick to act "
            "and quicker to anger. She made many of the oppidum's signal "
            "charms.",
            "She was not with Macrobius when the griffin killed him and "
            "still blames herself; killing that beast did not cool her "
            "rage, and she hunts griffins still, roaming the southern "
            "Dinaric Alps and the Prokletije, where he fell, and has built "
            "a fort there.",
        ),
        traits={"Quick-tempered": 3, "Competitive": 2, "Naturalist": 2},
    )
    m["adulio"] = b.magus(
        "Adulio",
        covenant=kezdo,
        house=TREMERE,
        age=41,
        summary=paragraphs(
            "A cives (of Coeris), looking thirty-six, who joined in 1204, "
            "two months after the Latins took Constantinople: the fall, at "
            "the end of his apprenticeship, convinced him Transylvania was "
            "in danger too, and he means to spare it what crusaders did to "
            "the Theban Tribunal. Thin as a reed and dark-haired, he looks "
            "ready for violence at any moment, and his familiar, a "
            "restless Eurasian lynx called Ucigas ('Killer' in Romanian), "
            "adds to the effect. He favours destructive Auram spells.",
            "Sixteen years with no great threat have disappointed him; "
            "brushes with giants have not sated him. The loudest "
            "warmonger in the oppidum, he sees danger everywhere, and the "
            "Quaesitors have censured him twice, once for needlessly "
            "provoking local faeries and once for deliberately killing a "
            "band of Latin knights raiding out of Epirus; neither changed "
            "him. A horse breeder's son with an eye for good mounts, he "
            "rides with a magic bridle Essedarius made.",
        ),
        traits={"Ambitious": 3, "Restless": 3, "Loyal": 2},
    )
    m["neculai"] = b.magus(
        "Neculai",
        covenant=kezdo,
        house=BJORNAER,
        age=47,
        summary=paragraphs(
            "The oppidum's aedile and a socius (of Domostron), though "
            "the book also says every member is a cives; he looks "
            "thirty-nine. Born in the Carpathian foothills of "
            "Hungary, he was found by a wandering Bjornaer and raised "
            "and apprenticed in the Stonehenge Tribunal; once "
            "gauntleted he longed for home and asked several "
            "Transylvanian oppida to take him, and Kezdö Válasz, "
            "short of an aedile, took him at once, an offer he "
            "accepted without enthusiasm. Small, hawk-like and "
            "beak-nosed, with hair so black it looks blue, he is an "
            "Intellego specialist who can talk to nearly any bird, "
            "beast or fish. His heartbeast is a pern, the honey "
            "buzzard, and he travels on the wing.",
            "He belongs to Clan Sirnas, the Bjornaer guardians, who "
            "distrust House Tremere and expect him to report on it. "
            "He resents that nearly as much as being paired with "
            "Adulio, and will not spy on anyone: he keeps the "
            "Gathering of Twelve Years' business to himself but tells "
            "his sodales he may speak there of what he has seen, and "
            "has attended twice since joining. Essedarius shrugs: the "
            "Tremere have nothing to hide and the Bjornaer nothing to "
            "fear. Essedarius has now sent him to visit Leona in the "
            "Prokletije, to keep her informed and to keep an eye on "
            "her.",
        ),
        traits={"Observant": 3, "Agile": 2, "Grumpy": 2},
    )
    b.link(m["essedarius"], "characters", m["leona"], "Fort partner")
    b.link(m["adulio"], "characters", m["neculai"], "Fort partner, resented")
    b.link(m["neculai"], "characters", m["leona"], "Sent to watch over her")
    p = transylvania.privileges
    p["essedarius"] = ("cives", "Leader of Kezdö Válasz")
    p["leona"] = ("cives", "")
    p["adulio"] = ("cives", "")
    p["neculai"] = ("socii", "")
    transylvania.aediles["kezdo_valasz"] = ["neculai"]


# ------------------------------------------------------- the zenodochia


def _zenodochium_places(transylvania: Transylvania) -> None:
    _add(
        transylvania,
        "bran_zenodochium",
        "The Bran Pass Zenodochium",
        summary=paragraphs(
            "A zenodochium House Tremere built in the Bran Pass, an "
            "important road, atop a sheer cliff at the pass's southern "
            "end. A band of southern knights has lately moved in and "
            "preys on the merchants passing below; their leader, kin at "
            "some remove to the royal house, is a rebel who hopes "
            "to raise the Vlachs against the royal army.",
            "Story seed: the House's elders want it back and send young "
            "magi; killing the knights and hiding the bodies may bring "
            "the king's men, and a subtler way may be wiser.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        transylvania,
        "plague_house",
        "The Plague House",
        summary=paragraphs(
            "A rural zenodochium near a village whose people have found "
            "it and learnt that the sick who lie in its hall usually get "
            "better. They use it as a pest house: at the first sign of "
            "illness the strong men carry the sick there and come back a "
            "month later to collect them or bury them.",
            "Story seed: grogs bring their badly hurt magus in and find "
            "Lucia, a village girl, near death of plague in the hall; the "
            "grogs may take her for an intruder, a servant or a maga, and "
            "the villagers, returning, may think the Gifted stranger "
            "means harm to their refuge, all the more if Lucia has died. "
            "The Tribunal does not mind villagers using it, so long as "
            "they keep it in repair.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        transylvania,
        "zadar_zenodochium",
        "The Lost Zenodochium of Zadar",
        ruined=True,
        summary=paragraphs(
            "After the bloodshed of 1203 the Tremere set up a "
            "zenodochium inside a regio, in a magical lacuna in Zadar, "
            "and, expecting more bloodshed, staffed it with a skilled "
            "surgeon and some helpers. Within months the House lost "
            "touch with them, and the regio itself seems to have "
            "vanished. The search has dwindled, but young magi still "
            "try now and then to find the surgeon. The book gives no "
            "aura.",
        ),
        secrets="Zadar's violence breeds Infernal auras and regiones over its "
        "worst killings; what became of the lacuna and its people is "
        "left to the storyguide.",
        **RUMOURED,
    )


def _zenodochia(transylvania: Transylvania, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "Not an oppidum but a service the Tribunal gives its magi: "
        "hidden safehouses where a magus taken ill or hurt on the road "
        "can find, or be carried by his grogs to, enchanted items that "
        "help him heal or heal him outright. Since they serve magi far "
        "from home, few stand near an oppidum. Most are in the "
        "countryside or the wilds (an empty wooden house by a lonely "
        "track, a cave on a quiet hillside, a hovel among the wheat), a "
        "few in the basements of town buildings, often run by a nearby "
        "oppidum's agents. Usually no one keeps them.",
        "Each holds enchanted items, casting tablets, ordinary supplies "
        "and up to two rooks of Corpus vis. Items and tablets must stay; "
        "vis and supplies must be replaced as soon as the user can. "
        "Grogs may use them, their magus answering for any damage they "
        "do; Redcaps often lodge in them, and a message left in one is a "
        "good way to reach the Redcaps. The Tribunal wants them used and "
        "is lenient with honest mistakes: stealing vis from one is a Low "
        "Crime, though a magus who cannot repay is usually let work off "
        "the debt for the Tribunal; damaging or destroying one on "
        "purpose is a High Crime, while a magus who mends one he "
        "damaged by accident, unasked, is not prosecuted.",
        "The Tremere generals planned the network in the Schism War, "
        "reasoning that one hidden hospital would be found and destroyed "
        "in the end, but a scatter of small ones could not all be, and "
        "that each Tremere should know only a few, in case of capture or "
        "treachery. In theory there are hundreds; many were never built, "
        "and how many stand in 1220, from a dozen to hundreds, and how "
        "keen the Tribunal still is to keep them, is the saga's choice.",
        "The Curantis, elected at each Tribunal for the term until the "
        "next and never twice running, tours them about a season a year, "
        "repairs them, must build at least one new one in his term, and "
        "has a Quaesitor's powers in cases touching them. He draws a rich "
        "vis salary and may requisition vis from the Tribunal's stores; "
        "the elders usually agree on a single candidate before the "
        "meeting. His Notary, chosen by the previous Curantis and serving "
        "as his aedile, is a magus, often a Redcap or a magus fresh from "
        "Gauntlet.",
    )
    what_matters = joined_lines(
        "Vis: up to two rooks of Corpus vis in each zenodochium, to be replaced after use",
        "Enchantments: the Hippocratic Staff, the Bowl of the Honest Traveler, the Chest of Good Food, the Vermin Ward, the Ankh of Moving Forward, and the two wards against disease demons and faeries",
        "Library: casting tablets of Arms of the Salamander, The Rite of Healing and Universal Poultice in each",
        "Hook: Zenodochium (the Minor Hook a covenant takes for one within a day's travel; visited by the Curantis every few years)",
        "Tension: the Bran Pass zenodochium is held by rebel knights",
        "Tension: the Zadar zenodochium and its surgeon are lost",
    )
    notes = paragraphs(
        "Items. The Hippocratic Staff, of twisted hyacinth round an amber, "
        "hangs above the hall's inner lintel with a constant effect, "
        "+9 to Recovery rolls for everyone inside (CrCo 34; the book's "
        "separate Disease Recovery effect is cut by its errata). The Bowl of the Honest "
        "Traveler, a beggar's bowl on a shelf, inclines all inside to "
        "honesty (ReMe 29, no Penetration): a would-be thief must fail a "
        "Personality roll against 12 to steal. The Chest of Good Food "
        "keeps a man-month of food from spoiling (CrAn(He) 24); users "
        "should restock it. The Vermin Ward, a statue of a maimed rat, "
        "keeps out animals without Magic Resistance (ReAn 24). The Ankh "
        "of Moving Forward, of silver, heals all wounds and Wound "
        "Penalties while worn but only holds healing back: they all "
        "return when it comes off (CrCo 60, Penetration 12). An enchanted "
        "cross over the door bars demons of Might 10 or less, and an iron "
        "horseshoe bars faeries of Might 10 or less (ReVi 35 each, "
        "Penetration 12). The casting tablets hold Arms of the "
        "Salamander (regrows the latest lost limb, 6 pawns), The Rite of "
        "Healing and Universal Poultice (all wounds, and all disease, "
        "for a group, a rook of vis each).",
        "A magus must lower his Parma to be helped, and an unconscious "
        "magus's Parma lapses at the next sunrise or sunset. The book "
        "says a season inside costs 6 Warping Points from the constant "
        "effects (a week for a Light Wound or a month for a Medium one "
        "costs 3); the Definitive Edition's Warping rules govern if they "
        "give a different count.",
        "Finding one: a character who has not been to a nearby "
        "zenodochium rolls Intelligence + Order of Hermes Lore against 9 "
        "after a year in the Tribunal or 12 for a visitor (Tremere +3), "
        "or Intelligence + Area Lore against 12; add 3 where they are "
        "rare. Few magi know where all of them are; the Tremere know "
        "most.",
        "Story seed: the Disease Trap. Someone has swapped a "
        "zenodochium's Hippocratic Staff for an Ague Staff that gives "
        "everyone in the room the ague at every dawn (PeCo 33, a Heavy "
        "Disease Wound), its maker's sigil hidden and a Shell of False "
        "Determinations making it read as the true staff. Who laid the "
        "trap, and for whom?",
        "The book names no Curantis for 1220. The zenodochia have no "
        "magi, aura or founding year of their own.",
    )
    zenodochia = b.covenant(
        "The Zenodochia",
        tribunal=tribunal,
        founded=None,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        season="Summer",
    )
    transylvania.covenants["zenodochia"] = zenodochia
    _zenodochium_items(b, zenodochia)


def _constant(
    name: str,
    arts: str,
    level: int,
    target: str,
    description: str,
    *,
    penetration: int = 0,
    requisites: str = "",
) -> InstilledEffect:
    """A constant effect as Against the Dark prints it: Touch and Sun,
    two uses a day with an environmental trigger (DE p. 258); `level` is
    the effect's own, before those and the Penetration are added."""
    technique, form = ART_PAIRS[arts]
    return InstilledEffect(
        id="",
        name=name,
        technique=technique,
        form=form,
        requisites=requisites,
        range="Touch",
        duration="Sun",
        target=target,
        level=level,
        description=description,
        uses_per_day="2",
        environmental_trigger=True,
        trigger="sunrise and sunset",
        penetration=penetration,
    )


ART_PAIRS = {
    "CrAn": ("Creo", "Animal"),
    "ReAn": ("Rego", "Animal"),
    "CrCo": ("Creo", "Corpus"),
    "ReMe": ("Rego", "Mentem"),
    "ReVi": ("Rego", "Vim"),
}


def _zenodochium_items(b: Builder, zenodochia: Covenant) -> None:
    """The enchanted items and Casting Tablets every zenodochium keeps
    (Against the Dark pp. 98-99), held by the network as one covenant."""
    items = (
        (
            "The Hippocratic Staff",
            "A staff of twisted hyacinth round an amber, hung above the "
            "hall's inner lintel. A magus must lower his Parma to benefit.",
            [
                _constant(
                    "Recovery Effect",
                    "CrCo",
                    30,
                    "Structure",
                    "+9 to Recovery rolls within.",
                ),
            ],
        ),
        (
            "The Chest of Good Food",
            "A chest carved with feasting; holds a man-month of food, "
            "which those who eat from it should replace.",
            [
                _constant(
                    "Preserve the Food",
                    "CrAn",
                    20,
                    "Group",
                    "Food of animal or plant stuff in the chest does not spoil.",
                    requisites="He",
                )
            ],
        ),
        (
            "The Vermin Ward",
            "A carved statue of a mutilated rat.",
            [
                _constant(
                    "Ward Against Vermin",
                    "ReAn",
                    20,
                    "Structure",
                    "Animals without Magic Resistance cannot enter.",
                )
            ],
        ),
        (
            "The Ankh of Moving Forward",
            "A silver ankh. Worn, it heals every wound and Wound Penalty, "
            "but only holds the healing back: they return when it comes off.",
            [
                _constant(
                    "Suspend the Wounds",
                    "CrCo",
                    50,
                    "Individual",
                    "All wounds healed and no Wound Penalties while worn.",
                    penetration=12,
                )
            ],
        ),
        (
            "The Bowl of the Honest Traveler",
            "A pauper's bowl on a shelf; a would-be thief resists with a "
            "Personality roll against 12. No Penetration, so Magic "
            "Resistance ignores it.",
            [
                _constant(
                    "Incline to Honesty",
                    "ReMe",
                    25,
                    "Structure",
                    "Everyone within is inclined to scrupulous honesty.",
                )
            ],
        ),
        (
            "Ward Against the Infernal Agents of Disease",
            "An enchanted cross over the entrance.",
            [
                _constant(
                    "Bar the Demons",
                    "ReVi",
                    25,
                    "Structure",
                    "Demons of Might 10 or less cannot enter.",
                    penetration=12,
                )
            ],
        ),
        (
            "Ward Against Mad Dreams",
            "An iron horseshoe over the entrance.",
            [
                _constant(
                    "Bar the Faeries",
                    "ReVi",
                    25,
                    "Structure",
                    "Faeries of Might 10 or less cannot enter.",
                    penetration=12,
                )
            ],
        ),
    )
    for name, description, effects in items:
        b.device(zenodochia, name, description=description, effects=effects)
    for spell_id, words in (
        (
            "spell_arms_of_the_salamander",
            "Restores the most recently lost limb; 6 pawns of vis.",
        ),
        ("spell_the_rite_of_healing", "Heals all Wounds of a group; a rook of vis."),
        ("spell_universal_poultice", "Cures a group of every disease; a rook of vis."),
    ):
        b.tablet(
            zenodochia, spell_id, description=f"{words} (Against the Dark pp. 98-99)"
        )


def _leviathan(transylvania: Transylvania, b: Builder, tribunal: Tribunal) -> None:
    cache = _add(
        transylvania,
        "leviathan",
        "Leviathan's Cache",
        summary=(
            "A hidden naval base somewhere among the southern Dalmatian "
            "islands, its place undisclosed, where House Tremere keeps the "
            "stores to support its small Adriatic fleet in a war. The book "
            "gives no aura."
        ),
        status="Rumoured",
        known="Locally",
    )
    leviathan = b.covenant(
        "Leviathan",
        tribunal=tribunal,
        founded=None,
        place=cache,
        summary=paragraphs(
            "House Tremere's mothballed naval base on the Adriatic, so "
            "named in its war plans, to be woken in wartime if Shrouded "
            "Bay looks unsafe. The Tremere and the Mercere each run a small "
            "trading fleet on the Adriatic, the safer of the Tribunal's two "
            "coasts and one of the world's busiest seas.",
            "No magus lives there. Phillip of Lycaneon holds an Arcane "
            "Connection to it and would likely move there in a naval war; "
            "with his skill at making ships' parts and the base's "
            "facilities, the House would lack crews, not hulls.",
        ),
        what_matters=joined_lines(
            "Facilities: stores and works to fit out ships, for Phillip's craft",
            "Hook: Superiors (House Tremere's war plans)",
        ),
        notes="The book gives no founding year, aura or season.",
        season="Summer",
    )
    transylvania.covenants["leviathan"] = leviathan


def _gigas(transylvania: Transylvania) -> None:
    _add(
        transylvania,
        "gigas",
        "Gigas",
        aura=1,
        summary=paragraphs(
            "A covenant of the Theban Tribunal, a hunting lodge south-"
            "west of Sofia, well to the north-west of Evredika's "
            "sancta in the Rhodopes. It is House Tremere's thinly "
            "veiled cat's paw among the Theban magi (described in The "
            "Sundered Eagle and the Theban pack), and has been told not to "
            "contest the vis Evredika claims. Not a Transylvanian "
            "oppidum, so not a covenant here. The Theban book gives it "
            "a weak Magic aura (1 here).",
            "Story seed: a hunting party led by a nobleman with a "
            "'pet' white wolf strips all of Evredika's vis sources, "
            "and Gigas is the obvious suspect. If its denials are true, "
            "who is framing it, and why?",
        ),
        secrets="The book leaves the true raiders to the storyguide.",
        **KNOWN_ORDER,
    )


# ------------------------------------------------------------- finishing


def _named(transylvania: Transylvania, words: tuple[str, ...]) -> Neighbour | None:
    """The town or place another part made whose name holds one of
    `words`: a town first, as the likelier home of a hidden house."""
    ours = {transylvania.places[key].id for key in REGIONS}
    found = [
        n
        for n in transylvania.b.saga.neighbours
        if n.kind in ("town", "place")
        and n.id not in ours
        and any(word.casefold() in n.name.casefold() for word in words)
    ]
    found.sort(key=lambda n: n.kind != "town")
    return found[0] if found else None


def finish(transylvania: Transylvania) -> None:
    """Put each place in its region, or in a site another part made
    there (the Bran Pass, Zadar), once the regions are built."""
    for key, (region, words) in REGIONS.items():
        place = transylvania.places[key]
        around = _named(transylvania, words) if words else None
        if around is None:
            around = transylvania.places.get(region)
        if around is not None:
            place.place_id, place.place_level = around.id, 0


# --------------------------------------------------------------- stats

P = Profile
HUNGARIAN = "Hungarian"


#: Each magus the chapter sketches without a stat block, by key.
PROFILES: dict[str, Profile] = {
    "essedarius": P(
        strong="sta pre int",
        arts={"Co": 9, "Re": 7, "Pe": 5, "Cr": 5, "Vi": 4},
        abilities={
            "Leadership": (5, "Kezdö Válasz"),
            "Ride": (4, "long journeys"),
            "Single Weapon": (4, "sword"),
            "Area Lore: Transylvanian Tribunal": (3, "borders"),
            "Intrigue": 2,
        },
        virtues=[vf_art("Affinity with {art}", "corpus"), "Dutybound"],
        native=HUNGARIAN,
    ),
    "leona": P(
        strong="int per sta",
        weak="dex qik",
        arts={"He": 9, "In": 7, "An": 5, "Pe": 4, "Re": 4},
        abilities={
            "Hunt": (4, "griffins"),
            "Ride": 3,
            "Magic Lore": (3, "magical beasts"),
            "Area Lore: Transylvanian Tribunal": (3, "mountains"),
            "Survival": (3, "mountains"),
        },
        virtues=[
            vf_art("Affinity with {art}", "herbam"),
            "Wrathful (Minor)",
            "Hatred (Minor)",
        ],
        native=HUNGARIAN,
    ),
    "adulio": P(
        strong="qik dex sta",
        weak="com",
        arts={"Au": 8, "Pe": 7, "Cr": 4, "Re": 4, "An": 3},
        abilities={
            "Ride": (4, "warhorses"),
            "Animal Handling": (3, "horses"),
            "Single Weapon": 3,
            "Awareness": 2,
        },
        virtues=["Wrathful (Minor)", "Ambitious (Minor)"],
        native="Romanian",
    ),
    "neculai": P(
        strong="per int qik",
        weak="pre",
        arts={"In": 9, "An": 8, "Aq": 4, "Mu": 4, "Co": 3},
        abilities={
            "Animal Ken": (5, "birds"),
            "Area Lore: Transylvanian Tribunal": 3,
            "Awareness": (3, "from the air"),
            "Stealth": 2,
        },
        virtues=["Dutybound"],
        native=HUNGARIAN,
    ),
}


def stats(transylvania: Transylvania) -> None:
    """Generated stats for the four magi of Kezdö Válasz the book names,
    none of whom has a printed stat block."""
    b = transylvania.b
    for key, profile in PROFILES.items():
        apply(b, transylvania.magi[key], profile)
