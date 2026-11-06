"""The Great Desert (Between Sand and Sea pp. 66-89), in paraphrase.

The Great Desert is a region place holding the Fezzan, the Central Great
Desert, the Tuareg redoubts, the Tanezrouft and the Ténéré, each with its
oases, towns and ruins, and beside them the trade roads, the Bilad-es-Sudan
and the lost places of the book's optional geographies. A settlement with a
printed aura stands inside a place that carries the aura, since a town has
none of its own. Sijilmasa belongs to the coasts part; its desert facts are
words in the Tanezrouft. The Camel of Virtue and the other beasts of the
appendix are not in this part's pages.

The Garamantian tombs and initiation are words: the book prints no curse,
ward or trap for them, and nothing to build a tomb from. The realm interpretations and the two courses of the Nile are
choices for a troupe, so they are dormant threats, as the story seeds are."""

from __future__ import annotations

from typing import Any

from ...models import BodyVis, Neighbour
from ..builder import Builder, characteristics, dormant, paragraphs

RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "In the region"}
LOCAL: dict[str, Any] = {"status": "Known", "known": "Locally"}
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
S = Builder.stage


def _place(b: Builder, name: str, **kw: Any) -> Neighbour:
    """A place known across the region unless `kw` says otherwise."""
    kw.setdefault("known", "In the region")
    return b.place(name, **kw)


def _story(
    b: Builder,
    name: str,
    summary: str,
    *,
    place: Neighbour | None = None,
    realm: str = "",
    secrets: str = "",
    stages: list[dict[str, Any]] | None = None,
) -> Neighbour:
    """A story seed, waiting for the storyguide to begin it."""
    return dormant(
        b.threat(
            name,
            summary=summary,
            place=place,
            realm=realm,
            secrets=secrets,
            stages=stages,
        )
    )


def build(b: Builder) -> None:
    desert = _great_desert(b)
    fezzan = _fezzan(b, desert)
    garama = _garamantians(b, fezzan)
    central = _central(b, desert)
    redoubts = _redoubts(b, desert)
    tanezrouft = _tanezrouft(b, desert)
    tenere = _tenere(b, desert)
    _roads(b, desert)
    _sudan(b)
    _creatures(b, desert, garama)
    _realm_readings(b, desert)
    _sources_of_the_nile(b, desert)
    _desert_stories(b, fezzan, redoubts, tanezrouft, tenere, central)


# -- the desert as a whole --


def _great_desert(b: Builder) -> Neighbour:
    desert = _place(
        b,
        "The Great Desert",
        summary=paragraphs(
            "Europeans imagine an ocean of sand no one can cross. In truth "
            "only a fifth to a quarter of it is sand, and those who know it "
            "find it hard and unsafe but passable, on horseback if need be. "
            "Water is the difficulty, not the going.",
            "Six kinds of country make it up. Erg is the rolling dune sea, "
            "almost bare of plants, some 20 percent of the whole. Reg, the "
            "stony plains of sand and black, red or white gravel, is some 70 "
            "percent. Hamadas are the plateaus and mountains; chott the salt "
            "flats left by old or seasonal water. Wadis are deep standing "
            "pools fed by rain or springs, and oases the fixed places of "
            "food and water where Berbers, Tuareg, jinn and the odd stranger "
            "meet to trade and rest. Almost every other water is seasonal, "
            "lasting through winter and spring and boiling off by autumn.",
            "It falls into the Fezzan, the Central Great Desert, the "
            "Tanezrouft in the west and the Ténéré in the south. Some say "
            "the Fezzan and the Ténéré run on into the Nubian Desert; most "
            "take that for the raving of men driven mad by jinn.",
            "Myrtle Trees of Virtue grow in some hidden wadis. Sardinians "
            "make the liqueur Mirto from the crushed berries, murabitin use "
            "them to sharpen their reading of dreams, Jewish scholars hold "
            "myrtle the scent and sign of Eden, and some theurgists keep a "
            "sprig on the tongue to improve their casting.",
            "Vis: a sprig of myrtle leaves with a flower or berry holds 2 "
            "pawns of Mentem. Its enrichment is in the Secrets.",
            "Books: travellers can read up on the routes in Arabic works. "
            "Abu Abdullah al-Bakri's Book of Routes and Places (1068, drawn "
            "from two centuries of merchants' reports) is a summa on Area "
            "Lore: Maghreb, level 3, Quality 10, with a tractatus on Area "
            "Lore: Great Desert, Quality 10; it is held in merchants' and "
            "nobles' private libraries in the Maghreb and Al-Andalus. Ibn "
            "Hawqal's Kitab Surat al-'Ard, Face of the Earth, in the same "
            "libraries, is a summa on Area Lore: Maghreb, level 5, Quality "
            "11, with tractatus on Area Lore: Provence, Iberia and Sicily, "
            "each Quality 11; its praise of Fraxinet makes some Hermetic "
            "scholars suspect he followed Jerbiton. Yusuf al-Warraq's On the "
            "Topography of North Africa is a tractatus on Area Lore: Maghreb, "
            "Quality 8, and al-Zuhri's Kitab al-Jaghrafiyya, Book of "
            "Geography, another, Quality 10.",
        ),
        secrets=paragraphs(
            "Sun (BS&S p. 66): the Deprivation check for lack of water comes "
            "every 4 hours in the deserts, and exposed skin takes +1 "
            "non-combat damage (ArM5 pp. 180-181).",
            "Dry quicksand in the ergs pulls a man under in two rounds, and "
            "he then suffocates. In the first round he may make a Strength "
            "or Quickness stress roll against Ease Factor 9 to get free; a "
            "botch traps his arms next round. After that it is up to his "
            "companions, though with free arms he may help in the second "
            "round, lowering their further Ease Factors by 3.",
            "Brigands prey on caravans not clearly well guarded, as far as "
            "their need drives them. Sandstorms and dust-storms can smother "
            "or flay: natural, the work of sorcerers, elemental jinn, or "
            "witches in disguise. Jinn and demons send false oases; the "
            "victim learns of it when her first long drink turns out to be "
            "sand.",
            "Myrtle of Virtue (p. 72): berries fermented in a silver urn "
            "underground for a season give a draught of +3 to all recovery "
            "rolls for a season. A flowering sprig gives its bearer Clear "
            "Thinker if the intended user sleeps with it under the pillow "
            "for a season, or by some Jewish traditions if it dries in the "
            "Holy of Holies, touched by each day's rising sun for a season. "
            "Soaked in seawater for a season in a place sacred to Aphrodite "
            "it stays supple and fresh and gives Venus' Blessing.",
            "Why slaves rarely flee (p. 84): all three faiths hold that a "
            "runaway is a thief bound for Hell, tempted by evil spirits, "
            "though each forbids enslaving its own. Many are freed anyway: a "
            "mother of her master's child, warriors after a campaign, "
            "domestics by will or charity. A runaway in the Maghreb has "
            "nowhere to go where slaves do not already do the work, and some "
            "would rather be a trusted ghilman than free and poor. Maghrebi "
            "Muslims also take suffering as God's will, which flight cannot "
            "change.",
        ),
    )
    _place(
        b,
        "The Great Desert Regio Network",
        inside=desert,
        status="Rumoured",
        levels=[
            Builder.level(
                "Tinariwen",
                0,
                see="Desert much like the mundane desert it touches.",
                enter="Through small, unmarked Magic auras deep in the sands, "
                "shown only by a slight change in the great dunes and a "
                "shimmer in the air.",
                notes="The book gives the higher regiones no aura strength. "
                "Guardian beasts and other wayfarers may be met; some paths "
                "end in dead ends or blank sand where thirst and heat bar "
                "going on or going back.",
            )
        ],
        summary=paragraphs(
            "Many regiones under the deep desert join into one great "
            "network, known to Camels of Virtue and to the deep nomads: the "
            "Bedouin of the Empty Quarter and the Tuareg, who call it "
            "tinariwen, 'the deserts', for its many landscapes. Some mundane "
            "Tuareg and the mysterious Blue Men can find their way, which is "
            "how nomads strike suddenly and melt into the sands.",
        ),
        secrets=paragraphs(
            "A character with the (Desert) Regio Network Minor Virtue "
            "(Realms of Power: Magic p. 45; the catalog's entry is "
            "{land} Regio Network) can enter and leave at different "
            "mundane places. Some may reach other deserts this way: the "
            "Sahara, the Empty Quarter, the Nefud, the Kyzylkum and Karakum, "
            "the Taklimakan, and perhaps unknown deserts beyond Mythic "
            "Europe.",
        ),
    )
    b.faction(
        "The Ibadi of the Desert",
        place=desert,
        faction="Faith or sect",
        summary=paragraphs(
            "An unusual Muslim sect, for whom leadership is open to any of the "
            "faithful and a bad or heretical leader may rightly be overthrown. "
            "Many fled to Wargala from Tahert when the "
            "Rustamid Imamate fell early in the 10th century; others live "
            "at Ghardaia and on Djerba.",
        ),
    )
    return desert


# -- the Fezzan --


