"""The Transylvanian Tribunal itself: the record and its summary (House
Tremere's Tribunal, its oppida and the five legal covenants, the Praeco
and the meeting at the Shipka Pass), the Peripheral Code and the
Tribunal's customs, the docket for the meeting of 1221, the first sites
of Pannonia and Domostron as ruins, and chapter one's good sites for a
new oppidum (build); then the Praeco and the Presiding Quaesitor, every
named magus's privilege and office, each oppidum's aediles, each site's
region and the Tribunal's totals (finish, once the parts that make the
regions, oppida and magi have built).

The Shipka Pass regio is bulgaria.py's (places["shipka_pass"]) and is
named here only; the Gyogy-to lake is hungary.py's and Starosel
bulgaria.py's, though chapter one lists them among the good sites.
Keys: the ruins are places["ruin_pannonia"] and ["ruin_domostron"]; the
good sites are places["kal_valley"], ["cakoc"], ["tomb_of_attila"],
["klingsohr"], ["sunken_city"], ["isle_of_achilles"] and
["seventy_seventh_island"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...tribunal_packages import transylvania as package
from ...tribunal_packages.transylvania import TRANSYLVANIA
from ..builder import paragraphs, secrets

if TYPE_CHECKING:
    from ...models import Character
    from . import Transylvania

NAME = "The Transylvanian Tribunal"
#: About 82 magi live in the Tribunal's oppida (the census of the book's
#: oppida); 42 of them are named.
MAGI_TOTAL = 82

SUMMARY = paragraphs(
    "The Tribunal of the Carpathian Basin: the Great Plain of Hungary and "
    "the mountains that ring it (the Alps excepted), with lands to the "
    "west and south that carry it to the shores of the Adriatic and the "
    "Black Sea. Its southern edge follows no river or ridge, only the vis "
    "sources the magi on either side have claimed. Werewolves, vampires and "
    "dragons haunt its forests and passes, and folk magicians hunt them "
    "with silver, prayer and hawthorn; yet mundane society here favours "
    "the magi more than anywhere in the West. Hungarian law lets them keep "
    "their own Code and courts, nobles owe no fealty for their land, and "
    "magic is no crime, so the Order rules what it owns openly.",
    "It is House Tremere's Tribunal, and the House's proof that magi who "
    "work together can build a better world, patiently and over "
    "generations. The Prima of Tremere, Poena, at Coeris, makes the policy "
    "that governs Transylvania; the Tremere vote as a block, so they get "
    "what they want lawfully and by vote, and they want the Tribunal as an "
    "institution to thrive. The magi owe far more to the whole than "
    "Western magi do, and live in a single economy of specialised "
    "settlements rather than self-sufficient manors.",
    "Oppida and the five legal covenants. Magi live in oppida, camps "
    "independent of one another, whose members come and go as their "
    "projects and the House's needs change. A Transylvanian covenant is "
    "something else: one of the five legal bodies a Grand Tribunal left "
    "the Tribunal after the Sundering, which the Tremere turned into "
    "classes of citizenship. Each magus holds a privilege, a written "
    "agreement with the Praeco witnessed by a Quaesitor and read into the "
    "Peripheral Code: cives (of Coeris), socii (of Domostron), coloniae "
    "(of Asclepius), hospites (of Diodorus) or foederati (of Pannonia). "
    "One oppidum mixes magi of several privileges by rule, and each has "
    "one or two aediles, the odd members who guard against corruption.",
    "The officers. The Praeco, Archmagus Albertus of Lycaneon, leads the "
    "Tribunal in name, chosen by vote but only with the Prima's approval, "
    "and keeps the office only while he keeps her favour; he levies the "
    "taxes the Tribunal approves, pays the Redcaps' and Quaesitores' "
    "stipends, and issues promissory notes. Benilda of Seuthopolis, the "
    "senior Quaesitor and legal head of Domostron, presides at the "
    "meetings, witnesses privileges and hears accusations. Other offices: "
    "the aediles of each oppidum, the Curantis of the zenodochia with his "
    "Notary, the Curator of Tablinum, and the lictors.",
    "The meeting. The Tribunal meets every seven years in a regio at the "
    "Shipka Pass, near Seuthopolis, which House Guernicus keeps for the "
    "Praeco. The book gives no year for the next meeting, so 1221 is "
    "assumed, and no season, so summer is assumed. The great meetings are "
    "short and seek consensus, mostly reading what has already been "
    "agreed into the Code; the magi come for the company and the deals "
    "made around them. Criminal cases go to the emergency Tribunals the "
    "Quaesitores call there every year, where Tremere advocates cast the "
    "proxies of all their Transylvanian housemates.",
    "About 82 magi live in the Tribunal's ten oppida: Coeris, Laniena, "
    "Evredika, Seuthopolis, Tablinum, Old Histria and Shrouded Bay, "
    "Lycaneon, the Scholomance and Kezdö Válasz. The zenodochia, its "
    "roadside hospitals for magi, and Leviathan, a naval cache kept for "
    "war, belong to the Tribunal; Gigas, across the border, is a Theban "
    "covenant the Tremere use as their cat's paw.",
    "Questions for 1221: the Valley of the Thracian Kings, which Benilda "
    "is keeping closed against the Tremere necromancers; a Mercere Portal "
    "from Old Histria to Venice; the standing of the Tribunal's own "
    "Redcaps with Harco; whether Laniena's training of Fectores is "
    "lawful; raids on Evredika's vis that point at Gigas; and a papal "
    "legate lodged with the Teutonic Knights, asking about the "
    "Scholomance.",
)


def build(transylvania: Transylvania) -> None:
    b = transylvania.b
    transylvania.tribunal = tribunal = b.tribunal(
        NAME,
        package=TRANSYLVANIA.key,
        summary=SUMMARY,
        meets_every=7,
        next_year=1221,
        next_season="Summer",
        meeting_place="the Shipka Pass",
        magi_total=MAGI_TOTAL,
    )
    for year, title, says in RULINGS:
        b.ruling(tribunal, title, year, says)
    _sites(transylvania)
    _docket(transylvania)


# -- the Peripheral Code and the Tribunal's customs --

#: The Peripheral Code and the customs the book gives as law: (year or
#: None, title, what it says).
RULINGS: tuple[tuple[int | None, str, str], ...] = (
    (
        848,
        "The five legal covenants",
        "After the Sundering a Grand Tribunal capped the Tribunal at five "
        "named covenants: Coeris, Domostron, Asclepius, Diodorus and "
        "Pannonia. All five have since moved or changed how they admit "
        "members, but in law they still stand, and no new covenant can be "
        "added. A body of outsiders that joins the Tribunal enters Pannonia. "
        "The Tremere do not ask for the limit to be lifted, lest it stir "
        "old fears, and no one else gains by asking.",
    ),
    (
        None,
        "Privileges",
        "Every resident magus holds a privilege: a written agreement with "
        "the Praeco, on the Tribunal's behalf, that sets the magus's place "
        "in Transylvanian society. A Quaesitor witnesses it and it is read "
        "into the Peripheral Code at a meeting. There are five broad kinds, "
        "one for each legal covenant, but each is bargained for, and terms "
        "may be added later as reward or punishment. A magus may leave the "
        "Tribunal freely, returning what he was paid for unfinished work; "
        "one who goes with great items, much vis or other treasures is "
        "pursued by the Tremere.",
    ),
    (
        None,
        "Cives (Coeris)",
        "Every Tremere belongs to Coeris, and may resign and rejoin at will. "
        "Other magi may be made cives as a mark of the Tribunal's esteem. A "
        "cives may draw on House Tremere's aid, send a Tremere proxy to the "
        "House's Decennial, stand for any office including Praeco, raise "
        "apprentices, move between oppida (if not Tremere), and wear black "
        "or grey at meetings; where cives are the larger group of an "
        "oppidum they choose its aedile from the others. In return a cives "
        "must live as the Tremere admire: cooperate, work usefully, muster "
        "for war and pay taxes.",
    ),
    (
        None,
        "Socii (Domostron)",
        "The socii are allies of other Houses treated much as if they were "
        "Tremere: nearly all the Quaesitores, Redcaps and dedicated "
        "hoplites, who are socii unless they are cives. They may hold any "
        "office but Praeco, raise an apprentice, draw dedicated resources "
        "and crisis taxes for their work, and wear designs like "
        "Decorations; where they are the larger group they name three "
        "candidates for aedile and the Praeco picks one. They must do their "
        "duty or renegotiate, give no one a fair cause for Wizard's War (as "
        "the Praeco judges), ask leave to found an oppidum, stand in as "
        "aediles when none can be found, and wear their badges at meetings.",
    ),
    (
        None,
        "Coloniae (Asclepius)",
        "The coloniae are young magi from other Tribunals settled under "
        "close terms to open up neglected corners of the land. They are "
        "promised aid in war or disaster, the resources named in their "
        "privilege and a share of new ones found. They may not choose "
        "their aedile, seek any office but aedile, call themselves "
        "archmagi, take apprentices without leave, invite other magi in "
        "(save Quaesitores, Redcaps and hoplites), behave scandalously, or "
        "wear what looks like a Decoration they have not earned. At meetings "
        "they go unshod (sandals and slippers are now allowed) and may eat "
        "no aphrodisiac, from shellfish and truffles to carrots and pepper.",
    ),
    (
        None,
        "Hospites (Diodorus)",
        "The hospites, the Tribunal's guests, are magi hired to practise a "
        "skill for House Tremere, and most live at Lycaneon. They are paid "
        "fairly, use what their task is given, escape many taxes, are "
        "protected if War is declared on them, and are not called to "
        "Wizard's Marches. They must ask leave before seeking office, taking "
        "an apprentice, binding a familiar, making a talisman, founding or "
        "changing oppidum, voting for a particular aedile, or wearing what "
        "looks like a Decoration; a privilege may grant some of these in "
        "advance, for less pay.",
    ),
    (
        None,
        "Foederati (Pannonia)",
        "The foederati are magi of covenants that left neighbouring "
        "Tribunals for shelter here, and each keeps the customs written "
        "into its privilege, offensive to the Tremere or not, so long as it "
        "breaks neither the Code nor the Tribunal's peace. They keep the "
        "resources they held when they joined, train apprentices (the "
        "eldest is taken on as a foederatus too), move oppidum with notice "
        "and may stand for any office. They need leave to drop the duties "
        "their privilege names, which only the Praeco and the magus together "
        "can change, to use the title archmagus, found oppida, invite magi "
        "in, or trade vis or items with outsiders other than the socii. "
        "Should Pannonia ever lack outsiders, some magi of other covenants "
        "join it automatically, so it never lapses.",
    ),
    (
        None,
        "The leaders of the legal covenants",
        "To keep the Tribunal whole after the Sundering, Tremere granted "
        "concessions to the other covenants' leaders, now paid by the "
        "Tribunal. Asclepius's members elect a leader each year, who is "
        "invited to Coeris for the Triumph of Asclepius: sixteen pawns of "
        "vis, three pounds of pure gold, six books of his choosing copied from a "
        "certain library, a fine dinner and lesser tokens, in return for "
        "minor duties to the other leaders that take about two seasons. "
        "Magi of any covenant, and non-residents, may hold it. The hospites "
        "elect their leader every seven years, with the Praeco's approval, "
        "for a smaller yearly payment. Domostron is led by the senior "
        "Quaesitor and Pannonia by the Orphic cult of the south, whose "
        "members long ago sold their concessions to the chief Mercere.",
    ),
    (
        None,
        "Oppida",
        "Every magus must belong to an oppidum in some sense, and keep "
        "broadly aware of what its other members are doing. An oppidum must "
        "have at least two members, at least one of them cives, and may not "
        "be made up wholly of one House, so in practice each has a Tremere "
        "and someone who is not.",
    ),
    (
        None,
        "Aediles",
        "Each oppidum has an aedile, the odd member set there to keep House "
        "Tremere from corruption and the others from treason; where cives "
        "and non-cives are equal in number it has two. Aediles have no set "
        "duties, but may demand an urgent audience with the Praeco and the "
        "chief Quaesitor, and the Quaesitores treat an aedile's "
        "disappearance, or War declared on one, gravely.",
    ),
    (
        None,
        "Decorations",
        "The Tribunal honours service with five Decorations, worn as "
        "jewellery or embroidery on a magus's robes, never awarded twice to "
        "the same magus; a higher one replaces a lower. The Laurel goes to the magus "
        "who leads a campaign against a foe that could destroy the Order "
        "(no one now wears it); the Myrtle to the general of a lesser "
        "campaign of more than one magical battle; the Oak to one who plans "
        "such a campaign without fighting in it; the Grass to a magus who "
        "saves other magi from death, first given to the defenders of "
        "covenants against the Diedne; and the Parsley for the killing blow "
        "on a magus the Tribunal has cast out.",
    ),
    (
        None,
        "The Praeco",
        "The Praeco is chosen by vote, not by age, and needs the Prima of "
        "Tremere's approval to take office and her goodwill to keep it. He "
        "has wider powers than Praecones elsewhere, ceded by the House "
        "slowly and reversibly. The Praeco appoints the Tribunal's envoys "
        "and asks magi to settle when the Prima wants an oppidum founded.",
    ),
    (
        None,
        "Taxes and stipends",
        "The Praeco gathers taxes for the projects each meeting assigns him, "
        "and the cives, socii, coloniae and some foederati must give "
        "reasonable aid to them. A large vis source is reserved for his "
        "use, once meant for the upkeep of the meeting site's wards, which "
        "the Quaesitores now see to. He also collects the stipends the "
        "Peripheral Code sets for the Redcaps and Quaesitores, and his "
        "Redcaps deliver them, so the Tremere can see what is claimed "
        "without spying and no one can call it a bribe from the House.",
    ),
    (
        None,
        "Promissory notes",
        "Before he could tax, the Praeco borrowed against his reserved vis "
        "by issuing notes promising payment, and he still issues them for "
        "trade and diplomacy. Old notes never redeemed pass from hand to "
        "hand as a currency of great value. Forging one is a crime, held to "
        "be fraud aimed at robbing a magus of the vis that is his power.",
    ),
    (
        None,
        "Annual emergency Tribunals",
        "Elsewhere the Quaesitores call emergency Tribunals when they must; "
        "in Transylvania House Guernicus calls one every year at the "
        "Tribunal site, to give swifter justice and accept newly trained "
        "apprentices sooner. A group of Tremere advocates holds proxies for "
        "every Transylvanian Tremere, so the vote always suits the House, "
        "which uses these meetings to keep its allies content and often "
        "concedes more than the votes require.",
    ),
    (
        None,
        "Wizard's War",
        "Magi keep their right under the Code to declare War, but the "
        "Tribunal strongly prefers that wizards fight wizards only in "
        "Marches voted at an emergency Tribunal. Quarrels go first to "
        "mediation by the Quaesitores or the Prima's people, and then to "
        "certamen; private Wars are very rare.",
    ),
    (
        None,
        "Certamen in place of War",
        "A challenge to certamen says the challenger would kill his rival "
        "if he were less civilised. The winner is treated as having spared "
        "a life he could have taken, the loser lives by his mercy, and the "
        "winner has the right to strike the loser once in the face. "
        "Certamen rules are otherwise the Definitive Edition's.",
    ),
    (
        None,
        "Certamen for love",
        "Most duels are fought for love, as sport or over small matters. "
        "Before two witnesses the Tribunal could question, the duellists "
        "declare that it is for love, the stake, how it is won if not by "
        "yielding (first sound blow, first wound or unconsciousness are "
        "common), forgiveness in advance for any hurt, and that the loser "
        "yields. They may not strike a blow at the end, use vis, gamble "
        "basely, wager an officer's duties, duel naked or drunk, use spells "
        "or items (or let onlookers) to sway the result, couple during the "
        "duel, or challenge one worn down by an earlier duel.",
    ),
    (
        None,
        "Dealings with outsiders",
        "Many oppida may not make treaties with foreign covenants or "
        "Tribunals. Trading arrangements with outsiders need either a "
        "place in the Peripheral Code or the Praeco's approval, witnessed by a "
        "Quaesitor; the Praeco's appointees speak for the Tribunal abroad.",
    ),
    (
        None,
        "Settlers and Gifted children",
        "No magus may bring a Gifted child into the Tribunal or invite a "
        "magus to settle. He may instead ask the Praeco to do it, which "
        "lets the Tremere govern how many magi live here.",
    ),
    (
        None,
        "Sales of vis and enchanted items",
        "Only the Praeco, the Prima of Tremere, the socii and their agents "
        "may sell vis or enchanted items to outsiders. Old Histria is the "
        "registry for every such sale in the Tribunal; the goods need not "
        "go there, as matching letters notarised by a Quaesitor suffice. "
        "The Praeco's people may bid for anything of interest, and buyers "
        "of common vis may consult the list of notes kept by the master of "
        "the vis trade at Old Histria.",
    ),
    (
        None,
        "Magical animals",
        "Magical animals may not be exported without licence, which lets "
        "House Tremere, ever seeking breeding stock for war, buy first on "
        "exports and bid alongside on imports. Selling through the Redcaps "
        "is lawful but recorded.",
    ),
    (
        None,
        "One name to a Tremere",
        "No two Tremere magi in the Tribunal may share a name, so that the "
        "House's records can tell each apart; a maga who arrives bearing a "
        "name already held may have to defend it by certamen.",
    ),
    (
        None,
        "Amaranth",
        "Amaranth, a faerie flower whose vis gives magi pleasant visions, "
        "addiction and Warping, is destroyed wherever it is found in "
        "Transylvania.",
    ),
    (
        None,
        "Lictors",
        "Lictors, magi sworn to long service as hoplites, guard the "
        "Quaesitores and follow their orders. They may call on any cives, "
        "socius, foederatus or colonus for reasonable aid, the Tribunal "
        "judging afterwards what was reasonable for the danger. All belong "
        "to one legal covenant and so wear the same red and silver sash, "
        "pinned with a winged silver brooch, the astraea, each with its own "
        "variation. Carrying a copy of a lictor's badge is a serious crime.",
    ),
    (
        None,
        "The zenodochia",
        "The Tribunal keeps safehouses for sick or wounded magi along its "
        "roads, and wants them used. Taking vis from one is a Low Crime, "
        "though a magus who cannot repay is usually let work off the debt "
        "for the Tribunal; damaging or destroying one on purpose is a High "
        "Crime, while one who repairs accidental damage unasked is not "
        "prosecuted. Items and casting tablets must stay; vis and supplies "
        "used must be replaced.",
    ),
    (
        None,
        "The Curantis",
        "Each meeting elects a Curantis to serve until the next, usually "
        "the single candidate the elders agree on beforehand; no one may "
        "serve two terms running. He tours the zenodochia for about a "
        "season a year, repairs them, must build at least one new one in "
        "his term, and has a Quaesitor's powers in cases touching them. He "
        "is paid generously in vis and may draw on the Tribunal's stores. "
        "His Notary, chosen by the previous Curantis and often a Redcap, "
        "serves as his aedile.",
    ),
    (
        None,
        "The Curator of Tablinum",
        "The Curator, who keeps the museum oppidum of Tablinum, holds "
        "office for life. The Transylvania Chronicle kept there is the "
        "authoritative record of the Tribunal's history and its rulings.",
    ),
    (
        None,
        "Mercere votes",
        "By the terms of their covenant with the Tribunal, only Gifted "
        "Mercere vote at its meetings; in exchange the Tribunal lets the "
        "families of unGifted Redcaps grow as large as they like.",
    ),
    (
        None,
        "Hedge wizards and Laniena",
        "The Code's Join or Die provision applies to Gifted hedge wizards. "
        "The Tribunal's policy lets Laniena train Gifted children as "
        "Fectores, hunters who are not Hermetic magi, on the ground that "
        "trainees are outside the Order and so outside the Code; once "
        "trained, each is offered the Order's protection. Laniena knows it "
        "lasts only on sufferance, since the High Crime of depriving a "
        "magus of his magic could be charged whenever the Tremere wished.",
    ),
)


# -- the ruins and the good sites --

#: Each site: (key, name, region key in `transylvania.places`, realm,
#: aura, status, known, ruined, summary).
SITES: tuple[tuple[str, str, str, str, int, str, str, bool, str], ...] = (
    (
        "ruin_pannonia",
        "Pannonia's first site",
        "hungary",
        "Divine",
        0,
        "Known",
        "In the Tribunal",
        True,
        "Where Pannonia was founded, as a fortified covenant of House "
        "Tremere near the old meeting point of the Transylvanian, Greater "
        "Alps and Roman Tribunals. A powerful monastery was later built at "
        "the springs of the river the covenant drew its water from, and its "
        "Dominion destroyed the magic aura. Pannonia's magi scattered into "
        "camps, the first in the Tribunal to do so, and the magi of Old "
        "Histria now gather most of its old resources. The book gives no "
        "date and does not name the river or the monastery.",
    ),
    (
        "ruin_domostron",
        "Domostron's first site",
        "bulgaria",
        "Magic",
        0,
        "Known",
        "In the Tribunal",
        True,
        "The first home of Domostron, the covenant Tremere's Hermetic "
        "allies founded, later wrecked by raiders from the Theban Tribunal. "
        "The book gives neither date nor place; it is set here near the "
        "Theban border only as a guess.",
    ),
    (
        "kal_valley",
        "The Kal Valley and Lake Balaton",
        "hungary",
        "Magic",
        0,
        "Known",
        "In the region",
        False,
        "A secluded valley in the Tribunal's west, wild yet within reach of "
        "the great cities of Hungary and Italy. Hungarians use its name for "
        "the dullest place on earth, so a troupe can put anything there "
        "without disturbing the history it wants to keep. Close by lies "
        "Lake Balaton, the Tribunal's western gateway: never deeper than "
        "about three metres, ringed by rich farmland and on the main trade "
        "routes, so stories pass by its shores. One of chapter one's sites "
        "suggested for a new oppidum.",
    ),
    (
        "cakoc",
        "Cakoc",
        "hungary",
        "Magic",
        0,
        "Known",
        "In the region",
        False,
        "A town near the Kal Valley with an odd pull on dragons. Saint "
        "George killed a black beast here long ago and so ended the custom "
        "of feeding it girls. In 1220 a green dragon lives in the nearby "
        "mountains; it scares the folk and takes their sheep but does little "
        "worse, so no one knows whether it is Infernal. It can talk, though "
        "it seldom bothers, beyond telling a shepherd to keep his dog close "
        "or lose it (see the Bestiary for the dragons). One of chapter "
        "one's sites suggested for a new oppidum.",
    ),
    (
        "tomb_of_attila",
        "The Tomb of Attila",
        "hungary",
        "Magic",
        0,
        "Rumoured",
        "In the region",
        False,
        "Somewhere under the bed of the Tisza lies Attila, king of the "
        "Huns, whom the Magyars count as their forefather and the founder "
        "of Buda. His people turned the river aside by a canal to bury him, "
        "his warriors cut themselves and rode about his body singing "
        "laments, and he was sealed in coffins of iron, silver and gold; "
        "then every labourer was killed so the place would be forgotten. "
        "Among his grave goods may be the Sword of Mars, a weapon fallen from "
        "the sky that let him scourge the world. One of chapter one's sites "
        "suggested for a new oppidum.",
    ),
    (
        "klingsohr",
        "Klingsohr's fields by the Tisza",
        "hungary",
        "Magic",
        0,
        "Rumoured",
        "In the region",
        False,
        "The plain near the Tisza where the hidden bard Klingsohr wanders "
        "in peasant clothes, singing of Hungary's beauty to the empty "
        "fields. In 1207 the Margrave of Thuringia held a contest at "
        "Wartburg for the title of king of poetry, the losers to be put to "
        "death; Wolfram von Eschenbach beat Henry of Ofterdingen, who "
        "lamented that the one bard better than both was absent. Henry "
        "followed the songs that drift through Hungary's leaves, birds and "
        "storm clouds, which settle in the mind unbidden, and found "
        "Klingsohr, who cared nothing for prizes but came to save Henry's "
        "life. Crowned with bay by Wolfram, he had the death sentences "
        "lifted and foretold the Margrave's family's fate, which has come "
        "true in every point. He still foretells what is to come for anyone "
        "in need of it, or kind to him. One of chapter one's sites suggested for a new "
        "oppidum.",
    ),
    (
        "sunken_city",
        "The Sunken City",
        "bulgaria",
        "Magic",
        0,
        "Known",
        "In the region",
        False,
        "A Roman city that slid almost whole into the Black Sea, tied in "
        "ancient times to astronomers and their Mysteries. A covenant here "
        "would reach easily into Greek culture and trade, the Tribunal's "
        "heart and the lands east of the Order; many Black Sea islands "
        "nearby have strange myths of their own. On a modern map it is near "
        "Kavarna. One of chapter one's sites suggested for a new oppidum.",
    ),
    (
        "isle_of_achilles",
        "The Isle of Achilles",
        "bulgaria",
        "Magic",
        0,
        "Known",
        "In the region",
        False,
        "A small Black Sea island where Achilles was buried. His temples "
        "are fallen, but since some mystical event in Roman times his "
        "spirit, Helen's and those of some of their followers dwell there. "
        "No woman may land, and men only by day, sleeping aboard ship if "
        "they stay longer; Achilles kills any visitor of Trojan blood, and "
        "Trojan princes settled as far as Rome and Britain. Fishermen use it "
        "as a safe anchorage in storms, if they dare. Tremere and their "
        "companions come to talk war with Achilles, calmer now than in "
        "life, and others ask Helen where ancient cities and temples lay; "
        "some scholars think the two are the heart of a mystery cult, "
        "though House Tremere has no record of one. Most tellers place "
        "Achilles' grave elsewhere, but the local folk and several ancient "
        "authors put it here. One of chapter one's sites suggested for a "
        "new oppidum.",
    ),
    (
        "seventy_seventh_island",
        "The Seventy-Seventh Island",
        "bulgaria",
        "Faerie",
        0,
        "Rumoured",
        "In the region",
        False,
        "The seventy-seventh island of the Black Sea lies under a darkness "
        "so thick a spoon would stand up in it. At its heart grow three "
        "reeds: in the middle one is trapped a maiden said to be the "
        "fairest in the world, and in the other two her handmaids. A witch "
        "guards them who must die the moment the Reed Maiden goes free. "
        "Only a steed raised on dragon's milk, fed live coals and given fire "
        "to drink can pierce the dark. One of chapter one's sites suggested "
        "for a new oppidum.",
    ),
)


def _sites(transylvania: Transylvania) -> None:
    b = transylvania.b
    for key, name, _region, realm, aura, status, known, ruined, summary in SITES:
        transylvania.places[key] = b.place(
            name,
            ruined=ruined,
            summary=summary,
            realm=realm,
            aura=aura,
            status=status,
            known=known,
        )


# -- the docket --


def _docket(transylvania: Transylvania) -> None:
    b, tribunal = transylvania.b, transylvania.tribunal
    assert tribunal is not None
    b.case(
        tribunal,
        "The Valley of the Thracian Kings",
        kind="motion",
        brought_by="House Tremere's necromancers, with House Verditius",
        against="Benilda of Guernicus (Seuthopolis)",
        charge="Four years ago a Tremere necromancer serving as a hoplite "
        "found the burial ground of the ancient Thracian kings, close to "
        "Seuthopolis. The Tremere necromancers want it opened, and the "
        "Verditius too, for the Thracians honoured smith gods. Benilda, "
        "wary of necromancers in good spirits, bars the site; she knows the "
        "Tremere will win in the end and hopes to look first or to shape "
        "who digs and why.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Harco and the Tribunal's Redcaps",
        kind="motion",
        brought_by="The Transylvanian Mercere",
        against="House Mercere's leaders at Harco",
        charge="The Tremere want the Tribunal's true Redcaps increased by "
        "35, which Harco, with only 150 members in the whole House, sees as "
        "upsetting its balance. For now Harco accepts the heads of the "
        "Transylvanian Redcap families as members and their kin as close "
        "agents, whom the Tribunal calls Redcaps anyway; the truce may fail "
        "if the Roman side presses for control, and a new one needs "
        "brokering. Senior local Redcaps also want Volante to raise heirs "
        "rather than take a new Gifted leader from Harco each generation.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "A Portal from Old Histria to Venice",
        kind="motion",
        brought_by="The magi of Old Histria",
        charge="Magi have long talked of a Mercere Portal joining Old "
        "Histria to its chapter house in Venice, in the Roman Tribunal. If "
        "the Tribunal decides on it, the Praeco must carry it out: a special "
        "levy of vis, Redcaps guarding it on the road, a colona who cannot "
        "pay, promissory notes and envoys to Harco, where Old Histria's "
        "chief Redcap must argue for it, and the invested arch brought back "
        "from Harco.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Whether Laniena is lawful",
        kind="charge",
        brought_by="(not yet brought: magi who think it so)",
        against="Laniena (Lexander and Murat the Younger)",
        charge="Some magi hold that raising Gifted children as Fectores, "
        "denied Hermetic magic, makes their masters delinquent and deprives "
        "them of their magical power, a High Crime. Laniena answers that "
        "the trainees are not members of the Order, so the Code does not "
        "protect them, and that each is offered the Order's protection once "
        "trained. Tremere policy backs Laniena for now, but the charge "
        "waits for the day the House is displeased.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Murat of Terezin's secret",
        kind="charge",
        brought_by="(no one: it is not known)",
        against="Murat the Younger of Ex Miscellanea (Laniena)",
        charge=secrets(
            "Secret; a case can be brought only once someone finds out.",
            "Murat of Terezin, founder of the Fectores, was secretly a "
            "dhampir and rose as a vampire after his death; he now lives as "
            "a kukudhi far from Laniena with his fourth mortal wife, father "
            "of more than twenty dhampir children. Only his pupil Murat the "
            "Younger knows, and has let him be. If Lexander learns of it, "
            "House Tremere's anger could fall on the whole oppidum.",
        ),
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Gigas and Evredika's vis",
        kind="charge",
        brought_by="Evredika",
        against="Gigas (Theban Tribunal), or whoever is framing it",
        charge="A hunting party led by a nobleman with a pet white wolf has "
        "stripped every one of Evredika's vis sources. Gigas, House "
        "Tremere's thinly hidden cat's paw in the Theban Tribunal, was told "
        "to leave Evredika's claims alone and seems the likeliest thief; if "
        "its denials are honest, someone is setting it up, and the question "
        "is who and why. A matter between two Tribunals.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "The papal legate and the Scholomance",
        kind="motion",
        brought_by="(the Tribunal's concern)",
        against="A papal legate lodged with the Teutonic Knights",
        charge="Legends of the Devil's School have reached Rome, and a "
        "legate has come to look into the Scholomance and its supposed "
        "diabolism, staying with the Teutonic Order while he builds his "
        "case. So far he has only hearsay, since only magi and former "
        "pupils know anything real; the Tribunal must decide how to keep it "
        "so without breaking the Code.",
        filed_year=1220,
        filed_season="Spring",
    )


# -- after every part has built --

#: Every living magus the book names, by slug, in the order of their
#: oppida; magi other parts make beyond these are added after them.
NAMED_MAGI: tuple[str, ...] = (
    # Coeris.
    "poena",
    "angiola",
    "dominic",
    "horatius",
    "janus",
    "isaac",
    "juturnus",
    "tatiana",
    "monica",
    # Laniena.
    "lexander",
    "murat",
    # Evredika.
    "oeagrus",
    "bozhidar",
    "yekaterina",
    # Seuthopolis.
    "benilda",
    "caledonia",
    "saturnino",
    "scipio",
    "terencia",
    "vigilia",
    # Tablinum.
    "nestor",
    "demetrius",
    "theodora",
    "theodore",
    # Old Histria and Shrouded Bay.
    "accursius",
    "leontine",
    "pahniro",
    "placido",
    "priscilla",
    "volante",
    "merit",
    # Lycaneon.
    "albertus",
    "arhmina",
    "clement",
    "phillip",
    "zalmoxis",
    # The Scholomance.
    "simium",
    "andrew",
    # Kezdö Válasz.
    "essedarius",
    "leona",
    "adulio",
    "neculai",
)

#: What finish could not find, for the report.
MISSING: list[str] = []


def _magus(transylvania: Transylvania, slug: str, role: str) -> Character | None:
    found = transylvania.magi.get(slug)
    if found is None:
        MISSING.append(f"{slug} ({role})")
    return found


def finish(transylvania: Transylvania) -> None:
    tribunal = transylvania.tribunal
    assert tribunal is not None
    saga = transylvania.b.saga
    MISSING.clear()

    praeco = _magus(transylvania, "albertus", "the Praeco")
    quaesitor = _magus(transylvania, "benilda", "the Presiding Quaesitor")
    tribunal.praeco_id = praeco.id if praeco is not None else None
    tribunal.quaesitor_id = quaesitor.id if quaesitor is not None else None

    members = package.entries(tribunal, package.KEY, "members")
    members.clear()
    seen: set[str] = set()
    order = [
        *NAMED_MAGI,
        *(k for k in transylvania.magi if k not in NAMED_MAGI),
    ]
    for slug in order:
        character = transylvania.magi.get(slug)
        if character is None:
            if slug in NAMED_MAGI:
                MISSING.append(f"{slug} (privilege)")
            continue
        if character.type != "magus" or character.id in seen:
            continue
        seen.add(character.id)
        privilege, office = transylvania.privileges.get(slug, ("", ""))
        entry: dict[str, Any] = {"character_id": character.id}
        if privilege in package.PRIVILEGES:
            entry["privilege"] = privilege
        elif privilege:
            MISSING.append(f"{slug} (privilege {privilege!r})")
        entry["office"] = office
        members.append(entry)

    aediles = package.aediles(tribunal)
    aediles.clear()
    for covenant_slug, magus_slugs in transylvania.aediles.items():
        covenant = transylvania.covenants.get(covenant_slug)
        if covenant is None:
            MISSING.append(f"covenant {covenant_slug} (aediles)")
            continue
        chosen = []
        for slug in magus_slugs[: package.AEDILES]:
            character = _magus(transylvania, slug, f"aedile of {covenant_slug}")
            if character is not None and character.id not in chosen:
                chosen.append(character.id)
        if chosen:
            aediles[covenant.id] = chosen

    for key, _name, region, *_ in SITES:
        site, around = transylvania.places[key], transylvania.places.get(region)
        if around is None:
            if f"region place {region!r}" not in MISSING:
                MISSING.append(f"region place {region!r}")
        elif site.place_id is None:
            site.place_id = around.id

    tribunal.covenants_total = len(
        [c for c in saga.covenants if c.tribunal_id == tribunal.id]
    )
    tribunal.magi_total = max(
        MAGI_TOTAL,
        len(seen)
        + sum(c.unnamed_magi for c in saga.covenants if c.tribunal_id == tribunal.id),
    )
