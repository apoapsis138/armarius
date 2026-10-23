"""The stories (C21) and story seeds (C22), in paraphrase.

Threats with stages, each opening with who drives it, with "if history
holds" years in the stages; chosen on import. Under way in 1220:
world["threat_majlis"] (the Majlis of 1220 and the grand vizier's
succession), ["threat_counter_crusade"] (the Order's counter-crusade
beside the Fifth Crusade), ["threat_nizaris"] (Jalal al-Din Hasan's
alliances and the feud with the Suhhar), ["threat_mecca"] (the Grand
Sharif's succession), ["threat_azi_dahak"] (the demon seeking a new
host, and the Shansabani heir), ["threat_ghur"] (the demons of Ghur
and Kabul), ["threat_merv"] (the race to copy Merv's books) and
["threat_durenmar"] (the apparition at the Grand Tribunal of 1228).
Dormant (threats.DORMANT) until the storyguide begins them:
["threat_itineris_serica"], with Cartophilius of Mercere as a sketch
Hermetic magus of no covenant (people["cartophilius"], type "magus",
house_mercere; C20), and ["threat_iberians"] (the Followers of the
Circle's return).

East.py's world["mongol_conquest"] and ["fifth_crusade"] are shared:
not remade, and their text not changed. `finish` sets the Mongols'
place (Bukhara, or Transoxiana) when no other part has; the Fifth
Crusade's Damietta lies outside this book's lands, so it keeps none
here.

`finish` also puts each story at the place where it plays out, links it
to the records the other parts made (found by key or by name, and
skipped when missing), and adds the book's story seeds (about a
hundred) as one line each under "Story seeds" in the summary (a
neighbour or character) or notes (a covenant or creature) of the record
each hangs on; a seed for the storyguide's eyes goes under that heading
in the record's secrets. A seed whose record is missing, or is one of
east.py's shared records (whose text is not this pack's to change),
goes to its region's place. The saga-shape frames of ch01 stay out
(C21), and so do the six origins for the Mongols, which are the
silk_road part's Genghis Khan's secrets; the seeds the stories above
are built from (a new grand vizier, the Zahhak, saving Merv's books,
the Iberian sahirs, the Mongol threat and the Aquila) are their
stages, not seed lines."""

from __future__ import annotations

import unicodedata
from typing import TYPE_CHECKING, Any

from ...models import Covenant, Creature
from ..builder import Builder, dormant, paragraphs

if TYPE_CHECKING:
    from . import Cradle

S = Builder.stage
DATED = "Fixed dates"
TRACK = "A track"
MERCERE = "house_mercere"


def build(cradle: Cradle) -> None:
    _majlis(cradle)
    _counter_crusade(cradle)
    _nizaris(cradle)
    _mecca(cradle)
    _azi_dahak(cradle)
    _ghur(cradle)
    _merv(cradle)
    _durenmar(cradle)
    _itineris_serica(cradle)
    _iberians(cradle)


# -- under way in 1220 --


def _majlis(cradle: Cradle) -> None:
    cradle.world["threat_majlis"] = cradle.b.threat(
        "The Majlis of 1220 and the Succession",
        antagonist="The viziers who would follow Kha'trazh, and his opponents",
        moves=TRACK,
        summary=paragraphs(
            "Driven by the old grand vizier's mortality and the "
            "ambitions of the viziers around him. Kha'trazh has led the "
            "Order of Suleiman for nearly thirty years and looks fifty, "
            "but he is close to a hundred, and most sahirs expect him "
            "to die soon. Whoever succeeds him decides whether the "
            "Suhhar keeps its cautious peace with the Order of Hermes or "
            "turns its counter-crusade loose.",
            "If he dies between meetings the five Asalat by custom name "
            "the vizier of the Dar al-Hikma to act for him. That is "
            "Niya, Gifted, young, and convinced that only Gifted sahirs "
            "can save a stagnant Order, a view so unpopular that she is "
            "unlikely to keep the seat when the viziers vote. The "
            "campaign will start the day the old man is buried.",
        ),
        stages=[
            S(
                "The Majlis of August",
                at=1,
                clues=(
                    "Viziers gather in Baghdad's summer bazaar for the "
                    "three days of 15 to 17 August 1220. The young "
                    "'Arkhaman comes from Sana'a as a new vizier with an "
                    "Infernal jinni in tow; Nil of Gundeshapur faces "
                    "accusations again; a sahir Kha'trazh expels becomes "
                    "a cause for his rivals."
                ),
                ignored=(
                    "Kha'trazh hears every speaker, keeps his peace with "
                    "the magi, and the factions count their friends for "
                    "next year."
                ),
                stopped="The meeting ends with the grand vizier's authority whole.",
                turned=(
                    "The troupe's own vizier, or a magus sponsored as a "
                    "sahir, wins a voice at the Majlis."
                ),
            ),
            S(
                "Kha'trazh dies",
                at=2,
                clues=(
                    "The grand vizier tires, sleeps through his own "
                    "councils, or is found dead in his chamber; some "
                    "will ask whether he was helped."
                ),
                ignored=(
                    "The Asalat meet and set Niya in his place until the "
                    "next Majlis, and her rivals begin to canvass openly."
                ),
                stopped="A cure or a guardian keeps him alive a few years longer.",
                turned="The troupe chooses whom the Asalat name to act for him.",
            ),
            S(
                "The election",
                at=3,
                clues=(
                    "Candidates court every vizier; one promises to "
                    "restore an expelled favourite, another a war on the "
                    "magi; a Follower of the Stone may try to take his "
                    "family's seat by a test of arms first. All five "
                    "Asalat must be there, and none may stand."
                ),
                ignored=(
                    "A Follower of the Heart is elected by acclaim, and "
                    "the counter-crusade gains or loses a patron by who "
                    "it is."
                ),
                stopped="A candidate who keeps the peace with the magi wins.",
                turned="The troupe's candidate takes the seat, with all it owes.",
            ),
        ],
    )


def _counter_crusade(cradle: Cradle) -> None:
    cradle.world["threat_counter_crusade"] = cradle.b.threat(
        "The Solomonic Counter-Crusade",
        antagonist=(
            "The Followers of the Stone and the Syrian viziers who would "
            "strike at the Levant"
        ),
        moves=TRACK,
        summary=paragraphs(
            "Driven by the Followers of the Stone, whose Asala first named "
            "the crusaders tools of Hell, and by the Syrian viziers. The "
            "Order of Suleiman counts itself still at war with the "
            "Franks and every Hermetic magus among them. While the Fifth "
            "Crusade holds Damietta, its sahirs gather what they can "
            "learn of the Order of Hermes: magi are welcomed in the lands "
            "of Islam, where they are easy to watch and easy to find "
            "again, and are studied for their weak places.",
            "The aim is a blow at the Levant that drives the invading "
            "magi out for good. The sahirs know from the First Crusade "
            "that open battle with magi goes badly for them, so the "
            "attack, when it comes, will use the Magic Realm's roads, "
            "the stars' timing and spirits, not ranks of wizards. "
            "Kha'trazh has so far held it back.",
        ),
        stages=[
            S(
                "Watching the magi",
                at=1,
                clues=(
                    "Hospitable strangers ask a visiting magus about his "
                    "covenant, his sodales and his habits; a summoned "
                    "spirit follows him home; a sahir offers to guide "
                    "him anywhere he likes."
                ),
                ignored=(
                    "The Suhhar learns which covenants of the Levant are "
                    "weakest and when their magi are away."
                ),
                stopped="The spies are found out and the magi warned.",
                turned=("The troupe feeds the watchers what it wants them to believe."),
            ),
            S(
                "Choosing the targets",
                at=2,
                clues=(
                    "Stone viziers press the Majlis for leave to act; "
                    "astrologers look for a favourable conjunction; "
                    "sahirs teach Solomonic magic to soldiers on the "
                    "Syrian front, as the old wazirs once did."
                ),
                ignored="The plan is agreed in private, outside the Majlis.",
                stopped=(
                    "The grand vizier forbids it, or a peace between the "
                    "orders takes its place."
                ),
                turned=(
                    "The blow is turned on the Order's real enemies, the "
                    "Mongols or the Infernal."
                ),
            ),
            S(
                "The strike",
                at=3,
                clues="Spirits mass in the Magic Realm behind a Levantine covenant.",
                ignored=(
                    "A covenant of the Levant is ambushed from the Magic "
                    "Realm, and its Tribunal calls for war on the sahirs."
                ),
                stopped="The attack is beaten off, and the sahirs lose face.",
                turned="The troupe brokers terms before blood is shed.",
            ),
        ],
    )


