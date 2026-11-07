"""The Greater Alps Tribunal itself: the record and its summary (a
Roman-minded Tribunal of rich old covenants that limits its own numbers,
buys chairs with vis, ostracises one magus a meeting and exports its
young), the Peripheral Code with the three rulings The Wizard's Grimoire
dates, the meetings and events the books date in the Diary, and the
Hermetic year in the calendar (build); then the Praeco, the chief
Quaesitor, the chairs each covenant holds and the Tribunal's totals
(finish).

Keys: the Praeco is magi["constance"] and the chief Quaesitor
magi["athena"] (covenants)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.seasons import YEARLY
from ...tribunal_packages import alps as package
from ..builder import paragraphs, titled

if TYPE_CHECKING:
    from .state import Alps

NAME = "The Greater Alps Tribunal"
#: The book's own counts: seven public covenants and about a hundred
#: magi (pp. 4, 24).
COVENANTS_TOTAL = 7
MAGI_TOTAL = 100
MEETING_PLACE = "The Covenant of the Icy North"

SUMMARY = paragraphs(
    "The Order's Tribunal of the high mountains, from Savoy and Geneva in "
    "the west through the Swiss lands, Rhaetia and the Dolomites to "
    "Bavaria, Salzburg, Carinthia and the Austrian marches in the east. "
    "Three Founders' domus magnae lie in or beside it, and its culture is "
    "old, proud and self-consciously Roman: its magi think of themselves "
    "as a senate of the wealthy, dress in stola and toga at formal "
    "occasions, and hold themselves aloof from the rest of the Order.",
    "A rich Tribunal that keeps itself rich by keeping itself small. Vis "
    "is plentiful because the covenants have limited their people to "
    "what their sources can bear: no new covenant has been allowed for "
    "centuries, and a magus votes only if his covenant has bought him a "
    "chair, pledging ten pawns of vis a year to his upkeep. Instead of "
    "new covenants the old ones keep chapters, lesser houses near useful "
    "resources, and trade them among themselves. The covenants live by "
    "trading services to one another (longevity potions, books, enchanted "
    "goods, beasts), so each has an interest in the peace, and war "
    "between covenants, which the Code calls disorder, is lawful but "
    "almost unthinkable.",
    "There are about a hundred magi in seven public covenants, and they "
    "live long: about three are recruited every two years. The young "
    "find it hard to be their own masters here, so most are sent away "
    "after their Gauntlet to the frontier Tribunals, Hibernia, the "
    "Levant, Novgorod, and called back decades later if they have "
    "proved worth a chair. The Tribunal exports its trouble this way, "
    "and seeds covenants at the Order's edges.",
    "Old grudges: an unofficial ill will toward House Tremere, dating "
    "from the Sundering and refreshed by the vampiric corruption, and a "
    "watch on the borders, where magi of the Rhine and Transylvania raid "
    "Alpine vis sources and the Bavarian Common. The Tribunal backs "
    "Novgorod against the Tremere.",
    "The meeting. It meets every seven years, most often at the "
    "motherhouse of the Covenant of the Icy North in Bavaria, which every "
    "covenant but Sinews of Knowledge prefers to the Praeco's home, and "
    "which was built to hold it. The first business is the ostracism; "
    "the Quinquennial Games follow a meeting. The Wizard's Grimoire dates "
    "rulings of the Tribunal to 1165 and 1194, which puts the meetings in "
    "1200, 1207 and 1214 and the next in 1221; the book gives no season, "
    "and autumn is taken here, as the Liberalia is forgone in a "
    "Tribunal's year and the Games, which follow it, fall in November. "
    "Informal and Quaesitorial tribunals meet at the Midsummer Fair each "
    "June.",
    "Officers. The Praeco is the eldest magus: the book makes La, then "
    "Prima of Criamon, Praeco, but she has since been ritually slain and "
    "Muscaria is Prima, so the eldest living magus whose age is given, "
    "Constance of Valnastium, is taken as Praeco here. The chief "
    "Quaesitor is Athena Alpina of Guernicus, Cato her deputy; Archmage "
    "Pietro of Flambeau is the lictor, the hoplite who leads a Wizard's "
    "March and carries the judges' symbols at the meeting.",
)

SECRETS = [
    titled(
        "Athena Alpina's ostracism",
        "Athena Alpina's even-handedness toward House Tremere, which her "
        "neighbours call blatant favouritism, may see her ostracised at the "
        "next meeting.",
    ),
    titled(
        "Why Cato came to the Alps",
        "Cato was sent to the Alps partly to make sure that, if Athena "
        "Alpina goes, Adrasteia of Tytalus does not become chief Quaesitor.",
    ),
    titled(
        "The dragon under the Alps",
        "A myth runs through the Alps that the mountains lie across the spine "
        "of a dragon so large it eats other dragons, and that widespread "
        "disorder would wake it. Few magi believe it wholeheartedly.",
    ),
]

#: The Peripheral Code: (year or None, title, what it says).
RULINGS: tuple[tuple[int | None, str, str], ...] = (
    (
        None,
        "Chairs and vagrancy",
        "A magus votes at the Tribunal only if his covenant has bought him "
        "a chair: it declares a permanent vis source, has the Quaesitores "
        "assess it, and pledges ten pawns a year of it to his upkeep, at "
        "least a year before the meeting if he is to vote. The vis is not "
        "paid to anyone; the pledge shows the covenant will not poach from "
        'its neighbours. Vis distilled from an aura ("farming") does not '
        "count. A magus with no chair is a vagrant, a Low Crime, though a "
        "chair registered at any time protects him from its punishments. "
        "A chair belongs to the covenant, whose council fills it when its "
        "magus leaves.",
    ),
    (
        None,
        "The yearly pawn",
        "Each covenant pays a pawn of vis a year to the senior members of "
        "Houses Guernicus and Mercere in the Tribunal. It began as a "
        "tradition and entered the Code; it was once a pawn for each magus.",
    ),
    (
        None,
        "Vis treaties",
        "Gifts of vis exchanged so often between two covenants that both "
        "sides want the supply guaranteed are ratified as treaties and "
        "entered in the Code; they are delivered in Frustration Week. A "
        "treaty's income may pay for a chair, but vis owed away may not.",
    ),
    (
        None,
        "No new covenants",
        "No new covenant may be founded unless it can show that, after its "
        "costs, it can spend ten pawns a year on each magus from sources "
        "no one else has claimed, and a pawn for the Quaesitores and "
        "Redcaps. None has been allowed for centuries; the Tribunal grows "
        "by chapters instead.",
    ),
    (
        None,
        "Ostracism",
        "As the first business of each meeting every magus writes on a "
        "sherd the name of the magus he most despises, or leaves it blank. "
        "If at least one magus in four named the one with the most sherds, "
        "that magus must leave the Greater Alps before the second full "
        "moon, for twenty-one years, or be Marched. The exile ends the day "
        "before a Tribunal. An ostracised Praeco is replaced by the next "
        "eldest, with no second vote; an ostracised chief Quaesitor by his "
        "deputy. An ostracised magus may hand the sigils he carries, his "
        "own aside, to another magus.",
    ),
    (
        None,
        "Amaranth",
        "All amaranth, the faerie flower that addicts magi, is to be "
        "destroyed. The traffic goes on, around Ingolstadt above all; the "
        "neighbouring Tribunals have not banned it, and the Grand Tribunal "
        "has never been asked.",
    ),
    (
        None,
        "Churches the Code protects",
        "The city of Constance and the monasteries of the Great and Little "
        "Saint Bernard passes, vital to the Redcaps and favoured by House "
        "Jerbiton, are named in the Code as places where even minor "
        "violence is judged interference with the Church.",
    ),
    (
        None,
        "Flagrant spending",
        "Covenants may not draw attention to themselves by making goods "
        "from vis to sell. The ruling was aimed at Sinews of Knowledge, "
        "which was ordered to stop its trade.",
    ),
    (
        None,
        "Pilate's ghost",
        "No magus may harvest vis from the ghost of Pontius Pilate on "
        "Mount Pilatus. The meeting that made the ruling also sent its "
        "condolences to the sodales of the magi crushed by the avalanche "
        "that spoiled the first attempt.",
    ),
    (
        None,
        "The Bavarian Common",
        "After the Sundering of Tremere destroyed the covenant of Highest "
        "Aspiration, several covenants raced to claim its resources. An "
        "emergency meeting gave its vis sources to the Quaesitores to "
        "harvest and divide among the covenants each year, and disbanded "
        "every rival chapter house in Bavaria but the Icy North's. The "
        "Common supports two chairs, for the quaesitor and the hoplite who "
        "keep it.",
    ),
    (
        None,
        "The estates of Tarragon Vale",
        "No estate of Tarragon Vale's vanished magi may be settled without "
        "proof of their deaths; until then the Quaesitores keep the "
        "covenant's vis income, spending only what its Aegis and its "
        "Shrouded Glen need. The heirs have pressed the matter at a meeting, "
        "and the Quaesitores' position was upheld pending further "
        "evidence.",
    ),
    (
        1165,
        "A sanctum a season",
        "Snadstrich of Ex Miscellanea, of no covenant, was said to have "
        "moved her sanctum seven times in one year. The Tribunal ruled that "
        "a magus may not establish a new sanctum more than once a season "
        "(The Wizard's Grimoire).",
    ),
    (
        1194,
        "Andru's pardon",
        "A faerie lord took grogs and covenfolk of Valnastium to use as "
        "pieces in a great game of his; its magi rescued them, killing "
        "many faeries. Andru argued that every magus may defend his "
        "property, servants included, and that the rescue was self-defence; "
        "the Tribunal narrowly accepted it and pardoned him (The Wizard's "
        "Grimoire; Sanctuary of Ice calls it a just war on one of the "
        "faerie kings of Val Fanes, and gossip says Andru claimed a "
        "summer prince's crown in it).",
    ),
    (
        1194,
        "Syrestis's fine",
        "Syrestis of Bjornaer, visiting covenants of the Greater Alps, "
        "killed livestock and game in his animal shapes, harming his "
        "hosts' relations with their neighbours. Both the Rhine and the "
        "Greater Alps heard the case: the Rhine fined him three pawns, the "
        "Greater Alps ten. A quaesitor ruled that he must pay the Greater "
        "Alps, where the crimes were done, and owed the Rhine nothing (The "
        "Wizard's Grimoire).",
    ),
)

#: The Diary: (year, season, title, details).
EVENTS: tuple[tuple[int, str, str, str], ...] = (
    (
        865,
        "Summer",
        "Sinews of Knowledge awarded",
        "The Grand Tribunal of 865 awards the site of the dead god's "
        "priesthood, sealed by House Guernicus since the Sundering, to "
        "Sancia filia Sabrina, who founds the Longevity Project there.",
    ),
    (
        1165,
        "Autumn",
        "A sanctum a season",
        "The meeting rules on Snadstrich's seven sancta in a year.",
    ),
    (
        1194,
        "Autumn",
        "Andru pardoned, Syrestis fined",
        "The meeting narrowly accepts Andru's defence of Valnastium's "
        "rescue of its servants from a faerie lord, and fines Syrestis of "
        "Bjornaer ten pawns.",
    ),
    (
        1198,
        "Spring",
        "The Vanishing Away",
        "The four magi of Tarragon Vale and its covenfolk vanish without a "
        "trace. The Quaesitores begin keeping its vis.",
    ),
    (
        1206,
        "Summer",
        "Athena Alpina made chief Quaesitor",
        "The Primus of Guernicus appoints Athena Alpina, trained in the "
        "Roman Tribunal, chief Quaesitor of the Alps.",
    ),
    (
        1214,
        "Autumn",
        "Athena sends away her hoplite",
        "At the meeting Athena is forced to send away one of her hoplites, "
        "a Tremere maga.",
    ),
    (
        1215,
        "Spring",
        "The Sicilian children",
        "A magical accident in Sicily brings about the birth of two dozen "
        "Gifted children at once.",
    ),
    (
        1217,
        "Spring",
        "Kentigern arrives",
        "Kentigern of Ex Miscellanea, newly retrained at Magvillus, joins "
        "the Quaesitores at the Icy North motherhouse.",
    ),
)

#: The Hermetic year, for the calendar: (title, season, note).
CALENDAR: tuple[tuple[str, str, str], ...] = (
    (
        "The Liberalia",
        "Spring",
        "The March feast, the Festival of Welcome of Houses of Hermes: "
        "Societates, at which the year's new magi are welcomed and "
        "Jerbiton petitions are heard. Valnastium sponsors it, mostly at "
        "Tarragon Vale; it is forgone in a Tribunal's year.",
    ),
    (
        "Frustration Week",
        "Spring",
        "In April, when the covenants deliver the vis their treaties owe.",
    ),
    (
        "The Midsummer Fair",
        "Summer",
        "The 3rd to the 10th of June at the Icy North motherhouse: the "
        "Quaesitores divide the Bavarian Common, covenants bid in Vim vis "
        "at inverse auctions, magi trade and socialise, and informal and "
        "Quaesitorial tribunals sit.",
    ),
)


def build(alps: Alps) -> None:
    b = alps.b
    alps.tribunal = tribunal = b.tribunal(
        NAME,
        package=package.ALPS.key,
        summary=SUMMARY,
        secrets=SECRETS,
        meets_every=7,
        next_year=1221,
        next_season="Autumn",
        meeting_place=MEETING_PLACE,
        covenants_total=COVENANTS_TOTAL,
        magi_total=MAGI_TOTAL,
    )
    for year, title, says in RULINGS:
        b.ruling(tribunal, title, year, says)
    for year, season, title, details in EVENTS:
        b.event(tribunal, year, title, details, season=season)
    for title, season, note in CALENDAR:
        b.calendar(title, 1220, season, repeats=YEARLY, note=note)
    b.calendar(
        "The Quinquennial Games",
        1221,
        "Autumn",
        note="The November games held after a Tribunal's meeting, if one is "
        "due that year; Decennial and Secular games mark the longer "
        "cycles.",
    )


#: The chairs each covenant has registered, as the members the book gives
#: it: the Cave's twenty-two, the Icy North's nineteen with the Bavarian
#: Common's two, Journeys End's eight, Sinews of Knowledge's six and
#: Valnastium's traditional twenty-one with the Bonisagus chair. Tarragon
#: Vale's are held in abeyance.
CHAIRS = {
    "cave": 22,
    "icy_north": 19,
    "journeys_end": 8,
    "sinews": 6,
    "valnastium": 21,
    "tarragon_vale": 0,
}


def finish(alps: Alps) -> None:
    tribunal = alps.tribunal
    assert tribunal is not None
    saga = alps.b.saga
    praeco, quaesitor = alps.magi.get("constance"), alps.magi.get("athena")
    tribunal.praeco_id = praeco.id if praeco is not None else None
    tribunal.quaesitor_id = quaesitor.id if quaesitor is not None else None
    for key, held in CHAIRS.items():
        covenant = alps.covenants.get(key)
        if covenant is not None:
            package.chairs(tribunal)[covenant.id] = held
    resident = [c for c in saga.covenants if c.tribunal_id == tribunal.id]
    ids = {c.id for c in resident}
    named = [m for m in saga.characters if m.type == "magus" and m.covenant_id in ids]
    tribunal.covenants_total = max(COVENANTS_TOTAL, len(resident))
    tribunal.magi_total = max(
        MAGI_TOTAL, len(named) + sum(c.unnamed_magi for c in resident)
    )