def _fezzan(b: Builder, desert: Neighbour) -> Neighbour:
    fezzan = _place(
        b,
        "The Fezzan",
        inside=desert,
        summary=paragraphs(
            "Mostly sandy erg, with chott and salt hollows where salt-loving "
            "plants grow as at Siwa. The Idehan Ubari Erg and the Great Erg "
            "wall it from the Central Great Desert to the west, the Libyan "
            "Sand Sea from Egypt to the east, and the Al-Hamada al-Hamra, the "
            "Red Plateau, from the Mediterranean; in the south the Ahaggar "
            "and the Bilma Erg begin the Ténéré. It was the Garamantians' "
            "land, and they left only ruins, graves and a road with their "
            "name.",
        ),
    )
    for name, summary in (
        (
            "The Haruj",
            "A vast dark field of volcanic cones and basalt in the south of "
            "the Fezzan, where several volcanoes sleep with hidden lakes in "
            "their calderas. The road from Awdjila to Murzuq skirts it; "
            "those forced to stop sometimes find wadis among the black rock.",
        ),
        (
            "Waw an-Namus",
            "One of the Fezzan's sleeping volcanoes, in the south-east, known "
            "by the black ash coating its slopes and the land around.",
        ),
        (
            "Al-Hamada al-Hamra",
            "The Red Plateau, the buffer between the desert and the "
            "Mediterranean in the north.",
        ),
        (
            "The Libyan Sand Sea",
            "The Fezzan's eastern edge towards Egypt, crossed by the "
            "Garamantian Road from Siwa. The dangerous way to Cairo and "
            "Alexandria runs through the sands here.",
        ),
    ):
        _place(b, name, inside=fezzan, summary=summary)

    kufra = _place(
        b,
        "Al Kufra",
        inside=fezzan,
        summary=paragraphs(
            "A lonely oasis under the Tibesti to the south-west and the "
            "Bilma Erg to the south. Most who reach it go on south-east into "
            "the Nubian desert, few south-west to Bilma, and some set out "
            "from it for distant Fada. Awdjila is 140 leagues north, Murzuq "
            "180 leagues north-west.",
            "Its Berbers live quietly and like their visitors brief. Three "
            "villages share the water: Al Jawf with rich gardens and date "
            "palms, the slave plantation of Ez-Zurgh, and Et-Tleilíb, keeping "
            "watch on the sands from the south-west corner, nearly four "
            "leagues from Al Jawf.",
        ),
    )
    _place(
        b,
        "The Field of Glass",
        inside=kufra,
        aura=4,
        **RUMOURED,
        summary=paragraphs(
            "East of Al Kufra in the Great Sand Sea, a stretch of desert "
            "strewn with green-white natural glass, in a Magic aura of 4.",
            "Vis: the clearest, brightest pieces, bared on windswept dune "
            "crests, hold Ignem or Auram vis, the best of them both. Very "
            "large pieces hold two or three pawns. Whether the aura outlasts "
            "the gathering of all the vis-bearing glass is an open question.",
        ),
    )
    atiq = _place(
        b,
        "The Mosque of Atiq",
        inside=fezzan,
        realm="Divine",
        aura=4,
        summary=paragraphs(
            "One of the oldest mosques in Africa, with odd conical domes, "
            "cool and pleasant within. Abdullah ibn Sa'ad ibn Abi as-Sarh, "
            "foster brother of the Caliph Uthman and once governor of Egypt, "
            "is buried at the oasis. The mosque gives all Awdjila a Divine "
            "aura of 4.",
        ),
    )
    b.town(
        "Awdjila",
        place=atiq,
        summary=paragraphs(
            "A mostly Berber oasis and a crossroads of trails, where they "
            "speak Berber at their daily business. Caravans from the south "
            "and from Egypt take on dates and water here, and go on to Al "
            "Kufra or to Murzuq past the Haruj. Northward, outside some "
            "ruins of Cyrene, a village has grown as the Genoese trade more "
            "with the caravans. Cairo lies 200 leagues east-north-east and "
            "Alexandria about 180 north-east, both across the Sea of Sand.",
        ),
    )
    djofra = _place(
        b,
        "The Djofra Oasis",
        inside=fezzan,
        summary=paragraphs(
            "Three mostly Berber communities, each with palm groves of sweet "
            "dates and some figs and goats. Murzuq is a distant 90 leagues "
            "to the south.",
        ),
    )
    b.town(
        "Sokna",
        place=djofra,
        summary="A walled village of 7 gates and 33 bastions, with a poorly "
        "kept fortress, its kasbah, inside. Its houses are of cut stone and "
        "unbaked brick.",
    )
    b.town(
        "Hon",
        place=djofra,
        summary="A small market town 7 leagues north-east of Sokna.",
    )
    b.town(
        "Waddan",
        place=djofra,
        summary=paragraphs(
            "Seven leagues south-east of Sokna, built up out of an old Roman "
            "town, with four mithraeums hidden under its streets. It sometimes "
            "holds a slave market that jinn attend, its stock brought from "
            "the south by caravans bound for Tripoli, Cairo or Murzuq; some "
            "rest here on the way to Ghat.",
        ),
    )
    b.town(
        "Murzuq",
        place=fezzan,
        summary=paragraphs(
            "An oasis town on the Garamantian Road and the Bilma Trail, a "
            "crossroads for Cyrene, Cairo, Ghat and the south. Ubari is "
            "thirty leagues north-west with the ruins of Garama between, and "
            "Ghat 75 leagues west.",
        ),
    )
    dawada = _place(
        b,
        "Ramlat Dawada",
        inside=fezzan,
        summary=paragraphs(
            "A swath of red sands just north of Murzuq with eleven very salty "
            "lakes. One teems with reddish prawns the nomads eat.",
        ),
    )
    _place(
        b,
        "The Changing Lake",
        inside=dawada,
        summary=paragraphs(
            "A salt lake near Murzuq whose water turns from red to green to "
            "blue and now and then yellow.",
            "Vis: twice a year, as the season and the colour change, red sand "
            "blows over the lake, and some floats by the shore reeds as 2 "
            "pawns each of Imaginem and Muto vis. Locals sometimes gather it "
            "and work it into their pots and bricks.",
        ),
    )
    ubari = _place(
        b,
        "Ubari",
        inside=fezzan,
        summary=paragraphs(
            "Twenty lakes ringed with date palms and rushes under the dunes "
            "of the Ubari Erg, with ruined villages on the shores of several. "
            "The lake water is extremely salty but wells give fresh. Tuareg "
            "camp here to net small red shrimp, ground to paste and shaped "
            "into cakes. Sebha is 28 leagues off.",
        ),
    )
    _place(
        b,
        "Sebha",
        inside=fezzan,
        summary="A stop 28 leagues from Ubari.",
    )
    _place(
        b,
        "The Cemetery of Hatya",
        inside=ubari,
        summary=paragraphs(
            "A Garamantian cemetery rising out of the sands 5 leagues east "
            "of Ubari: the Royal Tombs of Ahramat al-Hattia, the royal part "
            "of some 100,000 tombs scattered across the old kingdom. Many "
            "are enchanted, marking the sorcerer-kings' borders and keeping "
            "finely preserved corpses ready to be raised for any emergency.",
        ),
    )
    _place(
        b,
        "The Forest of the Jobar",
        inside=fezzan,
        **RUMOURED,
        summary=paragraphs(
            "A copse of trees of dark stone shot through with grey crystal, "
            "rising from the sands. After terrible sandstorms some fall and "
            "split; now and then the erg bares a new one. The Tuareg shun it "
            "for fear of the Jobar, a "
            "great lizard that creeps through the dunes under cover of "
            "storms and takes children. Bones of its kind lie across the "
            "desert, and nomads steer by them.",
            "Vis: split trees give fragments rich in Terram vis; one pawn in "
            "five is Herbam or Auram instead, but only in vis found in spring.",
        ),
        secrets="The book does not say where it lies (p. 68). It prints the "
        "second Form as Aurum, read here as Auram.",
    )
    return fezzan


# -- the Garamantians --


def _garamantians(b: Builder, fezzan: Neighbour) -> Neighbour:
    garama = _place(
        b,
        "Garama",
        inside=fezzan,
        summary=paragraphs(
            "The Garamantian capital, a ring of stunted palms around "
            "crumbling mud-brick and cut stone, left when the last "
            "sorcerer-king's palace was destroyed and its main foggaras fell "
            "in. Five centuries of caravans have stripped the surface; only "
            "those who can dig may find what the last Garamantians hid. The "
            "ruined Roman temple, set up after Balbus forced the kingdom into "
            "clientage, may once have drawn wizards wanting solitude and "
            "familiar surroundings in a still pagan land.",
        ),
    )
    b.faction(
        "The Garamantians",
        place=garama,
        faction="People or tribe",
        decides="Sorcerer-kings and an elite nobility",
        wants="Nothing now: they are gone, though their dead may still work.",
        summary=paragraphs(
            "A kingdom in the heart of the Fezzan from 400 BC to 600 AD, of "
            "eight cities, scores of villages and many forts under a line "
            "of one hundred kings. They raided south for slaves, drove off "
            "Rome until Balbus sacked several towns in 15 BC, and then lived "
            "as a nominal client of the Empire. Their sorcerer-kings took "
            "the feather as their sign, and their nobles hunted nomads for "
            "sport from horse-drawn chariots; the Roman Maternus wrote of "
            "going with a slave raid. Slaves guarded the borders, mined "
            "gems in the Tibesti, cut the foggaras, farmed barley, figs, "
            "grapes and wheat and herded shaggy long-horned oxen, while "
            "merchants sold salt, slaves and wheat to Rome. That trade made "
            "the first desert caravans.",
            "Slaves served on after death: blackened, tireless corpses that "
            "needed no water tilled fields and dug mines until they fell "
            "apart. The last king went off in Arab chains in 668. Islam's "
            "Divine auras, among the slaves who worshipped, undid the "
            "rituals, and battle scattered the corpse-warriors to the wind. "
            "The slaves rose under their soldier caste. The surviving lords "
            "spitefully ordered their last corpse-miners to collapse the "
            "foggaras, and without water the people melted into the nomad "
            "tribes or left.",
            "They wrote Punic in the Tifinagh alphabet, later taken up by "
            "the Berbers who absorbed their slaves and refugees; a little "
            "survives on rocks, ruins and buried urns. Some murabitin and "
            "Berber elders can teach the basics, but no one living in Africa "
            "has an effective score above 3. Summoned Garamantian ghosts "
            "speak the dead tongue, though nobles and merchants likely have "
            "some Latin too. They honoured Ammon above all, as Aman, whose "
            "temple and oracle stood at Siwah, now little but ruins and a "
            "small village.",
        ),
        secrets=paragraphs(
            "Their magic (pp. 70-71) was non-Hermetic, limited, and erratic "
            "near the Divine: preserving, animating, sensing through and "
            "commanding corpses, with a small side in sensing water. No text "
            "of its secrets left the kingdom, but some may lie in a hidden "
            "stronghold.",
            "Their ritual for binding a horde of corpses without an Arcane "
            "Connection to each counts in Hermetic research as a Minor "
            "Magical Breakthrough. It yields a simple supernatural ritual "
            "adding a corpse to a horde bound to an object, often a crown or "
            "feathered headdress. Its wearer may use Voice and Group levels "
            "of effect for spells on or through the horde, at Arcane "
            "Connection distance and past a usual Group's numbers. The ritual "
            "has no Penetration, works only on mundane corpses and cannot "
            "last in a Divine aura. Recovered bound objects can be researched "
            "as a source of Garamantian Lore or Insight (Ancient Magic p. 8).",
            "Hermetic Intellego far outdoes their water-sensing, but relics "
            "of it help to understand their methods or to translate Tifinagh.",
        ),
    )
    _place(
        b,
        "Zinchecra",
        inside=fezzan,
        summary=paragraphs(
            "Older than Garama, on a small plateau just north of it. Hardly "
            "anything remains, and the lake is salt flats now, but the spring "
            "still keeps a cut-stone fountain partly full all year.",
        ),
        secrets=paragraphs(
            "Buried in an urn in a small cave nearby is the last initiation "
            "script for Dowsing (ArM5 p. 64), in Tifinagh Punic. To "
            "self-initiate (Target Level 18; The Mysteries: Revised Edition "
            "p. 13) one must properly mummify and entomb 10 people in "
            "Garamantian tombs (+3), go to the cut-stone pool at the autumn "
            "equinox (+3), and bathe there by moonlight while ritually "
            "scarred, the equal of the Blatant Gift (+9). If Garamantian Lore "
            "+ Presence + Initiation Script bonus exceeds 18, one gains "
            "Dowsing for drinking water. Finding and reading the script may "
            "be a whole story arc.",
        ),
    )
    _place(
        b,
        "Sarir Tibesti",
        inside=fezzan,
        **RUMOURED,
        summary=paragraphs(
            "Ancient mines along thin veins of tanos, the green-blue gem "
            "amazonite, hidden in the Tibesti Mountains on the Ténéré border. "
            "Corpse-miners may still be at work in the dark, honeycombing "
            "the rock and piling up uncut stones for masters who will never "
            "come. Tanos was once cut for signets and seals, and gives a +3 "
            "Shape and Material bonus in such devices.",
        ),
    )
    _place(
        b,
        "The Foggaras of the Fezzan",
        inside=fezzan,
        summary=paragraphs(
            "Hundreds of leagues of tunnels cut through the rock to draw "
            "water, thick around the oases from Ghat to Murzuq to Djofra. "
            "Sand fills nearly all of them, and most can be reached only by "
            "magical digging. Silent warriors may lie sealed within, waiting "
            "for a necromancer strong enough to command them.",
        ),
    )
    _place(
        b,
        "The Forgotten Foggara",
        inside=fezzan,
        **RUMOURED,
        summary=paragraphs(
            "As the rebellion began, a noble set corpse-miners to dig him a "
            "new foggara; slaves killed him before he told anyone. The "
            "workers dug a great reservoir under a rocky outcrop until water "
            "drowned their cave. The flow keeps a small wadi green. The "
            "noble's lost supply cache may be close by.",
            "Vis: after rare storms the overflow leaves 5 pawns of Aquam vis "
            "on the wadi's shore, in bone fragments of the lost workers.",
        ),
    )
    return garama


