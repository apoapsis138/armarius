"""Constantinople, the Queen of Cities, as of 1220: the ruined capital
of the Latin Empire on its seven hills; its walls, harbours, forums,
cisterns, palaces and churches, with their shifting auras, regiones and
vis; the covenants of Michael's Tabula and Xylinites and their magi;
Passara of Verditius in the Magnaura and Formosos of Guernicus, who
hunts her; the Latin emperor, the Venetian Quarter and its podestà, the
vacant Latin patriarchate and the city's churches, the Studion among
them; and the guilds, gangs and councils of the streets, in paraphrase
of The Sundered Eagle chapter seven (with chapter two for the Latin
Empire and the city's broken wards, chapter three for the covenants'
politics, and chapter eleven for the relics still in the city).

The ruins of Thermakopolis and the Court of Fools are tribunal.py's,
put in places["constantinople"] there. Akgah's lair outside the walls
is realms.py's. Creatures are the Bestiary's: Belisarius, Porphyrio, the
ghosts of the Nika riots and Zeno are described in the summaries of the
places they haunt. Keys: the region is places["constantinople"]; the
covenants' sites are places["michaels_tabula"] and ["xylinites"];
Passara's palace is places["magnaura"]; the Latin emperor is
world["latin_emperor"] and the podestà world["podesta"], for the
Latin vassals of other parts to answer to."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.world import FULL
from ..builder import Builder, joined_lines, paragraphs, titled, vf_art
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from . import Theban

CRIAMON = "house_criamon"
FLAMBEAU = "house_flambeau"
GUERNICUS = "house_guernicus"
JERBITON = "house_jerbiton"
VERDITIUS = "house_verditius"

#: The lead line of a covenant's notes, before its secrets.
KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}
RUMOURED_TRIBUNAL: dict[str, Any] = {"status": "Rumoured", "known": "In the Tribunal"}


def _add(theban: Theban, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = theban.b.place(name, **kw)
    theban.places[key] = place
    return place


def build(theban: Theban) -> None:
    b = theban.b
    tribunal = theban.tribunal
    assert tribunal is not None, "tribunal.py builds the Tribunal first"
    _region(theban)
    _approaches(theban)
    _forums_and_waters(theban)
    _hippodrome(theban)
    _palaces(theban)
    _sacred_sites(theban)
    _lords(theban, b)
    _churches(theban, b)
    _towns(theban, b)
    _factions(theban, b)
    _michaels_tabula(theban, b, tribunal)
    _xylinites(theban, b, tribunal)
    _palace_magi(theban, b)


# ------------------------------------------------------------- the region


def _region(theban: Theban) -> None:
    _add(
        theban,
        "constantinople",
        "Constantinople",
        summary=paragraphs(
            "The Queen of Cities: New Rome, raised by Constantine the "
            "Great on old Byzantium in 330, on a triangle of seven hills "
            "between the Golden Horn and the Sea of Marmara, and "
            "enriched by every emperor after him, by none more than "
            "Justinian. Roman to the bone, it is a city of forums, "
            "colonnades, baths, palaces, churches and monasteries, and "
            "it keeps its hippodrome, its senate house, its aqueduct "
            "and its slave market. In 1220 it is a filthy, dangerous shadow of itself: "
            "about a third still lies burnt and broken from the siege "
            "and the fires of 1203 and 1204, its people number fewer "
            "than 200,000 where Justinian ruled nearly half a million, "
            "and the rich live wall to wall with the destitute. The "
            "Latin conquerors have shipped most of its relics and "
            "treasures west and spend more effort stripping it than "
            "mending it. Civil order has gone: each of its many peoples "
            "mistrusts the others and protects itself with street gangs "
            "or hired soldiers.",
            "Auras. Every place in the city lies in some aura, and each "
            "waxes and wanes with the calendar. The old gods' worship "
            "first left Faerie auras; Constantine's churches spread "
            "Divine ones that swallowed most of them; the city's many "
            "massacres, from the Nika riots to the sack of 1204, left "
            "Infernal patches that the weakened Dominion has not yet "
            "worn away. Magic auras were always few, most with "
            "preternatural tethers, and Jerbiton magi kept them alive by "
            "working magic in them every year; that has stopped since "
            "the conquest, so they are no longer tended. Most Divine "
            "auras here are Dominion, centred on an altar and as strong "
            "as the faithful who worship there, and so weaker than they "
            "were; the one relic left that could raise an empyreal aura "
            "is the Crown of Thorns, in the Venetian Quarter. Auras "
            "spread until they meet one as strong; where two of equal "
            "strength meet they simply touch, so a single step can lead "
            "from a Divine aura into an Infernal one.",
            "The broken wards. Constantine walked the city's bounds "
            "behind a plough, binding its spirits in a Sol Invictus "
            "invocation that Justinian later carried out to the new "
            "walls. Two level 50 effects came of it: God's City lowered "
            "the Might of every Faerie and Infernal being inside the "
            "walls by 10 (Penetration 20), and the Walls of the City of "
            "God gave anyone storming them three extra botch dice. Both "
            "have lain dead since 1204, when someone took the palladium "
            "from a sealed vault beneath the Column of Constantine, "
            "together with other relics. No one knows what the "
            "palladium looks like, where it is or who took it; put it "
            "and the relics back and the wards would wake. The great "
            "riots that shaped the city's history have also ceased "
            "since the fall, which some think a side effect of the "
            "bindings.",
            "The Order. Before the conquest the city held three "
            "covenants: Thermakopolis was wiped out, Moero's Garden fled "
            "to Nicaea with the Greek nobility, and Xylinites shut its "
            "gates. In 1220 two covenants of the Propontian phyle lie "
            "inside the walls, Michael's Tabula in the catacombs and the "
            "Criamon Clutch of Xylinites under an orphanage, while "
            "Passara of Verditius tends the automata of the Magnaura. "
            "Young Jerbiton magi above all want a covenant replanted in "
            "the city, and the Tribunal has not decided whether to "
            "encourage it; the site of Thermakopolis is the obvious "
            "place. Visiting magi rest and meet at the Baths of "
            "Zeuxippus.",
            "Vis in the city (each described in its place): the "
            "Medusas' Tears in the Basilica Cistern (8 pawns of "
            "Imaginem at the summer solstice), the Serpent Column in the "
            "Hippodrome (8 pawns of Animal, by a rite of ram's blood "
            "that Moero's Garden found), and a few unnamed sources in "
            "the catacombs that Michael's Tabula has found. The book "
            "does not say whether any of them is one of the polity's "
            "common sources.",
        ),
        secrets=[
            titled(
                "The demons of the circus factions",
                "Three demons have long taken a close interest in "
                "Constantinople: Golab, called the Seraphim's Foe, with "
                "Hulikang and Nike under him, who for centuries each ran one "
                "of the circus factions, the Greens and the Blues, and "
                "through them much of its politics and trade, despite the "
                "wards.",
            ),
            titled(
                "The new factions",
                "Some suspect the demons Hulikang and Nike now drive "
                "Constantinople's 'Frank' and 'Venetian' factions, and the "
                "stilled riots may be their doing rather than the wards'.",
            ),
            titled(
                "Akgah's lair",
                "The prince of Hell Akgah, who orchestrated Constantinople's "
                "fall, has his lair in an Infernal regio about a dozen miles "
                "outside the walls, and fought the Hagka in the Hippodrome "
                "in 1204.",
            ),
            titled(
                "Storyguide Notes",
                "The book leaves open whether the demons drive the 'Frank' "
                "and 'Venetian' factions. For Akgah's lair see the realms' "
                "places.",
            ),
        ],
        **KNOWN_ORDER,
    )


# ------------------------------------------------- the walls and approaches


def _approaches(theban: Theban) -> None:
    region = theban.places["constantinople"]
    _add(
        theban,
        "harbours",
        "The Harbours of Constantinople",
        inside=region,
        summary=paragraphs(
            "Most visitors come by sea, and harbours line both the northern "
            "and southern sea walls, each behind its own outworks and "
            "towers. On the Marmara side lie the busy Harbour of Theodosius, "
            "midway along the southern wall, where ships from every corner "
            "of Mythic Europe put in and where a party arriving by ship most "
            "likely lands; the Kontoskalion, where the shrunken imperial "
            "navy rides at anchor under Latin command; and the Harbour of "
            "Julian below the imperial palaces, once kept for the court. On "
            "the Golden Horn the two busiest ports, the Neorion and the "
            "Prosphorion, were given to the Venetians for their warships and "
            "merchantmen.",
            "From the quays the city's ruin is hard to see: merchantmen come "
            "in every day, boats ferry knights over the Bosporus, armed "
            "galleys hunt pirates and escort shipping, fishermen and "
            "dockers work without pause, and the conquerors keep the sea "
            "walls (thirty feet on the Golden Horn, forty-five on the "
            "Marmara, with hundreds of towers) in good repair. With so many "
            "soldiers about, the harbours are fairly safe.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "theodosian_walls",
        "The Walls of Theodosius",
        inside=region,
        summary=paragraphs(
            "The land walls, never yet breached, running from the Golden "
            "Horn to the Sea of Marmara behind a ditch built in sections "
            "that can be flooded one by one: an outer wall thirty feet "
            "high and seven thick, a raised terrace (the peribolos), "
            "then an inner wall forty feet high and some seventeen "
            "thick, with nearly a hundred towers; the strip between "
            "ditch and outer wall, the patateichion, is raised too. With "
            "the sea walls they close the city in completely. Of the ten "
            "great gates, five serve travellers and five the army, with "
            "smaller posterns between.",
            "The Golden Gate, a triumphal arch plated in gold between "
            "two great copper elephants, opened only for an emperor "
            "coming home victorious; it last swung open when Alexios V "
            "Murzuphlus slipped out through it by night after the "
            "crusaders took the walls. Further north, the gate of the "
            "Golden Mantle leads to Blachernae; it is crowned by a "
            "golden globe bearing a figure wrapped in a cloak, and "
            "legend says lightning will spare the city while the globe "
            "stays up. Folk think it ancient Greek work.",
            "Getting in is easy: travellers and traders pass the gates "
            "by day, and enough hidden ways exist for a small party to "
            "slip in after dark. Moero's Garden knows a secret passage "
            "under the walls near the Gate of Pege, which its search "
            "parties use to come hunting for lost treasures and relics.",
        ),
        secrets=[
            titled(
                "The globe of the Golden Mantle",
                "The globe of the Golden Mantle may be one of the protective "
                "enchantments Hermetic magi made for Constantinople, and one "
                "that failed.",
            ),
        ],
        **KNOWN_REGION,
    )
    _add(
        theban,
        "porphyrio",
        "Porphyrio's Lair",
        inside=region,
        summary=paragraphs(
            "Somewhere under the waters off the city lies the lair of "
            "Porphyrio, the giant whale that wrecked ships in harbour "
            "and along the strait for months until Belisarius, with one "
            "galley and a hundred sailors, fought it from dawn to "
            "sunset; bristling with spears and burnt by Greek fire, it "
            "sank, and was not seen for generations. It still surfaces "
            "near the city now and then, without pattern, and has never "
            "attacked a ship since, but its coming foretells disaster: "
            "it was last sighted in April 1203, a week before the "
            "Venetian fleet filled the Sea of Marmara.",
            "Theban magi, especially students of Hermetic divination, "
            "hold it to be a magical beast with a lair on the sea floor. "
            "Every search, even with Alexandria's glass submarine, has "
            "failed, and the current guess is that the lair lies in a "
            "Magic regio. The book gives the whale no stat block.",
        ),
        secrets="",
        **RUMOURED_TRIBUNAL,
    )


# ------------------------------------------ forums, markets and waterworks


def _forums_and_waters(theban: Theban) -> None:
    region = theban.places["constantinople"]
    _add(
        theban,
        "forum_constantine",
        "The Forum of Constantine",
        inside=region,
        summary=paragraphs(
            "The most famous of the city's open plazas, on the crown of "
            "the Second Hill, ringed by colonnades and porticoes at the "
            "gateway to the imperial quarter. It is one of the great "
            "daily markets, and its trade includes the slave markets "
            "and the brothels; the Mese, the colonnaded Middle Way, "
            "runs through it from the Philadelpheion crossroads on the "
            "Third Hill down to the palaces, linking every forum of the "
            "city. Its column carried a statue of Constantine until a "
            "storm destroyed it, and a cross has stood there since early "
            "in the twelfth century.",
            "Beneath the Column of Constantine lies a sealed underground "
            "vault, now empty, where the palladium at the heart of "
            "Constantine's wards was kept with other relics: the twelve "
            "baskets of the feeding of the five thousand, the axe Noah "
            "built the Ark with, the Magdalene's jar of perfume and the "
            "crosses of the two thieves. All went missing in 1204.",
        ),
        secrets=[
            titled(
                "Waking the wards",
                "Whoever restores the palladium and those relics to the vault "
                "beneath the Column of Constantine wakes both of the city's "
                "wards again.",
            ),
        ],
        **KNOWN_REGION,
    )
    _add(
        theban,
        "column_theodosius",
        "The Column of Theodosius",
        inside=region,
        aura=5,
        summary=paragraphs(
            "The heart of the Forum of Theodosius, also called the Forum "
            "Tauri, near the city's centre, where the butchers and "
            "fishmongers keep their stalls: a marble column 150 feet high "
            "with a spiral stair inside to a platform at the top. Its sides "
            "are carved with the Sibyl's prophecies in strange pictures and "
            "signs that make sense only once the event has come, the recent "
            "siege among them; Alexios V Murzuphlus was thrown from its top "
            "after his capture, and his death is carved on it too.",
            "It stands in a Magic aura of 5, the strongest and largest in "
            "the city, filling the forum to its edges; no neighbouring aura "
            "comes near it, so it never rises or falls. Magi have dreamt of "
            "a covenant here, but the place is too public and the aura "
            "stops at the buildings round it.",
            "Anyone who gazes at the carvings for an hour has a vision of "
            "things to come, as the Visions Flaw; only those with "
            "Premonitions can hope to read it (Intelligence + Premonitions "
            "against an Ease Factor the storyguide sets, 12 to begin with), "
            "and one who does gains some benefit when the event arrives, "
            "say +3 to a few rolls. The column is also a study source for "
            "Premonitions of Source Quality 6: it is built of six porphyry "
            "drums between iron bands, each good for one season's study, "
            "the top four reachable only by ladder or magic, in a crowded, "
            "distracting square (the windowless stair is no help).",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "basilica_cistern",
        "The Basilica Cistern",
        inside=region,
        summary=paragraphs(
            "A vast reservoir beneath the First Hill feeding the imperial "
            "quarter, its roof held up by 336 columns. It is one node in a "
            "maze of tunnels and chambers that runs to the Great Palace and "
            "to other rooms under the city. Water still reaches it through "
            "the Aqueduct of Valens, unrepaired for half a century, and the "
            "great open cisterns on the Fifth, Sixth and Seventh Hills, "
            "basins ringed with columns.",
            "The Medusas' Tears. In the north-western corner two columns "
            "rest on stone medusa heads, brought from far away under "
            "Justinian, one set upside down and one on its side. If the "
            "water has covered them all year, the moss round their eyes "
            "can be scraped off at the summer solstice as 8 pawns of "
            "Imaginem vis. Unclaimed.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "venetian_quarter",
        "The Venetian Quarter",
        inside=region,
        realm="Divine",
        summary=paragraphs(
            "The home of the Republic of Venice's officials and people in "
            "the city, walled off from the rest between 1205 and 1207 "
            "and patrolled by Venetian soldiers, with its own ports on "
            "the Golden Horn. Inside it is a hive of trade; most feel "
            "safe, but many Greeks hate the merchants' exemptions, which "
            "shut them out of the shipping trade, and mistrust runs "
            "between Venetians, the other crusaders and the Greeks. "
            "Life is harder for ordinary Venetians than for their "
            "officials: much of the quarter is still ash and rubble, "
            "home to armed gangs and bandits, and smugglers prize it as "
            "the easiest way into the city.",
            "Here, locked away, lies the Crown of Thorns: the Latin "
            "emperor's, pledged to the doge against a loan of 13,134 "
            "Mythic pounds, and never yet taken from the city. Entire, "
            "the crown has Faith 7 and the saintly powers Cure "
            "Blindness, Strengthen the Cripple and Mass Healing; each "
            "of its thorns is a relic in its own right. It is the one "
            "relic left in Constantinople strong enough to raise an "
            "empyreal aura.",
        ),
        secrets="",
        **KNOWN_REGION,
    )
    _add(
        theban,
        "zeuxippus",
        "The Baths of Zeuxippus",
        inside=region,
        summary=paragraphs(
            "A great bathhouse over a former temple of Zeus, adorned with "
            "more than eighty statues of famous Greeks and Romans and of the "
            "old gods, linked by passages to the Great Palace. It has been "
            "closed to the public since the Nika revolt of 532: some parts "
            "admit only nobles, others are given over to the army, and a "
            "former bathing hall serves as a prison, all far enough apart "
            "to keep bathers from prisoners. Near it, the old Temple of "
            "Aphrodite, made a royal stable late in the fourth century, "
            "still stands.",
            "The Jerbiton magi of the city met here so often that they "
            "jokingly called themselves the Covenant of the Baths of "
            "Zeuxippus. Theban magi know there was never such a covenant, "
            "but the joke has grown into a rumour that magi of far "
            "Tribunals still believe. Unpopular with the townsfolk, the "
            "baths give visiting magi a quiet place to rest, and they are "
            "the unofficial meeting place of magi and their associates.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "julian_library",
        "The Lost Julian Library",
        inside=region,
        summary=paragraphs(
            "The library Julian the Apostate built late in the fourth "
            "century, said to have held over 600,000 texts: his own "
            "books and copies of every learned and literary work his "
            "scholars could find, with many curiosities, some magical. "
            "The most famous was the Iliad and the Odyssey written in "
            "gold on a dragon's gut thirty-seven yards long, which is "
            "said to make its reader wiser.",
            "The building is long gone under later ones, and Julian's "
            "followers hid the collection after his death. Seekers of "
            "the Tribunal hunt it constantly and turn up lost sections "
            "now and then; the finest pieces are still hidden, and the "
            "competition for them is fierce.",
        ),
        secrets="",
        **RUMOURED_TRIBUNAL,
    )
    _add(
        theban,
        "moero_old_site",
        "The Old House of Moero's Garden",
        inside=region,
        summary=paragraphs(
            "The site in the older part of the city that Ionnia of "
            "Jerbiton identified in 1163 as the home of the poetess "
            "Moero, of about 300 BC, lying in one of the city's few "
            "lacunae; there she founded Moero's Garden, with Moero's "
            "summoned ghost as its patron. The covenant fled to Nicaea "
            "after the conquest, leaving most of its library and "
            "collections behind, and its magi long to return.",
            "Moero's ghost is still bound here, which is why Ionnia had "
            "to bind Hipparchus as the covenant's patron at Nicaea: the "
            "Tribunal requires a covenant's patron to live inside it. "
            "The covenant's search parties slip in through the passage "
            "near the Gate of Pege.",
        ),
        secrets="",
        **KNOWN_TRIBUNAL,
    )


# ----------------------------------------------------------- the Hippodrome


def _hippodrome(theban: Theban) -> None:
    region = theban.places["constantinople"]
    hippodrome = _add(
        theban,
        "hippodrome",
        "The Hippodrome",
        inside=region,
        realm="Divine",
        aura=1,
        summary=paragraphs(
            "The heart of the city, 1,600 feet long and 400 wide, its "
            "straight northern end joined to the Great Palace and kept "
            "for the imperial family, its southern end curved; at its "
            "height it seated 80,000. Jousts have taken the place of "
            "chariot races, but jugglers, dancers, beast-tamers and "
            "tumblers still perform, and festivals, holy days and "
            "imperial ceremonies are held here. The statues that lined "
            "its arcades, Athena, an eagle on a serpent, Helen of Troy, "
            "the wolf with Romulus and Remus, a hippopotamus with a "
            "crocodile in its jaws, are mostly destroyed, torn down for "
            "their inlaid metal or from spite; townsfolk say many of "
            "them could move, sing, play music or act out a scene. Down "
            "the middle runs the spina, the stone pier the chariots "
            "raced round, with two great monuments left: the Serpent "
            "Column at the south and the Egyptian Obelisk at the north.",
            "By day a Dominion aura of 1 surrounds stronger pockets: "
            "Faerie 2 round the Serpent Column, Magic 2 round the "
            "obelisk, and Infernal 2 in patches along the old track "
            "where the Nika fighting was worst and where the Bogomil "
            "leader Basil was burnt.",
            "The ghosts of the Nika riots. Justinian lured the rioting "
            "Greens and Blues into the Hippodrome, and Belisarius cut "
            "down 30,000 of them. Every 14 January, at night, hundreds "
            "of Infernal ghosts rise from the ground here crying 'Nika!' "
            "(Victory). The city's Dominion once held them inside; it "
            "is weaker now, and they roam the Great Palace and the "
            "streets.",
            "The automata of Ollaferus. Almost a third of the "
            "Hippodrome's statues were once automata by Ollaferus of "
            "Verditius, a second-generation magus who perfected the "
            "inner Mystery of automata for Verditius himself; each "
            "could play out one scene from Roman or Byzantine history "
            "or legend. Most have been smashed, melted or carried off. "
            "Verditius magi of the Tribunal want the few left, to "
            "decorate their workshops rather than to study, and pay "
            "others to haul half a ton of stone for them: a novice with "
            "a shard may be offered a token to neutralise it for "
            "delivering one.",
        ),
        secrets=[
            titled(
                "The battle among the statues",
                "In 1204 the demon Akgah fought the Hagka in the Hippodrome "
                "among the statues; the battle wrecked part of the arena, "
                "Akgah won, and the wounded Hagka fled. Crusaders who saw it "
                "took it for a vision of the lion of Venice triumphant.",
            ),
        ],
        **KNOWN_REGION,
    )
    _add(
        theban,
        "serpent_column",
        "The Serpent Column",
        inside=hippodrome,
        realm="Faerie",
        aura=2,
        levels=[
            Builder.level(
                "Belisarius's Hippodrome",
                4,
                "Faerie",
                enter=(
                    "Walk round the column widdershins holding a sword of Roman make."
                ),
                notes=(
                    "A regio as large as the Hippodrome, showing it in all "
                    "its ancient splendour, where Belisarius's urban "
                    "faeries replay the end of the Nika riots."
                ),
            )
        ],
        summary=paragraphs(
            "Three twisted bronze serpents rising to hold a bronze bowl "
            "between their heads, at the southern end of the spina. It "
            "first stood in Apollo's temple at Delphi; Constantine brought "
            "it to the porch of Hagia Sophia and then here. An ancient "
            "ritual older than Hermetic theory, meant to keep snakes out of "
            "Apollo's temple, now works like a ward over the whole city: no "
            "mundane snake can enter it, though snakes with a Might pay it "
            "no heed.",
            "Vis. Moero's Garden learnt that if a ram is sacrificed and its "
            "blood poured into the bowl at each solstice and equinox, the "
            "column drinks it; after the fourth offering, at the summer "
            "solstice, the blood comes back as a dark red clot worth 8 "
            "pawns of Animal vis.",
            "The Faerie aura of 2 comes from the faerie in the regio above "
            "the column, who calls himself Belisarius (see the Bestiary). "
            "Its level, Faerie 4, is the Hippodrome as it was; there he "
            "leads a little band of urban faeries in an endless staging of "
            "the riots' last battle, his imperial guard against the mob, "
            "as a lesson that rightful rule and tradition must win over "
            "change. He needs a human audience and sends his followers "
            "into the city to lure people in.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "egyptian_obelisk",
        "The Egyptian Obelisk",
        inside=hippodrome,
        aura=2,
        summary=paragraphs(
            "Set up at the northern end of the spina by Julian the Apostate, "
            "who fetched it from Egyptian Thebes as part of his campaign to "
            "revive the old gods. It broke on the journey: of its ninety "
            "feet only the top thirty survive, covered in hieroglyphs and in "
            "carvings of the Hippodrome's Roman spectacles. A Magic aura of "
            "2 surrounds it.",
            "Its carvings can be read as a riddle of the future: "
            "Intelligence + Magic Lore + a stress die against an Ease Factor "
            "of 15, handled as Hermetic divination; since it is older than "
            "the Order, its visions may break the Lesser Limit of Time. "
            "Each of the two lost thirds, if found, lowers the Ease Factor "
            "by 3, to 9 for the whole stone, but there are few clues to "
            "where they are.",
        ),
        **KNOWN_TRIBUNAL,
    )


# --------------------------------------------------------- the palaces


def _palaces(theban: Theban) -> None:
    region = theban.places["constantinople"]
    great = _add(
        theban,
        "great_palace",
        "The Great Palace",
        inside=region,
        summary=paragraphs(
            "The larger of the two imperial palaces, in the south-east "
            "overlooking the Sea of Marmara, adorned and extended "
            "throughout the city's history until it is really five: the "
            "Chalke, the Magnaura, the Daphne, the Sacred Palace and the "
            "Bucoleon, joined by passages and walks that also lead to the "
            "Hippodrome and the Baths of Zeuxippus. Like Blachernae it is a "
            "sprawl of fortified stone buildings full of riches, guarded "
            "day and night, and few are let in. Some thirty chapels belong "
            "to it, among them the Virgin of the Pharos. The palace schools "
            "of the Magnaura are among the most famous in the city.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "bucoleon",
        "The Palace of Bucoleon",
        inside=great,
        summary=paragraphs(
            "On the slope of the First Hill above the Marmara harbours, the "
            "home of the early emperors, close to the Hippodrome, Hagia "
            "Sophia and the Mese and riddled with secret passages under "
            "them. Under the Angeloi it housed favoured courtiers, the "
            "imperial kin and the empress. Baldwin of Flanders took it in "
            "1204, and it has been the residence of the Latin emperors "
            "ever since; it stands empty of its master in 1220, awaiting "
            "Robert of Courtenay.",
            "The Holy Lance of Longinus, in the city since the eighth "
            "century, lies in the Latin emperor's palace: a Roman pilum "
            "of Faith 3 whose saintly power is to Expel Demons.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "magnaura",
        "The Palace of Magnaura",
        inside=great,
        summary=paragraphs(
            "A huge palace whose name means 'fresh breeze', with many "
            "suites and a throne room for receiving honoured guests. Its "
            "marvels all still work: a golden throne that rises to the "
            "ceiling at a word, two gilded lions before it that open "
            "their jaws to roar and lash their tails, and a gilded "
            "bronze tree whose jewelled birds of precious metal sing. "
            "While visitors lay prostrate before the emperor, the "
            "throne rose, the lions roared and the birds sang together.",
            "The automata were made early in the tenth century by Aella "
            "of Verditius, a Cretan, who worked closer to the emperors "
            "than many liked and was charged several times with being a "
            "court wizard; her husband, Vaanes of Guernicus, defended "
            "her, and she was never convicted, though she was "
            "ostracised twice and came back both times to tend her "
            "works. Her heir in that duty, Passara of Verditius, keeps "
            "them from decay in 1220 and lives in apartments here given "
            "to her by the emperor's autocrat.",
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "Whether Passara serves the Latin emperor, as Formosos of "
                "Guernicus insists, the book leaves to the storyguide.",
            ),
        ],
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "blachernae",
        "The Palace of Blachernae",
        inside=region,
        realm="Infernal",
        aura=2,
        summary=paragraphs(
            "The smaller, newer imperial palace in the north-west corner of "
            "the city, on the Sixth Hill above the Golden Horn near the sea "
            "walls; built in the fifth and sixth centuries outside the "
            "walls, it was enclosed in 627 and became the favourite "
            "residence of the last Greek emperors, and their prison too: "
            "Isaac II Angelos was shut in one of its towers when his brother "
            "Alexios III overthrew him. Many old imperial crowns kept here "
            "were carried off in the three days of looting. That plunder "
            "and the notorious habits of the Angeloi, its last residents, "
            "have given the whole complex an Infernal aura of 2. The gate "
            "of the Golden Mantle leads to it.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "porphyry_chamber",
        "The Porphyry Chamber",
        inside=region,
        summary=paragraphs(
            "The imperial birthing room, walled in purple porphyry that "
            "Egypt sent in the fourth century and draped in purple silk; the "
            "book does not say in which palace it lies. A child born there "
            "to a reigning emperor and empress is porphyrogennetos, 'born "
            "in the purple', and outranks elder siblings born before the "
            "accession, even as a girl: Empress Zoe was crowned over male "
            "rivals on that claim. Such princesses may not marry outside "
            "the empire, though that rule has been broken, to ruin. Being "
            "born in the purple brings a claim to the throne, a good "
            "education and the people's love, and so many such children "
            "have been blinded or shut in convents and monasteries when "
            "their parents fell; with emperors changing so fast, several "
            "living people can claim the rank. The Latins honour the "
            "custom but loosely, and the room is no longer always guarded.",
            "Porphyrogenitos. A character born in the chamber gains a "
            "Supernatural Virtue at birth, free of the usual allowance, and "
            "because of the city's shifting auras it need not be Divine: on "
            "a simple die, 1 Infernal, 2 Magic, 3 or 4 Faerie, 5 to 9 "
            "Divine, and 10 a Major Virtue in place of the Minor (roll the "
            "realm again, ignoring another 10). Others assume the gift is "
            "God's blessing, as the emperors say; its true realm may stay "
            "hidden even from its bearer.",
        ),
        **KNOWN_REGION,
    )


# ------------------------------------------- holy and unholy sites


def _sacred_sites(theban: Theban) -> None:
    region = theban.places["constantinople"]
    _add(
        theban,
        "hagia_sophia",
        "Hagia Sophia",
        inside=region,
        realm="Divine",
        aura=5,
        summary=paragraphs(
            "The Church of the Holy Wisdom, the Great Church: the third "
            "church on its site and each bigger than the last, a basilica "
            "whose great dome, 168 feet above the floor and carried on "
            "columns, makes it seem round; it is the largest cathedral "
            "in Mythic Europe. It was stripped in the sack: its relics "
            "taken, its high altar broken up for the gold, its "
            "chandeliers torn down for the silver, and orgies of lust "
            "and slaughter in the three days of looting fouled its "
            "Divine aura. Worse to the Greeks, it has passed from the "
            "Orthodox to the Latin rite under a Latin patriarch who "
            "answers to the pope. Emperors are still crowned here, in "
            "ceremonies little changed from the Greek ones.",
            "Auras. The rebuilt high altar, a poor copy of the old, "
            "centres a Dominion aura of 5; the aisles and the outer "
            "porticoes have a Dominion aura of 2. The nave holds an "
            "Infernal aura of 7, left by the crusaders' massacre of "
            "more than a thousand innocents there, and with most of the "
            "relics gone the Dominion is too weak to wear it down.",
            "Relics too heavy to carry off still work. The Column of St. "
            "Gregory the Thaumaturge, one of the dome's supports, gives "
            "+6 to Recovery rolls and heals a wound one step faster (a "
            "Heavy Wound in a Medium Wound's time, a Light Wound in a "
            "day). On one of the nine doors from the narthex into the "
            "nave hangs a tube: a sick man who sets it to his lips has "
            "his illness drawn out of him.",
            "Its architects were Isidore of Miletus and the "
            "mathematician Anthemius of Tralles, who gathered columns "
            "from across the empire, those of Ephesus's Temple of "
            "Artemis among them. They quarrelled, Isidore wanting "
            "refinements drawn from Heron of Alexandria, and he had his "
            "way when Anthemius died within the year, of natural "
            "causes, it was said, though rumour doubted it. Theban "
            "magi, Catella of Alexandria above all, would like to study "
            "the building for Heron's ideas: a season of daily study "
            "would uncover them, and Catella will pay any magus with a "
            "workable plan in vis and gold for his time and notes.",
        ),
        secrets=[
            titled(
                "Heron's insights",
                "The insights from Heron are really there in Hagia Sophia's "
                "fabric, for a magus who spends the season.",
            ),
        ],
        **KNOWN_ORDER,
    )
    _add(
        theban,
        "holy_apostles_crypts",
        "The Crypts of the Holy Apostles",
        inside=region,
        realm="Infernal",
        aura=3,
        summary=paragraphs(
            "The crypts under the Church of the Holy Apostles, burial "
            "place of emperors and patriarchs until 1028, now looted by "
            "men who dug up the emperors for their crowns and jewels. "
            "By day the church's Dominion aura of 4 keeps down an "
            "Infernal aura of 3 rising from the crypts; at night the "
            "Dominion falls to 3 and the Infernal rises to 4, taking "
            "the church over and letting the thing below roam it.",
            "That thing is Zeno, emperor from 474 to 491: once "
            "Tarasicodissa, a mercenary chief of the Isaurians from the "
            "Taurus Mountains, hated, plotted against, overthrown and "
            "buried alive here, begging for mercy for three days before "
            "he fell silent. He never died. Demon-blooded, he needs no "
            "food or air and does not age; Leo Grammaticus painted him "
            "as shaggy, misshapen, goat-footed, hairy-legged, black of "
            "skin and absurdly built. Each night he climbs out of his "
            "open sarcophagus to prowl the church, but he cannot live "
            "outside an Infernal aura, so he can hardly leave it, and he "
            "kills and eats anyone he catches. The book gives him no "
            "stat block.",
            "Hermetic legend says city magi once hid occult books and "
            "papers in the crypts, trusting the ghosts of the emperors "
            "to guard them, and necromancers called up the ghosts of "
            "emperors not gone to Heaven in the Infernal aura of Zeno's "
            "lair. Both were perilous.",
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "The storyguide may hide almost any treasure here, perhaps a "
                "clue to another story, to be won only by getting past Zeno.",
            ),
        ],
        **RUMOURED_TRIBUNAL,
    )


# ------------------------------------------------------- the mundane world


def _lords(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    w["latin_emperor"] = b.lord(
        "Latin Emperor of Constantinople",
        title="duke",
        wealth="Wealthy",
        seat="The Palace of Bucoleon, Constantinople",
        ruler="Robert of Courtenay, emperor-elect (arrives 1221)",
        place=p["constantinople"],
        summary=paragraphs(
            "The emperor of Romania, as the crusaders call the empire "
            "they made in 1204. By their pact with Venice he holds a "
            "quarter of the old empire directly, while the Venetians "
            "and the other crusade lords take three-eighths each; under "
            "him come the vassalli, the Frankish barons and the Greek "
            "lords of simple homage who accepted the new order, among "
            "them the King of Thessaloniki, the Prince of Achaea and "
            "his barons, the Duke of Athens and the Duke of Naxos. His "
            "court is his private council of trusted men and the "
            "council of the empire, which joins him, the Venetian "
            "podestà with his council, and the Frankish barons; the old "
            "Byzantine bureaucracy runs on beneath, since taxes, courts "
            "and supplies still need clerks.",
            "Its emperors have not lasted. A college of six Venetians "
            "and six crusaders chose Baldwin of Flanders over Boniface "
            "of Montferrat; Baldwin was taken by the Bulgarians at "
            "Adrianople in 1205 and died in captivity. His brother "
            "Henry, crowned in August 1205, held the shrunken realm "
            "together until his sudden death in 1216, perhaps poisoned "
            "by his Bulgarian wife Maria, who fled. Peter of Courtenay, "
            "elected next, was seized by Theodore Komnenos Doukas of "
            "Epiros on his way from Durazzo in 1217 and is thought to "
            "have died his prisoner. His widow Yolanda reached the city "
            "by sea and ruled as regent from 1217 to 1219, making peace "
            "with Bulgaria and Nicaea and marrying her daughter Marie "
            "to the Nicene emperor. After her sudden death the throne "
            "went to her elder son Philip of Namur, who refused it; his "
            "brother Robert has accepted but will not reach the city "
            "until 1221.",
            "So the empire is leaderless in 1220, a narrow strip round "
            "its capital, and at war again: Nicaea has just broken three "
            "years of peace, and the outlook is poor. The emperor still "
            "owns the Crown of Thorns, though it is pledged to the "
            "doge, and the Holy Lance lies in his palace.",
            "The book leaves the throne simply empty; history has the "
            "barons governing through regents, Conon de Béthune until "
            "his death late in 1219 and then the papal legate Giovanni "
            "Colonna.",
        ),
        secrets=[
            titled(
                "Baldwin's fate",
                "Some say Baldwin was seen alive in Flanders, and House "
                "Tremere is whispered to know more of his fate than it says; "
                "the indiscreet Redcap who spread that tale died soon after "
                "in a fall from his horse, and the magistrates of the day let "
                "it lie.",
            ),
            titled(
                "Peter's fate",
                "The body of Peter, Latin Emperor of Constantinople, was "
                "never found either.",
            ),
            titled(
                "Maria of Bulgaria",
                "Hermetic gossip ties the vanished Maria of Bulgaria to the "
                "Daughters of Erictho.",
            ),
        ],
    )
    w["podesta"] = b.lord(
        "Podestà of Romania",
        title="count",
        wealth="Wealthy",
        seat="The Venetian Quarter, Constantinople",
        ruler="Ottaviano Quirino",
        place=p["venetian_quarter"],
        summary=paragraphs(
            "The governor Venice sends to rule its people and holdings in "
            "the east, kept on a short leash for fear the quarter breaks "
            "away from the republic. He deals with the Latin emperor, sits "
            "with his own council on the council of the empire, and runs "
            "the eastern Venetian possessions as he judges best, forever "
            "assuring Venice that its interests come first. The Venetian "
            "Council of Constantinople advises him, as the Council of "
            "Venice advises the doge, and both answer to the doge and that "
            "council in the end. The Venetian lands of western Greece are "
            "ruled straight from Venice, and Durazzo and Corfu are "
            "expressly outside his reach. He holds the Crown of Thorns in "
            "pledge for the doge. In 1220 the podestà is Ottaviano Quirino.",
        ),
    )


def _churches(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    region = p["constantinople"]
    patriarch = b.church(
        "The Latin Patriarchate of Constantinople",
        church="Archbishop's cathedral",
        ruler="Vacant since Gervase died in 1219",
        place=p["hagia_sophia"],
        summary=paragraphs(
            "Since the conquest the patriarch in Hagia Sophia has been a "
            "Latin under the pope, and the Orthodox Church in Constantinople "
            "is in theory subject to Rome; the Orthodox patriarch, Manuel I "
            "Charitopoulos, sits at Nicaea. Under the crusaders' pact Venice "
            "names the Latin patriarch: its man Thomas Morosini was the "
            "first, grudgingly accepted by Innocent III; the see stood empty "
            "from his death in 1211 until Gervase was appointed in 1215, "
            "and is empty again since Gervase died in 1219, the pope not "
            "yet having named a successor.",
            "The Latin Church has set up new sees with Latin bishops over "
            "mostly Orthodox priests, seeks more Latin clergy from the West, "
            "and has brought the Latin rite into many churches. Some clergy "
            "have accepted the union; many who reject it still serve in "
            "the new hierarchy, and most of the people stay loyal to "
            "Orthodoxy, so an attempt to stop the procession of icons on "
            "the Feast of the Triumph of Orthodoxy means a riot.",
        ),
    )
    patriarch.details["relics"] = [
        {"name": "The Column of St. Gregory the Thaumaturge", "saint": "St. Gregory"},
        {"name": "The healing tube on the nave door", "saint": ""},
    ]
    w["latin_patriarch"] = patriarch
    w["hagia_eirene"] = b.church(
        "Hagia Eirene",
        church="Large urban church",
        place=region,
        summary=(
            "The Church of the Holy Peace, the Old Church, the oldest in the "
            "city: the third building on its site, rebuilt when Justinian "
            "rebuilt Hagia Sophia, a rectangle under a central dome with an "
            "outer atrium and narthex. It held few relics and so escaped "
            "the worst of the plunder. Dominion aura 4."
        ),
    )
    w["pharos"] = b.church(
        "The Church of the Virgin of the Pharos",
        church="Chapel",
        place=p["great_palace"],
        summary=(
            "The 'Holy Chapel' of the crusaders, one of the thirty chapels "
            "of the Great Palace, kept for the emperor and his family. It "
            "became an immense treasury of relics, and every one has gone: "
            "two pieces of the True Cross, the Holy Lance's iron point, the "
            "nails from Christ's hands, His blood in a phial of crystal, "
            "His tunic, the Crown of Thorns, part of the Virgin's "
            "robe and the head of St. John the Baptist. Dominion aura 4, "
            "falling to 3 at night."
        ),
    )
    w["holy_apostles"] = b.church(
        "The Church of the Holy Apostles",
        church="Large urban church",
        place=region,
        summary=(
            "A Greek cross under five domes, once the busiest church in the "
            "city and the burial place of emperors and patriarchs until "
            "Constantine VIII was laid here in 1028. Its relics were "
            "stolen, many of them to Venice: the heads of Andrew, Luke "
            "and Timothy, and the Column of the Flagellation, where "
            "Christ was bound to be scourged. Looters even dug up the "
            "emperors. Its Dominion aura of 4 falls to 3 at night, when the "
            "Infernal aura of the crypts below overcomes it."
        ),
    )
    w["studion"] = b.church(
        "St. John the Baptist of Studius and the Studion",
        church="Monastery or nunnery",
        founded=463,
        place=region,
        summary=(
            "One of the city's most celebrated churches, founded by the "
            "Roman patrician Studius in 463, a plain basilica with nave, "
            "narthex and atrium, beside the Studion, the monastery whose "
            "stone buildings stand round a square and which is the "
            "intellectual heart of the empire. The church escaped the worst "
            "of the looting, perhaps because it gathered books rather than "
            "relics, and keeps a Dominion aura of 5. The Studion carries on "
            "as if the Latins were not there, and its library is the "
            "largest collection of church and secular books in either the "
            "Latin or the Byzantine Empire."
        ),
    )
    w["st_christopoulos"] = b.church(
        "The Monastery of St. Christopoulos",
        church="Monastery or nunnery",
        founded=823,
        place=region,
        summary=paragraphs(
            "A walled monastery of several acres inside the city walls, "
            "in a quarter mostly given to pasture and orchards, founded "
            "as a lavra of monks in cells in 823. Romanos III Argyros, "
            "Zoe's first husband, endowed it richly, founding in 1030 an "
            "orphanage and school paid for by the treasury and run by "
            "the monks, and in 1031 giving it a tiny, exquisite icon of "
            "a little-known saint, Loukia. Under a great golden icon of "
            "Christ Pantokrator over the gate lie a small vineyard, "
            "pastures and wide gardens; the basilica stands at the "
            "centre with the refectory, kitchen, laundry and bakehouse "
            "round it, and some thirty black clergy live in small "
            "wooden cell-houses scattered across the grounds. At the "
            "west end an ancient, roofless bathhouse keeps two baths, "
            "one a fishpond and one still used by the monks, with the "
            "infirmary and storehouses behind. At the east end are the "
            "guest quarters, the school and a hostel for sixty boys, the "
            "famous orphanage, with the master's house, the boys' "
            "refectory, a scriptorium and a library beside them.",
            "The orphanage was long a source of eunuchs for the palace: "
            "paying families sent boys to learn music, and those whose "
            "voices suited were gelded for the choirs, while children "
            "too dangerous to the throne were sent here to be "
            "castrated. The Latins still fund it, but they find the "
            "practice disgusting and the demand has nearly gone. The "
            "monks know that holy hermits of extreme mortification live "
            "in the old cistern under the orphanage, and leave them "
            "alone.",
        ),
        secrets=[
            titled(
                "Who the hermits are",
                "The hermits of the Monastery of St. Christopoulos are the "
                "Criamon magi of Xylinites.",
            ),
        ],
    )
    w["st_john_hebdomon"] = b.church(
        "The Church of St. John the Baptist at Hebdomon",
        church="Large urban church",
        place=region,
        summary=(
            "The chief of the many churches of Hebdomon, seven miles out "
            "along the Egnatian Road, in the town where the early emperors "
            "were crowned before riding through the Golden Gate to the "
            "Hippodrome."
        ),
    )


def _towns(theban: Theban, b: Builder) -> None:
    w = theban.world
    region = theban.places["constantinople"]
    emperor = w["latin_emperor"]
    w["constantinople_town"] = b.town(
        "The City of Constantinople",
        charter="Noble lord",
        ruler="The Latin emperor, through the city's prefect",
        answers_to=emperor,
        place=region,
        summary=(
            "The capital of the Latin Empire and still the greatest market "
            "of Mythic Europe: goods from the whole world are sold here, "
            "and anything can be had for a price. Its people number under "
            "200,000, a babel of tongues. The main streets run straight in "
            "the Roman way, and even the lanes are more ordered than in "
            "other cities; the Mese crosses the city from the Philadelpheion "
            "to the palaces. Most of the city is open to anyone brave "
            "enough, but some quarters are dangerous by day and all but the "
            "best-guarded buildings are deadly by night; the palaces are "
            "watched always, parish churches are always open, and the great "
            "churches are kept locked except for feasts and important "
            "visitors. The guilds trade where they always have: candle "
            "makers, goldsmiths, silversmiths and perfumers by the portico "
            "of Hagia Sophia, butchers and fishmongers in the Forum Tauri, "
            "cattle and horse dealers in the Forum Amastrianum, slaves and "
            "harlots in the Forum of Constantine."
        ),
    )
    w["hebdomon"] = b.town(
        "Hebdomon",
        charter="Noble lord",
        answers_to=emperor,
        place=region,
        summary=(
            "The largest town outside the walls, a middling city seven "
            "miles out on the European shore by the Egnatian Road to Rome. "
            "Once an imperial summer retreat, it grew into a naval port and "
            "a place of ceremony, where early emperors were crowned before "
            "processing through the Golden Gate to the Hippodrome. It has "
            "many churches, St. John the Baptist chief among them, a palace "
            "of Justinian, forums and monasteries; to the north lies the "
            "Campus, the plain where the army camped before campaigns. The "
            "round tower of the Cyclobion guards its harbour, a favourite "
            "landing for friend and foe alike, though the town itself has "
            "no walls; the crusaders first came ashore here. Its governor "
            "surrendered it to the Latins after the city fell, and they "
            "have held it since."
        ),
    )
    w["galata"] = b.town(
        "Galata",
        charter="Noble lord",
        answers_to=emperor,
        place=region,
        summary=(
            "A fortified town across the Golden Horn, for centuries one of "
            "the city's main defences. Its castle anchored the great chain "
            "that could be raised across the Horn to close the northern "
            "harbours, until the crusaders stormed it in June 1203 and broke "
            "the chain, a sign of what was coming. The crusaders lived here "
            "until April 1204, when they moved into the richer houses of "
            "the conquered city."
        ),
    )


def _factions(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    region = p["constantinople"]
    w["guilds"] = b.faction(
        "The Guilds of Constantinople",
        faction="Gild",
        decides="Its leader",
        ruler="The prefect of the city",
        place=region,
        rules="Every guild is run by the state, under the city's prefect",
        wants="Their old trades, quarters and privileges kept",
        offers="Goods of every kind, craftsmen, market news",
        summary=(
            "The city's trades have been organised in guilds far longer "
            "than in the West, and some exist here that Paris or London "
            "would not see for generations. They range from the silk "
            "makers, almost noble, to caulkers and street sweepers little "
            "better than peasants. Unlike Western guilds struggling for "
            "freedom from the magistrates, all of them are arms of the "
            "state, and even the greatest guild master obeys the prefect. "
            "Each still lives and sells in its old quarter."
        ),
    )
    w["gangs"] = b.faction(
        "The Gangs of Constantinople",
        faction="Brigands and mercenaries",
        decides="Its leader",
        place=region,
        wants="Safety for their own people, and loot",
        offers="Protection, muscle, smuggling, a way in by night",
        summary="With civil law gone since the conquest, every people of the "
        "city, Greek, Venetian, Frankish and the rest, guards its own "
        "with makeshift gangs or hired swords, and none trusts the "
        "others. Armed bands and bandits nest in the burnt-out ruins, "
        "the ash of the Venetian Quarter among them, and smugglers use "
        "the Venetian ports to slip goods in.",
        secrets=[
            titled(
                "Demons behind the factions",
                "Some suspect the demons Hulikang and Nike, once patrons of "
                "the Greens and Blues, of now stirring up a 'Frank' and a "
                "'Venetian' faction among the gangs of Constantinople.",
            ),
            titled(
                "Storyguide Notes",
                "The book does not say whether Hulikang and Nike stir the factions.",
            ),
        ],
    )
    w["venetian_council"] = b.faction(
        "The Venetian Council of Constantinople",
        faction="Council or assembly",
        decides="A council",
        ruler="The podestà",
        place=p["venetian_quarter"],
        wants="Venice's trade privileges kept and the quarter loyal",
        offers="Shipping, credit, the Golden Horn ports",
        summary=(
            "The council that advises the podestà, on the model of the "
            "council that advises the doge; it and the podestà answer to the "
            "doge and the Council of Venice. Through the podestà it sits in "
            "the council of the empire."
        ),
    )
    w["belisarius_court"] = b.faction(
        "Belisarius's Urban Faeries",
        faction="Faerie court",
        decides="Its leader",
        ruler="Belisarius (see the Bestiary)",
        realm="Faerie",
        place=p["serpent_column"],
        wants="Human watchers for their show",
        summary=(
            "A small troupe of city faeries in the regio above the Serpent "
            "Column, led by the faerie who calls himself Belisarius. They "
            "act the last battle of the Nika riots over and over, the rioters "
            "against Belisarius and his guards, and go out into the city to "
            "lure mortals in to watch."
        ),
    )


# --------------------------------------------------------- Michael's Tabula


def _michaels_tabula(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    region = theban.places["constantinople"]
    site = _add(
        theban,
        "michaels_tabula",
        "The Mithraeum of Michael's Tabula",
        inside=region,
        aura=3,
        summary=paragraphs(
            "A forgotten temple of Mithras under a ruined quarter of the "
            "city, in a Magic aura of 3, reached through the catacombs. "
            "The magi of Michael's Tabula have made it a rough council "
            "chamber, with the stone tablet of their oath laid on the "
            "old altar, and cut laboratories, some of them shared, in "
            "the chambers round it. New stone walls, raised with their "
            "patron's help, close every way in, and only a magus with "
            "one of the covenant's magical keys can pass them; trusted "
            "allies alone are brought below, and other visitors are "
            "met in the magi's houses in the city.",
            "The covenant has found a few sources of vis in the "
            "catacombs; the book does not describe them.",
        ),
        secrets="",
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "The newer of the two covenants inside Constantinople, of the "
        "Propontian phyle: a close band of devout magi, mostly Jerbiton, who "
        "lived through the sack of 1204 and swore to stay. In public the "
        "covenant is pledged to restoring the city to its old glory; its "
        "real aim is to drive the crusaders out, and several sympathetic "
        "magi and covenants help it in secret.",
        "Michael, a famed magus of Thermakopolis, led the Jerbiton who "
        "tried and failed to defend the city, and was the last of that "
        "covenant to fall, fighting. As he lay dying, he, his surviving "
        "apprentice Petros, Wilrich of Flambeau and three other Jerbiton "
        "magi, two of Moero's Garden and a city eremite, vowed their lives "
        "to the city's defence and swore never to leave it to the "
        "invaders. The oath was cut into a stone tablet, which named the "
        "new covenant. The survivors went down into the catacombs, some "
        "bitter and hungry for revenge, others praying for deliverance, "
        "made new sancta there and hid what magical resources they had "
        "left. The covenant was formally founded at the Tribunal of 1207, "
        "the first after the fall.",
        "It still feels like an underground resistance, fervent but "
        "disordered: its councils are loud and chaotic, the magi split "
        "over how cautious or daring to be against the Frankish rulers, "
        "yet they close ranks round their cause. Some in the Tribunal, the "
        "Quaesitores among them, eye the covenant and its likely meddling "
        "with suspicion, but more sympathise with it.",
        "About half a dozen magi, mostly Jerbiton and many living in the "
        "city since before the Fourth Crusade, all devout Christians, led "
        "by Petros, Michael's filius, and with Wilrich of Flambeau as its "
        "sword.",
    )
    what_matters = joined_lines(
        "Boon: Powerful Ally (Fylakas, the covenant's patron)",
        "Vis: a few unnamed sources in the catacombs",
        "Income: a generous gift of money and books every year or two, "
        "brought by a Redcap from a sponsor who stays anonymous",
        "Library: a young collection, partly old books saved from "
        "Thermakopolis, swelled by the anonymous sponsor's gifts",
        "Boon: Hidden Ways (the catacombs, sealed by walls only the magi's "
        "keys open); Criminals (a part-time following of rogues, spies and "
        "mercenaries)",
        "Hook: Urban; Mundane Politics (its covert war on the Latins); "
        "Poverty (too poor to keep many covenfolk); Fallen Temple (the "
        "mithraeum)",
        "Hook: Hermetic Politics (Quaesitores suspect it of meddling)",
        "Tension: the magi disagree how boldly to strike at the Franks",
        "Tension: Petros leads only out of respect for his pater, and "
        "thinks of leaving for a monastery",
        "Tension: some magi may hold knowledge or relics of Heron of "
        "Alexandria's legacy",
    )
    notes = paragraphs(
        "The patron, Fylakas. When the founders fled into the catacombs in "
        "1204, a mighty figure of living stone rose out of the ground to "
        "shield them from the crusaders and help them. They named it "
        "Fylakas, 'guard', and took it as their patron, but have never "
        "managed a long talk with it and know little of it. It commands the "
        "earth: it rules the catacombs' gateways and can shake the ground "
        "hard enough to damage or bring down buildings in the city. Most "
        "likely it is an ancient earth elemental.",
        "Covenfolk. The covenant cannot yet afford to hire or house many. "
        "Its magi have instead gathered a motley crew of rogues, spies "
        "and mercenaries who serve part-time and lead double lives, so "
        "that the covenant itself stays mostly out of sight.",
        "Founded: 1207, at the Tribunal after the fall; the oath was sworn "
        "in 1204. Season: the book gives none; it is a young covenant.",
    )
    hidden = [
        titled(
            "What Fylakas may be",
            "Fylakas may instead be a demon loosed from its binding in the "
            "sack, deceiving the pious magi of Michael's Tabula.",
        ),
        titled(
            "How far the magi would go",
            "Despite their piety, one or more of the magi of Michael's Tabula "
            "might stoop to demonic help if it would rid the city of the "
            "Franks.",
        ),
        titled(
            "Storyguide Notes",
            "The book leaves the anonymous sponsor's identity to the storyguide.",
        ),
    ]
    tabula = b.covenant(
        "Michael's Tabula",
        tribunal=tribunal,
        founded=1207,
        place=site,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        unnamed_magi=4,
        detail=FULL,
        season="Spring",
    )
    theban.covenants["michaels_tabula"] = tabula
    b.book(
        tabula,
        "The library of Michael's Tabula",
        "Other",
        language="Classical Greek",
        description=(
            "The book names no books. The covenant has begun a library, "
            "some of it old volumes saved from the fall of Thermakopolis, "
            "added to by the money and books an anonymous sponsor sends by "
            "Redcap every year or two. Some of the magi may hold knowledge "
            "or relics of Heron of Alexandria's legacy (Ancient Magic)."
        ),
    )
    _tabula_magi(theban, b, tabula)


def _tabula_magi(theban: Theban, b: Builder, home: Covenant) -> None:
    m = theban.magi
    m["petros"] = b.magus(
        "Petros",
        covenant=home,
        house=JERBITON,
        age=36,
        summary=paragraphs(
            "The leader of Michael's Tabula, a man of thirty-six in the body "
            "of a boy of eleven. His apprenticeship went wrong twice: his "
            "pater Michael botched his own Longevity Ritual, which took hold "
            "of the apprentice instead and stopped him growing; then Michael "
            "died defending the city just before Petros was to swear the "
            "Oath. Young and untried as he was, the covenant chose him as "
            "its leader out of respect for his pater.",
            "He is a sad man caught in a child's body. His prayers to grow "
            "up go unanswered, and he carries the shame of the city's fall "
            "and of Thermakopolis's end. At his lowest he has thought of "
            "entering a monastery, but he stays to honour Michael's cause.",
        ),
        traits={"Depressed": 2, "Meditative": 2, "Immature": 1},
    )
    m["wilrich"] = b.magus(
        "Wilrich",
        covenant=home,
        house=FLAMBEAU,
        age=51,
        summary=paragraphs(
            "A Saxon from the Holy Roman Empire who looks forty-three, one "
            "of the handful of 'Frankish' magi in the Tribunal, and one who "
            "fits the type: big, burly, fair and bearded, rough in his "
            "manners, and speaking Greek with a heavy accent. Under the "
            "bluster lies deep faith.",
            "He went on the Fourth Crusade as a knight in the following of "
            "the bishop of Halberstadt, having sworn, to quiet the "
            "Quaesitores, to use no magic while it lasted. Along the way "
            "he came to doubt the crusade's righteousness, and when the "
            "city fell he left the assault to defend the innocent and "
            "fight demons, ending up beside the dying magi of "
            "Thermakopolis and saving Petros. A formidable swordsman, he is "
            "the covenant's most martial magus and the keenest in its "
            "military plans. As a magus trained outside the Tribunal he is "
            "a metoikos.",
        ),
        traits={"Devout": 3, "Valiant": 3, "Crude": 1},
    )


# ----------------------------------------------------------------- Xylinites


def _xylinites(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    region = theban.places["constantinople"]
    site = _add(
        theban,
        "xylinites",
        "The Cistern of Xylinites",
        inside=region,
        aura=3,
        summary=paragraphs(
            "A huge vaulted cistern under the orphanage and eastern "
            "grounds of the monastery of St. Christopoulos, partly "
            "drained in the eleventh century and still flooded. Six fine "
            "laboratories are cut into its walls, reachable only by the "
            "little boats moored at the foot of the stairs; hidden "
            "staircases lead down from locked rooms in the orphanage "
            "buildings, and the cistern passes for a storehouse. Flooded "
            "tunnels branch off carrying water across the city, a maze a "
            "boat can explore, and the magi use them to slip out "
            "unseen on business.",
            "The icon of St. Loukia sits in a small shrine in an alcove "
            "still reachable only by boat. A Magic aura of 3 spreads "
            "from it in a perfect sphere wide enough to take in the "
            "orphanage and the eastern end of the monastery, and ends "
            "where it meets the Dominion over the middle and west of "
            "the grounds. The orphan boys tell tales of haunted "
            "storerooms and mad hermits below, and a few bold ones have "
            "broken curfew to explore the vaults.",
        ),
        secrets=[
            titled(
                "Where the aura comes from",
                "The Cistern of Xylinites' aura flows from Loukia herself: "
                "she is not dead but held in something like Twilight between "
                "this world and the Magic Realm, and magic pours through her "
                "into the world.",
            ),
        ],
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "A long-established covenant inside the walls of Constantinople, "
        "of the Propontian phyle: until 1204 a great Jerbiton covenant in "
        "the monastery and orphanage of St. Christopoulos, and now the "
        "Tribunal's only Clutch, three Criamon magi on the Path of the "
        "Body. Nearly destroyed when the city fell, it is fading into "
        "Winter with its new inhabitants. Its patron is St. Loukia of "
        "Berytus, a magical spirit held in a false icon.",
        "In 1071 Tikh of Jerbiton, hired as a teacher at the "
        "orphanage school, saw that the monastery's icon of St. Loukia was "
        "strange, and knew her for Loukia of Berytus, a Montanist heretic "
        "who claimed to have entered paradise bodily through the Holy "
        "Spirit and was put to death for blasphemy in the fourth century. "
        "With the abbot's leave he moved the icon from the church to the "
        "schoolroom, was amazed to see a Magic aura slowly grow round it, "
        "and quickly took it to the schoolmaster's house where he lived. "
        "Wanting room for a laboratory, he found and partly drained the "
        "cistern beneath, founding Xylinites in 1074.",
        "For 130 years its magi taught at the orphanage, which let them "
        "school many brilliant young men, find Gifted children left with "
        "the monks, and build strong ties inside the palace. The palace "
        "always wanted more eunuchs than it could find, and the school "
        "became a chief source of them; former pupils at court favoured "
        "the orphanage, and the Jerbiton lived well, studied freely and "
        "swayed the court at one remove, treading a fine line between "
        "serving the imperial court and great families and wielding "
        "political influence. The conquest ended that: three Jerbiton "
        "died fighting the attackers and the rest fled into exile, "
        "fearing the Tribunal's censure, while the court's officials "
        "scattered and the Latins, revolted by castration, stopped asking "
        "for eunuchs. The one magus who stayed, Artoud of Criamon, made "
        "the cistern a Clutch for mystical research. The Tribunal saw "
        "Xylinites turn inward and shut its gates to outsiders.",
        "Its life is fragile. Artoud's Blatant Gift keeps him from "
        "teaching or even meeting the monks, who believe him and the two "
        "apprentices he trained to be holy hermits given to fierce "
        "mortification. The covenant's companions now teach the orphans "
        "and deal with the monastery for it; visitors come and go as in "
        "any Orthodox house, and the staff barely deal with the monks, "
        "still less with the hermits. Children are still left at the "
        "orphanage, and now and then a Gifted boy abandoned by frightened "
        "parents has won the Clutch some standing at Tribunal. How long "
        "this can last, no one knows.",
    )
    what_matters = joined_lines(
        "Boon: Local Ally (St. Loukia, the covenant's patron)",
        "Vis: the book names none",
        "Income: the orphanage, still paid for from the imperial treasury "
        "by the Latins, and taught by the covenant's companions",
        "Library: the orphanage's library and scriptorium; St. Loukia's "
        "icon is unknowingly a summa of Animal Ken",
        "Allies: four eunuch priests among its companions, who say mass in "
        "nunneries across the city and have the ear of many retired "
        "noblewomen and at least one former empress",
        "Boon: Hidden Ways (the flooded tunnels under the city); Literate "
        "Covenfolk (the tutors)",
        "Hook: Urban; Monastery (the monks of St. Christopoulos, who must "
        "go on thinking the magi hermits); Infants (the orphans, some "
        "Gifted)",
        "Hook: Heretics (its patron is a Montanist heretic in a false "
        "icon); Dwindling Resource (the eunuch trade that once fed it)",
        "Tension: curious orphans keep sneaking into the vaults",
        "Tension: Trasaricus's imperial blood and hatred of the Doukas "
        "family make him a danger in the city",
        "Tension: Artoud gives fitful support to the League Against "
        "Idolatry's petition against the Ceremony of Propitiation",
    )
    notes = paragraphs(
        "The patron, St. Loukia. The icon is set in a gilded frame only six "
        "inches by four, a mosaic of tiny squares of gold, silver and "
        "coloured stone: a lovely young woman seated in a meadow with a "
        "lamb, while thriving flocks, birds and even the fish of the "
        "brook at her feet gaze at her. It glows with life, and now and "
        "then, it is said, the figure lifts her arms and shrieks a warning "
        "in a tiny voice. That has happened three times since the "
        "covenant came by it: before the fire that burnt the orphanage "
        "and killed many children, before Manzikert in 1071, and once more in "
        "spring 1204. Words in demotic Greek on the frame call her "
        "'Loukia, Herald of Last Things', and the Criamon watch it "
        "eagerly. She was likely a Montanist, of the early sect that "
        "sought direct experience of the spirit, whose founder claimed to "
        "be the Holy Spirit; a pantheist mystic of nature with a deep "
        "bond to every kind of beast, whose visions were of the Magic "
        "Realm, chiefly the part tied to the Form of Animal.",
        "Covenfolk. A small staff of grogs runs the covenant's mundane "
        "affairs in elaborate Byzantine robes that mark rank and office: "
        "grey for tutors, blue for orphans, black for servants. The four "
        "eunuch priests among its companions live in the priests' house "
        "by the master's house.",
        "Founded: 1074. The book dates the near-destruction to 1205 in "
        "places; the city fell in 1204.",
    )
    hidden = [
        titled(
            "What the icon teaches",
            "Meditating on Loukia's icon teaches Animal Ken. None of the "
            "magi of Xylinites has realised it, since they fear to meditate "
            "on it long, but the Criamon may find it out.",
        ),
        titled(
            "Loukia's fate",
            "Loukia is not dead but caught in something like Twilight "
            "between this world and the Magic Realm, which is why the aura "
            "pours from her icon.",
        ),
        titled(
            "Artoud and Trasaricus",
            "Artoud knows Trasaricus must soon be sent far from the city to "
            "avert disaster, but cannot bring himself to expel him.",
        ),
        titled(
            "Storyguide Notes",
            "Meditating on the icon works as a summa of Animal Ken, level 3, "
            "Quality 10.",
        ),
    ]
    xylinites = b.covenant(
        "Xylinites",
        tribunal=tribunal,
        founded=1074,
        place=site,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        detail=FULL,
        season="Winter",
    )
    theban.covenants["xylinites"] = xylinites
    b.book(
        xylinites,
        "The icon of St. Loukia",
        "Ability Summa",
        ability="Animal Ken",
        level=3,
        quality=10,
        language="Greek",
        description=(
            "A tiny mosaic icon of St. Loukia of Berytus, the covenant's "
            "patron, given to the monastery by Romanos III in 1031. Not a "
            "book: meditation on it teaches the Supernatural Ability "
            "Animal Ken as a summa, which the magi have not yet realised."
        ),
    )
    b.book(
        xylinites,
        "The orphanage library of St. Christopoulos",
        "Other",
        language="Greek",
        description=(
            "The book names no books. Beside the master's house stand the "
            "orphanage's scriptorium and library, kept up through the "
            "Jerbiton era when the covenant's magi taught there; what the "
            "fleeing Jerbiton took with them in 1204 is not said."
        ),
    )
    _xylinites_magi(theban, b, xylinites)


def _xylinites_magi(theban: Theban, b: Builder, home: Covenant) -> None:
    m = theban.magi
    m["artoud"] = b.magus(
        "Artoud",
        covenant=home,
        house=CRIAMON,
        age=175,
        summary=paragraphs(
            "Brother Artoud, leader of Xylinites, looking about "
            "seventy-one. Most of his life passed in central Anatolia's "
            "hills, in the Levant Tribunal, in a Criamon "
            "Clutch destroyed in the wars between the Sultanate of Rum "
            "and the empire. He is fanatically loyal to his House and "
            "cares little for the wider Order, which he thinks run by "
            "ignorant, boorish Frankish barbarians. His Gift is "
            "blatant. As a magus trained outside the Tribunal he is a "
            "metoikos.",
            "He has turned down Repose to stay and serve his House, and "
            "gives sporadic, half-hearted support to the League Against "
            "Idolatry.",
        ),
        secrets=[
            titled(
                "Artoud's body",
                "Artoud's body is in better shape now than at twenty-one: he "
                "does not age, shrugs off injuries quickly and moves with "
                "more than human grace, the fruit of long mastery of the "
                "flesh.",
            ),
            titled(
                "How Artoud hides it",
                "Artoud hides his unageing body, passing off the pale scars "
                "on his tanned skin as the marks of mortification, feigning "
                "a stoop and a slight limp among mundanes, and moving as "
                "little as he can.",
            ),
            titled(
                "Storyguide Notes",
                "Artoud's mastery is of the Path of the Body (Houses of "
                "Hermes: Mystery Cults).",
            ),
        ],
        traits={"Graceful": 5, "Pious": 3, "Devoted to House Criamon": 3},
    )
    m["theoderet"] = b.magus(
        "Theoderet",
        covenant=home,
        house=CRIAMON,
        age=75,
        summary=paragraphs(
            "A Criamon of the Clutch who looks forty-three, trained by "
            "Artoud. He is the orphanage's official castrator and, known for "
            "his medical skill, has often been called on to carry out "
            "blindings at the palace and across the city. With his deft "
            "Corpus magic and his mastery of Perdo Corpus he does it by "
            "magic, painlessly and safely, and he holds his work to be "
            "philosophically right: it serves Harmony where the likely "
            "alternative, execution or murder, would only add to Strife.",
        ),
        traits={"Pious": 3, "Fatalistic": 1, "Reclusive": 1},
    )
    m["trasaricus"] = b.magus(
        "Trasaricus",
        covenant=home,
        house=CRIAMON,
        age=21,
        summary=paragraphs(
            "The only member of Xylinites born in the Tribunal, Artoud's "
            "apprentice and a nephew of the deposed emperor Alexios IV "
            "Angelos, who was killed in 1204. Gelded as a small child "
            "because he was politically dangerous, he hates the Doukas "
            "family without mercy. His imperial blood fascinates "
            "Artoud, who will not expel him, though he sees that the young "
            "man must soon be sent far from Constantinople before he "
            "brings disaster.",
        ),
        traits={"Proud": 3, "Bitchy": 2, "Idle": 1},
    )


# ------------------------------------------------- magi of the palace


def _palace_magi(theban: Theban, b: Builder) -> None:
    m = theban.magi
    m["passara"] = b.magus(
        "Passara",
        covenant=None,
        house=VERDITIUS,
        age=None,
        summary=paragraphs(
            "Passara filia Bacauda filius Aella, a maga of Verditius with "
            "the Gentle Gift and of no covenant, who keeps the "
            "automata of the Palace of Magnaura safe from time and wear "
            "as her lineage's founder Aella did. She lives in apartments "
            "in the palace that the emperor's autocrat gave her, and, "
            "proud of her lineage and its mysteries, will live nowhere "
            "else. The book gives no age.",
            "Formosos of Guernicus believes she works for the Latin "
            "emperor and does more than tend the automata, and means to "
            "prove it.",
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "The book leaves whether Passara truly serves the emperor to "
                "the storyguide.",
            ),
        ],
    )
    m["formosos"] = b.magus(
        "Formosos",
        covenant=None,
        house=GUERNICUS,
        age=None,
        summary=paragraphs(
            "The grand-filius of Vaanes of Guernicus, who defended his wife "
            "Aella of Verditius against charges of being the emperor's "
            "court wizard. Formosos thinks Vaanes's part in that was "
            "criminal, and his pride will not let the matter rest: he is "
            "set on proving that Passara, Aella's heir in the Magnaura, is "
            "working for the Latin emperor and not merely keeping the "
            "automata, and will try to recruit player magi to look into "
            "her and her mundane dealings in secret. The book gives no age "
            "and names no covenant for him.",
        ),
    )


# ------------------------------------------------------------- finishing


def finish(theban: Theban) -> None:
    """Tie the city's records to those other parts make: Moero's Garden
    to Michael's Tabula and its old house, Formosos to Passara, and the
    podestà to Venice when a part has made the republic."""
    b = theban.b
    m = theban.magi
    b.link(
        m["formosos"],
        "characters",
        m["passara"],
        "Means to prove she serves the emperor",
    )
    b.link(m["passara"], "characters", m["formosos"], "Hunting her for the Tribunal")
    b.link(m["wilrich"], "characters", m["petros"], "Saved him in the fall of the city")
    tabula = theban.covenants["michaels_tabula"]
    garden = next((c for c in b.saga.covenants if c.name.startswith("Moero")), None)
    if garden is not None:
        b.link(tabula, "covenants", garden, "Two of the founders came from it")
        b.link(
            garden,
            "places",
            theban.places["moero_old_site"],
            "Its old house, where Moero's ghost is still bound",
        )
    venice = next(
        (
            n
            for n in b.saga.neighbours
            if n.kind == "lord"
            and n is not theban.world["podesta"]
            and ("Venice" in n.name or "Doge" in n.name)
        ),
        None,
    )
    if venice is not None:
        theban.world["podesta"].answers_to = venice.id


# --------------------------------------------------------------- stats

P = Profile
GREEK = "Greek"
CITY = "Area Lore: Constantinople"


#: Each magus the book sketches without a stat block, by character key.
PROFILES: dict[str, Profile] = {
    "petros": P(
        strong="int per com",
        weak="str sta",
        arts={"Me": 6, "Im": 5, "Re": 4, "In": 4, "Cr": 3},
        abilities={
            CITY: (4, "the catacombs"),
            "Theology": (2, "prayer"),
            "Leadership": (2, "covenant council"),
            "Etiquette": 2,
        },
        virtues=["Small Frame", "Depressed", "Pious (Minor)", "Dutybound"],
        native=GREEK,
    ),
    "wilrich": P(
        strong="str sta qui",
        weak="com pre",
        arts={"Ig": 8, "Pe": 6, "Cr": 4, "Re": 4, "Co": 3, "Te": 3},
        abilities={
            "Single Weapon": (6, "sword"),
            "Ride": (3, "battle"),
            "Infernal Lore": (2, "demons"),
            "Leadership": (2, "soldiers"),
            "Living Language: Greek": 3,
            CITY: 2,
        },
        virtues=["Warrior", "Large", "Pious (Minor)", "Dutybound"],
        native="High German",
        hermetic="Latin",
    ),
    "artoud": P(
        strong="dex qui sta",
        weak="com pre",
        arts={"Co": 9, "Mu": 6, "Re": 5, "Vi": 4, "In": 3, "Cr": 3},
        abilities={
            "Enigmatic Wisdom": (5, "the Path of the Body"),
            "Athletics": (3, "grace"),
            "Concentration": (3, "stillness"),
            "Area Lore: Levant Tribunal": 2,
            CITY: 2,
        },
        virtues=[
            "Station of Perfect Economy of Movement",
            "Station of Spiritual Nourishment",
            "Blatant Gift",
            "Pious (Minor)",
            "Proud (Minor)",
            "Stuck in Your Ways",
        ],
        native=GREEK,
        hermetic="Latin",
    ),
    "theoderet": P(
        strong="int dex per",
        weak="pre com",
        arts={"Co": 9, "Pe": 8, "Cr": 4, "Me": 3, "In": 3},
        abilities={
            "Medicine": (4, "surgery"),
            "Chirurgy": (4, "gelding"),
            "Enigmatic Wisdom": (3, "Harmony and Strife"),
            CITY: 2,
        },
        virtues=[
            ("Deft Form", {"form": "corpus"}),
            vf_art("Affinity with {art}", "corpus"),
            "Pious (Minor)",
            "Reclusive",
            "Infamous",
        ],
        native=GREEK,
    ),
    "trasaricus": P(
        strong="pre int com",
        weak="str sta",
        arts={"Me": 5, "Im": 4, "In": 3, "Co": 3},
        abilities={
            "Intrigue": (2, "the Angeloi"),
            "Etiquette": (2, "the court"),
            "Enigmatic Wisdom": 2,
            CITY: 2,
        },
        virtues=["Castratus", "Proud (Minor)", "Feud"],
        native=GREEK,
    ),
    "passara": P(
        strong="int dex com",
        arts={"Re": 7, "Te": 6, "Mu": 5, "Im": 4, "An": 3, "Vi": 3},
        abilities={
            "Craft: Goldsmith": (5, "automata"),
            "Magic Theory": (5, "enchantments"),
            "Etiquette": (3, "the imperial court"),
            "Intrigue": 2,
            CITY: (3, "the palaces"),
        },
        virtues=[
            "Gentle Gift",
            "Proud (Minor)",
            "Dutybound",
            "Infamous Master",
        ],
        age=120,
        native=GREEK,
    ),
    "formosos": P(
        strong="int per com",
        arts={"In": 8, "Me": 6, "Re": 4, "Vi": 4, "Co": 3},
        abilities={
            "Code of Hermes": (5, "the Peripheral Code"),
            "Folk Ken": (3, "magi"),
            "Intrigue": 2,
            CITY: 2,
        },
        virtues=["Proud (Minor)", "Obsessed (Minor)"],
        age=90,
        native=GREEK,
    ),
}


def stats(theban: Theban) -> None:
    """Generated stats for the magi of Constantinople, none of whom has
    a printed stat block."""
    b = theban.b
    for key, profile in PROFILES.items():
        apply(b, theban.magi[key], profile)
