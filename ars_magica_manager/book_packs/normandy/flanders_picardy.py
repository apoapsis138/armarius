"""Flanders and Picardy, as of spring 1220, in paraphrase of The Lion and
the Lily chapter eight: the two northern realms of the Tribunal, their
wild places and regiones, the living covenants of Florum's line (Florum
in Ghent, the Spider's Palace and Requies Aeterna) with their magi,
libraries and vis, the eremite Norlanus at Laon, and the mundane world
of the Countess of Flanders, the cloth towns, the sees of Picardy, the
abbeys and the factions round them.

The ruined covenant Infelicitas is tribunal.py's, and the oaths that
bind Florum's vassals to it are set in tribunal.py's finish. The
chapter prints no stat block: every magus here gets generated stats
from `PROFILES`, applied in `stats`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...arms import Arms
from ..builder import Builder, paragraphs, secrets
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from . import Normandy

# House ids, so a typo cannot slip into a record.
EX_MISC = "house_ex_miscellanea"
FLAMBEAU = "house_flambeau"
JERBITON = "house_jerbiton"
MERINITA = "house_merinita"
VERDITIUS = "house_verditius"

# The lead line of a covenant's notes, before its secrets.
STORYGUIDE = "What the players do not know."

KNOWN_TRIBUNAL = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY = {"status": "Known", "known": "Locally"}
RUMOURED = {"status": "Rumoured", "known": "Locally"}

#: The Count of Flanders' arms: or, a lion sable.
ARMS_FLANDERS = Arms("Or", charge="Lion", charge_tincture="Sable")


def _lines(*lines: str) -> str:
    """The lines as one text, one entry a line."""
    return "\n".join(lines)


def _add(normandy: Normandy, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and keep it under `key` for the other parts."""
    place = normandy.b.place(name, **kw)
    normandy.places[key] = place
    return place


def build(normandy: Normandy) -> None:
    b = normandy.b
    tribunal = normandy.tribunal
    assert tribunal is not None
    _regions(normandy)
    _flanders_places(normandy)
    _picardy_places(normandy)
    _florum(normandy, b, tribunal)
    _spiders_palace(normandy, b, tribunal)
    _requies_aeterna(normandy, b, tribunal)
    _norlanus(normandy, b)
    _flanders_world(normandy, b)
    _picardy_world(normandy, b)
    _factions(normandy, b)
    _vis(normandy)


def finish(normandy: Normandy) -> None:
    """Set the Countess, Tournai, Arras and Compiègne under the King of
    France, whose record another part makes."""
    king = normandy.world.get("king") or next(
        (
            n
            for n in normandy.b.saga.neighbours
            if n.kind == "lord" and "Philip" in n.name and "King" in n.name
        ),
        None,
    )
    if king is None:
        return
    for key in ("countess_of_flanders", "tournai", "arras", "compiegne"):
        record = normandy.world.get(key)
        if record is not None and record.answers_to is None:
            record.answers_to = king.id


# ---------------------------------------------------------------- places