# -- the Central Great Desert --


def _central(b: Builder, desert: Neighbour) -> Neighbour:
    central = _place(
        b,
        "The Central Great Desert",
        inside=desert,
        summary=paragraphs(
            "Bounded by the Mediterranean and the Ahaggar, by the Ubari Desert "
            "to the east and the Grand Western Erg and Tademaït Plateau to "
            "the west: erg, rocky hamada and dry valleys, the driest part of "
            "the Great Desert, with little plant life even in the wadis.",
        ),
    )
    regio = _place(
        b,
        "The Iter Praeter Caput Saxi",
        inside=desert,
        aura=2,
        levels=[
            Builder.level(
                "The Road Past the Stone Heads",
                5,
                see="A narrow desert track looping on itself, with a brackish "
                "well or waterhole every few miles.",
                enter="At the northern entrance outside the ruins of Roman "
                "Lepcis or the southern one by Agisymba, each in a Magic aura "
                "of 2 and marked by an overgrown milestone with faint Mercurian "
                "magic. Elsewhere the road is too narrow to find without a "
                "Camel of Virtue.",
                notes="Very secure, but useless as a covenant site.",
            )
        ],
        **RUMOURED,
        summary=paragraphs(
            "The Bab Ras al-Hammada, a thin line of Magic regio running "
            "hundreds of miles across the Fezzan, past the old Garamantian "
            "lands, to the fabled mountains of Agisymba. Pliny names it as "
            "the secret way of the Roman general Valerius Festus in the first "
            "century AD.",
        ),
    )
    b.link(regio, "places", central, "Passes by the Central Great Desert")
    _place(
        b,
        "Agisymba",
        inside=desert,
        **RUMOURED,
        summary=paragraphs(
            "A land far south of high mountains around a vast lake, home to "
            "giant beasts like the legendary monoceros and cameleopard, and "
            "rich in wild places with undiscovered vis. A small tribe of "
            "Plinian troglodytes lives hidden in its caves, remembering old "
            "Roman slave raids; they might make useful grogs.",
        ),
    )
    b.town(
        "Djanet",
        place=central,
        ruler="Tuareg and Berbers",
        summary=paragraphs(
            "A small Tuareg and Berber oasis in a valley on the western side "
            "of the Tassili n Ajjer, more a cluster of villages than a town, "
            "keeping a large date grove for trade with caravans on the "
            "Garamantian and Ghadames Roads. Ghat is about 25 leagues "
            "north-east, Ghadames 125 leagues north.",
        ),
    )
    _place(
        b,
        "The Arches of Djanet",
        inside=central,
        **LOCAL,
        summary=paragraphs(
            "More than a dozen natural rock arches within 7 leagues of "
            "Djanet, one shaped very like an elephant far bigger than any "
            "real one. A few rare texts by lost scholars of the Fay call them "
            "doors into a regio network; no one who tried has come back to "
            "say where they lead.",
        ),
    )
    oasis = _place(
        b,
        "Ain al-Faras",
        inside=central,
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "The oasis at the heart of Ghadames. The city's Divine aura of 3 "
            "does not reach many lacunae among its covered lanes.",
        ),
    )
    b.town(
        "Ghadames",
        place=oasis,
        charter="Rules itself",
        ruler="Seven Berber clans",
        summary=paragraphs(
            "A stoutly walled city held by seven Berber clans, each with its "
            "district and its souk. Covered walkways join most of the "
            "buildings in a maze of lanes that shuts out the worst of the "
            "heat and hides bandits and cutthroats. The Third Legion "
            "garrisoned it for nearly 200 years; its crumbling fort stands on "
            "a hill to the south-west.",
        ),
    )
    ghardaia_oasis = _place(
        b,
        "The Ghardaia Oasis",
        inside=central,
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "Five fortified villages, or ksours, built to one plan: houses "
            "in rings around a mosque whose minaret is the watchtower, inside "
            "a high wall. Grain and weapons are stored in the mosques, but "
            "people spend the summer out among the date palms. Their close "
            "building around the mosques gives the villages a Divine aura of "
            "3, and Ghardaia's own 4.",
        ),
    )
    daia = _place(
        b,
        "The Mosque of Daïa",
        inside=ghardaia_oasis,
        realm="Divine",
        aura=4,
        summary="The mosque of Ghardaia village, holding relics of the female "
        "saint Daïa, who lived in a cave (ghar) in the valley.",
    )
    b.town(
        "Ghardaia",
        place=daia,
        summary="Founded by Ibadi Muslims in the 11th century in honour of "
        "the saint Daïa.",
    )
    for name in ("Melika", "Beni Isguen", "Bou Noura", "El Atteuf"):
        b.town(
            name,
            place=ghardaia_oasis,
            summary="One of the five ksours of the Ghardaia Oasis.",
        )
    b.town(
        "Ghat",
        place=central,
        summary=paragraphs(
            "'The Last Oasis' to travellers on the Garamantian Road, on the "
            "eastern edge of the Tassili n Ajjer with the Idehan Ubari Erg "
            "north and the Bilma Erg south, and no real last, with Djanet 25 "
            "leagues away, though it lies off the regular road to Bilma. "
            "People stayed for the oasis, not for foggaras. The old town is "
            "dried mud-brick with covered walkways against the heat. A small "
            "fort on an outcrop to the south-west is the Garamantians' "
            "legacy, as is the cemetery of short grave pyramids north of "
            "town.",
        ),
    )
    b.town(
        "Wargala",
        place=central,
        summary=paragraphs(
            "An Ibadi stronghold, with a large mosque on the town square and "
            "a wall of six gates. Date groves and fruit and vegetable gardens "
            "flourish around it and feed its souk, known for its shady arcade "
            "and for a busy slave market that the local jinn use.",
        ),
    )
    return central


# -- the Tuareg redoubts --


def _redoubts(b: Builder, desert: Neighbour) -> Neighbour:
    redoubts = _place(
        b,
        "The Redoubts of the Tuareg",
        inside=desert,
        summary=paragraphs(
            "The Tuareg hold the south-central reaches around the great "
            "mountain plateaus, though they turn up anywhere in the sands. In "
            "the Tanezrouft and the Ténéré a string of waterless Magic auras "
            "almost rings these mountains, leaving only the caravan route "
            "into the Haggar massif from the north, so the homelands can "
            "hardly be reached without the Great Desert Regio Network.",
            "Painted dogs hunt in packs among the high peaks and raid the "
            "nomads' herds.",
        ),
    )
    ahaggar = _place(
        b,
        "The Ahaggar",
        inside=redoubts,
        summary=paragraphs(
            "The Tuareg's spiritual home and refuge, a plateau of hard black "
            "rock split into pinnacles and towers, its valleys full of cooled "
            "lava, lilac in the setting sun. The central peaks are the Atakor, "
            "'the place of stone'. Raptors nest here but the land only feeds "
            "the goats and sheep of the lesser Kel Ulli tribes; the Kel "
            "Ahaggar live mostly in the dark canyons around the edge.",
            "The Egyptians believed the destructive force strongest in these "
            "mountains (see the Great Hunger), which may only be where a "
            "powerful faerie tied to it claimed to come from.",
            "Vis: Tahat, Ilaman, Amjer, Tiouyen and Iherhe are the highest "
            "peaks, and the Tuareg say their spirits quarrelled over love. "
            "At the foot of Ilaman is the spring that opened when jealous "
            "Amjer struck his brother's shoulder; its water is a liquid form "
            "of Terram vis.",
        ),
        secrets=paragraphs(
            "The remotest heights are pocked with Magic auras. In the sharpest "
            "clefts at their feet lie small Infernal auras, home to demons "
            "and Infernal jnun of the Aerial Powers and Furies, who send flash "
            "floods down the gueltas.",
        ),
    )
    b.town(
        "Tamanghest",
        place=ahaggar,
        ruler="Tuareg herders",
        summary=paragraphs(
            "A rich oasis of ochre houses in the Ahaggar near the Tassili n "
            "Ajjer, with groves of lemons, dates, figs and almonds, millet, "
            "wheat and small goat herds. Its herders call themselves "
            "guardians of the Tassili's cypresses and have named every tree. "
            "It is an open secret among the tribes as a place to trade and "
            "rest; few outsiders come without the nomads' blessing.",
        ),
    )
    _place(
        b,
        "Abalessa",
        inside=ahaggar,
        **LOCAL,
        summary="A haven almost 17 leagues west of Tamanghest, with the "
        "sealed tomb of Tin Hinan, said to have healing properties.",
    )
    tassili = _place(
        b,
        "The Tassili n Ajjer",
        inside=redoubts,
        aura=2,
        summary=paragraphs(
            "The northern massif, the 'Plateau of Rivers', just north of the "
            "Ahaggar: rocky upland cut by deep gorges and hidden gueltas, "
            "with hundreds of natural arches, stands of cypress, myrtle and "
            "wild olive, and dozens of petroglyphs. The tribes hold it sacred "
            "and the Wind Spirits often rest here. The plateau lies under a "
            "Magic aura of 2.",
            "The ancient cypresses, tarout to the Tuareg, cluster in the "
            "eastern uplands, each over 2000 years old, gnarled, and with "
            "its own character. Many hold genius loci spirits protective of "
            "the Tuareg.",
        ),
    )
    _place(
        b,
        "Wadi Amazar",
        inside=tassili,
        **LOCAL,
        summary=paragraphs(
            "A stony wadi with the oldest grove, led by Tin-Balalan, 'the one "
            "with the pool at its feet'. Each tree is the body of a powerful "
            "genius loci, wiser than any man and a Magic guardian of its "
            "ground, like the elder trees of the German forests (Guardians "
            "of the Forest ch. 4; Realms of Power: Magic p. 106).",
            "Vis: Tuareg hedge magicians must beg a tree's spirit for timber. "
            "A fallen limb holds Vim vis, each tree's giving its own power "
            "once enriched: Tin-Balalan Puissant Leadership, Tin-Ambarak "
            "Puissant Ride, Tin-Gaded Wilderness Sense, Tin-Tamanzazt Lesser "
            "Immunity to Thirst. Wandering male inenden know the enrichment "
            "and must be bargained with or forced. Ancient cypress wood gives "
            "+3 to spirits and +3 to necromancy.",
        ),
    )
    air = _place(
        b,
        "The Aïr",
        inside=redoubts,
        aura=4,
        summary=paragraphs(
            "Nine circular volcanic massifs overlooking the Ténéré, long a "
            "Tuareg stronghold, with acacia-shaded wadis that fill after the "
            "rains of early autumn. Their graven rock art includes a pair of "
            "long-necked creatures like Pliny's cameleopardalis. Each site "
            "marks a strong Magic aura, at least 4, aligned to Animal or "
            "Terram, valued by Tuareg hedge wizards, who oddly do not claim "
            "the carvings. The art draws packs of painted dogs, spotted "
            "jackal-like beasts that must be driven off before any rite.",
        ),
    )
    _place(
        b,
        "Idoukal-n-Taghès",
        inside=air,
        levels=[
            Builder.level(
                "The Mediterranean garden",
                0,
                see="A Mediterranean climate, with plants and herbs not found "
                "in the desert, among them common European Herbs of Virtue.",
                notes="Herbam-aligned. The book gives no aura strength.",
            )
        ],
        summary="The tallest peak of the Aïr, above the pilgrimage village of "
        "Abatol, holding a Magic regio.",
    )
    _place(
        b,
        "The Adagh",
        inside=redoubts,
        realm="Faerie",
        summary=paragraphs(
            "A sandstone massif past the feared Tanezrouft, sometimes called "
            "the Adrar Ifoghas after the Kel Ifoghas who claim it. Unlike the "
            "other three its auras are mostly Faerie. Its rock art shows nomad "
            "life, and shifts from one visit to the next.",
        ),
        secrets="The book prints no strength for its auras (p. 74).",
    )
    b.faction(
        "The Kel Asouf",
        faction="Spirits and beings",
        place=redoubts,
        realm="Faerie",
        summary=paragraphs(
            "The People of the Empty Spaces, the true Faerie jnun of the "
            "desert, like the jinn of the Muslim north but wilder and darker. "
            "Some southern Tuareg tribes, the Kel Ifoghas, Iwellemmeden and "
            "Kel Geres, have many Faerie-blooded folk among them.",
        ),
    )
    return redoubts