def _nizaris(cradle: Cradle) -> None:
    cradle.world["threat_nizaris"] = cradle.b.threat(
        "Jalal al-Din Hasan's Alliances and the Feud",
        antagonist="Jalal al-Din Hasan, grand master of Alamut",
        moves=DATED,
        summary=paragraphs(
            "Driven by Jalal al-Din Hasan, who has led the Nizaris since "
            "1210 and has outwardly made them Sunni, which his followers "
            "take for taqiyya. He wants friends against the "
            "Khwarazm-shah: he has bound himself to the rulers of Arran "
            "and Azarbayjan and wed the emir of Gilan's four daughters, "
            "and looks to the caliph in the west and to Genghis Khan in "
            "the east.",
            "The Order of Suleiman has not forgiven Hasan-i Sabbah's "
            "murder of its grand vizier. It calls the Nizaris traitors, "
            "will not treat with them, and hunts known members by "
            "turning the crowd's fear on them; the Nizaris kill sahirs "
            "only when they stand in the imam's way. Each side's losses "
            "have matched the other's for a century, and Nil of "
            "Gundeshapur is suspected of standing too close to them.",
        ),
        stages=[
            S(
                "Envoys to the caliph and the khan",
                year=1220,
                season="Spring",
                clues=(
                    "Nizari envoys travel under false names to Baghdad "
                    "and toward the Mongol camps; the sahirs' astrologers "
                    "and spies mark them."
                ),
                ignored=(
                    "The imam's new friends make the Nizaris harder for "
                    "the Suhhar to touch."
                ),
                stopped="An embassy is waylaid and its letters taken.",
                turned="The troupe carries the imam's word, and his gratitude.",
            ),
            S(
                "The accusations at the Majlis",
                year=1220,
                season="Summer",
                clues=(
                    "Nil's accusers bring word of Nizari visitors to the "
                    "House of Healing."
                ),
                ignored=(
                    "Nil shrugs them off once more, and the feud goes on in the dark."
                ),
                stopped="The truth of Nil's ties comes out and is settled.",
                turned=(
                    "Nil becomes a channel between the two, the first "
                    "parley in a century."
                ),
            ),
            S(
                "The castles fall",
                year=1256,
                clues="If history holds, the Mongols come for the mountain fortresses.",
                ignored=(
                    "The Mongols destroy the Nizari strongholds of "
                    "Persia, Alamut among them."
                ),
                stopped="The sect's secret ways keep a castle or two alive.",
                turned="The sahirs and the Nizaris stand together at last.",
            ),
        ],
    )


def _mecca(cradle: Cradle) -> None:
    cradle.world["threat_mecca"] = cradle.b.threat(
        "The Succession at Mecca",
        antagonist="al-Hasan, son of the Grand Sharif Qatada",
        moves=DATED,
        summary=paragraphs(
            "Driven by al-Hasan, who means to succeed his father Qatada, "
            "Grand Sharif of Mecca since 1201, and will not wait. If "
            "history holds he takes the city this year by killing "
            "Qatada and many of their kin, and the Ayyubid sultan of "
            "Yemen, al-Mas'ud Yusuf, marches in to end the chaos and "
            "rules Mecca by the sword until he dies.",
            "The holy city's Dominion keeps wizards out, but not their "
            "agents, pilgrims or spirits; a sahir or magus who wants a "
            "debt from the next Sharif, or a relic from the Haram, has "
            "this year to earn it.",
        ),
        stages=[
            S(
                "The massacre",
                year=1220,
                season="Summer",
                clues=(
                    "Qatada's sons quarrel openly; al-Hasan gathers "
                    "armed men in the Hijaz; pilgrims hear rumours."
                ),
                ignored="Qatada and many of his family are killed.",
                stopped="The Grand Sharif is warned and lives.",
                turned="The troupe picks the heir who rules.",
            ),
            S(
                "The sultan of Yemen steps in",
                year=1220,
                season="Autumn",
                clues="Al-Mas'ud Yusuf's troops leave Yemen for the north.",
                ignored="Mecca comes under the Ayyubids' military rule.",
                stopped="The Sharifs settle their quarrel before he arrives.",
                turned="The troupe wins the sultan's favour in Mecca.",
            ),
            S(
                "The Sharifs return",
                year=1229,
                clues="If history holds, al-Mas'ud Yusuf dies.",
                ignored="The Grand Sharifs take Mecca back on his death.",
            ),
        ],
    )


def _azi_dahak(cradle: Cradle) -> None:
    cradle.world["threat_azi_dahak"] = cradle.b.threat(
        "Azi Dahak Seeks a Host",
        antagonist="Azi Dahak, Duke of the Spirits of Deceit, and the Shansabani heir",
        moves=TRACK,
        realm="Infernal",
        summary=paragraphs(
            "Driven by Azi Dahak, the three-headed serpent demon who "
            "hates Persia and rules it whenever he finds a willing body. "
            "The one he possesses becomes a Zahhak: a black snake grows "
            "from each shoulder, regrowing however often it is cut, and "
            "hungers for human brains. Mohammed al-Ghuri, the Shansabani "
            "sultan beaten fourteen years ago, was the most recent; another so soon would be unusual, but the demon is "
            "looking.",
            "Some Persian sahirs believe Genghis Khan is a new Zahhak, or "
            "listens to one: the way he has turned on Persia is the "
            "demon's way. The vanished Shansabani, Zahhak's own line, are "
            "rumoured to have an heir at the khan's court. Flame from a "
            "Mazdean temple harms the demon, and the first Zahhak, "
            "chained alive under Mount Damavand and no longer possessed, "
            "may advise those who would fight the next.",
        ),
        secrets=paragraphs(
            "The book leaves it to the troupe whether the demon is behind "
            "the Mongols. If he is, ridding the horde of him can be a "
            "whole saga; if not, he waits for another ruler's ambition.",
        ),
        stages=[
            S(
                "Whispers in the dreams of princes",
                at=1,
                clues=(
                    "Rulers dream of a serpent that promises power; a "
                    "governor grows greedy for conquest past all reason; "
                    "the Shansabani heir is seen among the khan's "
                    "advisers."
                ),
                ignored="The demon chooses his host.",
                stopped="The dreamer is warned, or purified at a fire temple.",
                turned="The troupe sets a trap for the demon in the dreamer.",
            ),
            S(
                "A new Zahhak",
                at=2,
                clues=(
                    "A ruler hides his shoulders; people vanish near his "
                    "palace; he learns sorcery overnight."
                ),
                ignored=(
                    "The Zahhak turns to evil and is taught the dark "
                    "arts, drawing power from other demons."
                ),
                stopped=(
                    "The possession is broken while the host still "
                    "resists, before he embraces evil."
                ),
                turned="The host fights the demon from within, with the troupe's help.",
            ),
            S(
                "The serpent's reign",
                at=3,
                clues="Virtue is mocked at court and cruelty rewarded.",
                ignored=(
                    "Persia falls under a tyrant like the first Zahhak, "
                    "and her sahirs must rise against him."
                ),
                stopped="A hero, perhaps Rostam roused, brings the Zahhak down.",
            ),
        ],
    )


def _ghur(cradle: Cradle) -> None:
    cradle.world["threat_ghur"] = cradle.b.threat(
        "The Demons of Ghur and Kabul",
        antagonist="The demons the Shansabani left behind, and the Shadowed One",
        moves=TRACK,
        realm="Infernal",
        summary=paragraphs(
            "Driven by the familiar demons and evil spirits the "
            "Shansabani abandoned when the Khwarazm-shah drove them out "
            "of Ghur. Malicious jinn haunt its roads, demons in human "
            "shape live in its towns, and in some of them they now rule "
            "openly while the Ghurs watch even their own families for "
            "signs of a stranger behind familiar eyes. No one has "
            "replaced the Shansabani as lords of the province.",
            "To the east, Kabul answers to a demon its people call only "
            "the Shadowed One, unseen even by his subjects, through four "
            "lieutenants with demon-given powers; his hold is tied to "
            "the trade in myrobalan, whose addicts fill the markets. "
            "Ghazni's wealth flows from a False God its people worship "
            "in secret.",
        ),
        stages=[
            S(
                "The roads close",
                at=1,
                clues=(
                    "Caravans through Ghur are lost; myrobalan spreads "
                    "west through the markets of Khurasan."
                ),
                ignored="More of Ghur's towns fall to their demons.",
                stopped="A town is cleansed and its demon driven out.",
            ),
            S(
                "The Shadowed One reaches out",
                at=2,
                clues=(
                    "Myrobalan merchants appear in Herat and Nishapur; "
                    "officials there begin to wear the addicts' stained "
                    "teeth."
                ),
                ignored="Kabul's demon has servants in the cities of Persia.",
                stopped="The trade is broken and the lieutenants unmasked.",
                turned=(
                    "The troupe learns the Shadowed One's name, and with "
                    "it a hold on him."
                ),
            ),
            S(
                "Ghur's demon kingdom",
                at=3,
                clues="The Mongols' coming leaves the province no human lord at all.",
                ignored=(
                    "Ghur becomes a land ruled by demons, a road for "
                    "Hell into the east."
                ),
            ),
        ],
    )


def _merv(cradle: Cradle) -> None:
    cradle.world["threat_merv"] = cradle.b.threat(
        "Saving Merv's Books",
        antagonist="The Mongol horde, and those who would profit from the panic",
        moves=DATED,
        summary=paragraphs(
            "Driven by the sahirs of Merv's house of wisdom, keepers of "
            "the grand vizier Nizam al-Mulk's library of magic, who "
            "learned from the Ghuzz what an invader does to a city. Merv "
            "holds thousands of books that exist nowhere else, in the "
            "'Aziziyah, the Kamaliyah, the Dumayriyah and the college "
            "libraries; the colleges and madrasas will not send them "
            "away, so the sahirs copy all they can before Genghis Khan "
            "comes.",
            "The copying turns up forgotten secrets (the place of "
            "Solomon's Seal, perhaps), tempts the sahirs to steal books "
            "the clerics keep locked away, and puts the best of Nizam "
            "al-Mulk's tomes on the road west, where hostile magicians "
            "wait for them.",
        ),
        stages=[
            S(
                "The copyists at work",
                year=1220,
                season="Spring",
                clues=(
                    "Sahirs buy up paper and ink, hire scribes and "
                    "borrow books they never return; a copied page names "
                    "something no one should know."
                ),
                ignored="A few hundred books are copied in time.",
                stopped="The troupe helps copy or carry the most precious.",
                turned=(
                    "A raid on the Dumayriyah frees a tome of Isma'ili "
                    "theology, and the Nizaris take an interest."
                ),
            ),
            S(
                "The caravan west",
                year=1220,
                season="Autumn",
                clues=(
                    "Nizam al-Mulk's chief tomes leave Merv under guard; "
                    "rival magicians, sahirs or magi, learn the road."
                ),
                ignored="The caravan is robbed, and its magic changes hands.",
                stopped="The books reach a safe house in the west.",
                turned="The troupe's own library is where they come to rest.",
            ),
            S(
                "Merv falls",
                year=1221,
                clues="If history holds, the Mongols come to Khurasan.",
                ignored=(
                    "Merv is sacked and its libraries perish; only what "
                    "was copied or carried away survives."
                ),
            ),
        ],
    )


