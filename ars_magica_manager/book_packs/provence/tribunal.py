"""The Provençal Tribunal itself: the record and its summary (with each
covenant's votes), the Peripheral Code and the Tribunal's customs, the
docket for the meeting of 1221, and every ruined, abandoned or lost
covenant the book names apart from Val-Negra, as ruined places (build);
then the officers, each ruin's region and its ties to living covenants
(finish, once the parts that make the regions, covenants and magi have
built)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...tribunal_packages.provence import PROVENCE
from ..builder import Secrets, paragraphs, titled

if TYPE_CHECKING:
    from ...models import Covenant
    from . import Provence

NAME = "The Provençal Tribunal"

#: Each covenant's votes at the meeting of 1221, in the book's order of
#: size; the app has no field for them, so they are kept in the summary.
VOTES: tuple[tuple[str, str], ...] = (
    ("The Coenobium Rhodanien", "about 20"),
    ("Aedes Mercurii", "18"),
    (
        "Castra Solis",
        "17, to which the Praeco's and the Presiding Quaesitor's votes are added",
    ),
    ("Tolosa Paratge", "9, split between its Black and White factions"),
    ("Ostal des Exiles", "6, although the Tribunal has not yet recognised it"),
    ("Bellaquin", "5"),
    ("Stella Durus", "5"),
    ("Ara Maxima Nova", "4"),
    ("Miniata Sophia", "4"),
    ("Tres' Band", "3, never cast: the band shuns Tribunal"),
)

VOTES_TEXT = "Votes at the meeting of 1221:\n" + "\n".join(
    f"- {covenant}: {votes}" for covenant, votes in VOTES
)

SUMMARY = paragraphs(
    "The Tribunal of the langue d'oc: by the Grand Tribunal's ruling of "
    "1129 it reaches wherever Occitan is spoken, from the Atlantic coast "
    "of Gascony across the Toulousain and the Narbonnais to the Rhône and "
    "the Alpine edge of Arelat, and from the Massif Central south into "
    "the Pyrenees and beyond them into Catalonia. Its magi, just over a "
    "hundred of them, lived quietly apart from the world until lately, "
    "in the wild south and the mountain strongholds; the gentle, personal "
    "bonds of paratge that bind the southern nobility left them freer than "
    "their sodales of the feudal north. The Albigensian Crusade has "
    "broken that ease: Mistridge, Lariander, Bentalone and Berinor have "
    "fallen in eleven years of war, refugees fill the covenants, and the "
    "question of what the Order should do about the crusade divides "
    "every council.",
    "Three powers dominate. In the west the pagan Mercurians of Aedes "
    "Mercurii and the Mithraic, Christian Flambeau of Castra Solis, the "
    "domus magna, each claim to be the true heirs of Val-Negra and of "
    "Flambeau himself, and despise one another. In the east the many "
    "chapters of the Coenobium, Jerbiton and Redcaps under the Chief "
    "Redcap Alazais, smother any rival covenant in its shadow and have "
    "grown steadily stronger while the crusade wrecked the rest. Old and "
    "proud covenants stand apart from both: Tolosa Paratge, now tearing "
    "itself apart over its Cathar magi, and Bellaquin, the bankers of "
    "Andorra. Mystery cults matter here more than almost anywhere: the "
    "Legion of Mithras, the Cult of Mercury, Matres & Matrones, the "
    "Knights of the Green Stone and the Gorgiastic Cathars all reach "
    "across covenant lines.",
    "Founding a covenant is easy: magi swear a charter together and a "
    "Quaesitor notarises it, and no vote is needed. Covenant oaths can be "
    "enforced at Tribunal, and a covenant may be spread over many sites "
    "or be no more than magi who meet in council now and then. The "
    "result is a land littered with the ruins of covenants that failed. "
    "Minutes and proclamations are written in Latin and Occitan both.",
    "The Tribunal meets every seven years. By custom the eldest magus is "
    "Praeco: now Dama of Merinita, a maga of great age and power who "
    "lives apart from her covenant, Castra Solis, in a small tower near "
    "Mimizan, favours female magi, and is heeded even by Aedes Mercurii. "
    "A Presiding Quaesitor is chosen at the close of each meeting, with "
    "two advisers. Each day of a meeting opens with the rite of the Cult "
    "of Mercury's flamen, masked and robed, who speaks for the gods and "
    "reads the omens; most magi think it a quaint relic and Castra "
    "Solis's pious magi a blasphemy, but the office carries quiet "
    "influence. Midius of Flambeau, of Aedes Mercurii, holds it now.",
    "The meeting of 1207, at Aedes Mercurii, spent a day on the Church's "
    "war on the Cathars and decided nothing; Oxioun of Tytalus argued for "
    "keeping out of mundane affairs. Months later the legate was killed "
    "and the crusade proclaimed, and the Traditionalist Presiding "
    "Quaesitor Protantus died; Senex held the office by 1210. The "
    "meeting of 1214, moved from besieged Toulouse to Castra Solis to the "
    "Mercurians' disgust, was the most bitter since the Schism War: "
    "charges of mundane interference flew, Normandy magi were accused of "
    "meddling and Tytalus of starting the crusade, Tolomae of Jerbiton "
    "was put out of the debate for demanding open magical war on the "
    "crusaders, and Aedes Mercurii's threat to walk out, which would have "
    "left the meeting without a quorum, was headed off only by Tibaut, "
    "then acting Presiding Quaesitor, and by the Chief Redcap's threat to "
    "suspend all Redcap service. Tres Ex Miscellanea was narrowly "
    "acquitted over the destruction of Mistridge.",
    "The next meeting is in summer 1221, at the ruins of Glanum near "
    "St-Rémy, chosen by agreement as neutral ground. Its first business "
    "is the Presiding Quaesitor: Tibaut died last year, and his filia "
    "Beatrice of Guernicus, nominally of Castra Solis but living at "
    "Glanum on the edge of the Coenobium's lands, has acted in his place "
    "at the Praeco's suggestion. She is presumed to succeed him, but she "
    "is young and without standing among the factions, and the choice "
    "may be contested. After that the crusade will fill the meeting: the "
    "Hermetic faidits want licence to defend themselves and reclaim what "
    "they lost, and look to Garus and the milites of Castra Solis; the "
    "conservatives led by Aedes Mercurii, with Ara Maxima Nova, Stella "
    "Durus and Miniata Sophia, want to keep out of it, and if the "
    "Tribunal intervenes they may boycott the meeting of 1227 and ask the "
    "Grand Tribunal of 1228 for a Tribunal of their own. Many senior "
    "magi are uneasy at the Coenobium's growing reach, and Tolosa "
    "Paratge's war may be raised if anyone brings a case.",
    VOTES_TEXT,
)

SECRET = [
    titled(
        "The unclaimed votes",
        "Fraxinetum Redux, the hidden successor of Fraxinetum on the Hyères "
        "islands, holds 3 votes it has never claimed, since the Tribunal does "
        "not know it exists.",
    ),
    titled(
        "Who killed the Presiding Quaesitors",
        "The Praeco killed both of the last two Presiding Quaesitors.",
    ),
    titled(
        "The death of Senex",
        "Senex, investigating the Praeco's cult of Matres & Matrones, slipped "
        "into her sanctum at Mimizan in 1210 while she was away at an akelarre "
        "and was caught there; his death was lawful under the Code, but she "
        "hid it.",
    ),
    titled(
        "The death of Tibaut",
        "Tibaut took up Senex's trail, and in 1219 Dama and her familiar Maju "
        "ambushed him near the road to Foix, stripping his Parma with Revoke "
        "the Protection of Bonisagus; he died of the serpent's poison at the "
        "Abbey of Saint Hilaire, where crusaders had carried him.",
    ),
    titled(
        "Tibaut's belongings",
        "Tibaut's belongings are still locked in the abbot's chest at the "
        "Abbey of Saint Hilaire.",
    ),
    titled(
        "Tibaut's letter",
        "A letter Tibaut sent Beatrice by an Iberian Redcap lies in the "
        "satchel of the Redcap, who died of his wounds beside the Via Domitia.",
    ),
    titled(
        "The Praeco's bargain",
        "Dama bought the Chief Redcap's tacit support with a Longevity Ritual "
        "for Alazais's mundane lover.",
    ),
    titled(
        "Beatrice and the cult",
        "Beatrice is suspected of sympathy with the cult of Matres & Matrones.",
    ),
    titled(
        "The cult's rumoured members",
        "Alazais and Mariola of Tolosa Paratge are rumoured to be members of "
        "the Matres & Matrones.",
    ),
]


def build(provence: Provence) -> None:
    b = provence.b
    provence.tribunal = tribunal = b.tribunal(
        NAME,
        package=PROVENCE.key,
        summary=SUMMARY,
        secrets=SECRET,
        meets_every=7,
        next_year=1221,
        next_season="Summer",
        meeting_place="The ruins of Glanum, near St-Rémy (Arelat)",
    )
    for year, title, says in RULINGS:
        b.ruling(tribunal, title, year, says)
    _ruins(provence)
    _docket(provence)


# -- the Peripheral Code and the Tribunal's customs --

#: The Peripheral Code: (year or None, title, what it says).
RULINGS: tuple[tuple[int | None, str, str], ...] = (
    (
        None,
        "Founding a covenant",
        "A covenant comes into being when its magi agree on a common aim, "
        "write a charter setting out their oath, and swear it together; "
        "the swearing is what counts. The one legal step is to have a "
        "Quaesitor notarise the charter, which makes it enforceable under "
        "the Code, and some groups put this off. No vote or approval of the "
        "Tribunal is needed, though it is polite to tell the nearest Mercer "
        "House and to send someone to the next meeting to announce the new "
        "covenant. A settlement never notarised (Glanum I and II, Portus "
        "Termini) was never a recognised covenant. The Provence package "
        "records this as its Open founding custom.",
    ),
    (
        None,
        "Covenant oaths enforceable",
        "A covenant's oath is part of the Peripheral Code here, and a "
        "Tribunal can rule on it. As a result many small quarrels within a "
        "council, settled elsewhere by certamen or among the members, are "
        "brought before the whole Tribunal.",
    ),
    (
        None,
        "Covenants on many sites",
        "A covenant need not live in one place. Its members may keep "
        "separate homes and meet in council only when needed: Castra Solis "
        "counts the Praeco at Mimizan and Marie of Merinita at Poitiers as "
        "members, and the Coenobium is a chain of chapters along the Rhône "
        "and the coast.",
    ),
    (
        None,
        "Residency",
        "A magus is resident who attended one of the last three meetings, "
        "or is voted resident at the first he attends. A magus Gauntleted "
        "in the Tribunal is resident until he has missed three meetings in "
        "a row. Residency lasts until the magus claims it in another "
        "Tribunal or attends and votes at another Tribunal's meeting.",
    ),
    (
        None,
        "Registering arrivals and departures",
        "Magi who settle in the Tribunal between meetings register either "
        "with both the Redcaps and the Praeco, or with their nearest "
        "neighbouring covenant, a Redcap guiding them there if they do not "
        "know the way. A magus who takes residency elsewhere must first "
        "register his leaving with the Provençal Redcaps or the Praeco, "
        "before voting at another Tribunal, or he breaks the Peripheral "
        "Code.",
    ),
    (
        1129,
        "The border of the Occitan tongue",
        "After quarrels with Normandy over the newly enlarged Tribunal, the "
        "Grand Tribunal fixed the border as running wherever the people "
        "speak Occitan. Disliked at first, the rule is now embraced as the "
        "ground of the Tribunal's claims to vis and other resources, and "
        "the Tribunal writes its minutes, proclamations and many other "
        "documents in Occitan as well as Latin.",
    ),
    (
        None,
        "The Praeco",
        "By custom the eldest magus of the Tribunal presides as Praeco.",
    ),
    (
        None,
        "The Presiding Quaesitor",
        "The Presiding Quaesitor, who runs the meeting, is appointed at the "
        "close of each meeting together with two advisers. When the office "
        "falls vacant between meetings an acting Presiding Quaesitor serves "
        "until the next meeting confirms or replaces him, as Tibaut did "
        "for Senex and Beatrice does for Tibaut.",
    ),
    (
        None,
        "The flamen of Mercury",
        "By ancient tradition a priest of the Cult of Mercury, in mask and "
        "robes of office, opens every day of a meeting with a rite, "
        "speaking for the gods and reading omens in the Tribunal's "
        "ceremonies. The rite goes unchallenged for its age, though few "
        "take it seriously.",
    ),
    (
        1012,
        "Val-Negra must not rise again",
        "After the fall of Val-Negra in the Schism War, and the panic over "
        "what was found sealed there, the Quaesitores decided in secret "
        "that the covenant must never be refounded, and House Flambeau "
        "made Castra Solis its domus magna instead. Few magi know the reason, and "
        "even the site is now lost.",
    ),
    (
        975,
        "Fraxinetum's destruction",
        "The magi of the eastern Tribunal who banded together against "
        "Fraxinetum's Moorish raiders worked through William I of "
        "Provence's army rather than a declared Wizard's War, and narrowly "
        "escaped the Quaesitores' censure for destroying a covenant that "
        "way. The league they formed became the Coenobium.",
    ),
    (
        None,
        "Bellaquin and mundane lordship",
        "Twice jealous neighbours charged Bellaquin with breaking its oath "
        "by its deep entanglement in feudal affairs; twice the Tribunal "
        "found it had brought no ruin on its accusers or the Order. The "
        "precedent: even heavy mundane involvement is tolerated so long as "
        "it causes no ruin to magi.",
    ),
    (
        1207,
        "No ruling on the Cathars",
        "The meeting at Aedes Mercurii debated the Church's campaign "
        "against the Cathars for a whole day and made no decision; the "
        "Mercurians' counsel of staying out of mundane affairs prevailed by "
        "default. No case has yet been brought against an avowedly Cathar "
        "magus.",
    ),
    (
        1214,
        "Grogs in a Wizard's War",
        "Tres Ex Miscellanea armed a company of mercenaries with magical "
        "weapons, called them his grogs, and used them and his magical "
        "siege engines to level Mistridge's tower. As his Wizard's War had "
        "been properly declared, and nothing in the Code forbids using "
        "grogs to wage one, the Tribunal acquitted him by a narrow vote. He "
        "then went into hiding from Mistridge's friends.",
    ),
    (
        1218,
        "The March of Tolomae",
        "Tolomae, once of the Coenobium and Bellaquin, led the Procrustean "
        "League in calling for open war on the Church. Renounced by the "
        "Mercurians and the Coenobium, he was cast out of House Jerbiton as "
        "orbus in 1216, fled rather than answer a Quaesitor's questions over "
        "the murder of the legate Pierre de Castelnau, and early in 1218 was "
        "Marched for repeated interference with mundanes and slain.",
    ),
    (
        None,
        "Glanum held neutral",
        "The ruins of Glanum, agreed as the compromise site for the meeting "
        "of 1221, may not be formally resettled until that question is "
        "settled. Only Beatrice of Guernicus lives there, as the "
        "Coenobium's guest.",
    ),
    (
        None,
        "The Coenobium's toll and code of hospitality",
        "A local custom of the Coenobium's towns, not a Tribunal ruling, but "
        "one every visitor meets. Magi openly visiting Avignon announce "
        "themselves and how long they will stay, and are asked to give a "
        "silver florin holding a pawn of vis, which pays for the "
        "covenant's non-Jerbiton specialists. In return they get food, "
        "lodging, laboratory space and a consul as patron, who answers for "
        "their conduct and protects them. The guest's part: give notice of "
        "the visit by Redcap if possible, bring the florin, state the "
        "purpose and length of the stay and say when leaving, behave with "
        "restraint and help the patron if asked, and go at once if told "
        "to. Magi who refuse are thought crass, watched, and quietly "
        "obstructed, even with charges at Tribunal. The Coenobium keeps its "
        "members' Latin names, and has let no new covenant thrive in "
        "southern Provence for over a century unless it joined as a "
        "chapter.",
    ),
)


# -- the fallen covenants --

#: Each ruined, abandoned or lost covenant: (key, name, region key in
#: `provence.places`, realm, aura, status, known, summary, secret).
#: Val-Negra belongs to val_negra.py.
RUINS: tuple[tuple[str, str, str, str, int, str, str, str, Secrets], ...] = (
    # The Toulousain.
    (
        "windgraven",
        "Windgraven",
        "toulousain",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "Founded 1060, destroyed 1197. Squat stone towers inside the "
        "remains of a Visigothic fortress on a rocky plateau in the south "
        "of the County of Toulouse. Its necromancers were notorious for "
        "cruelty, widely thought diabolists, and had sunk deep into Winter "
        "when Mistridge declared a lawful Wizard's War on them and battered "
        "the towers almost flat with giant boulders. Few grieved; the "
        "attack may have prompted Tres's destruction of Mistridge soon "
        "after. The book gives no aura.",
        "",
    ),
    (
        "lariander",
        "Lariander",
        "toulousain",
        "Infernal",
        6,
        "Known",
        "In the Tribunal",
        "Founded 1192, destroyed 1211. A Spring covenant of House Tremere "
        "in a faerie wood near the village of Montgey. In the summer of "
        "1211 peasants and southern knights slaughtered a column of German "
        "crusaders in the wood on their way to the siege of Lavaur, and de "
        "Montfort's reprisals burned the village and the trees and killed "
        "the bewildered Tremere, whose black robes were taken for those of "
        "Cathar perfecti. The massacre left an Infernal aura of 6 over the "
        "village site and the wood, where dark shapes move at night. "
        "Garsenda of Lariander, now of the Ostal des Exiles, believes "
        "herself the only survivor.",
        [
            titled(
                "Who stirred the villagers",
                "Garsenda herself, with faerie white ladies, stirred the "
                "villagers to attack the column in the hope of saving Lavaur.",
            ),
            titled(
                "Garsenda's guilt",
                "Garsenda blames herself for Lariander's ruin.",
            ),
        ],
    ),
    (
        "berinor",
        "Berinor",
        "toulousain",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "Founded 1089, fallen 1210. A modest Jerbiton covenant of the "
        "County of Toulouse, patron of many troubadours and trobairitz. It "
        "lived in a castle held for it by a mundane lord, and fell when de "
        "Montfort's men dispossessed him. Its survivors went to Tolosa "
        "Paratge.",
        "",
    ),
    (
        "bentalone",
        "Bentalone",
        "toulousain",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "Founded 1106, destroyed 1207. A Summer covenant in a castle that "
        "Simon de Montfort's army mistook for a Cathar stronghold and took "
        "by surprise assault. The book does not say where it stood.",
        "",
    ),
    (
        "filii_sinapis",
        "Filii Sinapis",
        "toulousain",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "Founded 1063, abandoned 1215. Founded by Flambeau of Sinapis, the "
        "Normandy liege covenant whose magi left Anjou when the feud of "
        "Flambeau and Tytalus ended, and abandoned after the crusade swept "
        "through. The book does not say where it stood.",
        "",
    ),
    (
        "penne",
        "Château de Penne (the first Bellaquin)",
        "toulousain",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "Bellaquin's home from the last years of the Schism War until about "
        "1200: a ruined castle restored by magic, high above the Aveyron in "
        "the Tarn, a day's march north-north-east of Toulouse. Flambeau "
        "built it as a stronghold, then left it to the Jerbiton, who made "
        "it one of the Order's most admired buildings and ruled the "
        "resettled land around it as lords. Caught between feudal "
        "obligations and its own intrigues, the covenant was ruined by "
        "mundane forces, perhaps steered by other magi. The survivors took "
        "what they could, destroyed the rest, left the site to their "
        "mundane proxies and moved to Andorra, where Bellaquin lives on.",
        "",
    ),
    # Gascony.
    (
        "bachlach",
        "Bachlach's Hermitage",
        "gascony",
        "Divine",
        2,
        "Known",
        "Locally",
        "The remains of a Diedne covenant in the wilds of Gascony, turned "
        "into a hermitage. Its magus Bachlach renounced his magic and hid "
        "from the Order as the hermit Estebe some years before the Schism "
        "War; his followers, the Valerenes of Agen, still live there apart "
        "from the world, seeking the Divine in nature and chasing the "
        "unicorns seen near Bazas. Each summer solstice they walk to "
        "Limoges to honour St. Valerie's bones. The buildings hold a Divine "
        "aura of 2, which turns to Magic 2 for the solstice night alone. "
        "His notes and journals lie in an "
        "old ossuary beside his crypt: a rare window on early Diedne magic "
        "and ritual, and a likely way to reopen old Schism War wounds.",
        [
            titled(
                "Bachlach and Valerie",
                "Bachlach was a pagan warrior-magus who beheaded Valerie when "
                "she refused to marry him; when she rose and carried her head "
                "to the archbishop at Limoges, he was converted on the spot.",
            ),
            titled(
                "The Valerenes' initiations",
                "Bachlach's followers' initiations may reenact the beheading.",
            ),
        ],
    ),
    (
        "nemetannais",
        "Nemetannais",
        "gascony",
        "Magic",
        3,
        "Known",
        "Locally",
        "A once-prominent Diedne covenant a mile from the village of La "
        "Romieu, founded in the mid-900s as a southern offshoot of "
        "Branugurix and destroyed by Flambeau in the Schism War. Six small "
        "pyramids of garluche sandstone, twelve to fifteen feet high and "
        "older than memory, once marking 'safe haven', bound a Magic aura "
        "of 3 that takes in a complex of caves, made unstable by the "
        "attack. The area swarms with feral magical cats, matagots "
        "(Magic Might 15), said to descend from the magi's familiars and to "
        "share the traits of the Founder Diedne's own.",
        "",
    ),
    (
        "lapurdum",
        "Lapurdum",
        "gascony",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "Founded 822, abandoned 858. A Flambeau covenant built around a "
        "mithraeum on a Roman camp's site where the Adour meets the sea, given up "
        "in the mid-ninth century under Viking raids and quarrels within. "
        "Its ruins lie lost somewhere beneath the city of Bayonne.",
        "",
    ),
    (
        "donjon_leyre",
        "Donjon Leyre",
        "gascony",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "Founded 955, destroyed 1008. An early vassal of Montverte (of the "
        "Normandy Tribunal) at the fork of the Leyre in the Landes, set up "
        "as a base for raids into the Basque Pyrenees. Every one of its "
        "founders died fighting in the Schism War.",
        "",
    ),
    (
        "diedne_gascony",
        "The two lost Diedne sites of Gascony",
        "gascony",
        "Magic",
        0,
        "Rumoured",
        "In the Order",
        "Two Diedne covenants of Gascony whose names were lost in the "
        "Schism War. Most Gascon Diedne fled their sites, often burning "
        "them before their attackers arrived. They are among the nine or "
        "more Diedne sites the Quaesitores struck from the records after "
        "the war: magi are forbidden to seek them out, though by now few "
        "know where not to look.",
        "",
    ),
    # The Pyrenees.
    (
        "mistridge",
        "Mistridge",
        "pyrenees",
        "Magic",
        0,
        "Known",
        "In the Order",
        "Founded 1050, destroyed 1209. A famous covenant of powerful magi "
        "in a magically raised tower on the brink of a precipice in the Val "
        "du Bosque, thought proof against any mundane assault. In 1197 it "
        "destroyed Windgraven. In the winter of 1209 Tres Ex Miscellanea, "
        "with two other Rusticani and a host of mercenaries carrying "
        "weapons he had made, declared Wizard's War on every member and "
        "brought the tower down with magical siege engines, killing the "
        "defenders; whether for Windgraven's sake or because Mistridge had "
        "scorned him as a hedge wizard is still unknown. His acquittal in "
        "1214 made the law on grogs in a Wizard's War. Rixenda Mistridge "
        "and other survivors went to the Ostal des Exiles.",
        "",
    ),
    (
        "askelarre",
        "Askelarre",
        "pyrenees",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "Founded 945, destroyed 1011. A covenant formed by a coven of "
        "Hermetic sorginak, Basque witches, whose members were spread "
        "across the Basque country. It was destroyed in the Schism War; "
        "Leo Augustus of Flambeau and Vegetius of Tremere died in the "
        "assault.",
        "",
    ),
    (
        "girona",
        "Val-Negra's chapterhouse near Girona",
        "pyrenees",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "A second portal and entrance to the Mercurian temple complex, at "
        "the eastern end of the Pyrenees near Barcelona, north of Girona. "
        "It was abandoned at the start of the Schism War, along with the "
        "portal that led to Val-Negra itself.",
        "",
    ),
    (
        "saint_jean",
        "Aedes Mercurii's outpost at Saint Jean Pied-de-Port",
        "pyrenees",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "Until 1177 Aedes Mercurii kept a large outpost in the city of "
        "Saint Jean Pied-de-Port on the pilgrim road. The townsfolk came "
        "to suspect its covenfolk of witchcraft, and the house was lost "
        "when Richard the Lionheart razed the city. Some Hermetic "
        "historians believe a Mercurian temple there held a lapis "
        "mercurius, now lost, which could give Insight into the old road "
        "magic.",
        "",
    ),
    # The Narbonnais.
    (
        "himinis_forge",
        "Himinis' Forge",
        "narbonnais",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "A fallen covenant of the Narbonnais, named in the Tribunal's "
        "lists; the book gives nothing more about it.",
        "",
    ),
    (
        "uxellodunum",
        "Uxellodunum",
        "narbonnais",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "A fallen covenant of the Narbonnais bearing the name of the old "
        "Gaulish hill-fort; the book names it and gives nothing more.",
        "",
    ),
    (
        "diedne_massif",
        "The two lost Diedne covenants of the Massif Central",
        "narbonnais",
        "Magic",
        0,
        "Rumoured",
        "In the Order",
        "Two Diedne covenants somewhere in the Massif Central, their names and sites "
        "lost: two of the nine or more that the Quaesitores struck "
        "from the records after the Schism War, which magi are forbidden "
        "to seek.",
        "",
    ),
    # Arelat.
    (
        "glanum",
        "The ruins of Glanum",
        "arelat",
        "Magic",
        0,
        "Known",
        "In the Order",
        "The ruins of the Roman town just south of St-Rémy, where two "
        "short-lived Hermetic settlements called Glanum stood in the ninth "
        "century, one Mercurian and one Mithraic. Both collapsed quickly, "
        "too narrow in their magic and too zealous to admit anyone outside "
        "their cult, and neither lasted long enough to have a Quaesitor "
        "review its charter and be recognised by the Lotharingian Tribunal "
        "of the day. Empty since the Schism War, the ruins were agreed as "
        "the neutral ground for the Tribunal of summer 1221 and may not be "
        "resettled until that is settled. Beatrice of Guernicus lives here "
        "as the Coenobium's guest; her sanctum is in effect a small chapter "
        "of Castra Solis, given to the even-handed study of the Roman "
        "shrines of the many cults that once flourished here. The book "
        "gives no aura.",
        "",
    ),
    (
        "barbegal",
        "Barbegal",
        "arelat",
        "Magic",
        5,
        "Known",
        "In the Tribunal",
        "Founded 895, abandoned 930. A Roman watermill complex a few miles "
        "north of Arles, home to three mage-smiths of House Verditius; one, "
        "an engineer, was said to have found how to draw vis of different "
        "Forms out of a Magic aura with enchanted waterwheels. Saracen "
        "raiding, abetted by Fraxinetum, emptied the undefended site, and "
        "its last survivor helped found the Coenobium. It keeps a Magic "
        "aura of 5. The broken remains of 13 of its magical wheels lie "
        "hidden under the undergrowth and three are missing: repairing the "
        "mill might recover its secret of vis on demand, a project the "
        "Coenobium, short of strong auras, would gladly sponsor.",
        "",
    ),
    (
        "birds_of_camargue",
        "The Birds of Camargue",
        "arelat",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "Founded 901, merged 970. A Bjornaer covenant in the marshes at the "
        "mouth of the Rhône, whose magi joined the Coenobium against the "
        "threat of Fraxinetum. Its site is no longer a covenant.",
        "",
    ),
    (
        "elisii_campi",
        "Elisii Campi (the Alyscamps)",
        "arelat",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "Founded 843, driven out 1009. A small covenant of Ex Miscellanea "
        "necromancers and spirit masters in the crypts of the Alyscamps, "
        "the old Roman necropolis of Arles. They lived through the Schism "
        "War underground, but the rising Coenobium quietly turned the "
        "townsfolk against them with rumours of diabolists under the "
        "tombs, and they fled. Many of the sarcophagi still carry their "
        "enchantments and traps, and the city council now gives "
        "sarcophagi away to honoured visitors.",
        "",
    ),
    (
        "portus_termini",
        "Portus Termini (the Verdon gorge)",
        "arelat",
        "Magic",
        0,
        "Rumoured",
        "In the Tribunal",
        "The refuge the necromancers of Elisii Campi sought in a hidden "
        "cave network in the Verdon gorge, under a new name. All contact "
        "with them was lost soon after, before the next meeting, so it was "
        "never registered as a covenant. Many suspect hoplites in the "
        "Coenobium's pay hunted them down.",
        "",
    ),
    (
        "fraxinetum",
        "Fraxinetum (La Garde-Freinet)",
        "arelat",
        "Magic",
        4,
        "Known",
        "In the Tribunal",
        "Founded 889, destroyed 975. The raiders' covenant in the dark "
        "granite Massif des Maures above St Tropez, named for the ash "
        "groves planted by its founder Sayyid Shajarat al-Darda (an "
        "Andalusian Herbam master House Flambeau disowns) with his Tytalan "
        "lieutenant Nasr ibn Amaf. For a century it secretly backed the "
        "Moorish raids on the cities of Provence and the fall of several "
        "small coastal covenants, until the ransom of Abbot Maieul of "
        "Cluny in 973 roused the eastern magi, whose army under William I "
        "of Provence broke the Moors at Tourtour and besieged the base; "
        "the magi vanished into the forest. The razed fort keeps a Magic "
        "aura of 4 inside a dense palisade of ash, and what remains of the "
        "defensive rituals wakes the larger trees against intruders, so "
        "peasants say the place is haunted and leave it alone.",
        [
            titled(
                "Fraxinetum's heirs",
                "Fraxinetum's heirs survive in secret as Fraxinetum Redux on "
                "the Hyères islands.",
            ),
        ],
    ),
    (
        "yf",
        "Yf",
        "arelat",
        "Magic",
        3,
        "Known",
        "In the Tribunal",
        "Founded 821, fallen 911. A Diedne covenant on the islet of Yf off "
        "Marseilles, a Magic aura of 3 around an ancient yew grove where "
        "its magi held their rites. It fell to Fraxinetum's Moors long "
        "before the Schism War; one of its magi joined the Coenobium's "
        "founders for revenge, but her line died out just before the war. "
        "Sleepers under the yews dream of green-robed magi whispering "
        "vengeance. Vis: each All Souls' Eve up to six of the youngest "
        "branches of the oldest yew can be cut, each a pawn of "
        "Extraordinary Intellego vis that, burnt, lets its bearer speak "
        "with the dead once as by Whispers Through the Black Gate. No "
        "covenant claims it.",
        [
            titled(
                "Who harvests the yew",
                "The magi of Fraxinetum Redux quietly harvest vis on the "
                "deserted isle of Yf.",
            ),
        ],
    ),
    (
        "castra_peccaius",
        "Castra Peccaius",
        "arelat",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "The ruins of a Hermetic settlement abandoned three centuries ago, "
        "on the east bank of the Petit Rhône across from where Aigues-Mortes "
        "will one day stand. The Coenobium's covenfolk still come to "
        "harvest salt vis from a brackish pond inside the ruins, on land "
        "its mundane dependents lease from the Abbey of Psalmody. If "
        "history runs its course the monks will sell the land to King "
        "Louis.",
        "",
    ),
    (
        "telo_martius",
        "Telo Martius",
        "arelat",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "A former Flambeau covenant at Toulon, under Mount Faron. The "
        "Coenobium now keeps a small chapter house on its site, run by a "
        "retired Redcap, the unGifted alchemist Aloysius Porphyri, who "
        "oversees the murex and kermes dye harvests.",
        "",
    ),
    (
        "turris_mascis",
        "Turris Mascis (the Tropaeum Alpium)",
        "arelat",
        "Divine",
        3,
        "Known",
        "In the Tribunal",
        "A short-lived, mostly Mercurian covenant, the 'Tower of the "
        "Masques', that studied the Trophy of Augustus at La Turbie, the "
        "Roman monument that by tradition marks the Tribunal's eastern "
        "limit; what it learned is lost. The statue of Augustus inside was "
        "mostly smashed by Christian mobs, the monument's stones are "
        "built into the village, and the church of St Michael's Divine "
        "aura of 3 smothers any magic in them. The town is under Genoa's "
        "sway.",
        "",
    ),
    (
        "portus_cottiae",
        "Portus Cottiae",
        "arelat",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        "Founded 821, overrun 906. The first Mercer House and a Mercurian "
        "covenant, founded by Julius Donnus of Flambeau, an outcast "
        "Mercurian from the Greater Alps, as a second home for the revived "
        "Cult of Mercury. Built in the Roman manner of the Alpine "
        "covenants, its motherhouse, Brigantium, stood in the cliffs above "
        "Briançon commanding the Montgenèvre pass and the upper Durance, "
        "with chapters kept by mansionarii at Gap (Vapincum), Chorges "
        "(Caturigomagus), Embrun (Ebrodunum) and Oulx (Ulcium). Berber "
        "raiders overran it in 906; the survivor Anaïs of Jerbiton fled to "
        "Avignon and pressed for the league that became the Coenobium.",
        [
            titled(
                "Brigantium",
                "Brigantium's magi brought the mountain down on the raiders "
                "and sealed themselves in; ghosts of the magi and Infernal "
                "shades of the attackers haunt the rubble, and Brigantium's "
                "Mercere Portal lies buried beneath.",
            ),
            titled(
                "Caturigomagus",
                "Caturigomagus is a sanctum under a ruined Roman way station a "
                "day beyond Chorges, its slain Merinita's books of Faerie "
                "magic guarded by three seductive dememoilles.",
            ),
            titled(
                "Vapincum",
                "Vapincum lies in the crypts under Gap cathedral, an old temple "
                "to Apollo, its weak aura smothered by the church's.",
            ),
            titled(
                "Ebrodunum",
                "Ebrodunum was a stabling post, its hidden shrine to Mercury "
                "built into the new cathedral and its aura gone; descendants "
                "of the covenfolk may hold books and records.",
            ),
            titled(
                "Ulcium",
                "Ulcium is a temple of Mars Ultor reached through a regio in "
                "the ruins above Oulx, the easiest to resettle but on the "
                "Roman Tribunal's border.",
            ),
            titled(
                "The heirs of Anaïs",
                "The heirs of Anaïs in the Coenobium may resist anyone who "
                "tries to reopen the sites of Portus Cottiae.",
            ),
        ],
    ),
)


def _ruins(provence: Provence) -> None:
    b = provence.b
    for key, name, _region, realm, aura, status, known, summary, hidden in RUINS:
        provence.places[f"ruin_{key}"] = b.place(
            name,
            ruined=True,
            summary=summary,
            secrets=hidden,
            realm=realm,
            aura=aura,
            status=status,
            known=known,
        )


# -- the docket --


def _docket(provence: Provence) -> None:
    b, tribunal = provence.b, provence.tribunal
    assert tribunal is not None
    b.case(
        tribunal,
        "The Presiding Quaesitor",
        kind="motion",
        brought_by="The Praeco",
        against="",
        charge="Tibaut of Guernicus died in 1219 (some accounts say 1214). "
        "His filia Beatrice of Guernicus has acted as Presiding Quaesitor "
        "since, at the Praeco's suggestion, and is presumed to take the "
        "office; but she is young, has no standing with the factions, has "
        "fallen out with Primus Garus, and would hand the office to a "
        "better candidate of her House if one appeared. Confirming or "
        "replacing her is the first business of the meeting.",
        filed_year=1220,
        filed_season="Spring",
        notice_given=True,
    )
    b.case(
        tribunal,
        "The deaths of Senex and Tibaut",
        kind="motion",
        brought_by="Beatrice of Guernicus (acting Presiding Quaesitor)",
        charge="Presiding Quaesitor Senex vanished in 1210, last seen "
        "going into a village to look into something, and was declared "
        "lost when he missed the meeting of 1214. Tibaut, who found in "
        "Senex's notes that he had been investigating a mystery cult, "
        "believed him dead and was himself looking into the Tribunal's "
        "cults when he died on the road near Foix. Beatrice suspects foul "
        "play but has no proof.",
        evidence="Senex's laboratory notes on an unnamed cult\n"
        "Tibaut's suspicions, shared with Beatrice\n"
        "Tibaut missed his meeting with Beatrice\n"
        "Luc of Ara Maxima Nova fought Tibaut in certamen over his "
        "questions about the Via Domitia",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Recognition of the Ostal des Exiles",
        kind="motion",
        brought_by="Gilbert of Flambeau (Ostal des Exiles)",
        charge="The House of Exiles, founded since 1214 under Castle "
        "d'Aguilar by survivors of Mistridge, Lariander and other fallen "
        "covenants, asks to be recognised as a covenant of the Tribunal, "
        "with its six votes.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "The faidits' petition",
        kind="motion",
        brought_by="The Hermetic faidits (Ostal des Exiles and refugees)",
        charge="The magi who lost their covenants to de Montfort's armies "
        "ask for licence to defend themselves against the crusaders and to "
        "win back their magical power, and want Garus and the milites of "
        "Castra Solis behind them, even with open magic. The Mercurian "
        "conservatives oppose any intervention in mundane affairs.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "A Tribunal of the Pyrenees",
        kind="motion",
        brought_by="Aedes Mercurii and the conservative covenants",
        charge="If the Tribunal intervenes against the crusade and the "
        "Church, Aedes Mercurii, Ara Maxima Nova, Stella Durus and Miniata "
        "Sophia may boycott the meeting of 1227 and, being the four "
        "covenants a Tribunal needs, ask the Grand Tribunal of 1228 to "
        "make them a Tribunal of their own. Bellaquin dreams of a Catalan "
        "Tribunal instead.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Tolosa Paratge's civil war",
        kind="charge",
        brought_by="(not yet brought)",
        against="The Black and White factions of Tolosa Paratge",
        charge="Since Marc killed Augustus in Wizard's War in 1218 and "
        "St. Tropez killed Marc, the covenant has split: the pro-Cathar "
        "Blacks hold the regio, the Whites wait in the city to retake it. "
        "Both sides are plainly depriving each other of magical resources, "
        "but the Quaesitores have not acted, out of respect for the "
        "covenant and because no one has brought a case. The Whites may "
        "appeal to the Tribunal in 1221.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "The Procrustean League's followers",
        kind="charge",
        brought_by="",
        against="The followers of Tolomae",
        charge="After Tolomae was Marched in 1218, several of his rumoured "
        "supporters fled to other covenants or vanished among the faidits "
        "of the langue d'oc. Some magi fear his cause will return, "
        "embittered by the war.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Marie of Merinita and the northern border",
        kind="motion",
        brought_by="Magi of the Normandy Tribunal",
        against="Marie of Merinita (Castra Solis)",
        charge="Marie keeps a manor at Poitiers, in lands usually held to "
        "be Normandy's, as a chapter of Castra Solis, attends Tribunal in "
        "Provence, and works to push the Tribunal's border north by "
        "spreading southern language and culture through Aquitaine, so "
        "that the 1129 rule of the Occitan tongue would carry the land "
        "with it.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "An undeclared covenant in the Hyères",
        kind="charge",
        brought_by="(no one: the Tribunal does not know of it)",
        against="Fraxinetum Redux",
        charge="Secret. Ahmad ibn Nasr of Tytalus and two Moorish magi keep "
        "an undeclared covenant among the Hyères islands, backing raids on "
        "the coast and harvesting vis on the islands, afraid that "
        "Fraxinetum's memory would bring a Wizard's War on them if they "
        "declared it. Aucassin of Tytalus lives as an eremite at Beaucaire "
        "under a false name. A case can only be brought once someone finds "
        "them out.",
        filed_year=1220,
        filed_season="Spring",
    )


# -- after every part has built --

#: The names the Coenobium may go by.
COENOBIUM = (
    "The Coenobium Rhodanien",
    "Coenobium Rhodanien",
    "The Coenobium",
    "Coenobium",
    "Mascum Sub Pontem",
)

#: Each fallen covenant's ties to living covenants: (ruin key, covenant
#: names tried in order, note).
TIES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("berinor", ("Tolosa Paratge",), "Took in its survivors"),
    ("lariander", ("Ostal des Exiles",), "Garsenda, its survivor, is here"),
    ("mistridge", ("Ostal des Exiles",), "Took in its survivors"),
    ("penne", ("Bellaquin",), "Bellaquin's first home"),
    ("girona", ("Aedes Mercurii",), "Its abandoned eastern portal"),
    ("saint_jean", ("Aedes Mercurii",), "Its lost outpost"),
    ("glanum", ("Castra Solis",), "Beatrice's sanctum, in effect a chapter"),
    ("fraxinetum", ("Fraxinetum Redux",), "Its secret heir"),
    *(
        (key, COENOBIUM, note)
        for key, note in (
            ("barbegal", "Its survivor helped found the Coenobium"),
            ("birds_of_camargue", "Merged into the Coenobium"),
            ("elisii_campi", "Driven out by the Coenobium"),
            ("castra_peccaius", "Harvests its salt vis"),
            ("telo_martius", "Its Toulon chapter stands here"),
            ("portus_cottiae", "Heirs of Anaïs, its survivor"),
            ("yf", "One of its magi joined the founders"),
        )
    ),
)

#: What finish could not find, for the report.
MISSING: list[str] = []


def _covenant(provence: Provence, names: tuple[str, ...]) -> Covenant | None:
    for name in names:
        try:
            return provence.covenant_named(name)
        except KeyError:
            continue
    MISSING.append(names[0])
    return None


def finish(provence: Provence) -> None:
    tribunal = provence.tribunal
    assert tribunal is not None
    b, saga = provence.b, provence.b.saga
    MISSING.clear()
    dama = provence.magi.get("dama")
    tribunal.praeco_id = dama.id if dama is not None else None
    if dama is None:
        MISSING.append("Dama (the Praeco)")
    # The Presiding Quaesitor is vacant until the meeting of 1221 settles
    # the succession; Beatrice is named in the summary and the docket.
    tribunal.quaesitor_id = None
    for key, _name, region, *_ in RUINS:
        site, around = provence.places[f"ruin_{key}"], provence.places.get(region)
        if around is None:
            if f"region place {region!r}" not in MISSING:
                MISSING.append(f"region place {region!r}")
        elif site.place_id is None:
            site.place_id = around.id
    for key, names, note in TIES:
        covenant = _covenant(provence, names)
        if covenant is not None:
            b.link(provence.places[f"ruin_{key}"], "covenants", covenant, note)
    tribunal.covenants_total = len(
        [c for c in saga.covenants if c.tribunal_id == tribunal.id]
    )