# -- the Tanezrouft --


def _tanezrouft(b: Builder, desert: Neighbour) -> Neighbour:
    tanezrouft = _place(
        b,
        "The Tanezrouft",
        inside=desert,
        summary=paragraphs(
            "The western Great Desert, from the Atlantic to the Western Erg, "
            "the Tademaït and the Ahaggar, and the Bilma Erg; the Chech Erg "
            "presses the Atlas in the north. Few but caravans and the "
            "hardiest Tuareg come here. The wind sweeps away the tracks of "
            "those ahead, and stragglers get lost or fall to hyenas and "
            "jackals.",
            "Sijilmasa, founded by Berbers in 757 on the road to Tangier, "
            "stands at its northern gate, struggling to live off the "
            "caravans of salt, gold and slaves. Old wealth from its great "
            "market in the western quarter raised its high ochre walls, "
            "stately temples and Sufi madrasas.",
        ),
    )
    mosques = _place(
        b,
        "The Mosques of Iwalatan",
        inside=tanezrouft,
        realm="Divine",
        aura=3,
        summary="Several mosques that give Iwalatan a Divine aura of 3.",
    )
    b.town(
        "Iwalatan",
        place=mosques,
        ruler="The Massufa Berbers",
        summary=paragraphs(
            "A wonder of cut stone, the southern end of the Iwalatan Road and "
            "the Taghaza Trail. The Massufa keep a few date groves with "
            "melons in their shade, and flocks of sheep, and after the long "
            "dry road its many wells taste all the sweeter. Timbuktu is 100 "
            "leagues east-south-east, and the salt mines of Taghaza 165 leagues "
            "north-north-east.",
        ),
        secrets="The book disagrees on the road to Taghaza: 165 leagues "
        "north-north-east from here (p. 74), 125 leagues south-south-east from "
        "there (p. 75).",
    )
    _place(
        b,
        "Tasarahla",
        inside=tanezrouft,
        summary=paragraphs(
            "No more than a spot in the dunes where water seeps from the "
            "ground, marked by a middling stone and a patch of mud, with a "
            "few fire rings and low walls to shield tents. New arrivals must "
            "often clear the well and wait; the flow is slow but steady. "
            "Taghaza is about 53 leagues north, ten days away, and Iwalatan "
            "about 75 leagues south-south-west.",
        ),
    )
    pits = _place(
        b,
        "The Salt Pits of Taghaza",
        inside=tanezrouft,
        realm="Infernal",
        aura=3,
        summary=paragraphs(
            "A rich chott dug into pits, with not a tree in sight and an "
            "Infernal aura of 3.",
        ),
    )
    b.town(
        "Taghaza",
        place=pits,
        ruler="The Massufa Berbers",
        summary=paragraphs(
            "Hardly an oasis: a barren mining town of the Massufa's all-male "
            "slaves, built of salt blocks and roofed with camel hide. Every "
            "threshold faces west, since evil jinn are said to be unable to "
            "enter from that side. Foreign merchants have a slightly better "
            "way-station on the east edge. The only food is camel, or dates "
            "and millet off the caravans; when these are late many slaves "
            "die. Flies swarm and the water is brackish. Yet the town is "
            "awash with gold and exotic goods from the south, traded with "
            "salt to northern caravans for slaves and manufactures.",
            "The Chech Erg lies north, and the El Djouf makes the 165 leagues "
            "south to Timbuktu a trek for only the most determined caravans. "
            "Iwalatan is 125 leagues south-south-east and Sijilmasa some 20 "
            "days north.",
        ),
        secrets="The book disagrees on the road to Iwalatan: 125 leagues "
        "south-south-east from here (p. 75), 165 leagues north-north-east from "
        "there (p. 74).",
    )
    tuwat = _place(
        b,
        "Tuwat",
        inside=tanezrouft,
        summary=paragraphs(
            "A string of oases some 30 leagues long where the Tanezrouft meets "
            "the Central Great Desert, with hundreds of date palms watered by "
            "seasonal pools and foggaras down to deep fossil water. Four "
            "fortified ksours with thick walls and watchtowers stand here: "
            "Buda in the north and Reggane in the south keep the foggaras, "
            "and the other two tend the palms. The Tademaït's sandstone "
            "walls, up to 500 paces high, ring it south and east, and dunes "
            "slump in from the north and west. The sirocco blows hard and "
            "sometimes attacks caravans.",
        ),
    )
    for name, where in (
        ("Buda", "the north"),
        ("Reggane", "the south"),
    ):
        b.town(
            name,
            place=tuwat,
            summary=f"A small ksour in {where} of Tuwat whose people maintain "
            "the foggaras.",
        )
    return tanezrouft


# -- the Ténéré --


def _tenere(b: Builder, desert: Neighbour) -> Neighbour:
    tenere = _place(
        b,
        "The Ténéré",
        inside=desert,
        summary=paragraphs(
            "The southern desert under the Aïr, with the Erg of Bilma at its "
            "heart and the Tibesti between it and the Libyan Desert. The "
            "Ennedi Hamada rises on its southern border, from which some "
            "claim to see the Nubian Desert or the haze of the Torrid Zone. "
            "Painted dogs try to steal from the nomads' goats and camels.",
        ),
    )
    b.town(
        "Aouderas",
        place=tenere,
        ruler="Tuareg",
        summary=paragraphs(
            "A small oasis among the massifs of the Aïr, peopled by Tuareg "
            "and their slaves, who trade water, shelter and dates for "
            "supplies. Most live in a hilltop fortress that guards the well "
            "and the harvest from raiders and jinn who prefer blood to trade. "
            "Timia is 15 leagues north-east through treacherous canyons, and "
            "Bilma 120 leagues east-north-east over the Erg of Bilma.",
        ),
    )
    b.town(
        "Bilma",
        place=tenere,
        summary=paragraphs(
            "The largest town before Siwa to the north or Nubia to the east, "
            "sheltered under the Kaouar Cliffs from the dunes, known for its "
            "gardens, salt mines and date groves. Caravans often turn back "
            "here for Egypt and Cyrenaica, or press on towards the fabled "
            "Sorcerer-King's lands. The oasis fortress of Djaba is 55 leagues "
            "north and Fachi due west.",
        ),
    )
    _place(
        b,
        "Fachi",
        inside=tenere,
        aura=4,
        summary=paragraphs(
            "A lonely citadel cut from volcanic rock in the Bilma Erg, living "
            "like Aouderas by salt, water and dates. A few sweet lakes make "
            "traders glad to deal before the 65 leagues east to Bilma or west "
            "to Timia. Its unspoiled state and lack of a mosque give it a "
            "Magic aura of 4.",
        ),
    )
    b.town(
        "Fada",
        place=tenere,
        ruler="Tuareg",
        summary=paragraphs(
            "A small, very isolated Tuareg town 200 leagues east-south-east "
            "of Bilma, a day north-north-west of the Great Desert's greatest "
            "stone pool: a rain-fed wadi at the foot of water-carved cliffs "
            "that never dries, ringed with trees, with camels, crocodiles and "
            "stranger creatures. Only those bound for the Nubian Desert or "
            "across the Torrid Zone come here.",
        ),
    )
    b.town(
        "Takedda",
        place=tenere,
        ruler="Tuareg, said to owe fealty to the wizard Sogolon Conde",
        summary=paragraphs(
            "The Bilma Trail's last western outpost, a Tuareg oasis with "
            "copper mines and date plantations, rumoured to answer to a "
            "wizard named Sogolon Conde. West lie the 'Lands of Thirst' and "
            "the roads towards the purported Sorcerer-King of Sosso. It is 45 "
            "leagues east over the Bilma Erg to the Aïr. Those seeking gold "
            "come here, as Bilma has little.",
        ),
    )
    b.town(
        "Timia",
        place=tenere,
        ruler="Tuareg",
        summary=paragraphs(
            "A valley paradise in Tuareg hands, famed for a huge deep stone "
            "well of dark water, a guelta that never empties and supports "
            "small orchards. The road from Aouderas to Bilma passes through, "
            "with 65 leagues of dunes to the next true rest at Fachi.",
        ),
    )
    for name, summary in (
        (
            "The Erg of Bilma",
            "The dune sea at the heart of the Ténéré, swaddling the Aïr. "
            "Rock salt is mined here in great quantities.",
        ),
        (
            "The Kaouar",
            "Cliffs and oases on the Bilma Trail, sheltering Bilma from the dunes.",
        ),
        (
            "Djaba",
            "An oasis fortress 55 leagues north of Bilma.",
        ),
    ):
        _place(b, name, inside=tenere, summary=summary)
    return tenere


# -- the trade roads --