def _durenmar(cradle: Cradle) -> None:
    cradle.world["threat_durenmar"] = cradle.b.threat(
        "The Apparition at Durenmar",
        antagonist="The Aquila's lost line, or a shaman walking in spirit",
        moves=DATED,
        summary=paragraphs(
            "Driven by whatever has stirred on the Great Steppe, where "
            "the Aquila, the lost second apprentice of Hercynius, was "
            "last seen riding east in the late eleventh century in "
            "search of untouched wilds. As the Mongols lay Transoxiana "
            "waste, ripples of its death and ruin reach the Order of "
            "Hermes: the Primus of Ex Miscellanea dreams strangely, "
            "diviners of several Houses foretell disaster, Tremere's "
            "spies hear of a danger in the east, the Tenens of the East "
            "frets at the chaos beyond the Levant, and even House "
            "Merinita reports new lands and stories stirring in Arcadia.",
            "At the Grand Tribunal of 1228, thirty-three years after the "
            "last, something walks through Durenmar's wards.",
        ),
        secrets=paragraphs(
            "Whether it is the Aquila himself or a shaman of his line "
            "travelling by phantasticum, the book does not say. If his "
            "lineage survived on the steppe, two centuries apart from the "
            "Order, its magic may no longer look Hermetic, its loyalty "
            "may lie with the nomads, and it may have given Parma Magica "
            "to the horde's hedge wizards.",
        ),
        stages=[
            S(
                "Ripples in the West",
                year=1220,
                season="Summer",
                clues=(
                    "Prophecies, dreams and Arcadian turbulence trouble "
                    "the Houses; Tremere puts its intelligence to work."
                ),
                ignored="The Order argues about the east and does nothing.",
                turned="The troupe is sent to see what is happening.",
            ),
            S(
                "The third day of the Grand Tribunal",
                year=1228,
                season="Summer",
                clues=(
                    "The Aegis stands, but a translucent man with a "
                    "legionary standard, or an eagle, or both at once, "
                    "takes shape beside the Praeco."
                ),
                ignored=(
                    "Philipus Niger's attack does nothing; the figure "
                    "looks round in silence and fades. Xavier of "
                    "Mercere, the old archivist, says it looks like the "
                    "lost Aquila."
                ),
                stopped="The spirit is caught or followed home.",
                turned=(
                    "The troupe goes east to find the Aquila's heirs "
                    "before anyone else does."
                ),
            ),
        ],
    )


# -- dormant until the storyguide begins them --


def _itineris_serica(cradle: Cradle) -> None:
    b = cradle.b
    cradle.people["cartophilius"] = b.magus(
        "Cartophilius",
        covenant=None,
        house=MERCERE,
        age=None,
        summary=paragraphs(
            "A magus of Mercere thought odd even by his own House's "
            "lights, son of Geographicus, who helped found an earlier "
            "covenant that travelled. At the last Normandy Tribunal he "
            "proposed another: a band of magi passing as a merchant "
            "caravan, going east to fabled Serica to find where silk "
            "truly comes from, and asking to be funded as a covenant "
            "devoted to research. He belongs to no covenant yet.",
        ),
    )
    cradle.world["threat_itineris_serica"] = dormant(
        b.threat(
            "Itineris Serica",
            antagonist="Cartophilius of Mercere and the Exarch of Tremere",
            moves=TRACK,
            summary=paragraphs(
                "Driven by Cartophilius of Mercere, who wants a covenant "
                "on the move that will cross Asia to Serica and find the "
                "source of silk. Several magi objected that the Order "
                "has never had a Seeker covenant of the kind; to "
                "everyone's surprise the Exarch of House Tremere backed "
                "the plan in full and offered two seasoned Tremere to "
                "ride with it. Whether he believes in it or just wants "
                "somewhere to send the hot-heads of the Burning Acorn "
                "Vexillation, no one is sure.",
                "As companions on the road the book suggests a Trianoma "
                "of the Nestorian faith who spies for her House, a Sufi "
                "master of House Criamon born among the Turks, and a "
                "Merinita of the Levant who knows the jinn. Their way runs "
                "through the lands the Mongols are burning.",
            ),
            stages=[
                S(
                    "Fitting out the caravan",
                    at=1,
                    clues=(
                        "Cartophilius looks for magi, grogs, camels and "
                        "silver; the two Tremere arrive with orders of "
                        "their own."
                    ),
                    ignored="The caravan leaves the west without the troupe.",
                    turned="The troupe joins it, or is it.",
                ),
                S(
                    "Through the war",
                    at=2,
                    clues=(
                        "Caravanserais stand empty, towns are ash, Mongol "
                        "scouts ride the roads, and the sahirs watch the "
                        "foreigners pass."
                    ),
                    ignored=(
                        "The caravan loses beasts and men, and perhaps "
                        "its Tremere, to the war."
                    ),
                    stopped="It reaches Badakhshan intact.",
                ),
                S(
                    "The Faerie road",
                    at=3,
                    clues=(
                        "Up the Wakhan the Faerie aura climbs with every "
                        "day's march, and side paths open into regiones."
                    ),
                    ignored="Some of the company stray into Arcadia and stay.",
                    turned="The road leads beyond the Order's maps, toward Serica.",
                ),
            ],
        )
    )


def _iberians(cradle: Cradle) -> None:
    cradle.world["threat_iberians"] = dormant(
        cradle.b.threat(
            "The Followers of the Circle Return",
            antagonist="Young Hermetic sahirs of Iberia",
            moves=TRACK,
            summary=paragraphs(
                "Driven by younger Hermetic sahirs of Iberia, heirs of "
                "the Followers of the Circle who left the Suhhar in the "
                "tenth century and joined the Order of Hermes. Their "
                "Solomonic magic has faded under the Code, but not the "
                "memory of where it came from, and they hate the "
                "Christian kingdoms' reconquest of al-Andalus. They may "
                "look east to their lost brethren for help or magical "
                "weapons against the heirs of Alfonso the Battler and "
                "the followers of Flambeau.",
                "If the Order of Suleiman takes a hand in Iberia's wars, "
                "peace between the two orders may be out of reach for "
                "decades.",
            ),
            stages=[
                S(
                    "An Iberian at the Majlis",
                    at=1,
                    clues=(
                        "A sahir from Iberia comes to Baghdad speaking "
                        "for a community outside the Order of Hermes, "
                        "reminds the viziers that another crusade "
                        "threatens Islam in the west, and asks them to "
                        "restore the old alliance."
                    ),
                    ignored="The viziers argue, and some promise help in secret.",
                    stopped="The Majlis refuses him.",
                    turned="The troupe carries word between east and west.",
                ),
                S(
                    "Weapons for al-Andalus",
                    at=2,
                    clues=(
                        "Solomonic devices and bound spirits turn up in "
                        "Iberian battles; House Flambeau notices."
                    ),
                    ignored=(
                        "The Order of Hermes blames the Hermetic sahirs, "
                        "and Iberia's Tribunal splits."
                    ),
                    stopped="The trade is uncovered before blood is shed.",
                ),
                S(
                    "Two orders at war",
                    at=3,
                    clues="Wizard Wars are declared in Iberia over sahir aid.",
                    ignored=(
                        "The Suhhar and the Order of Hermes fight in the "
                        "west as well as the east."
                    ),
                    turned="A settlement brings the Iberians home to one order or the other.",
                ),
            ],
        )
    )


# -- finishing: places, links and seeds --

#: A record a link or seed may land on: its kind ("covenant", "person",
#: "creature", "place" for places, "world" for the other neighbours),
#: its key in that dict, and names it may go by.
Target = tuple[str, ...]


def _key(name: str) -> str:
    """A name compared loosely: case, accents, hyphens, apostrophes and a
    leading 'The' set aside."""
    out = unicodedata.normalize("NFKD", name.casefold().strip())
    out = "".join(c for c in out if not unicodedata.combining(c))
    out = out.removeprefix("the ")
    for mark in ("-", "_", "'", "’", "‘"):
        out = out.replace(mark, " " if mark in "-_" else "")
    return " ".join(out.split())


def _named(records: list[Any], names: tuple[str, ...]) -> Any | None:
    """The first record whose name is one of `names`, or failing that
    whose name starts with one of them as a whole word, loosely
    compared."""
    if not names:
        return None
    wanted = [_key(n) for n in names]
    for record in records:
        if _key(record.name) in wanted:
            return record
    for record in records:
        name = _key(record.name)
        if any(name.startswith((n + " ", n + ",")) for n in wanted):
            return record
    return None