def _regions(normandy: Normandy) -> None:
    _add(
        normandy,
        "flanders",
        "Flanders",
        summary=paragraphs(
            "The small, flat, low-lying county between the North Sea and the "
            "Scheldt, the Tribunal's northern corner, with the Rhine Tribunal "
            "beyond the river. It matters far beyond its size: it is crowded "
            "with people and sprawling cities, and alone in Mythic Europe it "
            "lives by industry rather than farming, weaving fine woollen cloth "
            "from English wool. It cannot feed itself, and trades cloth and "
            "linen for imported grain.",
            "Once it was empty coastal marsh and creeks. Monasteries came first, "
            "and from the seventh century their monks drained and diked the "
            "land; Baldwin Ironarm, son-in-law of Charles the Bald, was given "
            "the county in 866, and later counts organised landowners into "
            "drainage societies, the Wateringues, and fortified the coast "
            "against the Vikings. Peace in the eleventh and twelfth centuries "
            "brought the wool trade, chartered towns, belfries, and comital "
            "castles in every great city: the chief palace is at Lille, and "
            "the keep of Douai, ringed by huge ramparts, has walls twelve feet "
            "thick.",
            "Serfdom is fading fast here. Patrician families and merchant gilds "
            "run most cities and the wool trade and have wrung power from the "
            "counts, who in turn side with the weavers, spinners and dyers "
            "against them; beneath both seethe the poorly paid workers, so "
            "every level of Flemish society is tense. Most folk speak Flemish, "
            "a Low German tongue.",
            "For the Order this is a backwater dominated by Florum and its "
            "vassals, who keep apart from the rest of the Tribunal and back "
            "the Lotharingian movement. Vis is scarce.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "picardy",
        "Picardy",
        summary=paragraphs(
            "The poorer cousin of Flanders, Normandy, the Ile de France and "
            "Champagne, which surround it: rolling hills and plains with "
            "scattered woods and, in the south-east, most of the Forest of "
            "Cuise. It has neither great trade nor great farmland, but rich "
            "sees, the mighty archbishopric of Reims among them, and many "
            "wealthy abbeys; several of its old Carolingian cities are raising "
            "cathedrals in the new French style.",
            "No single lord rules it. King Philip's hand lies heaviest: since "
            "1180 he has taken Valois, Clermont, Artois and lands about Amiens, "
            "and bishops rule most of the remaining counties. Flemish workers "
            "fleeing their masters have swelled the northern towns, bringing a "
            "young cloth trade and also unrest, which the bishops and the King "
            "put down harshly.",
            "Its few wild places, the Boulonnais coast, the Somme valley, the "
            "Forest of Cuise and the Montagne de Reims, hold most of the "
            "region's vis.",
        ),
        **KNOWN_TRIBUNAL,
    )


def _flanders_places(normandy: Normandy) -> None:
    flanders = normandy.places["flanders"]
    _add(
        normandy,
        "bavacum",
        "Bavacum and the Seven Roads",
        inside=flanders,
        aura=3,
        summary=paragraphs(
            "Deep in the Hainault forest where Flanders meets Brabant and "
            "Picardy, a crumbling milestone stands where seven overgrown Roman "
            "roads meet, and nearby lie the forest-buried ruins of Roman "
            "Bavacum, a supply town and garrison sacred to Mercury, sacked and "
            "left at the end of the third century. A Magic aura of 3 covers "
            "the junction and the ruins.",
            "On any day one of the seven roads is open: whoever takes it walks "
            "clear through the forest and, after a single morning, comes out "
            "within sight of the city at its far end; the other six are the "
            "slow, tangled tracks they look. Which road is open follows the "
            "seven planets, perhaps by some forgotten Mercurian working; the "
            "southern road, to Reims, opens when Mars is ascendant, coming out "
            "of the Forest of Cuise in view of the Porte de Mars. Going "
            "clockwise from due south the roads lead to Reims, Soissons, "
            "Cambrai, Boulogne, Utrecht, Cologne and Trier. Predicting the "
            "open road takes Intelligence + Artes Liberales against 12.",
            "On the Mercuralia, the fifteenth of May, every road is open at "
            "once, and old footprints show in the road surface; each imprint, "
            "carefully dug up, is a pawn of Rego vis.",
        ),
        **KNOWN_REGION,
    )


def _picardy_places(normandy: Normandy) -> None:
    picardy = normandy.places["picardy"]
    _add(
        normandy,
        "boulonnais",
        "The Boulonnais coast",
        inside=picardy,
        summary=(
            "The hills north of Boulogne that make the coast: a windswept wild "
            "country of chalk cliffs, headlands and dry valleys, from whose "
            "clifftops England can be seen on a clear day. One of the region's "
            "few wildernesses of interest to magi."
        ),
        **KNOWN_REGION,
    )
    somme = _add(
        normandy,
        "somme_marshes",
        "The marshes of the Somme",
        inside=picardy,
        summary=(
            "For a dozen miles below Amiens the Somme crawls through a swamp of "
            "peat bog and water meadow too shallow for much river traffic, "
            "home only to a few hamlets of peat-cutters and hunters."
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "blue_springs",
        "The Blue Springs of the Somme",
        inside=somme,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "Enchanted pools scattered about the edges of the Somme marshes, "
            "some beside little-used roads, each with a Faerie aura of up to 3. "
            "Turning shafts of blue light rise from them, and a close look, "
            "unwisely taken, shows laden carriages and other riches circling "
            "slowly in the depths.",
            "Water sprites are said to keep whatever falls in or is caught by "
            "the pools and to beguile travellers; yet a small child who slips "
            "in comes out with lovely blue eyes, and gifts freely given to the "
            "water may be repaid.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        normandy,
        "naours",
        "The Caves of Naours",
        inside=picardy,
        aura=2,
        summary=paragraphs(
            "A few hundred peasants farm dull fields about the village of "
            "Naours, on a limestone plateau six miles north of Amiens, but half "
            "their village lies a hundred feet underground: the muches, a "
            "cave town of hundreds of rooms that can shelter over a thousand, "
            "with more than a mile of streets, a smithy, brewery, bakeries, "
            "stores, byres, stables and a square, reached by chimneys, two "
            "stairways and a steep road. A Magic aura of 2 fills it.",
            "Hiding here from the Vikings, the villagers met a powerful cave "
            "spirit, a genius loci, and swore a pact of mutual protection with "
            "it that both sides still keep. The villagers are shy of showing "
            "their caves to anyone, but they are no pagans and go to the small "
            "church above ground.",
        ),
        **RUMOURED,
    )
    montagne = _add(
        normandy,
        "montagne_de_reims",
        "The Montagne de Reims",
        inside=picardy,
        summary=(
            "A wild, hilly forest beginning at the edge of Reims and running "
            "fifteen miles south to the Marne and twenty-five miles across: "
            "dense trees on a broken limestone plateau of small lakes, "
            "underground streams and chasms. It is poor hunting country, and "
            "the archbishops do not hunt anyway, so wild beasts roam freely. "
            "Several odd sites and vis sources lie within it."
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "grove_of_st_lie",
        "The Grove of St. Lie",
        inside=montagne,
        summary=(
            "On a ridge at the forest's northern edge, looking out over Reims "
            "and the plain, an old Gaulish burial mound stands in a ring of "
            "oaks, with a tiny chapel to St. Lie, a hermit saint of the fifth "
            "century. The pale flowers on the mound yield a few pawns of Creo "
            "vis, a tropaeum of the Tribunal."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "faux_de_verzy",
        "The Faux de Verzy",
        inside=montagne,
        realm="Faerie",
        aura=4,
        summary=secrets(
            "A dark grove of twisted, stunted black beeches in the east of the "
            "forest, with a Faerie aura of 4, which the local peasants avoid.",
            "The wilder stories say a dark, dwarfish folk carry off villagers "
            "who stray in; those who come back bear some deformity and will "
            "not speak of what happened.",
        ),
        **RUMOURED,
    )
    _add(
        normandy,
        "nanteuil",
        "Nanteuil",
        inside=montagne,
        summary=(
            "A remote vale near the heart of the forest where the Knights "
            "Templar keep a priory, an odd site for one, hard to reach and "
            "leading nowhere. The magus Norlanus wrote that he found it to be "
            "a regio, perhaps Divine: leaving the priory as a guest, he came "
            "out into a brighter version of the forest. Others say he merely "
            "had a strong Twilight episode."
        ),
        levels=[
            Builder.level(
                "The lighter forest",
                0,
                "Divine",
                enter="Leaving the priory as a guest, by Norlanus's account",
                notes=(
                    "A brighter, different version of the forest; its aura and "
                    "realm are not given, and whether it exists at all is "
                    "disputed."
                ),
            )
        ],
        **RUMOURED,
    )
    _add(
        normandy,
        "forest_of_cuise",
        "The Forest of Cuise",
        inside=picardy,
        summary=secrets(
            "A great finger of woodland south of Compiègne, some seventy miles "
            "long, reaching from the edge of the Ile de France toward the "
            "Ardennes. Much of it is the French kings' hunting chase: sunny, "
            "open woods of beech and oak over gentle hills, with winding "
            "rivers and ponds, full of deer, wolves and boar, and crossed by a "
            "few roads, many hunting paths and the odd village and monastery. "
            "The abbey of Prémontré lies in a hidden valley within it.",
            "The Tribunal knows of no real faerie presence here; if the forest "
            "has a faerie ruler, it is shy and kindly to mortals.",
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "laon_cliffs",
        "The cliffs of Laon",
        inside=picardy,
        summary=(
            "The rocky flanks of the great mount of Laon, where the eremite "
            "Norlanus of Jerbiton has hidden his sanctum and harvests a small "
            "source of Terram vis, his legacy by the Tribunal's grant for many "
            "years."
        ),
        **KNOWN_TRIBUNAL,
    )


# ---------------------------------------------------------------- Florum


def _florum(normandy: Normandy, b: Builder, tribunal: Tribunal) -> None:
    farm = _add(
        normandy,
        "the_farm",
        "The Farm, Ghent",
        inside=normandy.places["flanders"],
        realm="Faerie",
        summary=(
            "A district on Ghent's southern edge, once a flax farm a mile out "
            "of the city that Florum bought fifty years ago, foreseeing the "
            "city's growth; Ghent has since swallowed it. Almost three hundred "
            "people live there, in good tenements round a great factory. It "
            "stands over an ancient kabouter workshop, which gives it a Faerie "
            "aura (its strength is not given); Prunellie of Merinita chose the "
            "site."
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "Liege of a line of covenants and the leading power of the Order in "
        "the Low Countries, Florum lives by Flanders' new industry. Its name "
        "and badge are the blue flowers of flax. The Tribunal's rules on vis "
        "have split what would elsewhere be one covenant's resources between "
        "Florum and its vassals, binding them in a close alliance; together "
        "they want out of Normandy and are the leading supporters of the "
        "proposed Lotharingian Tribunal, complaining at every meeting about "
        "the rules on mundane interference and raiding.",
        "Founded in 907 as a small Jerbiton House covenant between Bruges and "
        "Ghent, on the site now called the Spider's Palace, it sat out the "
        "Schism War by moving most of its magi into Ghent, where an attack on "
        "them would rouse the Church. Its customs followed the Primi of "
        "House Jerbiton: when one urged city living, the magi returned to "
        "Ghent and founded a vassal at the old site to keep its resources; "
        "when another asked Jerbiton covenants to open their doors, both "
        "admitted magi of other Houses. The covenant is now in Ghent, with "
        "members from many Houses. (The chapter puts the move in the tenth "
        "century; the Tribunal's records and the timeline give 1117, when "
        "the Spider's Palace was founded.)",
        "The covenant's real home is the Farm, an enclosed suburb on Ghent's "
        "southern edge, with smaller holdings across the city gathered over "
        "the centuries. The great factory at its centre is a blind: the cloth "
        "is made there by magic, under illusions, through the gift of a "
        "faerie-blooded family, the Spinnen, and the factory makes that "
        "wealth look ordinary and so lawful under the Peripheral Code. The "
        "tenements round it, finer than most in the new parts of Ghent, "
        "house the staff and their families; all of them know their "
        "landlords as the old de Spinnen family, now headed by Piet de "
        "Spinnen, though not all know they serve magi. The covenant poses as "
        "a few old farming families; no property is ever sold or let to an "
        "outsider.",
        "Membership shifts, usually four to six magi. Two members are living "
        "at the Spider's Palace for its excellent laboratories; four are in "
        "residence: Rhesus of Verditius, who leads the magi, Calvinus of "
        "Jerbiton, Alroy of Flambeau, the covenant's champion, and "
        "Prunellie of Merinita. A Quaesitor, a Tytalan hoplite and a Redcap "
        "are staying as guests, using the covenant as a base while they "
        "look for a site for a House Guernicus covenant should the "
        "Lotharingian Tribunal come about.",
        "Florum has two vassals: the Spider's Palace, nearby and vital to its "
        "work, and Requies Aeterna in Picardy, a covenant in decline. Two "
        "earlier vassals have gone: Lixivia in Champagne (1021 to 1124) and "
        "Alcuin's Auberge, the Mercer House at Tours (1124 to 1197).",
    )
    what_matters = _lines(
        "Income: cloth woven by touch by the Spinnen, almost thirty of them in 1220, sold through international traders and much of it exported in secret",
        "Income: a mundane weaving workshop of the Spinnen's relatives, and a seat in Ghent's Weavers' Guild",
        "Vis: half the harvest of Requies Aeterna, its vassal, sent as a tithe",
        "Vis: Prunellie harvests faeries turned to standing stones in the fields of the Low Countries (Form and amount not given)",
        "Vis: the Spider's Palace keeps the old site's sources for the line",
        "Library: no titles given (see its library record)",
        "Boon: Wealth (the Spinnen's cloth)",
        "Boon: Strong Community (the Farm's families), Mystical Allies (a kabouter tribe)",
        "Hook: City (Ghent), Faerie Aura, Hermetic Politics (the Lotharingian movement)",
        "Hook: Guild (the Weavers' Guild of Ghent), Dark Secret (the Spinnen and the false family)",
        "Duty: each year a small party of covenfolk is sent, by drawing straws, to serve a year at Requies Aeterna; all dread it",
        "Tension: the Tribunal ordered its magical linen factory dismantled in 1081 and dismissed its appeal; in 1088 it was ruled against for upsetting Ghent's economy, the precedent behind the Code's ruling on mundane interference",
        "Tension: Confluensis used Florum's weakness after Alcuin's Auberge fell in 1197 to move the Mercer House to Cunfin",
        "Tension: Fudarus's agents in the Parisian Dyers' Guild are bitter rivals of Florum's",
        "Tension: suspected by some magi of raising the tidal wave of 1134 that opened the Zwin to Bruges; never investigated for want of evidence",
        "Tension: champion needed for Tourneys and raids; Alroy hopes to fight Tytali",
    )
    hidden = _lines(
        "Piet de Spinnen is Petrus, Calvinus's mundane son, born at Valnastium; a mercenary in Italy who faked his death to escape his rivals and was trained by an old Redcap to play the heir of the childless Arne de Spinnen, who was himself a front. The de Spinnens are a fiction the magi keep up.",
        "Two of Piet's children spent a year at the new university in Paris and then went secretly to Valnastium to be trained as servants of House Jerbiton.",
        "Calvinus's 'uncle Calvin' persona, his Italian wife and his daughter brought up by her grandparents are all invented; the daughter newly arrived in Ghent is his apprentice Sophia.",
        "The flax origin legend of the Spinnen is common knowledge in the Low Countries, so anyone with enough clues might guess what the spider-kin are.",
        "The visiting Quaesitor, hoplite and Redcap are scouting for Confluensis's planned Quaesitorial covenant and Mercer House in a Lotharingian Tribunal.",
    )
    florum = b.covenant(
        "Florum",
        tribunal=tribunal,
        founded=907,
        place=farm,
        summary=summary,
        what_matters=what_matters,
        notes=secrets(STORYGUIDE, hidden),
        realm="Faerie",
        unnamed_magi=2,
        season="Summer",
    )
    normandy.covenants["florum"] = florum
    _florum_magi(normandy, b, florum)
    b.book(
        florum,
        "Florum's library",
        "Other",
        description=(
            "No titles are given. Calvinus spends much of his time in his "
            "books, and the covenant's members, drawn from many Houses, "
            "follow their own interests: flax and weaving, urban and faerie "
            "magic, illusion. Vassals have the right to copy from it under "
            "their oath."
        ),
    )


def _florum_magi(normandy: Normandy, b: Builder, florum: Covenant) -> None:
    m = normandy.magi
    m["rhesus"] = b.magus(
        "Rhesus",
        covenant=florum,
        house=VERDITIUS,
        age=85,
        summary=(
            "Leader of Florum's magi: clean-shaven and muscular, looking about "
            "fifty-four. He came from the Roman Tribunal, partly to escape the "
            "professional jealousies of his House and partly because he is a "
            "weaver himself and wanted to study the spider-kin; the magical "
            "uses of flax are his chief interest. He backs the Lotharingian "
            "cause because he is weary of Normandy's ways, which make him "
            "defend resources that any other Tribunal would simply grant him."
        ),
        traits={"Proud": 3, "Dependable": 2, "Stubborn": 1},
    )
    m["calvinus"] = b.magus(
        "Calvinus",
        covenant=florum,
        house=JERBITON,
        age=59,
        summary=secrets(
            "A middle-aged magus with the Gentle Gift, looking about "
            "forty-five. Ghent knows him as 'Uncle Calvin', younger brother of "
            "Piet de Spinnen's late father, back from decades of trade in "
            "Italy, whose money is said to have paid for the Farm's last "
            "building; Piet plainly heeds his advice. A private man who reads a "
            "great deal and is said to speak five languages, he often "
            "negotiates or interprets for his nephew. Trained in urban magic "
            "like many Jerbiton, he is skilled at illusion, at spying on the "
            "covenant's mundane rivals, and at arranging crimes. His "
            "apprentice Sophia is charming and as bookish as he is, so that "
            "her cousins fear she will never marry.",
            "Piet is really his son Petrus. His Italian wife was invented, and "
            "the 'daughter' who has just arrived in Ghent, supposedly raised "
            "by equally invented grandparents, is Sophia.",
        ),
        traits={"Wily": 3, "Aloof": 1},
    )
    m["alroy"] = b.magus(
        "Alroy",
        covenant=florum,
        house=FLAMBEAU,
        age=82,
        summary=(
            "Florum's champion, for Normandy's habit of fighting over "
            "resources means most covenants need one: an older Flambeau, "
            "looking about sixty, with a distinguished war record in the "
            "Levant. Five years ago he decided to take an apprentice and chose "
            "Florum because it was rich, comfortable, far from the Saracens, "
            "and offered the odd Tourney. He has outlived his own "
            "expectations and killed most of what once frightened him; he "
            "hopes raising an apprentice and fighting Tytalus magi will "
            "rekindle him, a man of eager passions trying to shake off a "
            "veteran's boredom."
        ),
        traits={"Brave": 3, "Easily bored": 1},
    )
    m["prunellie"] = b.magus(
        "Prunellie",
        covenant=florum,
        house=MERINITA,
        age=104,
        summary=secrets(
            paragraphs(
                "An elderly maga, looking about sixty-one, who travels the Low "
                "Countries studying their peculiar faerie realm. Here, she "
                "teaches, the old gods and ancestral trees made a pact with the "
                "coming Church: faeries helped spread the Dominion and tame the "
                "forests, teaching men to clear woods, plough, sow wheat and flax "
                "and drive piles for dikes; one brought flax, a gnome invented "
                "starch, and the kabouters, a dwarfish folk, gave a hundred bells "
                "to the missionaries they favoured, and sang the first carillon "
                "of the Low Countries under a gnome's baton. Faeries who refused "
                "were hunted down by saints whom the friendly ones guided, and lie "
                "now as lone stones in the fields.",
                "Her House thinks her interest in urban faeries a little odd, but "
                "she is firmly allied with a tribe of kabouters and has taught "
                "others her urban faerie magic. She picked the Farm's site over "
                "an old kabouter workshop. She backs the Lotharingian Tribunal "
                "because she believes the faeries' strange surrender to the "
                "Divine belongs to Flanders, Brabant and perhaps Frisia alone.",
            ),
            "She could restore the stone faeries but usually harvests them for "
            "vis instead.",
        ),
        traits={"Generous": 3, "Secretive": 1},
    )
    m["piet_de_spinnen"] = b.magus(
        "Piet de Spinnen",
        covenant=florum,
        house="",
        age=None,
        summary=secrets(
            "The head of the de Spinnen family, Florum's landlords and public "
            "face in Ghent, and its willing spokesman. Rivals sneer at him as "
            "old Arne de Spinnen's bastard, which also explains his keen "
            "interest in the Church's works. He has several children, two of "
            "whom spent a year at the new university in Paris.",
            "He is Petrus, the mundane son of Calvinus of Jerbiton, born at "
            "Valnastium; a successful mercenary in Italy who made dangerous "
            "rivals, faked his death, and was trained by an old Redcap to be "
            "the heir the childless Arne needed. He is very content with how "
            "his life has turned out. His two children went on from Paris to "
            "Valnastium to train as servants of House Jerbiton.",
        ),
        type="companion",
    )


# ---------------------------------------------------------------- Spider's Palace


def _spiders_palace(normandy: Normandy, b: Builder, tribunal: Tribunal) -> None:
    site = _add(
        normandy,
        "spiders_palace_site",
        "The Spider's Palace",
        inside=normandy.places["flanders"],
        summary=paragraphs(
            "Florum's original site, a little more than two days' journey "
            "north of Ghent (Florum's history puts the old covenant between "
            "Bruges and Ghent). Here stood the thousand-year-old oak spirit "
            "that guarded the local people and led their ancestress to wed the "
            "spider prince, and here the spider built his bride a palace, "
            "which in time slipped out of the mundane world. The magi use it "
            "as their covenant building.",
            "It was raided several times in Florum's early days.",
        ),
        levels=[
            Builder.level(
                "The palace of the spider prince",
                0,
                notes=(
                    "The faded palace the magi live in, with excellent "
                    "laboratories; the aura and the way in are not given."
                ),
            )
        ],
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "Florum's vassal on Florum's first site, founded in 1117 when the "
        "Jerbiton magi went back to Ghent and wanted to keep their claim to "
        "the site's magical resources. Usually a single magus lives here to "
        "hold that claim; just now two members of Florum are also here, using "
        "its fine laboratories.",
        "Its magi see the need for two covenants on two such close sites, only "
        "so that no other magus may lawfully take the resources, as proof of "
        "what is wrong with Normandy's way of sharing out vis; the covenant is "
        "an eager supporter of its liege in the Lotharingian movement.",
    )
    what_matters = _lines(
        "Vis: the old site's sources, held as seisins for Florum's line (amounts not given)",
        "Labs: excellent laboratories in the faded palace, used by Florum's magi",
        "Boon: Regio (the palace has faded from the mundane world)",
        "Hook: Hermetic Politics (exists to keep a claim; backs the Lotharingian movement)",
    )
    palace = b.covenant(
        "Spider's Palace",
        tribunal=tribunal,
        founded=1117,
        place=site,
        level=1,
        summary=summary,
        what_matters=what_matters,
        unnamed_magi=1,
        season="Summer",
    )
    normandy.covenants["spiders_palace"] = palace
    b.book(
        palace,
        "The Spider's Palace's library",
        "Other",
        description=(
            "No books are named; the covenant is valued for its laboratories, "
            "and its resident magus may copy from Florum's library as a "
            "vassal."
        ),
    )


# ---------------------------------------------------------------- Requies Aeterna


def _requies_aeterna(normandy: Normandy, b: Builder, tribunal: Tribunal) -> None:
    site = _add(
        normandy,
        "old_nesle",
        "The ruins of old Nesle",
        inside=normandy.places["picardy"],
        aura=5,
        summary=paragraphs(
            "The deserted ruins of the old town of Nesle on the plains of "
            "central Picardy, about an unconsecrated graveyard where the "
            "Donatores fought their last great battle against the restless "
            "dead early in the twelfth century. The magic unleashed there left "
            "a Magic aura of 5. A new Nesle has been built a couple of miles "
            "away, and the locals think the ruins haunted.",
            "Beneath the graveyard the Donatores dug catacombs that hold most "
            "of their covenant.",
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "Eternal Rest: a small Winter covenant of the Donatores Requietis "
        "Aeternae, the Givers of Eternal Rest, an Ex Miscellanea tradition "
        "that helps the dead leave the world of the living. It is a vassal of "
        "Florum and of no political weight, though the Quaesitores have "
        "watched it closely. Most Donatores have left; it is little more than "
        "a shell on the site where their tradition began.",
        "In the eleventh century France suffered hauntings and hordes of "
        "walking dead, blamed on a cult of the dead said to be strongest in "
        "Picardy. Early in the twelfth, hedge wizards, clergy and others "
        "banded together and, guided from heaven, went to Nesle, which a band "
        "of undead warriors was ravaging. They won, at the cost of many lives "
        "and the town itself, and some of the hedge wizards stayed among the "
        "ruins lest the dead return. The Quaesitor Muirgheal arranged their "
        "admission to the Order, over the doubts of many Normandy magi; those "
        "who stayed declared a covenant in 1123 and swore fealty to Florum.",
        "As the dead stayed quiet, most of its magi spread across western "
        "Europe to work wherever the dead walked, and the covenant slid into "
        "Winter, though it remains the tradition's spiritual centre and the "
        "home of its library. Two magi remain: the ancient founder Eulogius "
        "and his youngest filius Henri. They barely keep up their sancta and "
        "the library and ignore the world; the townsfolk have forgotten the "
        "battle and see only a haunted ruin, and the Church has lost touch. "
        "Abroad, the magi pass for monks in their plain robes.",
        "Nearly all the covenfolk died or left, and none would come from a "
        "place of such ill repute, so the covenant pays Florum a larger vis "
        "tithe in return for a small party of servants each year, a posting "
        "Florum's covenfolk dread.",
        "Florum expects Requies Aeterna to follow it into a Lotharingian "
        "Tribunal; its magi will go along, expecting the Rhine magi there to "
        "reject vassalage and cancel their oath, which they would not mind.",
    )
    what_matters = _lines(
        "Vis: the site is rich in vis, Perdo and Corpus among it (amounts not given); roughly half goes to Florum as tithe",
        "Library: the noted library of Donatores lore, the tradition's chief repository",
        "Boon: Aura (Magic 5), Hedge Tradition (the Donatores)",
        "Hook: Haunted (reputation), Massacre Site (the battle of Nesle), Indebted (servants from Florum for a larger tithe)",
        "Hook: Beholden (vassal of Florum), Hermetic Politics (the Quaesitores' suspicion)",
        "Tension: the Quaesitores distrust its past dealings with the Church; several Donatores were trained clergy",
        "Tension: magi who distrust the Donatores could plot a Wizard's War on Eulogius to break the covenant and seize its vis, which would drag Florum in",
        "Hook: magi troubled by restless dead may seek its help, but persuading Eulogius or Henri to leave, or even finding the way in, is hard",
    )
    requies = b.covenant(
        "Requies Aeterna",
        tribunal=tribunal,
        founded=1123,
        place=site,
        summary=summary,
        what_matters=what_matters,
        notes=secrets(
            STORYGUIDE,
            "Philip of Atramentum Renatus was formerly a member here, and "
            "other Donatores are scattered across western Europe. Without "
            "Eulogius the covenant would surely fall.",
        ),
        aura=5,
        season="Winter",
    )
    normandy.covenants["requies_aeterna"] = requies
    m = normandy.magi
    m["eulogius"] = b.magus(
        "Eulogius",
        covenant=requies,
        house=EX_MISC,
        age=130,
        summary=(
            "Leader of Requies Aeterna and perhaps the last founder of the "
            "Donatores living; his age is uncertain, and he looks a hundred "
            "and four. His great days of hunting the restless dead are long "
            "past, and Final Twilight is probably near. His worst Twilight "
            "scars are a body slowly turning to a corpse, impossibly gaunt "
            "with dead, withered skin, and a pain in sunlight that keeps him "
            "in his underground sanctum. He remains an unequalled banisher, a "
            "master of Perdo, Corpus and Mentem."
        ),
        traits={"Addled": 3, "Forgetful": 1, "Sinister": 1},
    )
    m["henri"] = b.magus(
        "Henri",
        covenant=requies,
        house=EX_MISC,
        age=None,
        summary=(
            "Eulogius's youngest filius and his helper, a Donator who stays "
            "mostly from duty to his tradition, and has made himself keeper of "
            "the covenant's library and lore for the generations to come."
        ),
    )
    b.book(
        requies,
        "The library of the Donatores",
        "Other",
        description=(
            "The tradition's noted collection of Donatores lore on the "
            "restless dead and their banishing, its main repository, kept in "
            "the catacombs and preserved by Henri. No titles are given; it "
            "draws Hermetic interest to an otherwise forgotten covenant."
        ),
    )


# ---------------------------------------------------------------- Norlanus


def _norlanus(normandy: Normandy, b: Builder) -> None:
    normandy.magi["norlanus"] = b.magus(
        "Norlanus",
        covenant=None,
        house=JERBITON,
        age=None,
        summary=(
            "An elderly eremite who spends much of his time at the cathedral "
            "school of Laon, respected for his wisdom and the clarity of his "
            "writings, and for that long allowed a small vis legacy "
            "all to himself. His home is in the city, but his sanctum lies "
            "hidden in the mount's rocky cliffs, where the Terram vis is gathered. "
            "He wrote of finding a regio, perhaps Divine, at the Templar "
            "priory of Nanteuil."
        ),
    )


# ---------------------------------------------------------------- Flanders


def _flanders_world(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    flanders = normandy.places["flanders"]
    countess = b.lord(
        "Joan, Countess of Flanders",
        title="count",
        wealth="Wealthy",
        manors=10,
        seat="Lille",
        ruler="Joan of Hainault",
        place=flanders,
        arms=ARMS_FLANDERS,
        summary=paragraphs(
            "Countess of Flanders since 1205, niece of King Philip. Her father "
            "Baldwin IX was chosen Emperor of Constantinople in 1204 on the "
            "Fourth Crusade and died a captive a year later. Her husband "
            "Ferdinand, a prince of Portugal, was taken at Bouvines in 1214 and "
            "has sat in a Paris prison for six years; Joan, who has little "
            "love for him, refuses her uncle the ten thousand pounds he asks "
            "as ransom and governs alone, which Philip seems not to mind.",
            "Her house's main castle and palace is at Lille, with castles in "
            "every great city. The counts police the cloth fairs and keep the "
            "roads and waterways safe, and side with the craft gilds against "
            "the patricians. She commissioned two continuations of "
            "Chrétien's Perceval, partly to show herself the rightful heir of "
            "Philip of Flanders. Arms: or, a lion sable.",
        ),
    )
    w["countess_of_flanders"] = countess
    w["bruges"] = b.town(
        "Bruges",
        charter="Commune",
        ruler="A council of patricians",
        answers_to=countess,
        place=flanders,
        summary=paragraphs(
            "Brugge, Flanders' greatest port and a leading wool and weaving "
            "city. Baldwin Ironarm built a castle here against the Vikings in "
            "the ninth century, and Robert the Frisian made it his capital in "
            "1093; the old channel to the sea silted up and the town "
            "stagnated, until the great tidal wave of 1134 scoured a deep "
            "channel in the Zwin. A harbour was built at Damme, five miles "
            "off, and joined to Bruges by canal, and the city boomed again.",
            "Rival merchants asked the Church to look into the wave, some "
            "claiming the patricians of Bruges had it conjured; several magi "
            "suspected Florum or Infelicitas, but the Quaesitores never had "
            "evidence enough to investigate.",
            "The castle sits at the centre within brick ramparts that also "
            "hold a broad market square and St. Donatius, the largest church. "
            "Among the other churches is the Basilica of the Holy Blood, whose "
            "reliquary holds Christ's Blood, brought back from the Second "
            "Crusade by Count Thierry of Alsace. There is a large cloth market. "
            "The patrician council grants tax immunities and trading "
            "privileges and lets foreign merchants, though not local "
            "craftsmen, buy property; their enclaves lie outside the walls. "
            "The fair cycle ends here.",
        ),
    )
    w["holy_blood"] = b.church(
        "Basilica of the Holy Blood, Bruges",
        church="Parish church",
        place=flanders,
        summary=(
            "A church of Bruges holding a reliquary of the Blood of Christ, "
            "which Thierry of Alsace, Count of Flanders, carried home from "
            "the Holy Land after the Second Crusade. A potent relic."
        ),
    )
    w["ghent"] = b.town(
        "Ghent",
        charter="Noble lord",
        population=40000,
        ruler="Joan, Countess of Flanders",
        answers_to=countess,
        place=flanders,
        summary=paragraphs(
            "Gent, at the meeting of the Scheldt and the Lys: the largest city "
            "in Flanders and in northern Europe after Paris, with perhaps forty "
            "thousand people, bigger than London or Cologne, and home of "
            "Florum. It grew round the abbeys of St. Bavo and St. Peter that "
            "St. Amand founded in the seventh century; plundered twice by "
            "Vikings, it recovered after Baldwin II built a stone castle in "
            "the tenth.",
            "Many trade routes meet here. Wool and cloth rule, but almost "
            "anything can be bought in its huge markets, including Eastern and "
            "Mediterranean luxuries via the Champagne fairs; Italians, Jews "
            "and the Templars run a young banking trade, and the wool workers' "
            "guild grows stronger. The rich merchants have built stenen, "
            "fortified stone town houses, and in 1180 Count Philip of Alsace "
            "answered by rebuilding his castle on the model of the crusader "
            "castles: a strong keep with a ring of turrets and a moat from the "
            "Lys. The great church of St. Nicholas is half-built, and the "
            "Graslei docks run through the city's heart.",
            "The city is spreading fast with newcomers and foreigners into "
            "suburbs, one of which, the Farm, is Florum.",
        ),
    )
    w["ghent_abbeys"] = b.church(
        "Abbeys of St. Bavo and St. Peter, Ghent",
        church="Monastery or nunnery",
        order="Benedictine",
        place=flanders,
        founded=650,
        summary=(
            "The two monasteries founded by St. Amand, apostle of Flanders, in "
            "the seventh century, round which Ghent grew; they now stand at "
            "the centre of the city. (The founding year is approximate.)"
        ),
    )
    w["ypres"] = b.town(
        "Ypres",
        charter="Noble lord",
        answers_to=countess,
        place=flanders,
        summary=paragraphs(
            "Ieper, on an old Roman site refounded in the tenth century, now one "
            "of Flanders' largest cities. It lives by woollen cloth, with a "
            "great cloth market near the church of St. Martin, and also weaves "
            "linen, for the Lys is good for retting the flax grown all round. "
            "South of it the Heuvelland, Flanders' thinly peopled uplands, "
            "rises in wooded hills up to five hundred feet that overlook the "
            "lowland.",
            "Many cats live in the Cloth Hall, welcome in winter for keeping "
            "the mice from the cloth. In spring the superstitious townsfolk, "
            "who think them witches' creatures, bag every cat they can and "
            "throw them to their deaths from the top of the belfry beside the "
            "cloth market: the Kattenfeest. The cleverest cats hide and "
            "survive to hunt next winter's vermin.",
            "Hook: a clever cat, perhaps a familiar, begs the magi to stop the "
            "killing, and the cats would be grateful for ever. Hook: a "
            "sinister man in motley stirs the crowd and leads the march to the "
            "belfry laughing, then is seen picking over the dead cats, perhaps "
            "an urban hedge wizard collecting vis.",
        ),
    )
    w["antwerp"] = b.town(
        "Antwerp",
        place=flanders,
        summary=paragraphs(
            "A harbour on the Scheldt estuary, smaller and less notable than "
            "the great Flemish cities, that thrives on fish, grain and salt "
            "and on English raw wool. It grew from a Roman fort and was "
            "converted by St. Amand in the seventh century.",
            "Legend says the giant Druon Antigon once preyed on the estuary, "
            "wrecking ships and cutting off the hands of any who would not pay "
            "his toll or whom he disliked, until the soldier Silvius Brabo beat "
            "him, cut off his hand and flung it in the river. Brabo was given "
            "the land, and the city's name means hand-throwing; its arms show "
            "two severed hands before a castle.",
        ),
    )
    w["tournai"] = b.town(
        "Tournai",
        charter="Church",
        place=flanders,
        summary=paragraphs(
            "The seat of the bishopric of Flanders, an old, learned and pious "
            "city unlike the busy cloth towns. St. Piat converted the Roman "
            "town; under the Frankish kings it was a capital, where Chilperic "
            "is buried and Clovis was born, who founded the see. Since 1187 it "
            "has been free of the counts and answers directly to the French "
            "crown.",
            "The cathedral of Notre-Dame and its belfry dominate it. The "
            "Scheldt divides it, but the walls cross the river on stone arches "
            "and make boats stop and pay toll. Its artisans, and above all its "
            "gold- and silversmiths, are famous.",
        ),
    )
    w["bishop_of_tournai"] = b.church(
        "Bishop of Tournai",
        church="Bishop's cathedral",
        order="secular clergy",
        place=flanders,
        summary=(
            "The see of Flanders, founded by Clovis, seated at the cathedral of "
            "Notre-Dame in Tournai with its great belfry."
        ),
    )
    w["lille"] = b.town(
        "Lille",
        charter="Noble lord",
        answers_to=countess,
        place=flanders,
        summary=(
            "Seat of the Counts of Flanders, with their chief castle and "
            "palace, and the first town of the Flemish cloth fair cycle each "
            "year."
        ),
    )
    w["douai"] = b.town(
        "Douai",
        charter="Noble lord",
        answers_to=countess,
        place=flanders,
        summary=(
            "A Flemish town with one of the counts' grandest castles: a great "
            "keep inside huge ramparts, its walls twelve feet thick."
        ),
    )
    w["steenvoorde"] = b.town(
        "Steenvoorde",
        place=flanders,
        summary=paragraphs(
            "A Flemish town whose hero is Yan den Houtkapper, John the "
            "Woodcutter, a clever giant who made everlasting boots for "
            "Charlemagne and was given a huge suit of armour in return. The "
            "townsfolk dress a giant figure in that armour and carry it "
            "through the streets in procession every year.",
            "Hook: the armour may be blessed or magical, and would fit only "
            "someone with Giant Blood; stealing the town's dearest treasure "
            "would enrage it.",
        ),
    )


# ---------------------------------------------------------------- Picardy


def _picardy_world(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    picardy = normandy.places["picardy"]
    montagne = normandy.places["montagne_de_reims"]
    cuise = normandy.places["forest_of_cuise"]
    archbishop = b.church(
        "Archbishop of Reims",
        church="Archbishop's cathedral",
        order="secular clergy",
        place=picardy,
        summary=paragraphs(
            "The most powerful archbishop in France, who anoints and crowns its "
            "kings with the holy phial of oil a dove brought from heaven for "
            "the baptism of Clovis by St. Remigius, the kings' proof of their "
            "divine right. The archbishops have used that privilege shrewdly, "
            "acting as arbiters between claimants to the throne and keeping "
            "Reims prosperous.",
            "Their opulent palace keeps the coronation relics: the phial; "
            "Charlemagne's talisman, thought to hold a piece of the True Cross; "
            "a coronation chalice; and the reliquary of the Holy Thorn. The "
            "new cathedral of Notre-Dame, in the French style, has been rising "
            "at the south end of the city since 1210. Archbishop William of "
            "the White Hands granted the city its charter late in the twelfth "
            "century.",
        ),
    )
    w["archbishop_of_reims"] = archbishop
    w["reims"] = b.town(
        "Reims",
        charter="Church",
        answers_to=archbishop,
        place=picardy,
        summary=paragraphs(
            "The largest city of Picardy, where the kings of France are "
            "crowned. Capital of the Gaulish Remes, then a rich Roman city "
            "with roads to its gates, it saw Clovis baptised one Christmas at "
            "the end of the fifth century. Its cathedral school has been a "
            "beacon of the liberal arts for centuries, and the city has grown "
            "since its charter.",
            "At the north end stand Roman remains: the Porte de Mars, a "
            "triumphal arched gate in the wall, a ruined temple of Mars and "
            "an ancient forum. In the centre is the eighth-century monastery "
            "of St. Remigius, its basilica rebuilt grandly over his grave of "
            "533. The wild Montagne de Reims begins at the city's southern "
            "edge.",
        ),
    )
    w["st_remigius"] = b.church(
        "Abbey of St. Remigius, Reims",
        church="Monastery or nunnery",
        order="Benedictine",
        place=picardy,
        summary=(
            "The eighth-century monastery of the patron saint of Reims, who "
            "baptised Clovis; his basilica, raised over his grave of 533, has "
            "been rebuilt on a far grander scale."
        ),
    )
    w["reims_school"] = b.university(
        "Cathedral school of Reims",
        school="Cathedral school",
        answers_to=archbishop,
        place=picardy,
        summary=(
            "For centuries one of the great schools of the liberal arts. "
            "Hautvillers Abbey is a branch of it."
        ),
    )
    w["hautvillers"] = b.church(
        "Hautvillers Abbey",
        church="Monastery or nunnery",
        order="Benedictine",
        place=montagne,
        founded=660,
        summary=(
            "Founded in 660 by St. Nivard near the north bank of the Marne, a "
            "large abbey church in a quiet, lovely spot among vineyards, now a "
            "branch of the Reims school whose scriptorium makes some of the "
            "finest illuminated manuscripts anywhere. A few miles upstream is "
            "Ay, an old Gaulish village of vintners with a royal residence the "
            "kings seldom visit."
        ),
    )
    w["nanteuil_priory"] = b.church(
        "Templar priory of Nanteuil",
        church="Monastery or nunnery",
        order="Knights Templar (military order)",
        answers_to=w.get("templars"),
        place=normandy.places["nanteuil"],
        arms=Arms("Argent", charge="Cross", charge_tincture="Gules"),
        summary=(
            "A priory of the Knights Templar in a remote vale in the middle of "
            "the Montagne de Reims, oddly placed, hard to reach and on the "
            "road to nowhere; Norlanus believed it stands at a regio."
        ),
    )
    w["soissons"] = b.town(
        "Soissons",
        charter="Church",
        place=picardy,
        summary=paragraphs(
            "A city amid rich farmland in the Aisne valley. It was the capital "
            "of Syagrius's Roman kingdom of Soissons until Clovis beat him at "
            "its gates; when a defiant soldier smashed a vase Clovis wanted "
            "returned to Reims, the king killed him a year later at a review "
            "of his troops, reminding him of the vase. For a time it was the "
            "Frankish capital under Chlotar, son of Clovis.",
            "Its cathedral of St. Gervais and the abbey church of St. John of "
            "the Vines are forever being enlarged with the abbey's wealth.",
        ),
    )
    w["st_john_of_the_vines"] = b.church(
        "Abbey of St. John of the Vines, Soissons",
        church="Monastery or nunnery",
        place=picardy,
        summary=(
            "Founded in the eleventh century, it has grown under royal "
            "patronage into one of the richest abbeys in France, and its money "
            "builds both its own great church and the cathedral of Soissons."
        ),
    )
    w["arras"] = b.town(
        "Arras",
        charter="Noble lord",
        place=picardy,
        summary=paragraphs(
            "Seat of the county of Artois on the Flemish border, now the "
            "King's, once capital of the Atrebates and Roman Atrebatum. Its "
            "large grain market draws Flemish traders exchanging woollen cloth "
            "for grain.",
            "It is full of renowned troubadours and entertainers, a tradition "
            "begun in the twelfth century by its most famous trouvère, Gautier "
            "d'Arras, best known for Eracle, the romance of Heraclius who "
            "becomes Emperor of Constantinople.",
        ),
    )
    w["st_vaast"] = b.church(
        "Abbey of St. Vaast, Arras",
        church="Monastery or nunnery",
        order="Benedictine",
        place=picardy,
        summary=(
            "Founded by St. Aubert in the seventh century on the slopes of the "
            "Baudimont hill, it keeps the relics of St. Vaast, first bishop of "
            "Arras."
        ),
    )
    count_of_boulogne = b.lord(
        "Count of Boulogne",
        title="count",
        seat="Boulogne",
        place=picardy,
        summary=(
            "Lord of an important county on the Channel; the present count, "
            "not named, has begun rebuilding the ruined walls and ramparts "
            "about the old Roman castle of the upper town."
        ),
    )
    w["count_of_boulogne"] = count_of_boulogne
    w["boulogne"] = b.town(
        "Boulogne",
        charter="Noble lord",
        answers_to=count_of_boulogne,
        place=picardy,
        summary=(
            "Roman Bononia, between two hills where the Liane meets the sea: "
            "Claudius's base for invading Britain and then the chief port "
            "linking the province to the Empire. Now a county seat, a busy "
            "port and fishing town, and a place of pilgrimage. The upper town "
            "has grown round the old Roman castle."
        ),
    )
    w["notre_dame_de_boulogne"] = b.church(
        "Notre-Dame de Boulogne",
        church="Bishop's cathedral",
        place=picardy,
        summary=(
            "In 636 the Virgin appeared to a small congregation in the chapel "
            "of Boulogne and sent them to the shore, where a boat with neither "
            "sail nor crew grounded gently, bearing her statue. The statue, a "
            "famous relic, is kept in the cathedral and draws pilgrims, for it "
            "is believed to keep travellers safe; the kings of France "
            "customarily make the pilgrimage, and English kings have come too."
        ),
    )
    bishop_of_amiens = b.church(
        "Bishop of Amiens",
        church="Bishop's cathedral",
        order="secular clergy",
        place=picardy,
        summary=(
            "Keeper of two great relics: half the cloak St. Martin of Tours, "
            "then a Roman horseman, cut in two for a freezing beggar, and the "
            "greater, the head of John the Baptist, which came back with the "
            "Fourth Crusade in 1206. The church burned in 1218, and the bishop "
            "and his flock have already begun a much larger cathedral worthy "
            "of the relic."
        ),
    )
    w["bishop_of_amiens"] = bishop_of_amiens
    w["amiens"] = b.town(
        "Amiens",
        charter="Church",
        answers_to=bishop_of_amiens,
        place=picardy,
        summary=(
            "The historical capital of Picardy, chief town of the Gaulish "
            "Ambiani and Roman Samarobriva, where St. Martin shared his cloak. "
            "Lands about it have lately passed to the King. Downstream the "
            "Somme spreads into marsh."
        ),
    )
    w["corbie"] = b.church(
        "Abbey of Corbie",
        church="Monastery or nunnery",
        order="Benedictine",
        place=picardy,
        founded=657,
        summary=paragraphs(
            "The leading monastery of northern France, in a quiet spot of the "
            "Somme valley above Amiens, founded in 657 by St. Bathilde, wife "
            "of Clovis II, and raised to greatness by Charlemagne's cousin St. "
            "Adalard. Hundreds of monks lived here; it was famed for theology "
            "and its library, where the Carolingian script was first written, "
            "and the last Lombard king, Desiderius, was exiled here. At its "
            "height it was perhaps the heart of western Christendom and "
            "founded many daughter houses.",
            "St. Ansgar, Apostle of the North, was born here in 801, carried "
            "its ways to Corvey in Saxony, became archbishop of Hamburg and "
            "preached in the Norse lands.",
        ),
    )
    bishop_of_laon = b.church(
        "Bishop of Laon",
        church="Bishop's cathedral",
        order="secular clergy",
        place=picardy,
        summary=(
            "A see founded by St. Remigius, who was born in Laon. A century "
            "ago Bishop Gaudry bought from the King the revocation of the "
            "commune his weakness had let the townsfolk win, and took cruel "
            "revenge; the town rose, burned the palace and the old cathedral, "
            "and killed him and his men. Bishops and people have been uneasy "
            "ever since, the kings ruling now for one, now for the other. The "
            "new cathedral of Notre-Dame is nearly finished in the French "
            "style."
        ),
    )
    w["bishop_of_laon"] = bishop_of_laon
    w["laon"] = b.town(
        "Laon",
        charter="Church",
        answers_to=bishop_of_laon,
        place=picardy,
        summary=paragraphs(
            "A city on a rocky ridge over a mile long and a quarter wide, "
            "rising three hundred feet from the plain: Roman Laudunum, which "
            "held out against the Germanic invaders, and under the "
            "Carolingians in the ninth and tenth centuries for a while the "
            "capital of France, richly endowed by Charles the Bald. Hugh Capet "
            "plotted with its bishop to take it from the Carolingians and then "
            "ruled from Paris, and Laon lost its political weight.",
            "It is still a centre of learning, its cathedral school famous "
            "since Anselm of Laon in the eleventh century. Spires and towers "
            "climb to the new cathedral; beside the old church of St. Martin "
            "is a Templar chapel and commandery. Roads wind down slopes of "
            "vineyards to the lower town. The eremite Norlanus of Jerbiton "
            "lives here, his sanctum hidden in the cliffs.",
        ),
    )
    w["laon_school"] = b.university(
        "Cathedral school of Laon",
        school="Cathedral school",
        answers_to=bishop_of_laon,
        place=picardy,
        summary=(
            "A renowned school, at its height under Anselm of Laon in the "
            "eleventh century, where Norlanus of Jerbiton spends much of his "
            "time and is respected for his wisdom."
        ),
    )
    w["compiegne"] = b.town(
        "Compiègne",
        charter="Noble lord",
        place=picardy,
        summary=(
            "A small, ancient city on the Oise in southern Picardy, born of the "
            "country palace Charles the Bald built in imitation of "
            "Charlemagne's at Aachen; the town grew round the royal abbey of "
            "St. Cornelius founded after it. The Forest of Cuise stretches "
            "south of it."
        ),
    )
    w["st_cornelius"] = b.church(
        "Abbey of St. Cornelius, Compiègne",
        church="Monastery or nunnery",
        place=picardy,
        summary=(
            "The royal abbey that keeps St. Cornelius's relics, the burial "
            "place of the old Carolingian kings before St. Denis took that "
            "role."
        ),
    )
    w["premontre"] = b.church(
        "Abbey of Prémontré",
        church="Monastery or nunnery",
        order="Premonstratensian canons",
        place=cuise,
        founded=1120,
        summary=paragraphs(
            "Mother house of the Premonstratensians, in a hidden valley of the "
            "Forest of Cuise, ten miles from Laon to the west. St. Norbert, "
            "a German born near Cleves, gave away his goods and vowed himself to "
            "poverty after a revelation, when a storm threw him from his "
            "horse. In midwinter 1120 he came with the bishop of Laon to a "
            "clearing where a monastery had once failed, was ordained there, "
            "and founded his own; he became a friend of St. Bernard of "
            "Clairvaux.",
            "His order, also called Norbertines, was modelled on the "
            "Cistercians and approved by the Pope in 1126: strict canons in "
            "white habits who preach and follow the rule of St. Augustine. It "
            "now has several hundred houses across western Europe, most in "
            "northern France, Germany and England.",
        ),
    )


# ---------------------------------------------------------------- factions


def _factions(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    flanders = normandy.places["flanders"]
    w["flemish_patricians"] = b.faction(
        "The Flemish patricians and merchant gilds",
        faction="Gild",
        place=flanders,
        decides="Councils of the leading families in each city",
        wants="Control of the cities and the wool trade, and more power from the counts",
        offers="Wealth, trade privileges, property for foreigners",
        summary=(
            "The powerful merchant gilds and patrician families who run most "
            "Flemish cities and the lucrative wool trade, and have gradually "
            "forced power out of the counts' hands. The richest have built "
            "fortified stone town houses."
        ),
    )
    w["flemish_craft_gilds"] = b.faction(
        "The Flemish craft gilds",
        faction="Gild",
        place=flanders,
        wants="A check on the merchants, and better lives for the workers",
        offers="The counts' alliance against the patricians",
        summary=(
            "The weavers, spinners and dyers, rivals of the merchants and "
            "friendlier to the counts, who often ally with them. The wool "
            "workers' guild of Ghent is growing in power, and many Spinnen sit "
            "in the city's Weavers' Guild. Below them the mass of grimy, "
            "barely paid workers nurses resentment."
        ),
    )
    w["cloth_fairs"] = b.faction(
        "The Flemish cloth fairs",
        faction="Other",
        place=flanders,
        rules="The counts guard the fairs and keep the roads and waterways safe",
        summary=(
            "A cycle of trade fairs from February to November, held in turn at "
            "Lille, Mesen, Ypres, Torhout and Bruges, given over to fine "
            "woollen and linen cloth rather than general trade. Most goods "
            "travel by water."
        ),
    )
    w["beguines"] = b.faction(
        "The Beguines",
        faction="Other",
        realm="Divine",
        place=flanders,
        rules=(
            "No vows and no renouncing of marriage, but a common rule; chosen "
            "poverty, not harsh; manual work, charity and cottage crafts"
        ),
        wants="A pious, simple common life with some independence",
        offers="Care of the sick, sewing and weaving, labour in return for protection",
        summary=paragraphs(
            "A movement that has sprung up of itself among widows and single "
            "women, who are beginning to gather in convents in the towns. "
            "They take their name from St. Begga, a seventh-century abbess in "
            "Andenne in Brabant. Unlike nuns they take no vows and may still "
            "marry. Most come from wealthy families, for piety, family trouble, "
            "the wish for a simple shared life with some freedom, or all of "
            "these, and they nurse the sick or sew and weave.",
            "A beguinage is a small walled town at the edge of a larger one, "
            "rows of cottages round one or more square courts about a church. "
            "They are just beginning to flourish in Flanders; by the middle of "
            "the century there will be large ones in Ghent, Bruges and other "
            "cities of Flanders, Brabant and northern Picardy.",
            "Hook: a new beguinage near the covenant draws away its "
            "discontented women, leaving it short-staffed. Hook: a beguinage "
            "oppressed by a harsh landlord asks the covenant's protection and "
            "would work for it to be freed of its debt, at the cost of the "
            "landlord's enmity.",
        ),
    )
    if not any("Brabançon" in n.name for n in normandy.b.saga.neighbours):
        w["brabancons"] = b.faction(
            "The Brabançons",
            faction="Other",
            wants="Pay, and plunder when the pay runs out",
            offers="Hardened soldiers for hire",
            summary=paragraphs(
                "Freebooting mercenaries, also called Brabanters after the duchy "
                "of Brabant east of Flanders where they come from, now active "
                "chiefly in Aquitaine. In 1179 Pope Alexander III named them in a "
                "ban on mercenaries and excommunicated anyone who hired or "
                "sheltered them, to little effect.",
                "King Philip hired a troupe to harry his unruly vassals, the "
                "count of Sancerre among them, then sent them to help the young "
                "Henry make war on his father Henry II; on the way they "
                "massacred Noialle, and when the young king could not pay them "
                "they turned to sacking monasteries. In the 1180s the "
                "Capuchonnes rose against them and killed three thousand brigands "
                "in Auvergne in 1183, then became brigands themselves.",
            ),
        )
    w["spinnen"] = b.faction(
        "The Spinnen",
        faction="Family",
        realm="Faerie",
        ruler="Piet de Spinnen (the de Spinnen family, a front)",
        place=flanders,
        members=30,
        wants="To live well and stay hidden",
        offers="Cloth spun by touch: tents, ropes and sails too",
        summary=secrets(
            "A Ghent family of faerie blood, descended from a maiden whose "
            "ancestral oak, at the end of its thousand years and as the "
            "Church came, summoned faerie and mystic princes to woo her. She "
            "refused them all, and the oak told her to wed Spin Head, the last "
            "and ugliest, whose dowry would replace the dying forests. The oak "
            "died, the spider passed a simple test and took human shape, and "
            "he gave his bride the first flax plant, weaving her wedding dress "
            "from it with his fingers.",
            "A few in each generation can turn their own weight of fibre into "
            "cloth each day by touch (the Virtue Faerie Blood (Spinnen)), or "
            "unweave old cloth within the same limit; some make tents, ropes "
            "or sails instead. Pelagius of Jerbiton found a dozen soon after "
            "the Order's founding; in 1220 there are almost thirty, all "
            "employed by Florum and living far better for it. They hide in "
            "plain sight, many in the Weavers' Guild of Ghent, and their "
            "relatives weave by ordinary means in the covenant's workshop. "
            "Their flax legend is widely known, so the wary might guess the "
            "truth.",
        ),
    )
    w["kabouters"] = b.faction(
        "The kabouters of the Low Countries",
        faction="Faerie court",
        realm="Faerie",
        place=flanders,
        summary=(
            "A dwarfish faerie folk who sided with the coming Church: they "
            "gave a hundred bells to the missionaries they approved of and "
            "sang the first carillon of the Low Countries under a gnome's "
            "baton. A tribe of them is firmly allied with Prunellie of "
            "Merinita, and an ancient kabouter workshop lies under Florum's "
            "Farm, giving it its Faerie aura."
        ),
    )
    w["donatores"] = b.faction(
        "The Donatores Requietis Aeternae",
        tradition="trad_donatores_requietis_aeternae",
        faction="Other",
        realm="Magic",
        place=normandy.places["old_nesle"],
        wants="To give the restless dead their rest, and to banish those that will not go",
        offers="Expert banishers of the dead",
        summary=(
            "The Givers of Eternal Rest, an Ex Miscellanea tradition born of "
            "the hedge wizards, clergy and others who fought the plague of "
            "restless dead in Picardy and won the battle of Nesle; the "
            "Quaesitor Muirgheal brought them into the Order in 1109. Their "
            "spiritual home and library are at Requies Aeterna, but most have "
            "scattered across western Europe to wherever the dead walk; one, "
            "Philip, has lately joined Atramentum Renatus. Some magi have "
            "always distrusted them."
        ),
    )


# ---------------------------------------------------------------- vis


def _vis(normandy: Normandy) -> None:
    c = normandy.covenants
    normandy.tenure(
        "Spider's Palace's sources (amounts not given)",
        c["spiders_palace"],
        "seisin",
        notes="The reason the vassal exists: it keeps Florum's old site's vis lawfully in the line.",
    )
    normandy.tenure(
        "Graveyard of old Nesle (Perdo and Corpus, rich)",
        c["requies_aeterna"],
        "seisin",
        notes="About half goes to Florum as the vassal's tithe, raised in return for servants.",
    )
    normandy.tenure(
        "Cliffs of Laon (a small source of Terram)",
        None,
        "legacy",
        until=1221,
        notes=(
            "Granted to Norlanus of Jerbiton, an eremite with no covenant, and "
            "renewed for many years for his wisdom; up for renewal at the next meeting."
        ),
    )
    normandy.tenure(
        "Footprints on the Seven Roads, Bavacum (Rego, a pawn an imprint)",
        None,
        "luctatio",
        notes=(
            "Dug up on the Mercuralia, 15 May. The book gives no tenure; "
            "entered as a luctatio since the harvest rests on the day and "
            "careful digging."
        ),
    )


# ---------------------------------------------------------------- stats

P = Profile


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


def _focus(focus: str) -> tuple[str, dict[str, str]]:
    return ("Minor Magical Focus", {"focus": focus})


#: Each magus's generated-stats profile, by key in normandy.magi.
PROFILES: dict[str, Profile] = {
    "rhesus": P(
        strong="int dex",
        native="Italian",
        arts={"He": 6, "Cr": 4, "Re": 4, "Mu": 3, "Te": 2, "Vi": 2},
        abilities={
            "Craft: Weaver": (4, "linen"),
            "Leadership": (2, "magi"),
            "Code of Hermes": (2, "the Perthean Compact"),
            "Living Language: Flemish": 2,
        },
        virtues=[
            _art("Affinity with {art}", "herbam"),
            "Inventive Genius",
            "Proud (Minor)",
            "Obsessed (Minor)",
        ],
    ),
    "calvinus": P(
        strong="int com pre",
        native="Italian",
        arts={"Im": 6, "In": 4, "Me": 4, "Mu": 3, "Re": 3},
        abilities={
            "Guile": (3, "false identities"),
            "Intrigue": (3, "Ghent merchants"),
            "Living Language: Flemish": 4,
            "Living Language: French": 3,
            "Area Lore: Ghent": (3, "the underworld"),
            "Etiquette": 2,
        },
        virtues=[
            "Gentle Gift",
            "Linguist",
            "Dark Secret",
            "Reclusive",
        ],
    ),
    "alroy": P(
        strong="sta str",
        native="French",
        arts={"Ig": 7, "Cr": 4, "Pe": 4, "Re": 3, "Co": 3, "An": 2},
        abilities={
            "Single Weapon": (3, "sword"),
            "Area Lore: Holy Land": 2,
            "Teaching": (2, "apprentices"),
            "Living Language: Flemish": 1,
        },
        virtues=[
            _art("Puissant {art}", "ignem"),
            "Warrior",
            "Hermetic Prestige",
            "Overconfident (Minor)",
            "Driven (Minor)",
            "Reckless (Minor)",
        ],
        reputations={"Veteran of the Levant (Hermetic)": 2},
    ),
    "prunellie": P(
        strong="int per",
        native="Flemish",
        arts={"Te": 5, "Mu": 4, "Vi": 4, "Cr": 3, "He": 3, "In": 3},
        abilities={
            "Faerie Lore": (5, "faeries of the Low Countries"),
            "Area Lore: Low Countries": (3, "faerie sites"),
            "Living Language: French": 2,
        },
        virtues=[
            "Second Sight",
            ("Social Contacts", {"group": "a tribe of kabouters"}),
            "Generous (Minor)",
            "Secretive",
            "Faerie Friend",
        ],
    ),
    "eulogius": P(
        strong="int sta",
        weak="qik pre",
        native="French",
        arts={"Pe": 7, "Co": 6, "Me": 6, "Re": 3, "In": 3, "Vi": 3},
        abilities={
            "Dominion Lore": (3, "the restless dead"),
            "Magic Lore": (3, "ghosts"),
            "Organization Lore: Donatores": 4,
            "Penetration": (4, "Mentem"),
        },
        virtues=[
            "Ghostly Warder",
            "Susceptibility to Sunlight",
            "Disfigured",
            "Twilight Prone",
        ],
    ),
    "henri": P(
        age=40,
        strong="int com",
        native="French",
        arts={"Pe": 5, "Co": 4, "Me": 4, "In": 3, "Re": 2},
        abilities={
            "Organization Lore: Donatores": (3, "lore"),
            "Profession: Scribe": (3, "copying"),
            "Dominion Lore": 2,
        },
        virtues=[
            "Second Sight",
            "Book Learner",
            "Dutybound",
            "Humble",
        ],
    ),
    "norlanus": P(
        age=90,
        strong="int com",
        native="French",
        arts={"Te": 6, "In": 4, "Re": 4, "Cr": 3, "Me": 3},
        abilities={
            "Artes Liberales": (4, "rhetoric"),
            "Philosophiae": 3,
            "Teaching": (3, "clear writing"),
            "Etiquette": (2, "the clergy"),
        },
        virtues=[
            "Good Teacher",
            "Hermetic Prestige",
            "Reclusive",
            "Arthritis",
        ],
    ),
}


def stats(normandy: Normandy) -> None:
    """Stat every magus this part made, from their profile."""
    for key, profile in PROFILES.items():
        character = normandy.magi.get(key)
        if character is not None:
            apply(normandy.b, character, profile)