def _roads(b: Builder, desert: Neighbour) -> None:
    for name, summary in (
        (
            "The Iwalatan Road",
            "The western route, from Marrakesh by way of Sijilmasa, through "
            "the pass held by the fortress of Tamdoult, across the Tanezrouft "
            "to fading Aoudaghost, then on to Iwalatan. Its caravans mostly "
            "bring back gold.",
        ),
        (
            "The Taghaza Trail",
            "From Sijilmasa twenty-five days south to Taghaza, ten more to "
            "the well at Tasarahla, and fifteen south to Iwalatan, though "
            "some bear south-south-east at Tasarahla. Gold and slaves go "
            "north, manufactures and salt come back. The great expeditions "
            "of thousands of camels leave at the start of the cool season in "
            "November, a smaller one in March, and rasher small parties at "
            "any time. Northbound caravans disperse from Sijilmasa to Fez, "
            "Tahert, Tangier, Tlemcen and Tunis.",
        ),
        (
            "The Ghadames Road",
            "Two forks in Ifriqiya, from Tunis and from Tripoli, meet at "
            "Wargala and go on to Ghadames, then south-east to Takedda or "
            "south-west into the Tanezrouft. Slaves, salt and gold go north, "
            "manufactures and slaves south. It keeps west of most of the "
            "Ahaggar, long and dangerous.",
        ),
        (
            "The Garamantian Road",
            "From Siwa over the Libyan Sand Sea to Zaouila and Ghat, then "
            "south to end at Tadekka. Northbound caravans often run on past "
            "Siwa to the souks of Cairo and Alexandria. As dangerous as the "
            "Ghadames Road, it keeps mostly east of the Ahaggar.",
        ),
        (
            "The Bilma Trail",
            "The shortest route, from Cyrene or Cairo through the Great Sand "
            "Sea to Murzuq, south between the Ahaggar and the Tibesti to the "
            "Kaouar oases and over the dunes to Bilma, where it turns east "
            "for Nubia or west for the Western Desert. Slaves, salt and ivory "
            "come north for horses, weapons and manufactures. Bilma is about "
            "21 days from Takedda and the same from Murzuq.",
        ),
    ):
        _place(b, name, inside=desert, summary=summary)
    for name, summary in (
        ("Tamdoult", "A fortress guarding a pass on the Iwalatan Road."),
        ("Aoudaghost", "A fading city on the Iwalatan Road."),
        ("Zaouila", "A stop on the Garamantian Road past the Libyan Sand Sea."),
    ):
        _place(b, name, inside=desert, summary=summary)
    b.custom(
        "The Desert Caravans",
        place=desert,
        decides="The caravan guide",
        wants="Goods carried across and profit shared out.",
        summary=paragraphs(
            "The crossing goes by stages of about 7 leagues (21 miles) and "
            "takes two to three months one way, on the backs of camels and "
            "slaves. Gold, slaves and salt go north; slaves, glass and horses "
            "go south, among much else. Northbound too are ivory, gum arabic, "
            "ostrich feathers, kola nuts, ebony and cloth, cotton cloth, "
            "hides, goatskins and leatherwork. Southbound are dates, figs, "
            "sugar, cowries, copper, ironwork, paper, books, tools, weapons, "
            "cotton, silk, textiles, ceramics and armaments, serving as "
            "currency with the nomads. Salt and copper from the desert are "
            "bought along the way. Wheeled vehicles cannot cross, since no "
            "road stays clear of sand, so bulk trade is rare. Barbary steeds, "
            "bred for slavers rounding up people where horses are unknown, "
            "cost ten to thirty slaves each.",
            "Thousands of slaves cross each year, half-starved and carrying "
            "the goods, many expected to die. Moorish pirates take pagans "
            "from Rus, Christians from the Mediterranean and England, and the "
            "least scrupulous Muslims from Iberia and the Levant. Those from "
            "the south reaching the Maghreb are mostly women, at 3 to 9 "
            "Mythic Pounds, though a ruler may buy men for war, as Marrakesh's "
            "founder bought 2,000. Islamic law frees a concubine who bears a "
            "Muslim's child, and soldiers die or win freedom, so demand and "
            "prices stay high.",
            "Berbers and Tuareg bring most of the caravans from the south, "
            "with hundreds of camels, into the markets in March and November; "
            "Muslim traders go the other way. The Genoese have traded along "
            "the coast since the mid-11th century, with enclaves at Safi, "
            "Sale, Tangier, Orano, Algiers, Bona, Tunis, Mahadia and Tripoli, "
            "chiefly for gold, timber, salt, cheese, wine, oil and grain, and "
            "take part in the slave trade too: many of their households keep "
            "two or three slaves. Many places forbid keeping Christian slaves, "
            "and an owner should free one who converts, which keeps demand "
            "from the north up.",
            "Merchants bound for one city gather at its departure city, buy "
            "rested camels and choose a guide, on whom everything depends. He "
            "sets a day in the cool months, October to March. The merchant "
            "stays home, sending a trusted slave or young relative. Up to two "
            "thousand camels move as one, a stage a day, by night and "
            "morning, by a winding route that ends each day at water, though "
            "camels need it only every ten days, for a well may be dry, "
            "poisoned, buried, beset by bandits or not where he remembers.",
            "A guide needs Area Lore to follow paths the sandstorms change, "
            "languages to deal with the tribes, Leadership to hold his men "
            "in trouble, the stars to steer by, and often dealings with "
            "creatures of the realms. He is paid in money or shares of cargo. "
            "Four days out a pair of runners goes ahead to warn the Sudanese, "
            "never one alone, for the demons of the desert play with single "
            "runners until they go mad or die of thirst; they earn pounds of "
            "gold for a few days' work. At a Maghrebi city everyone must buy, "
            "sell and change camels before the caravan leaves, and some "
            "cities see one a year or one in ten years, so the pressure is "
            "intense and crime by and against merchants pays.",
            "Camels come in two breeds: big, slow pack camels, by far the "
            "commoner, and swift saddle camels used as combat mounts, faster "
            "than oxen and carrying more than horses. Caravans make 15 to 25 "
            "miles a day. The wealthy and pilgrims ride in small canopies, "
            "often for two, shielded from sun and sand, with room to talk, "
            "play chess or eat.",
        ),
        secrets=paragraphs(
            "The Ride Ability covers camels. Many warriors ride a camel to "
            "battle and change to a horse to fight. Camel statistics are in "
            "the book's Bestiary Appendix (p. 136).",
        ),
    )


# -- the Sudan --


def _sudan(b: Builder) -> None:
    sudan = _place(
        b,
        "The Bilad-es-Sudan",
        **RUMOURED,
        summary=paragraphs(
            "The 'Land of the Blacks' south of the desert, fringed by the "
            "fertile Sahel, the 'shore', fed in the west by the Senegal and "
            "the Niger, with Sudanese, Berber and Arab people. Its people "
            "want no foreigners past the trade camps at the desert's edge, "
            "and in some places trade only at oases, sending agents into the "
            "desert to meet them. They say it is to hide the source of their "
            "gold, but there is no other way to it, and merchants would warn "
            "them of any invasion like the one that came once from the Tell.",
            "Kombuh Saleh lies here.",
        ),
        secrets=paragraphs(
            "Theories traded at dinner parties in the Tell (pp. 81-82): that "
            "the Sudanese are faeries; that their way of life would disgust "
            "the Arabs; that they are the servant caste of a people who shun "
            "Allah's servants, such as evil jinn; that the gold comes "
            "corruptly, perhaps as monsters' excrement; that the desert truly "
            "is the world's edge and the Sudan is in Faerie; that gold is as "
            "cheap as sand to them; or that their faerie rulers want the "
            "journey, not the gold, and every trade good ever brought sits "
            "in a pile outside Kombuh Saleh.",
            "If history holds, the kingdoms here are small and war-tossed, "
            "between the fall of the Empire of Ghana in 1204 and the founding "
            "of the Empire of Mali about 1240.",
        ),
    )
    b.lord(
        "The Sorcerer-King of Sosso",
        title="",
        ruler="Soumaoro Kanté",
        place=sudan,
        summary=paragraphs(
            "Soumaoro Kanté, rumoured ruler beyond the trade routes and "
            "Caliph of Kanem, of a nominally Muslim kingdom, a shadow whose "
            "name Berbers and Tuareg only whisper, since he is said to hear "
            "it on the desert wind. Merchants' tales of him are written off "
            "as the madness of the long road, yet something at the end of "
            "the routes keeps demanding slaves, and the merchants will not "
            "say who buys them.",
        ),
    )
    b.custom(
        "The Silent Traders",
        place=sudan,
        wants="Their sources of gold kept secret.",
        summary=paragraphs(
            "Those who deal in gold guard its source. Northern caravan "
            "masters leave wares on an agreed stone and withdraw; the gold "
            "traders come out, leave what they think fair, signal and hide. "
            "The caravan takes the gold or signals it is too little, back and "
            "forth until one side leaves with gold or goods. Locals say two "
            "plants have roots of pure gold, a tale for the gullible.",
        ),
        secrets=paragraphs(
            "Who they are the book leaves open: faeries feeding on the "
            "exchange, demons breeding greed, tribesmen without speech, or "
            "emissaries of a lost kingdom such as Atlantis, Prester John or "
            "the Sorcerer-King of Sosso.",
        ),
    )


# -- the creatures --