#: The records east.py shares with other packs: their text is never
#: changed here, so a seed that hangs on one goes to its region instead.
SHARED = frozenset(
    {
        "iraq",
        "georgia",
        "greater_armenia",
        "jinnistan",
        "qaf",
        "harut_and_marut",
        "order",
        "stone",
        "river",
        "jinn",
        "baghdad",
        "mosul",
        "caliph",
        "al_kamil",
        "al_aziz",
        "lord_of_mosul",
        "king_of_georgia",
        "nizaris",
        "imam",
        "sultan_of_rum",
        "emperor_of_trebizond",
        "fifth_crusade",
        "mongol_conquest",
        "al_khidr",
    }
)


def _lookup(cradle: Cradle, target: Target) -> Any | None:
    """The record a target names, or None when no part has made it."""
    kind, key, *names = target
    saga = cradle.b.saga
    if kind == "covenant":
        return cradle.covenants.get(key) or _named(saga.covenants, tuple(names))
    if kind == "person":
        return cradle.people.get(key) or _named(saga.characters, tuple(names))
    if kind == "creature":
        return cradle.creatures.get(key) or _named(saga.creatures, tuple(names))
    found = (cradle.places if kind == "place" else cradle.world).get(key)
    return found or _named(saga.neighbours, tuple(names))


def _shared_ids(cradle: Cradle) -> set[str]:
    """The ids of the shared records this pack holds."""
    return {found.id for key in SHARED if (found := cradle.find(key)) is not None}


def _c(key: str, *names: str) -> Target:
    return ("covenant", key, *names)


def _m(key: str, *names: str) -> Target:
    return ("person", key, *names)


def _k(key: str, *names: str) -> Target:
    return ("creature", key, *names)


def _p(key: str, *names: str) -> Target:
    return ("place", key, *names)


def _w(key: str, *names: str) -> Target:
    return ("world", key, *names)


ARABIA = _p("arabia", "Arabia")
MESOPOTAMIA = _p("mesopotamia", "Mesopotamia")
PERSIA = _p("persia", "Persia")
SILK_ROAD = _p("silk_road", "The Silk Road")

#: Each story's place: the first target found, a covenant giving its own
#: site.
PLACES: dict[str, tuple[Target, ...]] = {
    "threat_majlis": (_p("majlis_hall"), _w("baghdad"), MESOPOTAMIA),
    "threat_counter_crusade": (_w("baghdad"), MESOPOTAMIA),
    "threat_nizaris": (_p("alamut", "Alamut"), _p("daylam", "Daylam"), PERSIA),
    "threat_mecca": (_w("mecca", "Mecca"), _p("hijaz", "The Hijaz"), ARABIA),
    "threat_azi_dahak": (
        _p("damavand", "Mount Damavand", "Damavand"),
        _p("mazandaran", "Mazandaran"),
        PERSIA,
    ),
    "threat_ghur": (_p("ghur", "Ghur"), PERSIA),
    "threat_merv": (_w("merv", "Merv"), _p("khurasan", "Khurasan"), PERSIA),
    "threat_durenmar": (_p("great_steppe", "The Great Steppe"), SILK_ROAD),
    "threat_itineris_serica": (_p("wakhan", "The Wakhan"), SILK_ROAD),
    "threat_iberians": (_p("majlis_hall"), _w("baghdad"), MESOPOTAMIA),
}

#: The shared threats' places, set only when no part has set one.
SHARED_PLACES: dict[str, tuple[Target, ...]] = {
    "mongol_conquest": (
        _w("bukhara", "Bukhara"),
        _p("transoxiana", "Transoxiana"),
        SILK_ROAD,
    ),
}

#: The links `finish` makes where the other parts made the target:
#: (story, link kind, the target, note).
LINKS: tuple[tuple[str, str, Target, str], ...] = (
    ("threat_majlis", "characters", _m("khatrazh"), "The ageing grand vizier"),
    (
        "threat_majlis",
        "characters",
        _m("niya"),
        "Would act for him; unlikely to keep it",
    ),
    ("threat_majlis", "characters", _m("arkhaman"), "A new vizier this summer"),
    ("threat_majlis", "characters", _m("nil"), "Accused again"),
    ("threat_majlis", "characters", _m("meriq"), "An Asala; votes"),
    ("threat_majlis", "covenants", _c("dar_al_hikma"), "Its vizier acts by custom"),
    ("threat_majlis", "places", _w("order"), "Whose grand vizier it is"),
    ("threat_majlis", "places", _w("heart"), "The family of most grand viziers"),
    ("threat_majlis", "places", _w("stone"), "Picks its Asala by a test of arms"),
    ("threat_majlis", "places", _p("majlis_hall"), "Where it meets"),
    ("threat_counter_crusade", "places", _w("order"), "Plans it"),
    ("threat_counter_crusade", "places", _w("stone"), "Drives it"),
    ("threat_counter_crusade", "places", _w("fifth_crusade"), "What it answers"),
    ("threat_counter_crusade", "places", _p("island_fortress"), "Where war is talked"),
    ("threat_counter_crusade", "characters", _m("khatrazh"), "Holds it back"),
    ("threat_nizaris", "places", _w("nizaris"), "The sect"),
    ("threat_nizaris", "places", _w("imam"), "Its master"),
    ("threat_nizaris", "places", _w("order"), "Its old enemy"),
    (
        "threat_nizaris",
        "places",
        _w("emir_of_gilan", "Emir of Gilan"),
        "His father-in-law",
    ),
    ("threat_nizaris", "places", _w("atabeg_uzbek", "Atabeg Uzbek"), "An ally"),
    ("threat_nizaris", "places", _w("khwarazm_shah"), "The enemy he courts against"),
    ("threat_nizaris", "places", _w("caliph"), "A friend he seeks"),
    (
        "threat_nizaris",
        "places",
        _w("genghis_khan", "Genghis Khan"),
        "A friend he seeks",
    ),
    ("threat_nizaris", "places", _p("alamut", "Alamut"), "His seat"),
    ("threat_nizaris", "characters", _m("nil"), "Suspected of ties"),
    ("threat_mecca", "places", _w("sharif"), "The Grand Sharif"),
    ("threat_mecca", "places", _w("al_masud"), "Steps in"),
    ("threat_mecca", "places", _w("mecca", "Mecca"), "The city"),
    ("threat_mecca", "places", _p("mecca_haram"), "The Haram"),
    ("threat_azi_dahak", "creatures", _k("azi_dahak"), "The demon"),
    ("threat_azi_dahak", "places", _w("shansabani"), "Zahhak's line; an heir at court"),
    ("threat_azi_dahak", "places", _w("genghis_khan", "Genghis Khan"), "A Zahhak?"),
    ("threat_azi_dahak", "places", _w("mazdeans"), "Their fire harms him"),
    (
        "threat_azi_dahak",
        "places",
        _p("damavand", "Mount Damavand"),
        "The first Zahhak",
    ),
    ("threat_azi_dahak", "places", _w("yatus"), "Guard a rite against Persia's foes"),
    ("threat_ghur", "places", _p("ghur", "Ghur"), "Its haunted towns"),
    ("threat_ghur", "places", _w("kabul", "Kabul"), "The Shadowed One's city"),
    ("threat_ghur", "places", _w("ghazni", "Ghazni"), "Its False God"),
    ("threat_ghur", "places", _w("shansabani"), "Left the demons behind"),
    ("threat_merv", "covenants", _c("bayt_merv"), "Copies the books"),
    ("threat_merv", "places", _w("merv", "Merv"), "Its libraries"),
    ("threat_merv", "places", _w("mongol_conquest"), "What is coming"),
    ("threat_merv", "places", _w("nizaris"), "Want a tome of their theology"),
    ("threat_durenmar", "places", _w("mongol_conquest"), "The ruin in the east"),
    ("threat_durenmar", "creatures", _k("steppe_spirits"), "The steppe's spirits"),
    ("threat_durenmar", "creatures", _k("spirit_shaman"), "A walker in spirit?"),
    (
        "threat_itineris_serica",
        "characters",
        _m("cartophilius"),
        "Proposes it",
    ),
    ("threat_itineris_serica", "places", _p("wakhan", "The Wakhan"), "The road east"),
    ("threat_itineris_serica", "places", _w("mongol_conquest"), "In its path"),
    ("threat_iberians", "places", _w("circle"), "The Followers of the Circle"),
    ("threat_iberians", "places", _w("order"), "Asked to help"),
    ("threat_iberians", "places", _p("majlis_hall"), "Where the plea is heard"),
)


