"""The Hibernian Tribunal itself: the record and its summary (the meeting
on the Hill of Tara, the Sacred Council, the honey, the mantles, the
two languages, the "Younger House", the English Council and the
macgnímartha), the island of Ireland as the Tribunal's region, the
Peripheral Code and its customs with the past rulings of 980, 1186, 1193
and 1195, the docket for the meeting of 1221, the ruins of the Schism War
and the lost covenant of Uisneach, the Ordo Hiberniae and the English
Council as factions, and Cú Chonnacht, the independent Bjornaer (build);
then the Praeco and the Presiding Quaesitor, the package's cathaigh,
ambassadors, treaties and túatha, each ruin's province, each covenant's
leaning, and the Tribunal's totals (finish, once the parts that make the
provinces, covenants and magi have built); and Cú Chonnacht's generated
stats (stats).

Keys: places["ireland"]; the ruins are places["ruin_salmons_eye"],
["ruin_widows_throat"], ["ruin_lughs_retreat"], ["ruin_warblers_way"],
["ruin_diedne_vigil"] and ["ruin_uisneach"]; the factions are
world["ordo_hiberniae"] and world["english_council"]; the independent
magus is magi["cu_chonnacht"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models import new_instance_id
from ...tribunal_packages import hibernia as package
from ..builder import paragraphs, secrets
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Character, Covenant, Neighbour
    from . import Hibernia

NAME = "The Hibernian Tribunal"
#: The magi the book counts in the nine covenants (8 at Circulus Ruber,
#: 6 at Cliffheart, 3 at Elk's Run, 6 at Ashenrise, 3 at Lámbaird, 3 at
#: the Paruchia, 6 at Praesis, 7 at Qui Sonant and 6 at Vigil); the
#: Redcaps of the two Mercer Houses and the independent magi are not
#: residents at law.
MAGI_TOTAL = 48
#: The covenants at law: the Mercer Houses keep no cathach and are not
#: counted.
COVENANTS_TOTAL = 9
MERCER_HOUSES = ("leth_moga", "leth_cuinn")

SUMMARY = paragraphs(
    "The Tribunal of the whole island of Ireland, on the western rim of "
    "Mythic Europe: five provinces, Connacht, Leinster, Munster, Ulster and "
    "Meath at the centre, where tribal kingdoms under hereditary Irish kings "
    "share the land with English lords who have seized much of it since the "
    "invasion of 1169 and 1170. The Order came in 778 and was ruled from "
    "Britannia for a time, then left in 898 to stand on its own; its Code "
    "took shape in the ninth century and has barely changed since. Hibernia "
    "has no domus magna, and most of the Order thinks it backward and odd.",
    "A Tribunal of conflict. Tytalus and Merinita magi founded it, and its "
    "customs reward rivalry: Wizard War is easy to declare, certamen is "
    "common, grogs raid rival covenants, and a covenant that cannot hold its "
    "land is thought unworthy of it. The art is to dominate, not to kill. "
    "The deepest split is between the native magi, who call themselves the "
    "Ordo Hiberniae, and the continental newcomers they call the English, "
    "who have come over the last fifty years to claim land and reform the "
    "Code. The fall of Praesis to the English in a year-long Wizard War is "
    "the question every magus now turns on.",
    "Covenants and their cathaigh. A covenant is recognised by the Praeco "
    "once it has held land, cattle and a cathach, a storied magical trophy "
    "it took rather than made, for a year, and its name is entered at Leth "
    "Moga. It votes only while it brings the cathach to the meeting. There "
    "are nine covenants and two Mercer Houses, Leth Moga in the south and "
    "Leth Cuinn in the north, which are not covenants at law. A magus who "
    "lives outside a covenant is a vagrant with no vote. Dozens of covenants "
    "have fallen over the centuries, so a new one can rarely be sited with "
    "fewer than a dozen ruins within a day's ride.",
    "The meeting. Every seven years the magi gather on Meath's Hill of Tara, "
    "Cnoc na Teamhrach, in the great ráth round the Lia Fáil. The "
    "last meeting was in 1214, which Praesis, under siege, could not attend, "
    "so the next is in 1221; the book gives no season, so summer is "
    "assumed. Circulus Ruber arranges each one and raises a camp by magic "
    "for the seven days and nights it lasts: hearths smoking, banners, "
    "servants and familiars everywhere, a fire pit and food kept by each "
    "covenant, bards wandering between them and fine weather held by spells. "
    "Covenants bring all the consortes and custodes they can, to look "
    "strong. Business is done in Latin, but Irish is what is heard between "
    "sessions. Indrechtach of the Paruchia, a Hermetic member of the Céli "
    "Dé, opens and closes the meeting with prayers and blessings.",
    "The Sacred Council. Before the meeting opens, the Praeco, the "
    "Presiding Quaesitor and invited magi meet the embassies of the hedge "
    "wizards, the faeries and the magical beasts, hear their quarrels, and "
    "confirm each faction's ambassador. Those ambassadors hold a voting "
    "sigil for the meeting and their votes count as any magus's: Fothaid "
    "for the Fir Bolg, Ainid for the Fomórach, the Eagle King for the beasts "
    "of magic, Mug Ruith for the Tuatha Dé, and an ambassador the Coill Trí "
    "choose. House Merinita speaks for faeries who send no one. The English "
    "have argued against these votes at every meeting since they came.",
    "The English Council. The magi not born to Hibernia meet on their own "
    "at the start of each meeting to agree a common line, usually on "
    "reforming the Code, and lately on the aggression of Lámbaird. They "
    "find agreement hard and lack a leader able to see past Praesis.",
    "Customs. Bees matter to an Irish covenant, each covenant's honey "
    "tastes of its own place, and the magi trade jars of it at every "
    "meeting, which the continental magi find quaint. The Ordo Hiberniae "
    "wear patchwork mantles by rank: an apprentice one colour, one in the "
    "macgnímartha three, a magus five, a covenant's head six and the Praeco "
    "seven; the newcomers dress as at home. Irish magi call House Ex "
    "Miscellanea the Younger House, since it was the last formed, and its "
    "newly arrived members dislike it. Irish glosses in Hermetic books cost "
    "a reader who has no Irish the usual +1 for quality. The Ordo loves "
    "Vitae Magorum, lives of great magi written as Order of Hermes Lore, "
    "and the Hermetic Computus, Artes Liberales tractatus for reckoning "
    "durations, moons and laboratory work. Vis is left where it lies until "
    "it is needed, so few covenants keep much in store, and many sources "
    "are made casting places.",
    "The macgnímartha. Between apprenticeship and the Oath a young Irish "
    "magus spends a year or so on 'youthful exploits', away from the parens "
    "and outside the Code, without the Parma Magica. Most test themselves "
    "against faeries, some against mundanes or other magi, and what they "
    "steal from covenants is usually ransomed back. The treaty with the "
    "Coill Trí is silent about them, so they often slip into Connacht. "
    "Each comes back with a Reputation of 1 for how they behaved, and some "
    "choose a year of service at Leth Moga instead.",
    "The officers. The Praeco is Milvia of House Bonisagus, of Circulus "
    "Ruber, aged 164, who has held the office for the last four meetings; "
    "Visioturpis of House Guernicus, Hibernia's oldest Quaesitor, also of "
    "Circulus Ruber, presides. Conán Derg of Merinita, the eldest magus, "
    "gave up the office in 1186 after losing an arm. Hibernia keeps few "
    "hoplites: every covenant is expected to defend itself and lend its "
    "strength to the Tribunal.",
)


def build(hibernia: Hibernia) -> None:
    b = hibernia.b
    hibernia.tribunal = tribunal = b.tribunal(
        NAME,
        package=package.KEY,
        summary=SUMMARY,
        meets_every=7,
        next_year=1221,
        next_season="Summer",
        meeting_place="the Hill of Tara",
        covenants_total=COVENANTS_TOTAL,
        magi_total=MAGI_TOTAL,
    )
    _ireland(hibernia)
    for year, title, says in RULINGS:
        b.ruling(tribunal, title, year, says)
    _ruins(hibernia)
    _docket(hibernia)
    _factions(hibernia)
    _cu_chonnacht(hibernia)


# -- the island --


def _ireland(hibernia: Hibernia) -> None:
    hibernia.places["ireland"] = hibernia.b.place(
        "Ireland",
        status="Known",
        known="In the Order",
        summary=paragraphs(
            "Mythic Ireland, the whole island and the Hibernian Tribunal's "
            "region, steeped in magic: enchanted lakes and woods, faerie "
            "hosts, hags, giants, beasts that speak, saints who take "
            "vengeance and demons. Its five provinces are Connacht in the "
            "west, Leinster in the east, Munster in the south, Ulster in the "
            "north and Meath between them; the Eiscir Riada splits it into "
            "Leth Cuinn, Conn's Half, to the north and Leth Moga, Mogha's "
            "Half, to the south, and the two Mercer Houses are named for "
            "them.",
            "The English came in 1169 and 1170 and their settlers live "
            "mostly in the south-east; Irish kings rule the rest, and no one "
            "is strong enough to keep the peace, so lords raid one another "
            "and make and break alliances as it suits them. The Lord of "
            "Ireland is King Henry III of England, aged 14, whose regent is "
            "William Marshal the younger, his father having died in 1219.",
            "The druids' heirs, hedge wizards of many traditions, are too "
            "many and too stubborn to be made to join the Order. Most live "
            "in Connacht, which the Treaty of Cnoc Maol Réidh closes to "
            "covenants, and many belong to the Coill Trí, a league that "
            "mimics the Order. The elder races, the Fomórach, the Fir Bolg "
            "and the Tuatha Dé, are the Order's allies, and Ireland's "
            "history, its people say, keeps repeating: each people to come "
            "has driven the last into a corner, and the native magi fear "
            "that the English magi will drive them into Connacht in turn.",
        ),
    )


# -- the Peripheral Code and the Tribunal's customs --

#: The Peripheral Code and the customs the book gives as law: (year or
#: None, title, what it says).
RULINGS: tuple[tuple[int | None, str, str], ...] = (
    (
        898,
        "The Treaty of Cnoc Maol Réidh",
        "At its first meeting as a Tribunal of its own, Hibernia made the "
        "Treaty with the hedge wizards of Connacht binding, with every "
        "private treaty then standing between a druid and a magus. Most of "
        "the Code is made of treaties like it: particular bargains between "
        "named parties, not general rules, so a Munster case of 1134 need not "
        "decide a like case in 1220. The English call this unworkable and ask "
        "for change at every meeting. Its clauses are on the Treaties list.",
    ),
    (
        None,
        "Treaties",
        "Anyone with the right to be heard at Tribunal may make a treaty: a "
        "magus, a covenant, the Order, the Tuatha Dé, the Coill Trí and so "
        "on. A treaty may be for a time, for ever, or until a stated "
        "condition frees the parties. The parties reach it themselves with a "
        "Quaesitor's help, and the Tribunal's part is to see that they agree. "
        "No treaty may break the Code or bind a magus against the Oath. A "
        "hedge wizard who wants a treaty or a hearing needs the Coill Trí to "
        "sponsor him, and faeries and beasts treat only through their "
        "ambassador.",
    ),
    (
        None,
        "Founding a covenant",
        "Any magus may found a covenant by proving land, wealth and a "
        "cathach: a place to live that the magi have defended for a year, "
        "cattle (Ireland's old measure of wealth), and the trophy. Once all "
        "three have been held a year the covenant asks the Praeco to "
        "recognise it, its name and lands are written down at Leth Moga, and "
        "the Redcaps begin to call. Others may try to take the cathach in "
        "that year, and if they do the covenant cannot form; they must keep "
        "to the Code and may harm no resident without Wizard War.",
    ),
    (
        None,
        "The cathach",
        "A cathach must answer to Intellego Vim as magical, though not "
        "necessarily Hermetic; it must have been taken, from the land, the "
        "magic realm or another magus, and how it was won becomes part of "
        "the covenant's story; it must be storied, legendary itself or made "
        "by a famous hand; and it must be shown at each meeting and be kept "
        "outside the Aegis of the Hearth between them. The custom goes back to "
        "the four founders of Circulus Ruber, who swore to hold their land "
        "and its treasures for a year. Great families keep cathaigh too.",
    ),
    (
        None,
        "Holding another's cathach",
        "A magus found with a cathach another covenant justly claims is "
        "treated as if caught in a sanctum and loses his immunity, and the "
        "same holds for its cattle. A thief who means to claim the robbed "
        "covenant's resources must keep the cathach a year against all "
        "comers. Stealing every cathach could leave the meeting without a "
        "quorum, though magi without one can still be heard through allies "
        "who kept theirs.",
    ),
    (
        None,
        "Representation and votes",
        "No magus is represented without his covenant, and no covenant "
        "without its cathach, which must be carried to the meeting and kept "
        "on show. A magus whose covenant shows it has one vote and may lend "
        "it as a proxy as elsewhere.",
    ),
    (
        None,
        "Residency and vagrants",
        "A magus is resident, and votes, only through a recognised covenant. "
        "One outside any covenant is a vagrant, however long he has lived in "
        "Ireland: no Redcaps call, he has no voice, his property has no "
        "protection, and he may be exiled. Many solitary magi live so all "
        "the same; to vote, one must found a covenant of one, with land, "
        "cattle and a cathach.",
    ),
    (
        None,
        "No chapter houses or vassals",
        "Hibernia recognises neither chapter houses nor liege and vassal "
        "covenants. A magus who would leave his covenant must join or found "
        "another, or give up the Tribunal's protection.",
    ),
    (
        None,
        "A covenant's lands",
        "A covenant's lawful lands are its vis sources: all those a magus can "
        "walk round between sunrise and sunset, using no spell or enchanted "
        "device to go faster. Raiding them is depriving a magus of his magical "
        "power. Everything outside is common land: a covenant may mark a "
        "source there with its symbol, but must defend it itself, and "
        "certamen is often fought over such sources.",
    ),
    (
        None,
        "Forfeiting immunity",
        "Slaying a magus outside Wizard War is a High Crime, with the usual "
        "defences. A magus forfeits his immunity by trying to take an "
        "apprentice from a covenant, taking a cathach, entering a sanctum, "
        "attacking a familiar, or raiding a covenant's protected vis.",
    ),
    (
        None,
        "Declaring Wizard War",
        "War is declared in person, in public and before witnesses, though "
        "not necessarily to its target, and it starts a month later; no "
        "letter of warning is needed. A declaration kept from its target on "
        "purpose has been ruled void. One declaration may name several "
        "enemies, and draw in the allies of either side, as in a war on "
        "'Meadhbh and all who hold to the Gáe Bulg'.",
    ),
    (
        None,
        "Extended Wizard War",
        "No pause is required between months of War, and the Code presumes "
        "a War extended unless it is shown otherwise, so it lasts until one "
        "side dies, yields or makes a treaty. Most such Wars sink into raids "
        "and theft, fought by grogs and hired men, until someone calls a "
        "truce; submission is the aim more often than death.",
    ),
    (
        None,
        "Certamen",
        "The aggressor names the Technique and the defender the Form, as the "
        "Definitive Edition already has it; the Hibernian custom is that "
        "neither may veto the other's choice, and nothing limits who may "
        "challenge, when, or how often. Refusing a challenge shames a magus "
        "as anywhere, but using vis in a duel carries no stigma.",
    ),
    (
        None,
        "The ambassadors",
        "The Tribunal holds itself the magical authority over all Ireland, so "
        "each recognised supernatural faction may send a voting ambassador, "
        "confirmed at the Sacred Council and given a sigil for the meeting; "
        "its vote counts as any magus's. The Tuatha Dé confirm theirs at the "
        "Council; the Fomórach and the Fir Bolg send royal kin; other "
        "faeries may send one or be spoken for by House Merinita; beasts of "
        "magic who speak and understand men may choose one, or a magus "
        "stands for them. The Infernal has never tested this right.",
    ),
    (
        None,
        "Speaking creatures",
        "A creature that speaks any human tongue counts as a man and may be "
        "represented at Tribunal: no covenant should harm it or take from "
        "its territory without leave or a fair return. Even the Ordo "
        "Hiberniae keeps this loosely.",
    ),
    (
        None,
        "Allies of the Order",
        "The Fomórach, the Tuatha Dé, the Fir Bolg and, by the Treaty, the "
        "Coill Trí are the Order's allies, and must be warned of Wizard War "
        "as a magus would be, so they can make terms first. A hedge wizard "
        "too must be declared on before he is attacked; killing one without "
        "it is assaulting the Order's allies. Magi who declared War on 'all "
        "hedge wizards' have been talked into letting it lapse.",
    ),
    (
        None,
        "The rights of hedge wizards",
        "A hedge wizard may claim one protected vis source; any others he "
        "uses are common land. Redcaps must carry the Order's messages to "
        "the Coill Trí as to any covenant, but visits to single hedge "
        "wizards are a courtesy. A hedge wizard may ask a covenant to take "
        "him in, and is then expected to swear the Oath and join the "
        "Younger House.",
    ),
    (
        None,
        "Mundane interference",
        "Hibernia's Quaesitors take the Transitionalist view: in so small a "
        "Tribunal, with magi born among the people and kings long used to "
        "asking druids for counsel, dealings with mundanes cannot be helped. "
        "A charge of interference must show that the Order was put in danger.",
    ),
    (
        None,
        "Guarding the auras",
        "Magic and Faerie auras, often tied to great events of Irish history, "
        "are in the Order's keeping. Defending one against mundanes who would "
        "spoil or destroy it, or punishing them for it, is not interference, "
        "and the Tribunal backs a strong hand. Drawing vis out of an aura is "
        "frowned on as bad husbandry.",
    ),
    (
        None,
        "Scrying",
        "A scrying charge carries a heavy burden: without clear signs of "
        "magical spying found by a trustworthy witness, the Tribunal requires "
        "that the knowledge could not have been had without magic. Most magi "
        "accept some scrying as unavoidable and settle it privately.",
    ),
    (
        None,
        "The Presiding Quaesitor's veto",
        "The Presiding Quaesitor may set aside a decision only when it plainly "
        "conflicts with any reasonable reading of the Oath or the Code, which "
        "leaves Hibernia room to read the Code in its own way. Magvillus has "
        "reviewed the Hibernian Code many times, before and after the English "
        "came, and each time found its oddities lawful.",
    ),
    (
        None,
        "Apprentices and the macgnímartha",
        "One in the macgnímartha is outside the Code and no longer the "
        "parens's charge. A Bonisagus who wants another's apprentice must "
        "claim the child at a Tribunal, when the Coill Trí or the parens "
        "first present them or at a later meeting, before the macgnímartha "
        "begins.",
    ),
    (
        None,
        "Exile",
        "In place of casting a magus out of his House or the Order, Hibernia "
        "exiles him: he must leave the island or be Marched. An exile may ask "
        "to return if a resident magus will stand surety and plead for him; "
        "the Tribunal decides by free vote. A magus who flees overseas while "
        "under judgment has exiled himself, and must come back by the next "
        "meeting or be cast out of the Order.",
    ),
    (
        None,
        "Sanctions, naidm and ráth",
        "Like Irish law, which avoids putting men to death, the Tribunal "
        "seldom calls a March or takes a familiar or talisman; it wants "
        "redress for the injured and better conduct, through fines, duties, "
        "restrictions and exile. A naidm is named to see the penalty paid, and "
        "those close to the offender, his covenant, parens and filii, stand "
        "surety (ráth), paying or suffering in his place if he defaults. A "
        "fine is rarely raw vis: more often the injured party is given use of "
        "the offender's vis source for a term.",
    ),
    (
        None,
        "Trafficking with demons",
        "The only crime the Tribunal answers with a March as a matter of "
        "course. When the Oath's call to slay a magus is invoked, it is "
        "carried out in earnest, though Hibernian justice stops at the shore.",
    ),
    (
        None,
        "Censuring creatures and the Coill Trí",
        "A faerie or beast that sets the mundane world against the Order is "
        "punished as the case deserves: faeries have been chained, beasts "
        "driven from their haunts for a time or put to a covenant's "
        "service, and once a creature was bound into servitude, a sanction "
        "few want repeated. Members of the Coill Trí, who have no Code, are "
        "judged case by case and may be made to serve, pay vis each season "
        "for a year, or keep out of a district, and their ambassador must "
        "see the judgment met.",
    ),
    (
        None,
        "The Mercer Houses",
        "Leth Moga and Leth Cuinn are not covenants: they keep no cathach, "
        "need no cattle, and stand because they serve the Tribunal, under "
        "many rulings of the Code that guarantee them.",
    ),
    (
        None,
        "The Red Book of Cloyne",
        "When magi asked in the twelfth century to use the Red Book as "
        "testimony, Diarmait of Leth Moga agreed that each Redcap's own "
        "witness may be called, but the book, which he inherited from his "
        "parens, is his own and lies under his sanctum marker. The Tribunal "
        "upheld this, and several magi resent it.",
    ),
    (
        None,
        "Revoke the Protection of Bonisagus",
        "Enchanting the effect into a device that anyone may use, or whose "
        "effect never runs out, is forbidden, lest it fall into the wrong "
        "hands. Casting the spell on a conscious magus outside Wizard War or "
        "a March may be taken as the first step of a killing.",
    ),
    (
        980,
        "The Battle of Teamhrach",
        "Vigil was not punished for magically securing an alliance of Máel "
        "Sechnaill mac Domnaill with the kings of Leinster and Ulster against "
        "Olaf Cuaran of Dublin, nor for fighting beside them to drive the "
        "Norse from Tara: keeping Teamhrach from the northmen was held vital "
        "to the Tribunal's sanctity, though it was plain interference.",
    ),
    (
        1186,
        "Ashenrise's cathach",
        "While the hall was in uproar and magi were declaring War on the "
        "newcomers, the Praeco Conán Derg accepted the dug-up corpse of Rhiannon, a former Prima of Merinita, "
        "as Ashenrise's cathach: against those who said it was no magical "
        "treasure, he ruled that the raw vis grown in its bones made it one.",
    ),
    (
        1193,
        "Lámbaird reprimanded",
        "Lámbaird's magi, suspected of helping the Wicklow clans against the "
        "English by magic, were reprimanded by the Tribunal but not "
        "sanctioned, since nothing tied the Order to the raids.",
    ),
    (
        1195,
        "The Grand Tribunal and Damisona",
        "At Durenmar the Grand Tribunal heard a long debate on whether "
        "Hibernia needed a Code modelled on Stonehenge's, against those who "
        "held a Tribunal free to set its own. Those whose apprentices, "
        "in their macgnímartha, had attacked Damisona of Jerbiton's "
        "party in 1190 and killed three grogs were found guilty only of a Low "
        "Crime, to Stonehenge's outrage.",
    ),
)


# -- the ruins --

#: Each ruin: (key, name, province key in `hibernia.places`, places that
#: may sit closer (tried in order), realm, aura, status, known, summary).
RUINS: tuple[tuple[str, str, str, tuple[str, ...], str, int, str, str, str], ...] = (
    (
        "ruin_salmons_eye",
        "Salmon's Eye (Súil Bradáin)",
        "munster",
        (),
        "Magic",
        2,
        "Known",
        "In the Tribunal",
        secrets(
            "A Diedne covenant of Munster that took Donn, the death god of "
            "the Tuatha Dé, as its ally in the Schism War. With Donn's host "
            "it destroyed Warbler's Way; then the Hibernian magi united, "
            "beat the Munster Diedne, razed Salmon's Eye and drove Donn back "
            "to his island, Teach Duínn. The book does not say where it "
            "stood; the aura is assumed.",
            "Cliffheart has spent two centuries asking why the Munster "
            "Tuatha Dé sided with the Diedne and still does not know; "
            "whatever bound Donn to this place may be found in its ruins.",
        ),
    ),
    (
        "ruin_widows_throat",
        "The Widow's Throat (Scornach Baintrí)",
        "ulster",
        (),
        "Magic",
        2,
        "Known",
        "In the Tribunal",
        "A large Diedne covenant of Ulster that brought a fleet of Fomóir "
        "warships into the Schism War: five sailed up the Shannon toward "
        "Lugh's Retreat while five fell on Circulus Ruber from the sea. Once "
        "the fleet at sea was beaten and Circulus Ruber relieved, the magi "
        "turned north and destroyed it. The book does not place it in "
        "Ulster; the aura is assumed.",
    ),
    (
        "ruin_lughs_retreat",
        "Lugh's Retreat (Cúlráid Logha)",
        "connacht",
        ("breifne", "dartry_mountains", "hollow_of_shannon"),
        "Magic",
        3,
        "Known",
        "In the Tribunal",
        "A Diedne covenant at the Hollow of Shannon, the lonely spring in "
        "the Dartry Mountains where the Shannon rises. The first Hermetic "
        "attack, two months after the fall of the Widow's Throat, failed, "
        "and Fomóir warriors from the river fleet joined its defence. Two "
        "years after that first attack the magi came back with the druids "
        "and hedge wizards of Connacht, warned by the Redcaps, and killed "
        "Diedne and Fomóir alike. Poets call it the Third Battle of "
        "Moytirra. Some Diedne escaped, to die at Clontarf in 1014. The "
        "aura is assumed.",
    ),
    (
        "ruin_warblers_way",
        "Warbler's Way (Cosán Ceolaire)",
        "munster",
        ("lough_leane", "killarney"),
        "Faerie",
        2,
        "Known",
        "In the Tribunal",
        "A Hermetic covenant of three Merinita in the woods round Lough "
        "Leane, destroyed by the Munster Diedne and Donn's forces about a "
        "year after the Widow's Throat fell. Its survivors fought on to "
        "Clontarf and then founded Cliffheart on Cape Clear Island. The "
        "realm and aura are assumed from its Merinita founders and the "
        "faerie woods.",
    ),
    (
        "ruin_diedne_vigil",
        "The Diedne Vigil",
        "ulster",
        ("sperrin_mountains", "sperrins"),
        "Magic",
        2,
        "Known",
        "In the Tribunal",
        "The first Vigil, a Diedne covenant in the foothills of the "
        "Sperrins, which won its standing by killing the great black pig "
        "that dug the ditches guarding old Ulster and taking its tusks. "
        "Dublin's rune wizards raided it in 830; it recovered and helped "
        "defend other covenants, until the Diedne withdrew from the "
        "Tribunal and a band of Merinita sacked it after 851 and carried the "
        "tusks to Malin Head, where the new Vigil stands. The aura is "
        "assumed.",
    ),
    (
        "ruin_uisneach",
        "The lost covenant of Uisneach",
        "meath",
        ("uisneach",),
        "Magic",
        5,
        "Known",
        "In the Tribunal",
        secrets(
            "A covenant founded on the Hill of Uisneach early in the Order's "
            "time in Ireland, for its strong aura and the Stone of Division, "
            "where oaths and treaties binding the whole Tribunal are sworn. "
            "One summer evening it vanished and left no trace; only scraps of "
            "record remain and even its name is forgotten. It seems likely "
            "another covenant will one day rise here.",
            "Folk tales tell of a mighty magician who wanted to rule all the "
            "others in Ireland, broke a geas, and was carried off by the Good "
            "Folk for his pride. The truth is not known.",
        ),
    ),
)


def _ruins(hibernia: Hibernia) -> None:
    b = hibernia.b
    for key, name, _province, _near, realm, aura, status, known, summary in RUINS:
        hibernia.places[key] = b.place(
            name,
            ruined=True,
            summary=summary,
            realm=realm,
            aura=aura,
            status=status,
            known=known,
        )


# -- the docket --


def _docket(hibernia: Hibernia) -> None:
    b, tribunal = hibernia.b, hibernia.tribunal
    assert tribunal is not None
    when: dict[str, Any] = {"filed_year": 1220, "filed_season": "Spring"}
    b.case(
        tribunal,
        "The extended Wizard War against Praesis",
        kind="motion",
        brought_by="(not yet brought: magi of the Ordo Hiberniae and others)",
        against="Ballack of Tytalus (Praesis)",
        charge="Ballack besieged Praesis for a year under the Hibernian rule "
        "that a Wizard War runs on until death, surrender or treaty, and "
        "took it when Báetáin gave up the cathach for Meadhbh's safe "
        "conduct. For most of the English it was the first such War they "
        "had seen. Opinion is divided on whether to lodge a formal "
        "challenge, and the Tribunal may be asked whether the War was "
        "lawfully waged and whether Meadhbh, in sanctuary at Qui Sonant, "
        "has any claim left.",
        **when,
    )
    b.case(
        tribunal,
        "May Praesis's new masters show the Gáe Bulg?",
        kind="motion",
        brought_by="(the Tribunal's question for 1221)",
        against="Praesis (Ballack and Guillaume)",
        charge="Praesis did not attend the meeting of 1214, being under "
        "siege, and did not show its cathach. Its new masters have held the "
        "Gáe Bulg since about 1215, longer than the year a thief must keep a "
        "cathach to claim a covenant's resources, and expect no trouble "
        "presenting it; but it came to them by a bargain at the end of the "
        "siege, not by holding it against the old masters, and those who "
        "back Meadhbh may say Praesis has no right to sit.",
        **when,
    )
    b.case(
        tribunal,
        "The test of the Treaty of Cnoc Maol Réidh",
        kind="motion",
        brought_by="English magi, with some Irish magi who covet Connacht",
        against="The Coill Trí",
        charge="Successive Tribunals have treated the Treaty as binding "
        "without ever putting it to the vote, and any move to question it "
        "is shouted down. The English say hedge wizards are given rights "
        "here that no other Tribunal would allow and that mock a Code made "
        "for Hermetic magi; some Irish magi have long eyed Connacht too. "
        "The day it is formally tested is close.",
        **when,
    )
    b.case(
        tribunal,
        "Reforming the Peripheral Code",
        kind="motion",
        brought_by="Helles of Tytalus (Ashenrise), for the English Council",
        against="The Ordo Hiberniae",
        charge="Helles moves at every meeting to bring the Code up to date: "
        "general laws in place of private treaties, an end to the Treaty's "
        "privileges, and continental practice on vis and Wizard War. He has "
        "made little headway. In return the Irish magi lay charges of High "
        "Crimes against him and his sodales at every meeting, which he "
        "spends his seasons glossing the Code to answer.",
        **when,
    )
    b.case(
        tribunal,
        "The ambassadors' votes",
        kind="motion",
        brought_by="The English Council",
        against="The ambassadors of the Sacred Council",
        charge="Since they arrived the English have argued at every meeting "
        "that giving the votes of faeries, giants and beasts the same weight "
        "as a magus's is unlawful and beneath the Order.",
        **when,
    )
    b.case(
        tribunal,
        "Lámbaird and the Normans",
        kind="charge",
        brought_by="(not yet brought: English magi suspect it)",
        against="Lámbaird (Dalton Ballaugh)",
        charge=secrets(
            "The English Council is growing worried by Lámbaird's open "
            "hostility, and its raids against English interests are "
            "suspected. The Tribunal reprimanded it in 1193 but found "
            "nothing to sanction.",
            "Lámbaird's magi do lend magic to the Wicklow clans resisting "
            "the English, and leave no witnesses. If proved, it is plain "
            "interference with mundanes.",
        ),
        **when,
    )
    b.case(
        tribunal,
        "The Ua Cathail against Elk's Run",
        kind="charge",
        brought_by="The Ua Cathail of the Cenél Áeda na hEchtge (expected)",
        against="Elk's Run (Oswald and Lugardis)",
        charge="The Ua Cathail resent the English magi of Elk's Run and the "
        "help they give their rivals the Uí Sheachnasaigh, who serve the "
        "covenant, and may soon complain to the Tribunal of interference. "
        "Lugardis is working against it. The other covenants may take the "
        "complaint up, though that is unlikely: the charge would need to "
        "show that the magi's meddling put their sodales in danger.",
        **when,
    )
    b.case(
        tribunal,
        "Guillaume's raids into Connacht",
        kind="charge",
        brought_by="(not yet brought: the Coill Trí, through their ambassador)",
        against="Guillaume Flambeau of Normandy (Praesis)",
        charge="Guillaume has not crossed into Connacht himself, but for two "
        "seasons his Bréifne mercenaries have been finding and stripping vis "
        "sources there while he briefs Praesis's foreign guests on what his "
        "spies have found. The Treaty makes the Coill Trí masters of their "
        "own places and promises them justice.",
        **when,
    )
    b.case(
        tribunal,
        "Igneous Drake's killings",
        kind="charge",
        brought_by="(not yet brought: the Coill Trí, or the Irish covenants)",
        against="Igneous Drake of Flambeau (Elk's Run)",
        charge="Igneous burns raiders caught inside his ring of fire, "
        "macgnímartha among them, along with Ua Cathail bandits and any "
        "hedge wizard who annoys him outside Connacht, thinking the Tribunal "
        "enforces no law between magi. Killing a hedge wizard without "
        "declaring War is assaulting the Order's allies, and he has lately "
        "begun declaring War on Irish magi he thinks have slighted Elk's "
        "Run.",
        **when,
    )
    b.case(
        tribunal,
        "Faolán in Connacht",
        kind="charge",
        brought_by="(not yet brought: the Tribunal, once it learns where he is)",
        against="Faolán of Ex Miscellanea",
        charge="Faolán fled into Connacht before Praesis fell and has stayed "
        "far beyond the three nights the Treaty allows a magus, which no "
        "member of the Coill Trí can waive. He thinks himself nearer to the "
        "druids than to the Order. When the Tribunal finds out, it will want "
        "him fetched back.",
        **when,
    )
    b.case(
        tribunal,
        "A Redcap who votes",
        kind="motion",
        brought_by="(rumoured: the Primus of House Mercere)",
        against="Dáire an Chogaidh of Mercere (Leth Cuinn)",
        charge="Dáire an Chogaidh, heir to Leth Cuinn, hates all things "
        "English since fighting de Courcy in his macgnímartha, and has voted "
        "at Tribunal, against his House's custom of neutrality. It has made "
        "him famous, and his House's Primus is said to be preparing an "
        "answer.",
        **when,
    )
    b.case(
        tribunal,
        "Who maimed Conán Derg?",
        kind="charge",
        brought_by="(never brought)",
        against="(unknown; some suspect Faisgia of Cliffheart)",
        charge="Two months after the meeting of 1186, Conán Derg was set "
        "upon while walking alone near Connacht and had his right arm cut "
        "off at the shoulder. He would not have it regrown, saying a leader must be "
        "whole, and gave up the office of Praeco. Some magi think Faisgia "
        "waylaid him, since it happened where she often travels; he neither "
        "confirms nor denies it, and she laughs at the idea.",
        **when,
    )
    b.case(
        tribunal,
        "Access to the Red Book of Cloyne",
        kind="motion",
        brought_by="Magi who want its records as evidence",
        against="Diarmait mac Fergaile (Leth Moga)",
        charge="The Tribunal upheld Diarmait's claim that the Red Book is his "
        "own, under his sanctum marker, though the Redcaps' testimony may be "
        "called. Several magi still dislike the ruling. Diarmait himself now "
        "thinks the book should be seen, though never copied, so a motion "
        "to open it may find him willing.",
        **when,
    )


# -- the factions --


def _factions(hibernia: Hibernia) -> None:
    b, w = hibernia.b, hibernia.world
    ireland = hibernia.places["ireland"]
    w["ordo_hiberniae"] = b.faction(
        "The Ordo Hiberniae",
        faction="Other",
        decides="A vote of all",
        place=ireland,
        wants="To keep the Code, the Treaty and the old ways, and Ireland's "
        "magic in its own keeping",
        offers="Deep lore of Irish legend, alliances with the elder races, "
        "and votes at Tara",
        rules="Magi of Irish Hermetic lineages; patchwork mantles by rank",
        summary=paragraphs(
            "The native Hermetic magi, as they name themselves: raised to "
            "Irish lineages that have lived and worked in Hibernia for "
            "generations, steeped in Irish legend, and judging law as much "
            "by Brehon custom as by the Code. Circulus Ruber leads the "
            "traditionalists. They see the English as a new flock of black "
            "birds, the omen that once foretold the fall of the Fir Bolg, "
            "and fear being driven into Connacht as each people before "
            "them was driven into its corner.",
            "They are not of one mind. Some younger Irish magi, many still "
            "in their macgnímartha, have taken up the English argument that "
            "no part of Ireland should be closed to the Order and that the "
            "old treaties with hedge wizards, beasts and faeries should go, "
            "and a few joined the siege of Praesis. If the Ordo loses the "
            "Tribunal as it lost Praesis, centuries of custom could be gone "
            "within a generation.",
        ),
    )
    w["english_council"] = b.faction(
        "The English Council",
        faction="Other",
        decides="A council",
        place=ireland,
        wants="A Code on the continental model: general law, vis harvested "
        "when it appears, no votes for faeries and beasts, Connacht opened",
        offers="Votes, and the backing of Stonehenge and House Tremere",
        rules="Meets at the start of each Tribunal to agree a common line",
        summary=paragraphs(
            "The magi not native to Hibernia, called the English after the "
            "Stonehenge magi who first came to look, though they hail from "
            "across the continent. House Tremere took notice once England "
            "invaded around 1170, after Gerald of Wales's books and "
            "Stonehenge's reports painted the Tribunal as dangerous and "
            "archaic, and backed the first comers; over fifty years they "
            "have come to claim land and to reform the Code. They find the "
            "hedge wizards' protections and Connacht's status improper, and "
            "are as set in continental ways as the Irish are in theirs.",
            "They meet as a council at each meeting's start to agree their "
            "stance, mostly on reform and lately on Lámbaird's aggression, "
            "but agreement is hard among so many views, and the council "
            "wants a leader who can look past Praesis. Helles of Ashenrise "
            "leads the reform debate. Some of them have now raised "
            "apprentices in Ireland, denied the macgnímartha, and in a "
            "generation the line between Irish and English may blur.",
        ),
    )


# -- the independent magus --


def _cu_chonnacht(hibernia: Hibernia) -> None:
    hibernia.magi["cu_chonnacht"] = hibernia.b.magus(
        "Cú Chonnacht Cluasach Mac Tire",
        covenant=None,
        house="house_bjornaer",
        age=None,
        summary=secrets(
            "An independent Bjornaer magus, a vagrant at law: he belongs to "
            "no covenant, so he has no vote, no Redcap calls on him and "
            "nothing he owns is protected by the Code. He is famous for the "
            "Wizard War between him and Gráinne inghean Uaitéar of Vigil, "
            "which has never ended though the two have met face to face "
            "many times, the Tribunal's best example of a War that runs on "
            "until someone dies, yields or makes a treaty.",
            "The book says nothing more of him. His heartbeast is assumed "
            "to be a wolf, from his name (mac tíre is Irish for a wolf, and "
            "cluasach means big-eared).",
        ),
    )


# -- after every part has built --

#: Which Hermetic faction each covenant leans to, for its link from the
#: faction: (covenant key, faction key, note).
LEANINGS: tuple[tuple[str, str, str], ...] = (
    ("circulus_ruber", "ordo_hiberniae", "Leads the traditionalists"),
    ("cliffheart", "ordo_hiberniae", "Traditionalist; admits no English magi"),
    ("lambaird", "ordo_hiberniae", "Fierce foe of the English agenda"),
    ("paruchia", "ordo_hiberniae", "Irish, though for a Christian Tribunal"),
    ("qui_sonant", "ordo_hiberniae", "Traditionalist; neutral ground"),
    ("vigil", "ordo_hiberniae", "Traditionalist"),
    ("elks_run", "english_council", "English magi from Stonehenge"),
    ("ashenrise", "english_council", "The reformers, from Moles Magna"),
    ("praesis", "english_council", "Taken by the English in the siege"),
)

#: Magi the factions are linked to: (magus key, faction key, note).
FACTION_MAGI: tuple[tuple[str, str, str], ...] = (
    ("helles", "english_council", "Leads the debate for reform"),
    ("ballack", "english_council", "Took Praesis"),
    ("conan_derg", "ordo_hiberniae", "Former Praeco; held to the old Code"),
)

#: The ambassadors confirmed for 1221, in the book's order: (faction,
#: ambassador).
AMBASSADORS: tuple[tuple[str, str], ...] = (
    ("The Fir Bolg", "Fothaid"),
    ("The Fomórach", "Ainid"),
    ("The beasts of magic", "The Eagle King"),
    ("The Tuatha Dé", "Mug Ruith"),
    ("The Coill Trí", "the Coill Trí's ambassador"),
)

#: The Treaty of Cnoc Maol Réidh's clauses, in the book's order.
CNOC_MAOL_REIDH: tuple[str, ...] = (
    "The Order founds no covenant in Connacht, and no magus spends more "
    "than three nights running under a Connacht sky or roof.",
    "The Coill Trí give the Order seven Gifted children at each Tribunal.",
    "The Coill Trí have the right to be heard at Tribunal, their "
    "grievances are considered, and the Order does not deny them justice.",
    "The Coill Trí are masters of their own places; the Order is master of all others.",
    "The lands of Qui Sonant Pro Quieto are a safe haven for everyone.",
    "Magical places outside Connacht are in the Order's protection until "
    "the Order gives that charge back.",
    "The Coill Trí may use the beasts of the coast as they wish, save those "
    "of Vigil, which are the Order's alone.",
    "Members of Praesis may enter Connacht for three reasons only: to "
    "pursue Hermetic justice, when Manannán mac Lir expressly asks it, and "
    "to find bees for their hives.",
    "No magus or druid alone may set aside a clause: a magus invited into "
    "Connacht by a druid must still leave after three days.",
)

TREATIES: tuple[dict[str, Any], ...] = (
    {
        "title": "The Treaty of Cnoc Maol Réidh",
        "parties": "The Order of Hermes in Hibernia and the Coill Trí",
        "year": 898,
        "witness": "Negotiated by Fedelmid Ua Heirméais of Mercere",
        "ends": "Never by one party alone; a clause is added when a "
        "Tribunal votes it and every ceannaire agrees",
        "terms": paragraphs(
            "Made after High-King Congalach Cnogba's embassy of 844, brought "
            "by the Chief Bard Cormacan, on behalf of hedge wizards harried "
            "by the Order; signed in 851 once the Diedne had withdrawn, "
            "refused by the Diedne, rejected by the Grand Tribunal of 865, "
            "and made binding at Hibernia's first meeting in 898. It is "
            "named for Connacht's highest mountain, and its terms apply "
            "'between druids and magi', not to lesser hedge wizards. Druids "
            "can change it only through a magus who proposes it for them.",
            "\n".join(f"{n}. {clause}" for n, clause in enumerate(CNOC_MAOL_REIDH, 1)),
        ),
    },
    {
        "title": "The surrender of Praesis",
        "parties": "Ballack of Tytalus; Báetáin Ua Traimair for Praesis",
        "year": 1215,
        "witness": "",
        "ends": "Fulfilled when the cathach changed hands",
        "terms": "As the last of Praesis's allies fled, Báetáin bargained "
        "with Ballack: the Gáe Bulg, Praesis's cathach, in return for safe "
        "passage for Meadhbh, who went into sanctuary at Qui Sonant. Ballack "
        "has held Praesis since.",
    },
    {
        "title": "Vigil's laboratory for House Verditius",
        "parties": "Vigil and House Verditius",
        "year": None,
        "witness": "",
        "ends": "No end is given; the treaty is largely forgotten",
        "terms": "A member of House Verditius may claim one laboratory at "
        "Vigil, a Merinita covenant. It dates from the days when Vigil's "
        "magi traded vis to Verditius crafters.",
    },
)

#: What finish could not find, for the report.
MISSING: list[str] = []


def _look(found: dict[str, Any], key: str, role: str) -> Any:
    record = found.get(key)
    if record is None:
        MISSING.append(f"{key} ({role})")
    return record


def finish(hibernia: Hibernia) -> None:
    tribunal = hibernia.tribunal
    assert tribunal is not None
    b, saga = hibernia.b, hibernia.b.saga
    MISSING.clear()

    praeco: Character | None = _look(hibernia.magi, "milvia", "the Praeco")
    quaesitor: Character | None = _look(
        hibernia.magi, "visioturpis", "the Presiding Quaesitor"
    )
    tribunal.praeco_id = praeco.id if praeco is not None else None
    tribunal.quaesitor_id = quaesitor.id if quaesitor is not None else None

    cathaigh = package.cathaigh(tribunal)
    cathaigh.clear()
    for slug, entry in hibernia.cathaigh.items():
        covenant: Covenant | None = _look(hibernia.covenants, slug, "cathach")
        if covenant is not None:
            cathaigh[covenant.id] = dict(entry)

    ambassadors = package.ambassadors(tribunal)
    ambassadors.clear()
    for faction, name in AMBASSADORS:
        ambassadors.append(
            {
                "id": new_instance_id(),
                "faction": faction,
                "name": name,
                "confirmed": True,
            }
        )

    treaties = package.treaties(tribunal)
    treaties.clear()
    treaties.extend(dict(t) for t in TREATIES)

    tuatha = package.entries(tribunal, package.KEY, "tuatha")
    tuatha.clear()
    tuatha.extend({"name": n, "ceannaire": c} for n, c in hibernia.tuatha)
    if not hibernia.tuatha:
        MISSING.append("the Coill Trí's túatha (otherworld)")

    for key, _name, province, near, *_ in RUINS:
        ruin = hibernia.places[key]
        around: Neighbour | None = next(
            (hibernia.places[k] for k in (*near, province) if k in hibernia.places),
            None,
        )
        if around is None:
            MISSING.append(f"place {province!r} (for {key})")
        elif ruin.place_id is None:
            ruin.place_id = around.id

    for slug, faction, note in LEANINGS:
        covenant = hibernia.covenants.get(slug)
        if covenant is None:
            MISSING.append(f"{slug} (leaning)")
        else:
            b.link(hibernia.world[faction], "covenants", covenant, note)
    for slug, faction, note in FACTION_MAGI:
        magus = hibernia.magi.get(slug)
        if magus is not None:
            b.link(hibernia.world[faction], "characters", magus, note)

    mercer = {c.id for k, c in hibernia.covenants.items() if k in MERCER_HOUSES}
    resident = [
        c for c in saga.covenants if c.tribunal_id == tribunal.id and c.id not in mercer
    ]
    ids = {c.id for c in resident}
    named = [m for m in saga.characters if m.type == "magus" and m.covenant_id in ids]
    tribunal.covenants_total = COVENANTS_TOTAL
    tribunal.magi_total = max(
        MAGI_TOTAL, len(named) + sum(c.unnamed_magi for c in resident)
    )


# -- generated stats --

#: Cú Chonnacht, whom the book names but does not sketch: a roving
#: Bjornaer, built as a wolf-hearted hunter of the wilds.
PROFILES: dict[str, Profile] = {
    "cu_chonnacht": Profile(
        strong="sta per str qik",
        weak="com pre",
        arts={"Mu": 7, "An": 7, "Co": 6, "Re": 4, "Pe": 4, "In": 3},
        abilities={
            "Heartbeast": (6, "the wolf"),
            "Survival": (4, "forests"),
            "Hunt": (4, "tracking"),
            "Stealth": (3, "woods"),
            "Brawl": (3, "bites"),
            "Animal Ken": (2, "wolves"),
            "Area Lore: Ireland": (2, "the wild places"),
        },
        virtues=[
            "Sharp Ears (Minor)",
            "Wilderness Sense",
            "Enemies",
            "Wrathful (Minor)",
            "Proud (Minor)",
        ],
        age=90,
        native="Irish",
    ),
}


def stats(hibernia: Hibernia) -> None:
    """Generated stats for Cú Chonnacht, the Tribunal's one independent
    magus, who has no stat block."""
    b = hibernia.b
    for key, profile in PROFILES.items():
        magus = hibernia.magi.get(key)
        if magus is not None:
            apply(b, magus, profile)