def _creatures(b: Builder, desert: Neighbour, garama: Neighbour) -> None:
    b.creature(
        "Garamantian Walking Dead",
        page="p. 69",
        size=0,
        place=garama,
        how_many="Hordes, once",
        tires=False,
        block={
            "characteristics": characteristics(-2, -2, 0, -2, 3, 3, 1, 0),
            "virtues_flaws": ["No Fatigue", "Improved Soak"],
            "abilities": [("Brawl", 3, "fist")],
            "traits": {"Persistent": 3, "Walking Dead": 3},
            "reputations": {"Don't Exist (local)": 3},
        },
        attacks=[
            b.attack("Fist", 0, 7, 4, 5),
            b.attack("Grapple", 0, 3, 6, None),
        ],
        soak=11,
        encumbrance="0 (0)",
        equipment="Ragged clothes, now and then a mining tool.",
        appearance="A shrivelled, leathery corpse blackened by the sun, in "
        "tattered rags, with pale, milky, pupil-less eyes and a slow, "
        "stuttering gait.",
        notes=paragraphs(
            "Lies still unless carrying out its last orders, which it repeats "
            "until it cannot or until a more important order applies. A "
            "season's study makes one a source of Garamantian Lore or Insight. "
            "No vis.",
            "Printed wounds: -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated "
            "(16-20), Destroyed (21+).",
        ),
    )
    b.creature(
        "Amur, the Pale Fox of Virtue",
        page="p. 77",
        realm="Magic",
        might=15,
        form="Animal",
        size=1,
        season="Spring",
        confidence=(0, 0),
        place=desert,
        block={
            "characteristics": characteristics(1, 0, -2, -5, 1, -1, 2, 2),
            "virtues_flaws": [
                "Perfect Balance",
                "Nocturnal",
                "Ambush Predator",
                "Crafty",
                "Good Jumper",
                "Keen Sense of Smell",
                "Gigantic",
                "Gift of Speech",
                "Improved Abilities",
                "Improved Attack",
                "Improved Damage",
                "Improved Damage",
                "Improved Initiative",
                "Improved Soak",
                "Improved Soak",
                "Lesser Power",
                "Personal Power",
                "Personal Power",
                ("Minor Flaw", {"flaw": "Restricted Magic"}),
            ],
            "abilities": [
                ("Area Lore: Great Desert", 4, "oases"),
                ("Athletics", 4, "running"),
                ("Awareness", 3, "food"),
                ("Brawl", 3, "bite"),
                ("Concentration", 2, "Imaginem effects"),
                ("Guile", 4, "lying"),
                ("Hunt", 4, "prey"),
                ("Living Language: Arabic", 4, "conversations"),
                ("Stealth", 4, "stalking prey"),
                ("Survival", 4, "desert"),
            ],
            "traits": {"Fox": 3, "Sly": 3},
            "reputations": {"Wily (local)": 3},
        },
        attacks=[
            b.attack("Dodge", 2, None, 5, None),
            b.attack("Bite", 5, 11, 7, 8),
        ],
        soak=3,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Give Chase",
                1,
                -4,
                "Mentem",
                rtd=("Eye", "Sun", "Ind"),
                level=15,
                does="Its gaze fills a victim with the wish to chase it until "
                "sunrise or sunset. ReMe 15 (Base 4, +1 Eye, +2 Sun): Lesser "
                "Power (15 levels, -2 Might cost).",
            ),
            b.power(
                "Gone to Ground",
                1,
                0,
                "Animal",
                rtd=("Per", "Mom", "Ind"),
                level=20,
                does="Teleports to a place within 500 paces to which it has an "
                "Arcane Connection. ReAn 20 (Base 20): Personal Power (20 "
                "levels, -1 Might cost). Not while observed.",
            ),
            b.power(
                "Unsporting Stalker",
                0,
                1,
                "Imaginem",
                rtd=("Per", "Conc", "Ind"),
                level=3,
                does="Blends into the terrain, +3 to vision-based Stealth "
                "checks. MuIm 3 (Base 1, +1 Diam, +1 moving images): Personal "
                "Power (5 levels, -1 Might cost, +15xp Concentration). The book "
                "prints Duration Conc but prices +1 Diam.",
            ),
        ],
        vis=[BodyVis(3, "Animal", "in its tail")],
        encumbrance="0 (0)",
        appearance="Pony-sized, long in the body with a narrow head and "
        "muzzle, big ears and short limbs; sandy fur, ivory at the belly, the "
        "tail darkening to a sooty tip.",
        notes=paragraphs(
            "Natural Weapons, Teeth: Init 0, Atk +3, Def +1, Dam +1. Printed "
            "Flaw Restricted Magic (it cannot use Gone to Ground while "
            "observed) is recorded as its Minor Flaw; the catalog has no Flaw "
            "of that name. Wounds: -1 (1-6), -3 (7-12), -5 (13-18), "
            "Incapacitated (19-24), Dead (25+).",
            "Pale Foxes live in small family groups, rest in burrows up to 10 "
            "paces deep through the midday heat, and go out at twilight, "
            "needing no water. They love a good trick or a long chase, leaving "
            "tracks and glimpses to draw it out, and taunt hunters and steal "
            "their kills.",
            "Enrichment: its tail lining a cloak hood or boots of the finest "
            "gazelle hide, made only by moonlight, gives Puissant Guile (the "
            "cloak) or Puissant Stealth (the boots). A tail makes one item.",
        ),
    )
    b.creature(
        "Axudad, the Deathstalker Scorpion of Virtue",
        page="pp. 81-82",
        realm="Magic",
        might=10,
        form="Animal",
        size=-2,
        season="Summer",
        confidence=(0, 0),
        cunning=True,
        place=desert,
        how_many="Dozens guard the hidden wadi of The Bitter Fruit",
        block={
            "characteristics": characteristics(-2, -2, -5, -6, -4, 2, 2, 3),
            "virtues_flaws": [
                "Magic Animal",
                "Lightning Reflexes",
                "Magical Monster",
                "Infamous",
                "Aggressive",
                "Ambush Predator",
                "Extra Natural Weapons",
                "Grapple",
                "Tough Hide",
                "Venomous",
                "Gigantic",
                ("{form} Resistance", {"form": "Ignem"}),
                "Lesser Power",
                "Personal Power",
                "Susceptible to Deprivation",
            ],
            "abilities": [
                ("Area Lore: Great Desert", 2, "rock outcroppings"),
                ("Athletics", 3, "sprinting"),
                ("Awareness", 3, "spotting prey"),
                ("Brawl", 4, "sting"),
                ("Concentration", 2, "remaining still"),
                ("Guile", 1, "lying"),
                ("Hunt", 3, "small game"),
                ("Ignem Resistance", 4, "solar heat"),
                ("Penetration", 5, "Animal"),
                ("Stealth", 4, "ambush"),
                ("Survival", 3, "desert"),
            ],
            "traits": {"Fierce": 3, "Scorpion": 3},
            "reputations": {"Deadly (local)": 5},
        },
        attacks=[
            b.attack("Pincers", 3, 9, 10, 0),
            b.attack("Grapple", 3, 9, 0, None),
            b.attack("Sting", 7, 9, 2, -3),
        ],
        soak=4,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Venomous Sting",
                0,
                0,
                "Animal",
                does="If its Attack Advantage beats the victim's armor "
                "Protection (not Soak), the victim suffers an exceptionally "
                "debilitating poison (Stamina roll against Ease Factor 6, "
                "Incapacitating), wounded or not.",
            ),
            b.power(
                "Drive Berserk",
                1,
                -1,
                "Mentem",
                rtd=("Touch", "Diam", "Ind"),
                level=10,
                does="Its touch drives the target to attack everything nearby "
                "for a Diameter. CrMe 10 (Base 4, +1 Touch, +1 Diameter): "
                "Lesser Power (10 levels, -1 Might cost, 5xp Concentration, "
                "+5xp Penetration).",
            ),
            b.power(
                "Lie in Wait",
                0,
                2,
                "Imaginem",
                rtd=("Per", "Conc", "Ind"),
                level=10,
                does="Sitting still, it looks like a plain rock or small dune. "
                "MuIm 10 (Base 5, +1 Conc): Personal Power (10 levels, -1 Might "
                "cost, +10xp Concentration).",
            ),
        ],
        vis=[BodyVis(2, "Mentem", "in its stinger")],
        encumbrance="0 (0)",
        appearance="A dull black or slate grey creature with crab-like "
        "chitinous legs, glossy obsidian eyes, "
        "oversized pincers and a barbed tail arched over its back; as big as "
        "a healthy dog or a six-year-old child.",
        notes=paragraphs(
            "Natural Weapons: pincers Init +0, Atk +3, Def +3, Dam +4; tail "
            "sting Init +4, Atk +2, Def -6, Dam +1. The book prints Grapple "
            "Defense as +* and Sting Damage as -3* with no key, so Grapple "
            "Defense is 0 here. Wounds: -1 (1-3), -3 (4-6), -5 (7-9), "
            "Incapacitated (10-12), Dead (13+).",
            "Cruel and belligerent, it hunts warm creatures sleeping by fires "
            "or on sunny rocks, and lurks under the sand to sting what steps "
            "over it.",
            "Enrichment: its stinger set on a willow handle, anointed with "
            "Alkhad gourd sap and left a month plunged in a dune, carried as "
            "a token, gives Greater Immunity to Venom. The Tuareg claim the "
            "creeping Alkhad or Tadjalt plant and its inedible gourds cure "
            "scorpion venom; the cut gourd's milky sap is said to purge "
            "poison.",
        ),
    )
    b.creature(
        "Demon of Thirst and Despair",
        page="p. 83",
        realm="Infernal",
        might=10,
        form="Aquam",
        size=1,
        order="Accusers (variant)",
        how_many="A kind; they haunt the desert",
        place=desert,
        weakness="Protected Group: it can prey only on solo travellers.",
        block={
            "characteristics": characteristics(1, 1, 0, 1, 2, 2, 2, 1),
            "virtues_flaws": ["Weak-Willed"],
            "abilities": [("Brawl", 6, "trample")],
            "traits": {"Doubt": 3},
        },
        attacks=[b.attack("Trample", 8, 16, 14, 13)],
        soak=7,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Coagulation",
                1,
                -1,
                "Terram",
                does="Takes a material form in one round, most often a wave of "
                "grinding stones, and may discorporate almost at once. Its "
                "rocky body can hide trails and landmarks.",
            ),
            b.power(
                "Elemental Control of Water",
                0,
                1,
                "Aquam",
                does="Variable cost: any Creo, Muto or Rego Aquam effect at 1 "
                "Might a magnitude, minor effects of level no higher than its "
                "Might. It taunts those dying of thirst.",
            ),
            b.power(
                "Envisioning",
                1,
                0,
                "Mentem",
                does="Subtly alters dreams to make them more ominous and depressing.",
            ),
            b.power(
                "Obsession",
                3,
                -5,
                "Vim",
                does="When a human commits a venial sin and it spends Might, "
                "then at the next crisis of worthiness the storyguide rolls a "
                "simple die +3 and the player a simple die + a suitable "
                "Personality Trait - adjustments for harsh surroundings. If "
                "the demon's total is higher, the character gains Doubt +1; "
                "acting on it puts him in a state of sin, and the demon then "
                "coagulates and kills him.",
            ),
        ],
        vis=[BodyVis(2, "Perdo", "tainted, in its body")],
        appearance="Often an elemental of grinding stones, or a moving pillar "
        "of salt, rarely a human shape, which it never shows to those strong "
        "enough to fight it.",
        notes=paragraphs(
            "Rules from Realms of Power: The Infernal. Abilities include "
            "specialization in the Attack and Defense totals. Wounds: -1 (1-6), "
            "-3 (7-12), -5 (13-18), Incapacitated (19-24), Dead (25+).",
            "It misleads travellers until hardship and fear of death cost "
            "them their faith, then kills them before they can repent, often "
            "turning its body into a grave and tempting the victim to throw "
            "himself in; the few with human form make pools and drown them. "
            "It is why caravan runners go in pairs.",
        ),
    )
    b.creature(
        "Aisha Qandisha",
        page="p. 85",
        realm="Faerie",
        might=45,
        form="Mentem",
        size=-1,
        place=desert,
        tires=False,
        block={
            "characteristics": characteristics(3, 1, 5, 5, 0, 0, 1, 1),
            "virtues_flaws": [
                "Greater Power",
                "Greater Power",
                "Greater Power",
                "Ritual Power",
                "Ritual Power",
                "Ritual Power",
                "Ritual Power",
                "Faerie Sight",
                "Faerie Speech",
                "Hybrid Form",
                ("Sovereign Ward", {"ward": "can't harm women"}),
                "Incognizant",
            ],
            "abilities": [
                ("Area Lore: Local", 9, "riverbeds"),
                ("Awareness", 6, "victims"),
                ("Brawl", 6, "claws"),
                ("Carouse", 9, "victims"),
            ],
            "traits": {"Destructive": 3, "Gleeful": 2, "Merciless": 2},
        },
        attacks=[b.attack("Clawed hands", 1, 11, 12, 2)],
        soak=-1,
        powers=[
            b.power(
                "Allure",
                1,
                0,
                "Mentem",
                level=10,
                does="+3 on all rolls to impress others. Base 3, +1 Touch, +2 Sun.",
            ),
            b.power(
                "Grant Major Flaw (Wildness)",
                10,
                -19,
                "Vim",
                rtd=("Touch", "Mom", "Ind"),
                level=50,
                does="Ritual, no Hermetic equivalent. Her lover grows helpless "
                "before all faeries, and suffers a different random Minor "
                "Personality Flaw each scene, stilled briefly by ecstatic "
                "experience such as dance, music or wandering dry riverbeds "
                "in hope of meeting faeries again.",
            ),
            b.power(
                "Grant Minor Flaw (Impotence)",
                5,
                -9,
                "Vim",
                rtd=("Touch", "Mom", "Ind"),
                level=50,
                does="Ritual, no Hermetic equivalent. Her lover cannot have sex "
                "with others.",
            ),
            b.power(
                "Guide",
                1,
                0,
                "Mentem",
                level=30,
                does="Leads a character into danger like the Common Sense "
                "Virtue, but serving her ends. ReMe Base 5, +2 Voice, +1 Conc, "
                "+2 Group.",
            ),
            b.power(
                "Hound",
                2,
                -1,
                "Corpus",
                level=20,
                does="Tells her the direction and distance of her human quarry. "
                "InCo Base 3, +4 Arc, +1 Conc.",
            ),
            b.power(
                "Invisibility",
                2,
                -2,
                "Imaginem",
                level=15,
                does="A personal Veil of Invisibility (ArM5 p. 146). Base 4, +2 "
                "Sun, +1 moving image. The book prints '1 point, Init 0, "
                "Mentem' before these figures.",
            ),
            b.power(
                "Pine Away",
                4,
                -3,
                "Corpus",
                level=40,
                does="A major disease, Ease Factor 15, causing a Light Wound, "
                "treatable with Faerie Lore or Medicine; the victim loses the "
                "will and the vitality to live. Base 30 (5 + 25 virulence), +2 "
                "Voice.",
            ),
            b.power(
                "Silent Motion",
                1,
                0,
                "Imaginem",
                level=10,
                does="Constant: she moves without a sound. Base 3, +2 Sun, +1 "
                "constant. The book prints '1 point, Init 0, Mentem' before "
                "'1 point, constant, Imaginem'.",
            ),
            b.power(
                "Steal Judgment",
                2,
                -2,
                "Mentem",
                level=15,
                does="The target believes almost any lie she tells; an "
                "Intelligence roll against Ease Factor 6 resists, easier for "
                "truly incredible lies. Base 4, +1 Eye, +2 Sun. The book prints "
                "'1 point, Init 0, Mentem' before these figures.",
            ),
        ],
        vis=[BodyVis(9, "", "bones of a goat")],
        equipment="Any trappings of a woman of wealth and dubious virtue.",
        appearance="A beautiful woman with the legs of a goat, though her "
        "Presence and Allure stop this hindering her.",
        notes=paragraphs(
            "Not a player character. A famous jinn from Morocco, an ancient "
            "creature of sterility and temptation who walks dry riverbeds "
            "seducing men. She profits from the Hunger's barrenness without "
            "quite serving it. She prefers not to fight, seducing attackers "
            "or vanishing and sending enthralled men against them.",
            "Stamina is printed as Tireless. The block lists her Abilities as "
            "Pretenses, 'many, but notably' these. Greater Powers x3 cover "
            "Guide, Hound, Pine Away, Steal Judgment, Invisibility and Silent "
            "Motion; Ritual Powers x4 the two Grants. Her vis has no printed "
            "Art. Wounds: -1 (1-4), -3 (5-8), -5 (9-12), Incapacitated "
            "(13-16), Dead (17+).",
        ),
    )