#: The book's story seeds: (targets, title, text, for the storyguide
#: alone). Each goes on the first of its targets that exists and is not
#: shared, or else on the last target, its region.
SEEDS: tuple[tuple[tuple[Target, ...], str, str, bool], ...] = (
    # -- ch01 to ch03: the Order and the old caliphate --
    (
        (MESOPOTAMIA,),
        "The Unholy Trinity",
        "Mahound, Termagant and Apollyon, the three gods Europe wrongly "
        "thinks the Muslims worship, are real demons of the False Gods "
        "who stir up hatred between Christian and Muslim wherever they "
        "can; a troupe with friends of both faiths may spend a saga "
        "hunting them.",
        False,
    ),
    (
        (MESOPOTAMIA,),
        "Disputes over the Caliphate",
        "the 'Abbasids missed at least one Umayyad, and perhaps more; a "
        "hidden heir of that house, or a Shi'i claimant, asks the "
        "characters to help him to the throne, with an old relic or a "
        "power of his own to make the request hard to refuse.",
        False,
    ),
    (
        (_p("babylon", "Babylon", "The Ruins of Babylon"), MESOPOTAMIA),
        "The Sacred Vessels",
        "the Temple vessels Belshazzar drank from may never have gone "
        "back to Jerusalem; turned Infernal, they pass from owner to "
        "ruined owner, or, still holy, they wait in Babylon's ruins for "
        "someone worthy.",
        False,
    ),
    (
        (_m("khatrazh"), _p("majlis_hall"), MESOPOTAMIA),
        "A Test of Arms",
        "the Followers of the Stone choose their Asala by combat, and a "
        "vengeful sahir who hates Kha'trazh may challenge his own family's "
        "head to win the seat and a vote against him.",
        False,
    ),
    (
        (_m("khatrazh"), _p("majlis_hall"), MESOPOTAMIA),
        "The Vizier's Opposition",
        "Kha'trazh expels a well-loved sahir accused of betraying the "
        "Suhhar, and the leader of his opponents promises to bring the "
        "exile back in exchange for votes.",
        False,
    ),
    (
        (_w("circle"), _p("majlis_hall"), MESOPOTAMIA),
        "The Sixth Asala",
        "sahirs outside the five families demand a sixth seat among the "
        "Asalat, and take a six-pointed star as their sign.",
        False,
    ),
    (
        (_p("majlis_hall"), MESOPOTAMIA),
        "The Sahir-Magus",
        "a magus who can summon spirits is admitted to the Suhhar and "
        "offers to speak for his sodales; that threatens Kha'trazh's "
        "policy of avoiding a fight with the Order of Hermes, and he may "
        "quietly urge other sahirs to challenge the newcomer to a duel.",
        False,
    ),
    (
        (_w("heart"), MESOPOTAMIA),
        "The Lady of the Vanished Chamber",
        "sahirs who feel for spirits sense a woman's presence in "
        "Al-Khayzuran's old room in what was Harun's palace, and many "
        "dream of her; perhaps the tales told of her have drawn a faerie "
        "queen to live there, who trades power to sleepers for stories.",
        False,
    ),
    (
        (_c("dar_al_hikma"), MESOPOTAMIA),
        "Yahya's Connections",
        "Yahya the Barmakid is said to have kept lasting Arcane "
        "Connections to every member of the First Council; they may lie "
        "in his grave in Baghdad, in his house, or in his cell in the "
        "abandoned prison, which has an evil name.",
        False,
    ),
    (
        (_c("dar_al_hikma"), MESOPOTAMIA),
        "The Two Wanderers",
        "Al-Zill Habib and Al-Hajjaj left Baghdad in the mid-800s after a "
        "visit from the Sufi Fozail-e Iyaz and told their pupils not to "
        "follow; travellers still share meals with a young man in white "
        "and a hooded companion in black who seem not to have aged in "
        "four centuries.",
        False,
    ),
    (
        (_w("star"), MESOPOTAMIA),
        "The Astrologer's Spirit",
        "many sahirs think al-Fazari never died but became a spirit, as "
        "his father did; whoever could summon him would learn what his "
        "prophetic pictures foretold, but no one has shown they can.",
        False,
    ),
    (
        (_w("hand"), PERSIA),
        "A Son in the Far East",
        "some say one of Jabril ibn Bakhtyshu's sons went east with the "
        "miracle-worker Dawud al-Kharita and began a line of Christian "
        "magician-kings that would give the world Prester John.",
        False,
    ),
    # -- ch04: the jinn --
    (
        (ARABIA,),
        "The List of Suleiman",
        "Solomon is said to have written down the True Name of every "
        "jinni in a book that amends itself as jinn are born and die; "
        "sahirs claim to have found its pages bound into other books of "
        "Lore, where old names come and go between readings, though "
        "whether these are true fragments or faerie forgeries no one "
        "knows.",
        False,
    ),
    (
        (MESOPOTAMIA,),
        "The Corruption of the West",
        "almost every Infernal being of these lands is a jinni, and so "
        "open to Sihr; but Europe's demons have followed the Crusades "
        "into Outremer, and as merchants, missionaries and magi travel "
        "further east they will bring their own sins and devils with "
        "them, the Unholy Trinity among them.",
        False,
    ),
    (
        (MESOPOTAMIA,),
        "The Dark Sufis",
        "a heretical Sufi path honours Iblis for refusing to bow to Adam, "
        "taking it for love of God alone: unwitting diabolists, one of "
        "whom poses as a holy man to lead a Criamon magus astray.",
        False,
    ),
    (
        (_k("qareen"), MESOPOTAMIA),
        "A Pious Companion?",
        "a character of rare piety may persuade a dark Faerie qareen to "
        "submit to Islam and become a guardian, easy to mistake for an "
        "angel; an Infernal qareen is a true demon and can never be "
        "redeemed.",
        False,
    ),
    (
        (_k("qareen"), MESOPOTAMIA),
        "An Unwanted Guest",
        "a magus newly come to the east finds a Faerie qareen has "
        "attached itself to him, unbeliever though he is; mastering it "
        "is reason enough for the Suhhar, and an open-minded group of "
        "sahirs sends him a courteous invitation to join.",
        False,
    ),
    # -- ch05: the Mazdeans --
    (
        (_p("transoxiana", "Transoxiana"), SILK_ROAD),
        "The Accursed Turanians",
        "the Turanians, a once-holy tribe led astray by Hell, made war on "
        "the Iranians, and the soldier who killed Zoroaster raised the "
        "fortress Arvandasp by sorcery; their Infernal relics, the "
        "prophet's death-blade among them, may still lie north of the "
        "Oxus.",
        False,
    ),
    (
        (_w("mazdeans"), PERSIA),
        "The Demon-Blooded Paladins of Manochir",
        "Alexander broke up the paladins of Manochir, tried to end the "
        "line of a white-haired, demon-blooded son of their greatest "
        "knight, and buried their arms in the desert, a mace said to "
        "fell an elephant at one blow and a belt that kept its wearer "
        "from harm; a cache of them would be a prize, if untainted.",
        False,
    ),
    (
        (_w("mazdeans"), PERSIA),
        "A Heretical Revival",
        "a Hermetic follower of the Cult of Mithras finds scrolls in a "
        "European Mithraeum tying his cult to the Mazdeans and hinting "
        "where in Persia Mithras was born; how will he take a living "
        "faith that counts Mithras a divine spirit?",
        False,
    ),
    # -- ch06: Arabia --
    (
        (_k("zawbaa"), ARABIA),
        "Death by Zawba'a?",
        "a man is found flayed in a room dusted with fine sand; the "
        "trail leads to a secret circle of sahirs from a minor sect who "
        "have learned to bind the whirlwind jinn and loose them on "
        "their political enemies.",
        False,
    ),
    (
        (_p("najd", "The Najd"), ARABIA),
        "The Stone Lovers",
        "wizards who settle by two man-shaped rocks in a remote Magic "
        "aura offend the Bedouin, who count the stones as kin: the "
        "giant lovers Aja and Salma, banished there for five hundred "
        "years; dark jinn haunt the rocks by night, and too much magic "
        "may wake the giants.",
        False,
    ),
    (
        (_p("lukmans_nest", "The Nest of Lukman's Falcons"), _p("hijaz"), ARABIA),
        "The Seven Falcons of Lukman",
        "Lukman of 'Ad stayed young through the lives of seven falcons "
        "from one nest, each living eighty years; the nest lies in a "
        "Magic regio after a hard climb in western Arabia, and a fledgling "
        "raised there spares its trainer all Aging rolls for eighty "
        "years, at a Warping Point a year and a quick ageing when it "
        "dies.",
        False,
    ),
    (
        (_w("tayma", "Tayma'"), _w("khaybar", "Khaybar"), ARABIA),
        "The Jews of Tayma' and Khaybar",
        "the Jewish towns can raise fierce armies in days, allies worth "
        "having against a sudden host, but their elders distrust magic "
        "and must be convinced that the characters' cause is just.",
        False,
    ),
    (
        (_p("bahrayn", "Bahrayn"), ARABIA),
        "The Fate of the Black Stone",
        "while the Qarmatians held it, a renegade sahir stole the Black "
        "Stone for a ritual of unknown purpose and was killed at great "
        "cost, the stone broken in seven; now he has been seen again, "
        "and the heirs of those who fought him are dying one by one.",
        False,
    ),
    (
        (_w("hajar", "Hajar"), _p("hajar", "Hajar"), ARABIA),
        "The Ghosts of Hajar",
        "a child is lost in Hajar's streets at night, and the local "
        "sahirs, who cannot command the dead, ask for help before the "
        "ghostly soldiers find it; laying the ghosts and lifting the "
        "curse could become a long tale.",
        False,
    ),
    (
        (_p("empty_quarter", "The Empty Quarter"), ARABIA),
        "The Valuable Quarter",
        "local sahirs call the Empty Quarter the Valuable Quarter, for "
        "the Twilight Void and the Magic Realm are easy to enter there "
        "and rich in vis; coming back is far harder, and those who do "
        "return changed, some even initiated into Sihr and never trusted "
        "again. The Primi of Criamon and Merinita, at odds over what "
        "lies at its heart, are recruiting young magi for a joint "
        "expedition.",
        False,
    ),
    (
        (_w("medina", "Medina"), _p("medina_haram"), ARABIA),
        "The Lava Flows of Medina",
        "the earthquakes that crack the old lava fields round Medina are "
        "no accident but the work of enemies trying to melt them again "
        "and drown the holy city in fire.",
        False,
    ),
    (
        (_w("mecca", "Mecca"), _p("mecca_haram"), ARABIA),
        "The Lost Lords of Mecca",
        "the Jurhumites, jann-blooded lords of Mecca before Islam, live "
        "on as dark Faerie jinn with a few jinn-blooded sahirs adopted "
        "into the clan; they know secret ways into the closed cities and "
        "may court magi in their feud with Mecca's rulers. Are they "
        "behind Medina's lava, or scapegoats for renegade sahirs?",
        False,
    ),
    (
        (_p("zamzam", "Zamzam"), _p("mecca_haram"), ARABIA),
        "The Restoring Waters of Zamzam",
        "on the night Ramadan ends the Divine aura at the well dips and "
        "its water can be drawn by moonlight as Aquam vis; each mouthful "
        "restores all lost Fatigue, and magi may covet it as a path to "
        "an Insight on the Limit of Energy.",
        False,
    ),
    (
        (_p("zamzam", "Zamzam"), _p("mecca_haram"), ARABIA),
        "The Marid of the Well",
        "the marid Zamzam lies in a smothered Magic regio at the foot of "
        "the well, keeping its water pure and hating the Dominion that "
        "holds it; it knows things of the distant past no one else "
        "does, but how could anyone speak with it unseen in Islam's "
        "holiest shrine, and what would it do if freed?",
        True,
    ),
    (
        (_p("mosque_of_the_jinn", "The Mosque of the Jinn"), ARABIA),
        "The Mosque of the Jinn",
        "a Merinita magus hires the characters to study the faeries who "
        "worship there without making a Divine aura; the jinn, who feed "
        "on human prayer, resent being watched rather than joined.",
        False,
    ),
    (
        (_p("abqar", "The Valley of 'Abqar", "'Abqar"), ARABIA),
        "Poets and Qareen",
        "the 'abqari, poets with an artistic qareen, can lampoon their "
        "foes into misfortune; a journey to 'Abqar may be part of a "
        "Merinita Keepers of Tales initiation, or draw Jerbiton and "
        "Redcaps who love the Thousand and One Nights.",
        False,
    ),
    (
        (_p("ukaz", "'Ukaz"), _w("ukaz", "'Ukaz"), _p("hijaz"), ARABIA),
        "The Poetry Festival at 'Ukaz",
        "each year a tribe of jinn sponsors the old poetry contest at "
        "'Ukaz between Mecca and Medina, and the prize changes: the way "
        "to 'Abqar, kinship with the tribe forever, or a young jinni's "
        "service; magi and sahirs come to compete.",
        False,
    ),
    (
        (_w("daughters_cult", "The Cult of the Daughters"), _w("taif"), ARABIA),
        "Farida's Fears",
        "the Cult of the Daughters finds al-Manat's sanctuary and begins "
        "a three-part rite that may bring back the goddesses or harm the "
        "Ka'ba; Farida, the family's newest member, has doubts, and may "
        "fear the child she carries is meant to replace her.",
        False,
    ),
    (
        (_w("sanaa", "Sana'a"), ARABIA),
        "The Food of Sana'a",
        "a cooking pot from Sana'a carries a hedge enchantment that makes "
        "every meal delicious and slowly Warps whoever eats from it; if "
        "such pots are common the whole town may be Warping unawares, "
        "and someone made them.",
        False,
    ),
    (
        (_p("marib", "Ma'rib"), _p("ghumdam", "Ghumdam"), _p("yemen"), ARABIA),
        "King Suleiman and the Queen of Sheba",
        "Sheba's sun-worship may survive at Ma'rib, its gods faeries or "
        "demons posing as a heavenly trinity; the mukkaribs' magic may "
        "have commanded celestial spirits; the hoopoe's kin could guide "
        "or serve; the queen's throne and glass hall may still be "
        "somewhere; and perhaps Suleiman and the queen never died.",
        False,
    ),
    (
        (_k("nisnas"), ARABIA),
        "An Escaped Nisnas",
        "a fleeing nisnas begs the characters to save it from the people "
        "who mean to eat it; it is half a man, but has it a soul?",
        False,
    ),
    (
        (
            _p("trees_that_cry_blood", "The Trees That Cry Blood"),
            _p("hadramawt", "Hadramawt"),
            ARABIA,
        ),
        "The Trees That Cry Blood",
        "five old trees in Hadramawt's coastal hills give frankincense "
        "holding Rego Terram vis when tapped in a storm, guarded by fierce "
        "flying serpents that ignore storax smoke and wards; rivals soon "
        "learn of the harvest, and too much magic may wake the trees "
        "themselves.",
        False,
    ),
    (
        (_p("ubar", "Ubar", "Iram"), ARABIA),
        "Discovering the Lost City",
        "a map, a survivor's descendant or a fall through dry quicksand "
        "leads to Iram whole in a cavern under the sands, full of riches "
        "and dried corpses, strong in Magic and built for giants twelve "
        "yards tall: a covenant site, if the last stonesmith giants of "
        "'Ad allow it.",
        False,
    ),
    (
        (_w("witches_of_nizwa", "The Witches of Nizwa"), _w("nizwa"), ARABIA),
        "The Witches of Nizwa",
        "the witches may be Infernalists, faerie wizards, exiled "
        "Soqotran witches, agents of the Olibanum King working against "
        "the Suhhar, or heirs of Sheba's astral sorceresses; or the "
        "rumours may be false, which matters if the characters want a "
        "covenant nearby.",
        False,
    ),
    # -- ch07: Mesopotamia --
    (
        (_w("samarra", "Samarra"), MESOPOTAMIA),
        "A Samarran Covenant",
        "the sprawling half-ruined palaces may hide Magic auras and "
        "devices left by the caliphs' sorcerers, and the wells and canals "
        "still work: a covenant site, if the townsfolk will have foreign "
        "wizards.",
        False,
    ),
    (
        (_w("golden_court"), _p("golden_baghdad", "Golden Baghdad"), MESOPOTAMIA),
        "The Wandering Caliph",
        "for four centuries sahirs have told of meeting Harun al-Rashid "
        "with his vizier and executioner, a chance talk with three "
        "strangers that ends in Golden Baghdad; they think him the "
        "faerie city's ruler, choosing guests for what they can add to "
        "it.",
        False,
    ),
    (
        (_p("ctesiphon", "Ctesiphon"), _w("al_madain"), MESOPOTAMIA),
        "The Ruined Palace",
        "the great arch over the Persian emperors' throne room at "
        "Ctesiphon draws students of Hermetic Architecture, perhaps as "
        "an initiation task, though the locals eye foreigners digging in "
        "the ruins.",
        False,
    ),
    (
        (_p("dayr_al_aqul", "Dayr al-'Aqul"), _w("al_madain"), MESOPOTAMIA),
        "The Enemies of Dayr al-'Aqul",
        "someone is turning the Tigris, and the monks of Dayr al-'Aqul "
        "rescue the characters from its sudden shift: the sahirs of Dayr "
        "Qunna, who dislike the Dominion near them, or a spirit too strong "
        "for them, or Dayr Hizqil's monks after the river toll, or one of "
        "Hizqil's madmen (a sahir Dayr Qunna left there, his mind blasted "
        "by what he called), or a sorcerer feigning madness, or a demon "
        "or faerie enjoying it all.",
        False,
    ),
    (
        (_p("ubulla", "Ubulla"), MESOPOTAMIA),
        "The Whirlpool at Ubulla",
        "the jinni chained on the riverbed is not dead, and sorcerers mean "
        "to free it as a weapon against the caliph; stop them directly, "
        "or warn the caliph while they work?",
        False,
    ),
    (
        (_w("basra", "Basra"), MESOPOTAMIA),
        "The Thief of Basra",
        "a man caught stealing books of lore from Basra's library swears "
        "a sorcerer holds his family; the qadi gives the characters a "
        "week to prove it before the hand comes off, unless the thief "
        "lied and slips away while they look.",
        False,
    ),
    (
        (_p("nimrods_furnace", "Nimrod's Furnace"), _p("kutha", "Kutha"), MESOPOTAMIA),
        "Nimrod's Furnace",
        "God's rescue of Abraham made the furnace holy and shut its fire "
        "demon inside; a corrupt cabal would light it again by weakening "
        "Kutha's faith and burning holy men in it.",
        False,
    ),
    (
        (_w("hilla", "Hilla"), MESOPOTAMIA),
        "The Scholars of Hilla",
        "a crippled Shi'i sahir sends the characters to Hilla with "
        "questions for the scholar Muhammad ibn Muhammad, and they find "
        "three of that name who loathe one another; getting all three "
        "answers without offending any takes tact.",
        False,
    ),
    (
        (_p("uruk", "Uruk"), MESOPOTAMIA),
        "In Enkidu's Place",
        "those who step through the temple door at Uruk find Gilgamesh, "
        "who wants one of them to be his Enkidu and sends them into the "
        "wild to wait for Shamhat.",
        False,
    ),
    (
        (_p("ighraq_gorge"), _k("ighraq"), MESOPOTAMIA),
        "The Jinni Block",
        "Ighraq al-Siq sleeps in a tower tomb of stone at the gorge, "
        "loosed when intruders trip some unknown trigger; whoever stands "
        "on the block may try to command him with Sihr or scouring, but "
        "a failed attempt frees him, angry.",
        False,
    ),
    (
        (_w("kufa", "Kufa"), MESOPOTAMIA),
        "The House of Ibn Muljam",
        "the poisoned sword that killed 'Ali lies buried in a Kufa house "
        "where his murderer hid, tainting it and binding his ghost there; "
        "a friend who has bought the house asks for help, and by the time "
        "the characters arrive the ghost has possessed him.",
        False,
    ),
    (
        (_p("jazira", "The Jazira"), MESOPOTAMIA),
        "Tensions in Mosul",
        "a wizard with the Blatant Gift who went to find a magical cause "
        "for Mosul's famed kindness has turned its people against one "
        "another instead, and needs mediators while he undoes his "
        "meddling.",
        False,
    ),
    (
        (_p("barqaid", "Barqa'id"), _p("jazira"), MESOPOTAMIA),
        "Against the City of Thieves",
        "the characters beat off raiders from Barqa'id, and the grateful "
        "village that saw it expects them to destroy the robbers' town.",
        False,
    ),
    (
        (_w("nasibin", "Nasibin"), _p("jazira"), MESOPOTAMIA),
        "The Battle for Nasibin",
        "the roses and the scorpions of Nasibin are the outward signs of "
        "a stalemate between an angel and a demon fighting for its souls; "
        "either may ask the characters' help, and the demon may pass "
        "itself off as the angel.",
        False,
    ),
    (
        (_w("amid", "Amid"), _p("jazira"), MESOPOTAMIA),
        "The Death of Tenik",
        "Amid's faeries re-enact the old raid of Tigran and Vasdes but "
        "cannot end it, for no one remembers that Tenik died between the "
        "warbands to stop the fight; the faerie host grows with the city, "
        "and someone must play Tenik without dying.",
        False,
    ),
    (
        (_p("siffin", "Siffin"), _p("jazira"), MESOPOTAMIA),
        "The Dead of Siffin",
        "one of the dead at Siffin looks like a character's ancestor, "
        "hinting at unknown kin or a magical line, or like someone still "
        "alive, perhaps a warning; finding out means a closer look at a "
        "grave others would not want disturbed.",
        False,
    ),
    (
        (_w("harran", "Harran"), _w("sabians"), MESOPOTAMIA),
        "The Heat Is On",
        "the Sabian magi left in Harran are making the town hotter to "
        "drive its people out so they can dig for their tradition's "
        "treasures and revive their cult; magi may sympathise, or seek a "
        "compromise.",
        False,
    ),
    (
        (_w("edessa", "Edessa"), _p("jazira"), MESOPOTAMIA),
        "The Holy Mandylion",
        "the Image of Edessa is held by Otto de la Roche, Duke of Athens, "
        "excommunicated and all but invincible with it; an Armenian lord "
        "or magus, or an evil threatening Edessa, sends the characters "
        "to bring it home.",
        False,
    ),
    (
        (_p("sanjah_bridge", "The Sanjah Bridge"), _p("jazira"), MESOPOTAMIA),
        "The Missing Talisman",
        "the talisman set in the bridge's crown has been stolen and the "
        "bridge is crumbling far too fast; the villages that need it ask "
        "the characters to find the thief and restore its power in time.",
        False,
    ),
    (
        (_w("brass_smiths"), _w("arzanjan", "Arzanjan"), MESOPOTAMIA),
        "To Learn the Craft",
        "a Verditius magus wants the brass-smiths' secret and urges a "
        "character to be initiated into the guild, which means "
        "convincing its elders their Mystery will not be spread abroad.",
        False,
    ),
    (
        (_p("lake_urmiya", "Lake Urmiya"), _p("azarbayjan"), MESOPOTAMIA),
        "The Sorcerer's Tower",
        "the lonely tower by Lake Urmiya would make a covenant, or an "
        "old-fashioned delve: the sorcerer who bred the lake's dog-fish "
        "surely left other hybrids in it and the tunnels below.",
        False,
    ),
    (
        (_w("maragha", "Maragha"), _p("azarbayjan"), MESOPOTAMIA),
        "Dim Skies and Rotten Fruit",
        "clouds gather over Maragha, which never sees them, and the "
        "melons rot overnight: the spirit that kept the town prosperous "
        "has turned against it, and someone must learn why and make "
        "amends.",
        False,
    ),
    (
        (_w("barvan", "Barvan"), _p("azarbayjan"), MESOPOTAMIA),
        "To Build a Mosque",
        "Barvan wants a great mosque, its pleasure-loving governor would "
        "rather not pay, and the townsfolk cannot agree which mosque to "
        "enlarge; the characters are asked to mediate.",
        False,
    ),
    (
        (_p("azarbayjan", "Azarbayjan"), MESOPOTAMIA),
        "Khidr and the Water of Life",
        "al-Khidr makes the best of mysterious advisers, whose strange "
        "counsel always proves right; those who seek the Water of Life "
        "need his guidance, and he gives it only to the pure in "
        "purpose.",
        False,
    ),
    (
        (MESOPOTAMIA,),
        "Sorcery, Treason, and Plot",
        "the characters foil a magical attempt on the King of Georgia's "
        "life and are told to find the culprit: a magus would have "
        "broken the Code, and anyone else is a power the Order should "
        "know of.",
        False,
    ),
    (
        (_p("armenian_site", "The Armenian Highlands"), MESOPOTAMIA),
        "A Greater Armenian Covenant",
        "Greater Armenia's isolated sites may keep high Magic auras and "
        "its politics leave room for newcomers who stay modest; but its "
        "winters make supply hard, and other magi may race the "
        "characters for the best sites.",
        False,
    ),
    # -- ch08: Persia --
    (
        (_w("hindijan", "Hindijan"), _p("fars", "Fars"), PERSIA),
        "The Well of Hindijan",
        "treasure-hunters have spent many fruitless nights at Hindijan "
        "seeking a hoard rumoured there; a certain well draws them, but "
        "its fumes kill birds that fly over it, and no one has yet gone "
        "down.",
        False,
    ),
    (
        (
            _p("darabgerd", "Darabgerd"),
            _w("darabgerd", "Darabgerd"),
            _p("fars"),
            PERSIA,
        ),
        "Summoner's Salts",
        "a sahir given a princely store of the salt of seven colours "
        "suddenly calls far greater jinn, but the salt is tainted to "
        "addict them, his jinni wants ever more, and his benefactor's "
        "favours grow larger; he needs a way out, and to expose the giver.",
        False,
    ),
    (
        (_p("istakhr", "Istakhr"), _p("fars"), PERSIA),
        "The Spying Sahir",
        "the sahir who has the Cup of Jamshid uses it to spy on his "
        "neighbours, the characters perhaps among them, and sees a "
        "respected citizen doing something monstrous; unable to say how "
        "he knows, he steers the characters by what he knows of them.",
        False,
    ),
    (
        (_w("shiraz", "Shiraz"), _p("fars"), PERSIA),
        "The Imamzadihs of Shiraz",
        "two rival shrines, one healing limbs and one feet, compete for "
        "an emir with an abscessed foot; witnesses to their cures are "
        "caught in riots, and the emir may ask the characters which "
        "shrine will heal him.",
        False,
    ),
    (
        (_w("jiruft", "Jiruft"), _p("kirman", "Kirman"), PERSIA),
        "The Lion-Shah",
        "the jinni who rules Jiruft's lions asks the characters to "
        "protect the lions of Kamfiruz from the emir hunting them and "
        "bring them to Jiruft, offering his thanks and the lions' in "
        "return.",
        False,
    ),
    (
        (_p("wall_of_gurgan", "The Great Wall of Gurgan"), _w("yatus"), PERSIA),
        "Sealing the Breach",
        "to meet a danger to Persia, the Mongols, a Zahhak or something "
        "unseen, the characters seek the yatus of Damavand's initiation "
        "into a Focus against Persia's enemies, which works only in the "
        "Wall of Gurgan's aura; first they must mend the deliberate "
        "breach in the wall and face whatever made it.",
        False,
    ),
    (
        (_p("gandom_beriyan", "Gandom Beriyan"), PERSIA),
        "Why Go to Hell?",
        "few go willingly to Gandom Beriyan: to catch a villain before he "
        "gives himself fully to Hell, by blundering in while fleeing the "
        "Balu (who may then rescue them), or to forge or unmake an item "
        "of power, or for a mystery's initiation, in the hottest place "
        "on earth.",
        False,
    ),
    (
        (_w("zutt"), _p("seistan", "Seistan"), PERSIA),
        "The Idol of Zur",
        "the golden ruby-eyed idol taken from Mount Zur at the conquest, "
        "now owned by a Zutt family, has for years been walking slowly "
        "home; the characters meet the family following it, and no one "
        "knows what its return will bring.",
        False,
    ),
    (
        (_w("zaranj", "Zaranj"), _p("seistan", "Seistan"), PERSIA),
        "Rostam Roused",
        "Rostam's tiger skin is the emir of Ghur's, his mace lies "
        "forgotten in a tomb of Samarkand's Shahr-i-Zindah, and bringing "
        "both to his body may wake the hero for a time to defend Persia; "
        "with the Mongols coming, Persian sahirs may try, and a tale of "
        "Rostam in Elysium may give clues.",
        False,
    ),
    (
        (_w("herat", "Herat"), _p("khurasan"), PERSIA),
        "The Riddles",
        "a ghoul controls the emir of Herat, who has demanded a visitor "
        "neither clothed nor bare, neither walking nor riding, to speak "
        "to him neither in nor out of doors, or the city falls; whoever "
        "solves it must then answer the ghoul's three riddles, and only "
        "a killer meeting a string of impossible conditions can slay it.",
        False,
    ),
    # -- ch09: the Silk Road --
    (
        (_p("oxus", "The Oxus"), _p("jaxartes", "The Jaxartes"), SILK_ROAD),
        "A River Runs Through It",
        "the Oxus and Jaxartes freeze each winter because Faerie jinn "
        "win their yearly struggle with the Magic spirits of the banks, "
        "letting nomads and their stories across; in summer the old "
        "spirits rule again and the water flows to the fields.",
        False,
    ),
    (
        (_p("oxus", "The Oxus"), _w("gurganj", "Gurganj"), _p("khwarazm"), SILK_ROAD),
        "Spirits of the Oxus Delta",
        "the Oxus's great spirit has split into many lesser ones along "
        "the canals, held by Gurganj's dykes, which pre-Islamic sahirs "
        "strengthened with enslaved jinn; Ahurani the old fertility "
        "spirit is yoked to the shah's harvests, and Old Jahyun and the "
        "Son of the Oxus may each be bargained with against the other.",
        False,
    ),
    (
        (_p("transoxiana", "Transoxiana"), SILK_ROAD),
        "Caravans",
        "a great caravan, a moving town of thousands of beasts and men "
        "stopping at caravanserais a day apart, makes a cover for "
        "wandering magi or a shield for native travellers, and a source "
        "of tales of trade and discovery.",
        False,
    ),
    (
        (_p("naw_bahar", "Naw Bahar"), _p("bactria"), SILK_ROAD),
        "Naw Bahar",
        "a fire still burns at the heart of the empty temple outside "
        "Balkh, tended by no one anyone sees, and its Divine regio hides "
        "a small Zoroastrian community; few dare go in.",
        False,
    ),
    (
        (_p("ai_khanoum", "Ai Khanoum"), _p("bactria"), SILK_ROAD),
        "The Altars of Alexander",
        "the altar hidden in a temple at Ai Khanoum links to some seventy "
        "sites; a spell cast at Arcane Connection range while touching "
        "it reaches them all at a +4 Penetration multiplier, a way into "
        "the east for Seekers or a lifeline home for colonists.",
        False,
    ),
    (
        (_p("sogdian_rock", "Sogdian Rock"), _p("sogdiana"), SILK_ROAD),
        "A Covenant on the Rock?",
        "the Rock is a natural fortress of caves and cisterns in a Magic "
        "aura of 3, stronger perhaps in its depths, reached only by "
        "paths a few tribesmen know and haunted by the thirty who fell "
        "climbing it for Alexander: a base for magi exploring the east.",
        False,
    ),
    (
        (_p("kalyan_minaret", "The Kalyan Minaret"), _w("bukhara"), SILK_ROAD),
        "The Sheikhs Beneath the Well",
        "under an octagonal platform by the Po-i-Kalyan mosque a dry "
        "well leads down to a heap of skulls in a small Magic aura, each "
        "an Arcane Connection to summon its restless sheikh; an imam the "
        "minaret's builder slew lies beneath the tower.",
        False,
    ),
    (
        (_w("bukhara", "Bukhara"), SILK_ROAD),
        "The Lost Books of Bukhara",
        "after the Mongols burn Bukhara, poets and Merinita storytellers "
        "mourn its libraries until the grief may give a faerie library "
        "life; its books turn up on odd stalls and in forgotten stacks, "
        "and a reader who wishes for it is drawn into Arcadia, to visit "
        "once and leave with only a token.",
        False,
    ),
    (
        (_w("bukhara", "Bukhara"), SILK_ROAD),
        "The Wishing Tree",
        "in the village of Kasri Orifon, barren women crawl under the "
        "arch of a dead mulberry, home to a faerie jinni of fertility; "
        "passing beneath it leads into a tiny Faerie regio.",
        False,
    ),
    (
        (_k("elephant"), SILK_ROAD),
        "Elephants of Alexander",
        "the bones at ancient battlefields can call back war elephants' "
        "ghosts, which interest House Tremere; faerie elephants of Hind, "
        "many-tusked and swinging spiked balls, still roam the far "
        "eastern mountains and Persia's southern deserts.",
        False,
    ),
    (
        (_p("wakhan", "The Wakhan"), _p("badakhshan"), SILK_ROAD),
        "The Faerie Road to Serica",
        "the upper Oxus valley is one long narrow Faerie aura, 2 near Ai "
        "Khanoum and 6 in the Wakhan, with regiones off the path that "
        "lead to dead ends, lost kingdoms or the realms of Faerie, "
        "Arcadia most often.",
        False,
    ),
    (
        (_p("lahzvard", "The Mines of Lahzvard"), _p("badakhshan"), SILK_ROAD),
        "Untouched Stone",
        "an old magus needs a man-sized block of fresh lapis untouched by "
        "hands or magic for his longevity potion, and it must come from "
        "Lahzvard by mundane roads through the Mongol chaos, a fortune "
        "too big to hide from bandits.",
        False,
    ),
    (
        (_k("ruq"), SILK_ROAD),
        "The Ruq's Nest",
        "faerie ruqs carry those they seize into strange tales far "
        "away, as Sinbad was; valleys under their nests are said to be "
        "strewn with fist-sized diamonds holding Faerie-tainted vis.",
        False,
    ),
    (
        (_p("roof_of_the_world", "The Roof of the World"), _p("badakhshan"), SILK_ROAD),
        "Janaindar, the City Above the Clouds",
        "nomads speak of a city at the Magic Realm's edge on a peak above "
        "the clouds, reached only by magic or a ruq, whose people claim "
        "an ancient magical race as ancestors: Nephilim, Hyperborea, or "
        "a hidden covenant of old magi?",
        False,
    ),
    (
        (_p("taklimakan", "The Taklimakan"), SILK_ROAD),
        "The Black and the Blue",
        "the black hurricanes, wind spirits that tear caravans apart as "
        "sandstorms, split their loyalty between the Gök Buran, a great "
        "daimon in a stronger Magic regio at the desert's heart, and its "
        "rival Great Lop, a Duke of Hell.",
        False,
    ),
    (
        (_p("talas", "Talas"), _p("jaxartes", "The Jaxartes"), SILK_ROAD),
        "The Endless Nomad Cycle",
        "near Talas a road from Arcadia ends by an old nomad fort, and "
        "down it the Jaxartes spirit sends a faerie horde under a new "
        "name every few centuries; the Mongols may be only the latest "
        "telling.",
        False,
    ),
    (
        (_k("steppe_spirits"), SILK_ROAD),
        "The Ride of the Shaman",
        "a character drawn alone onto the steppe by visions survives a "
        "killing night and is made a shaman of the Great Tengri, at a "
        "Crisis of ageing and two Warping, gaining the Nightwalker's "
        "spirit travel and the Pagan Flaw.",
        False,
    ),
    (
        (_k("steppe_spirits"), SILK_ROAD),
        "The Founder's Final Work",
        "the Great Tengri, untouched by Mercurian rites or the Dominion, "
        "is a vast store of magic for a magus who would finish "
        "Hercynius's work of bringing Merinita's nature magic into "
        "Hermetic theory.",
        False,
    ),
)