# -- what the desert really is --


def _realm_readings(b: Builder, desert: Neighbour) -> None:
    _story(
        b,
        "The Two Great Spirits: The Red and the Black",
        paragraphs(
            "One way to read the Great Desert: Africa is the battlefield of "
            "two great Magical spirits, the Great Hunger and the Hope, too "
            "vast for magic to touch or to speak usefully with men. Each "
            "makes servants and tools, some of which may become familiars "
            "and draw magi into the war.",
            "The Red's creatures poison wells and fill oases, helped by "
            "faeries who burn crops and towns; its greatest children are the "
            "spirits of the places it has consumed. Men whose heads, to Second "
            "Sight, are fennec foxes tend a seemingly endless horde of "
            "Set-beasts. Most Northwest African traditions favour the Red. The "
            "coast cities live by the Dominion, which helps the Black by "
            "protecting farmers; in pagan days they had powerful faeries.",
            "The Black's lieutenants are mostly in Egypt. One who met the "
            "Romans calling herself Africa, a gigantic ghostly woman near "
            "Tunis, utters prophecies fated to come true, whether or not on "
            "the Faithful. Elsewhere it has the geniuses of great natural "
            "features, rain spirits, enigmatic horus-beasts, crafter "
            "traditions that call rain, and perhaps a sect of sorcerer "
            "Blemmyes once of the Temple at Philae, who would look human "
            "except to Second Sight.",
            "Egyptians called the two the Black Land and the Red Land, and "
            "spirits and faeries repeat the colours: rival ants, chess pieces, "
            "feuding warlords. Red goes with desert, mountain, sand, chaos, "
            "foreigners, fire and the Set-beast; Black with river, oasis, "
            "soil, order, Africans, water and the Horus-beast.",
        ),
        place=desert,
        realm="Magic",
        secrets="Lieutenants of either side may initiate seekers into "
        "Mysteries that turn their side's power on the other; Red Initiations "
        "such as desiccation are in the book's next chapter.",
        stages=[
            S(
                "The Red grows",
                at=1,
                ignored="Oases shrink, the Plateau loses its fertility and "
                "desert tribes push into the Tell, with the Almohads too weak "
                "to stop them, as when the Beni Hallali came from Persia and "
                "wrecked irrigation across the east.",
            ),
            S(
                "The Hope grows",
                at=1,
                ignored="Rain increases and the desert gets easier to cross. "
                "More slaves are needed to farm, cities of strange cultures "
                "rise at new oases, forgotten faeries are remembered in "
                "resettled ruins, and nomads turn farmer, enriching the "
                "kingdom and making the Reconquista harder.",
            ),
        ],
    )
    _place(
        b,
        "The Kingdom of the Ghouls",
        inside=desert,
        realm="Faerie",
        **RUMOURED,
        summary=paragraphs(
            "The spirits at the desert's edge claim a vast kingdom of ghouls "
            "lies hidden in its gravel and sand. Ghouls mostly crave man's "
            "flesh but can be kind: girls rescued from ghoulish husbands have "
            "crept back, and a woman lives there still with seven ghoulish "
            "brothers, having fled a sultan to return to her monstrous "
            "husband. Its king never appears.",
            "The old way to kill a ghoul: run home, for ghouls usually taunt "
            "their prey a few nights and may spare you a night for a finger "
            "put through the keyhole. Next day dig a grain pit behind your "
            "door, goad the ghoul to a frenzy, let it burst in and fall, then "
            "fill the pit with firewood and roast it. Ghouls kill each other "
            "the same way, and it works on lions too.",
        ),
        secrets=paragraphs(
            "A choice for the troupe (the Faerie reading, p. 86). Use the "
            "cannibal spirit of Realms of Power: Faerie or The Cradle and the "
            "Crescent's tribe, or rework faeries into ghoulish knights, giants "
            "and beasts.",
            "The ruler may be an ancient ghoul, an angel, a demon, a mortal "
            "tale-teller, the ghost of a Criamon Primus, nobody, or whatever "
            "spirit is nearest in the story.",
            "The treasury is a cave that opens when asked in the name of a "
            "mysterious person. The stealthy, minding the ghouls' keen noses, "
            "may overhear the name from guards; it may be an Arcane Connection "
            "to the Ghoul King or the vault's maker.",
        ),
    )
    _story(
        b,
        "The Punishment of God",
        paragraphs(
            "The Infernal reading: the world was a garden until man invented "
            "lying. God swore to drop one grain of sand from the sky for each "
            "lie, and men laughed at so small a thing.",
        ),
        place=desert,
        realm="Infernal",
        secrets=paragraphs(
            "In this version the Great Desert has an Infernal aura of 2, "
            "higher where people hid in it to do crimes. Demons dance on its "
            "sands, parts are almost the Fiery Pit, Hell has gates in the "
            "mountains, and Infernal smiths forge weapons for the last war in "
            "the Hoggar.",
        ),
    )
    _story(
        b,
        "The Crack Between the Worlds",
        paragraphs(
            "The high fantasy reading: the caravans come not from the far "
            "south but from other worlds, by portals deep in the desert.",
        ),
        place=desert,
        secrets=paragraphs(
            "Faerie markets: each caravan is a troupe of faeries bearing "
            "real, exhausted goods, trading for vital things or a part in "
            "mortal stories.",
            "Wounded worlds: the Hope and the Hunger fight in other worlds "
            "too. Slavers from a Hunger-ruled world trade gold they cannot "
            "eat and captives they will not feed; or traders from a world "
            "drowned in fecundity, the Black's kind face a mask, come for "
            "life-giving salt with the gold that breeds under their earth.",
            "Unknowable places: the caravans come from deep in the Magic "
            "Realm, as spirits or the Realm's way of clearing travellers' "
            "leavings. Magi who follow pass into the Twilight Void and never "
            "come back to tell.",
        ),
    )


# -- the sources of the Nile --


def _sources_of_the_nile(b: Builder, desert: Neighbour) -> None:
    western_nile = _place(
        b,
        "The Western Nile",
        inside=desert,
        **RUMOURED,
        levels=[
            Builder.level(
                "The faded river",
                0,
                see="The Nile of the Blacks, full of magical spirits sheltering "
                "from the mundane world, and a battleground of the Red and the "
                "Black.",
                notes="The book says a high Magic aura without a number. It "
                "lies far from the mortal world and is hard to reach.",
            )
        ],
        summary=paragraphs(
            "Many Arabic geographers say the Nile rises in the Atlas, runs "
            "south over the Great Desert, joins the Nil-es-Sudan, follows "
            "something like the Senegal and the Niger, then turns east, "
            "splits around a vast island and rejoins. Across almost all the "
            "continent it turns north, taking water from the south, some say "
            "from the Mountains of the Moon past the unlivable Equator, and "
            "flows on through Nubia and Egypt.",
        ),
        secrets=paragraphs(
            "The standard setting of this book: the Western Nile exists but "
            "has faded into a regio as the Red defeats the Black. Victories "
            "for the Hope draw it closer. A shattering injury to the Hunger, "
            "on the scale of the European Forest's splitting (Guardians of "
            "the Forest), might bring it back to the world.",
            "A troupe may instead use real geography, where the Nile rises in "
            "central Africa and the Sahel lies beyond the desert. That suits "
            "characters built around crossing the desert, and gives it a more "
            "realistic tone; the Western Nile suits high fantasy and a "
            "permeable desert.",
        ),
    )
    black_city = _place(
        b,
        "The Black City",
        inside=desert,
        **RUMOURED,
        summary="A city deep in the desert of a king in mourning, whose "
        "people wear black and paint their houses, mosque and wall black.",
    )
    _story(
        b,
        "The King in Mourning",
        paragraphs(
            "The king of the Black City found his wife drugged him nightly to "
            "visit a lover. He tricked her into taking the drug herself, went "
            "to the lover in her clothes and beheaded him, and she died of "
            "shock at the sight of the head. He mourns until a true woman is "
            "found, and steers travellers towards talk of women, with no "
            "interest in ribaldry.",
        ),
        place=black_city,
        stages=[
            S(
                "A virtuous woman is named",
                at=1,
                clues="Above all one with a terrible husband.",
                ignored="He may send her a string of white pearls. Any woman "
                "who wears it turns into a dove and flies straight to his "
                "kingdom, where he takes it off and she is herself again.",
            ),
            S(
                "A new queen",
                at=2,
                ignored="His people wash the town white in celebration.",
            ),
        ],
    )
    silent = _place(
        b,
        "The City of the Silent Princess",
        inside=desert,
        **RUMOURED,
        summary="A desert city whose palace is ringed with 100 stakes, nearly "
        "all bearing a young man's head.",
    )
    _story(
        b,
        "The Silent Princess",
        paragraphs(
            "The ruler's lovely daughter is mute. He has sworn no man may wed "
            "her unless he makes her speak, and beheads each who fails, no "
            "more than 100 in all, so she may never marry.",
        ),
        place=silent,
        secrets="She speaks if shocked into botching a Personality Trait "
        "roll, most easily by storytelling. Her servants know this has been "
        "tried and love stories fail; tales of outrage and vice rewarded may "
        "anger her into shouting.",
    )
    _place(
        b,
        "Zerzura",
        inside=desert,
        **RUMOURED,
        summary=paragraphs(
            "A secret oasis far to the west of the Nile, the refuge of the "
            "young men and women of Kush, sent there when an invader pushed "
            "south after their line lost Egypt's throne; he did not follow "
            "into so harsh a desert. Arab writers claim one visit: a city of "
            "plain Egyptian influence, guarded by a tribe of black giants, "
            "whose people worship a great bird. Its statue stands over the "
            "gate with the key in its beak. No Hermetic magus has heard the "
            "story yet, but Seekers will want it when they do.",
        ),
        secrets="All its people sleep unaging under a king and queen; a "
        "thief may carry off what he can if he dodges the guards and does not "
        "stray near the couple, lest they wake. Why they sleep and what will "
        "wake them is unrecorded.",
    )
    _story(
        b,
        "The Long Voyage",
        "A saga hook: a covenant of magi sets out from North Africa to find "
        "the Nile's headwaters and travels for years through strange kingdoms "
        "beyond the desert, to dissolve at last under the Lighthouse of "
        "Alexandria.",
        place=western_nile,
    )
    _story(
        b,
        "Making the Nile Fit for Transport and Trade",
        paragraphs(
            "The Western Nile may be easy to navigate, the chief road of West "
            "Africa, or hard, with the covenant's work being to open it. Its "
            "headwaters are south of the Atlas: a city there might command the "
            "passes to the Maghreb, or the characters may found one, cutting "
            "passes and tunnels, bridging, killing predators and beating "
            "bandits and petty lords.",
            "Like the Nile above Aswan it may have cataracts, to be removed "
            "by magic, portaged, canalled, or crossed with magical cranes, "
            "river sections flowing through the air, or tame elementals. "
            "Millet and sorghum are the great bulk trade; leatherwork, "
            "cotton, ebony, indigo, gum arabic, bronze and brass need less "
            "capital. Gold would likely move to the river. Would they let "
            "slaves pass on 'their' river?",
        ),
        place=western_nile,
    )
    atlas_city = _place(
        b,
        "The City in the Atlas",
        inside=desert,
        **RUMOURED,
        summary="A secluded green valley in the Atlas with a rich stone city, "
        "where gold is for tools, gems are trinkets, and the one piece of "
        "glass is worth all the rest.",
    )
    _story(
        b,
        "The Tin Lamp",
        paragraphs(
            "A sweet seller gone bankrupt crossed the Atlas to beg among "
            "strangers, carrying his last possession, a lamp of tin and red "
            "glass, and found a city no outsider had reached. The Pasha "
            "entertained him three days. Ashamed, he gave the lamp as all he "
            "owned, and the Pasha, who had never seen glass and could match "
            "the gift with nothing, loaded twelve camels with treasure. His "
            "family lives rich in their home city still.",
            "The tale goes on that his wicked brother sold everything to "
            "trade there, and was robbed by bandits and perhaps killed; or "
            "reached the city with a glass gift of his own, and was given in "
            "return the Pasha's greatest treasure, the little tin lamp.",
        ),
        place=atlas_city,
        secrets="The tale is told all over the Near East, so they may be "
        "faeries playing at wealth and poverty, or the valley may be real.",
    )
    _story(
        b,
        "The Modern Garamantes",
        "With a Western Nile the Garamantian kingdom need never have fallen, "
        "its capital safe on the river's fertile land and the Fezzan ruins "
        "only a lost colony. They raid neighbours and rob merchants, their "
        "chariots sweeping out of the moonlit desert for slaves. Their great "
        "export is carbuncles or carnelian, whose Virtuous Form lets the "
        "holder see in the dark.",
        place=western_nile,
    )
    _story(
        b,
        "Prester John on the River",
        "In 1220 Prester John is thought to be in India; contact with the "
        "Mongols later moves him to Ethiopia or near it. A troupe wanting his "
        "legend and The Cradle and the Crescent's hooks with historical "
        "Mongols can set his kingdom on the Western Nile.",
        place=western_nile,
    )
    aphrodisiac = _place(
        b,
        "The Kingdom of the Perfect Aphrodisiac",
        inside=western_nile,
        **RUMOURED,
        summary="Arabic geographers tell of a Western Nile kingdom where a "
        "root grows, one dose letting a man have sex at will for the rest of "
        "the day. By law every plant is its king's, who has two hundred wives "
        "and will not sell into Muslim lands for fear of tempting men with "
        "only four. Old rulers who ask are refused or sent herbs for "
        "impotence. Its land tortoises are so big that a man can stand in "
        "their tunnels, and oxen teams pull them out for eating.",
    )
    _story(
        b,
        "The Root of the Two Hundred Wives",
        "The characters may be asked to steal the herb. What if it holds Creo "
        "vis, and how are the grogs to be kept at their duties?",
        place=aphrodisiac,
    )
    dragon = _place(
        b,
        "The Kingdom of the Choosing Dragon",
        inside=western_nile,
        **RUMOURED,
        summary="A Western Nile kingdom whose notables stand in a half circle "
        "before a treasure-decked cave. A dragon with a serpent's body, a "
        "camel's head and a lion's mane crawls out, touches one man's chin "
        "with its nose and turns back; he must run and pull out a handful of "
        "hairs from its mane or tail, and their number is the years of his "
        "reign.",
    )
    _story(
        b,
        "Shaving the Dragon",
        "A character with the right magic items might pin the dragon down and "
        "shave it bare. Do the locals accept this king? Can the dragon "
        "answer?",
        place=dragon,
        secrets="The prophecy works as the Death Prophecy Virtue, though a "
        "few kings do not actually die when their reign ends.",
    )