def _add(record: Any, attr: str, more: str) -> None:
    setattr(record, attr, paragraphs(getattr(record, attr) or "", more))


def _place_of(cradle: Cradle, targets: tuple[Target, ...]) -> str | None:
    """The id of the first target's place found: a covenant's site, or
    the record itself."""
    for target in targets:
        found = _lookup(cradle, target)
        if found is None:
            continue
        place_id = found.place_id if target[0] == "covenant" else found.id
        if place_id:
            return place_id
    return None


def finish(cradle: Cradle) -> None:
    world = cradle.world
    for key, kind, target, note in LINKS:
        found = _lookup(cradle, target)
        if found is not None and key in world:
            Builder.link(world[key], kind, found, note)
    for key, targets in PLACES.items():
        place_id = _place_of(cradle, targets)
        if key in world and place_id:
            world[key].place_id = place_id
    for key, targets in SHARED_PLACES.items():
        threat = world.get(key)
        if threat is not None and threat.place_id is None:
            threat.place_id = _place_of(cradle, targets)
    _seeds(cradle)


def _seeds(cradle: Cradle) -> None:
    """Each seed on the first of its targets that exists and is the
    pack's own, as one line under a "Story seeds" heading; a seed for
    the storyguide alone goes under the heading in the record's secrets."""
    shared = _shared_ids(cradle)
    lines: dict[tuple[int, str], tuple[Any, list[str]]] = {}
    for targets, title, text, hidden in SEEDS:
        record = None
        for target in targets:
            found = _lookup(cradle, target)
            if found is not None and found.id not in shared:
                record = found
                break
        if record is None:
            continue
        if hidden:
            attr = "secrets"
        elif isinstance(record, (Covenant, Creature)):
            attr = "notes"
        else:
            attr = "summary"  # a neighbour or a character
        entry = lines.setdefault((id(record), attr), (record, []))
        entry[1].append(f"{title}: {text}")
    for (_, attr), (record, seeds) in lines.items():
        _add(record, attr, "Story seeds:\n" + "\n".join(seeds))