# -- the story seeds --


def _desert_stories(
    b: Builder,
    fezzan: Neighbour,
    redoubts: Neighbour,
    tanezrouft: Neighbour,
    tenere: Neighbour,
    central: Neighbour,
) -> None:
    _story(
        b,
        "The Vexillation of the Fata Morgana",
        "Tremere diviners saw a Mongol invasion coming, and a vexillation "
        "went into the Fezzan disguised as a Genoese caravan to make an "
        "emergency redoubt in the Garamantian foggaras. They guard its place "
        "and purpose fanatically.",
        place=fezzan,
        stages=[
            S(
                "A cache is found",
                at=1,
                clues="The characters plunder a supply cache by chance, or "
                "stumble on the magi in the ruins.",
            ),
            S(
                "The secret at stake",
                at=2,
                ignored="The Tremere may kill to protect it, in a Wizard War "
                "beyond Mythic Europe's borders that may not keep the Order's "
                "conventions.",
                stopped="The two groups find a settlement.",
            ),
        ],
    )
    _story(
        b,
        "A Covenant in Agisymba?",
        "Remote, rich in untapped magic and easily reached by the Iter Praeter "
        "Caput Saxi, Agisymba would suit isolationists, or those wanting a "
        "menagerie or a unique familiar.",
        place=central,
    )
    _story(
        b,
        "An Atakor Covenant?",
        "Cut off by distance, desert and fierce tribes, the Tuareg bastion "
        "might draw wizards or a cooperative of sahirs of the Order of "
        "Suleiman tired of politics, at the price of utter isolation. Once "
        "subdued or allied, the proud Tuareg make fine covenfolk who know the "
        "shifting regiones, and the land is well guarded, with strong Magic "
        "auras and untouched resources.",
        place=redoubts,
    )
    _story(
        b,
        "Wages of Sin",
        "A devout magus uncovers a vast hoard of gold at Taghaza and must "
        "master his own greed, then ask whether taking away so easy a supply "
        "would hurt Hell's plans.",
        place=tanezrouft,
        realm="Infernal",
        secrets="The flies are a horde of False God demons. Where death and "
        "murder are common they feed on the sin, and whisk away gold from "
        "hovels and caravans whenever a weak fool needs tempting.",
    )
    _story(
        b,
        "Breaking the Bonds",
        paragraphs(
            "Taghaza's slaves walk free but the desert holds them, living on "
            "imported food and water. Magi might feed them by magic and upset "
            "the whole economy. Would they welcome a new master? The southern "
            "traders, needing the salt, may offer gold or turn to violence.",
            "A second great salt mine, Taodeni, lies undiscovered further "
            "south, away from the trade route; settling it would also draw "
            "the region's power brokers.",
        ),
        place=tanezrouft,
        secrets="Anyone living at Taghaza or Taodeni takes -3 on Aging rolls "
        "for the conditions (ArM5 p. 170), plus any Warping from the aura.",
    )
    _story(
        b,
        "Where Does All That Salt Go?",
        "Slabs of rock salt go south on camels in the yearly Azalai, and no "
        "miner or overseer knows where. In two or three months the camels "
        "return with new slaves, gold and ivory, and the northern Massufa "
        "traders have learnt not to ask. Guides cannot quite describe the "
        "dealings, grow distant, and in the end stop returning, replaced by "
        "look-alike kin with similar names. Some exotic goods are touched by "
        "Faerie or carry tainted vis.",
        place=tanezrouft,
        secrets=paragraphs(
            "The Azalai may end in Arcadia, where salt becomes goods and "
            "captives are changed and sent north as black slaves with altered "
            "memories. At least one merchant is a disguised faerie with Spirit "
            "Away (Realms of Power: Faerie pp. 23-24); guides are men Warped "
            "away or minor faeries.",
            "Or demons run it to punish sinners, whose fragments of memory "
            "make Taghaza a mundane purgatory.",
        ),
    )
    _story(
        b,
        "The Mines of Despair",
        "Taghaza's miners tell scraps of lives beyond the desert, sharing "
        "only the memory of being brought to the pits and of missing their "
        "families.",
        place=tanezrouft,
        secrets="Exposure to the site's Infernal occupants gives nearly all "
        "mundane miners Weak Willed through Warping, and most hold the "
        "equivalent of the Delusion Flaw: the memories are false, and neither "
        "mundane nor magical means show it. Some miners and overseers are "
        "incognizant dark faeries or demons who feed on the suffering and warp "
        "the memories of the miners and female slaves.",
    )
    _story(
        b,
        "The Stolen Prize",
        "The Pale Fox of Virtue snatches a bow, satchel or waterskin and "
        "offers a bargain: if a lone character catches it, it will show the "
        "group a vis site, a short cut through a regio, or a buried caravan "
        "the wind has bared. It relishes wordplay and accepts clever readings "
        "of the rules if the words stand: only one must catch it, but others "
        "may chase.",
        place=fezzan,
    )
    _story(
        b,
        "Men of War",
        "The rumoured Sorcerer-King of Sosso has an endless hunger for slaves "
        "for his wars against rivals and the deep desert's jinn.",
        place=tenere,
        secrets="Some claim he can use traded salt and gold as Arcane "
        "Connections, and see and hear through the slaves he sends into "
        "Mythic Europe.",
    )
    _story(
        b,
        "Lost...",
        "Moorish pirates seize covenfolk travelling on business.",
        place=tanezrouft,
        stages=[
            S(
                "The trail south",
                at=1,
                clues="Arcane Connections point to the Maghreb, but something "
                "masks the prisoners' exact whereabouts.",
                stopped="The characters find them in the coast markets before "
                "they are sold.",
            ),
            S(
                "Across the sands",
                at=2,
                ignored="After any misstep they must plunge into the desert "
                "after their friends.",
            ),
        ],
    )
    _story(
        b,
        "...And Found",
        "Disciplined, well-trained pagan grogs from the south offer the magi "
        "their service, and Frosty Breath of the Spoken Lie finds them honest. "
        "They need no church or mosque, but in civilization they hide or "
        "slip away at bad moments.",
        secrets="They are a slave-soldier cadre who killed guards in their "
        "escape. Their owner comes to reclaim his property before a local "
        "magistrate.",
        stages=[
            S("Strange absences", at=1),
            S(
                "The owner's claim",
                at=2,
                ignored="The matter goes before a magistrate.",
            ),
        ],
    )
    _story(
        b,
        "The Archetypical Road",
        "The desert crossing is a road story, ripe for faeries to steal "
        "vitality from: guides, beasts and bandits all fit, and all survive "
        "against the odds. Do the fay enjoy the slaves' suffering, the "
        "travellers' misery, the merchants' greed, or all three?",
        realm="Faerie",
        place=tanezrouft,
    )
    _story(
        b,
        "The Time-Lost",
        "If the Sudan is strange and faerie, its slaves may come from a "
        "kingdom fallen into Faerie, from isles near India, or from Europe "
        "before the Flood. Faeries hoarding people from disasters may change "
        "supply as stocks run down: a thousand on sale, speaking classical "
        "Latin and claiming to be from Pompeii.",
        realm="Faerie",
        place=tenere,
    )
    _story(
        b,
        "Fantastic Slaves",
        "The southern slaves may not be human: faeries, constructs from "
        "strange factories, Plinian races, spirits bound in solid forms, or "
        "the dead forced to labour.",
        place=tenere,
    )
    _story(
        b,
        "The Bitter Fruit",
        "A chieftain's son among neighbouring Berbers has been stung by a "
        "Deathstalker Scorpion of Virtue, and dozens of them guard the only "
        "nearby Alkhad gourds in a hidden wadi. Numbers doom a charge, and "
        "those passing under a ward find the gourds hidden: they must deceive "
        "the deceivers.",
        place=central,
        stages=[
            S(
                "The gourds won",
                at=1,
                stopped="The tribe may serve as grogs for a time, reveal a "
                "local jinn's hidden external vis, or show an unknown spring.",
            )
        ],
    )
