"""The Stonehenge Tribunal itself (ch10, ch02, ch11): the record and its
summary (a Tribunal long held by Blackthorn through inquorate meetings,
revived since 1201, meeting a year behind the Order at Blackthorn), the
Peripheral Code's one printed ruling, the Diary of its history and its
twenty fallen covenants (S4, S9), and the Redcaps' rounds (build); then
the Praeco and the presiding Quaesitor and the totals (finish).

Keys: the Praeco is magi["talion"] and the presiding Quaesitor
magi["iudicium"] (covenants)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...tribunal_packages import stonehenge as package
from ..builder import paragraphs

if TYPE_CHECKING:
    from ..records import Records

NAME = "The Stonehenge Tribunal"
#: The book's nine active covenants and its 49 named magi, Ebroin in
#: Immanola's place (S5): nothing unnamed to add.
COVENANTS_TOTAL = 9
MAGI_TOTAL = 49
MEETING_PLACE = "Blackthorn"

SUMMARY = paragraphs(
    "The Order's Tribunal of England and Wales, born in 817 when Pralix's "
    "Ordo Miscellanea, founded at Cad Gadu after her war on the warlock "
    "Damhan-Allaidh, joined the Order as House Ex Miscellanea. It has never "
    "been an easy place for magi: the land is thick with royal officials, "
    "sheriffs and bishops, the Church is everywhere, and every established "
    "covenant has had to make its own accommodation with the mundane "
    "authorities, not always with the Tribunal's leave. Its history is a "
    "long list of covenants that rose and fell, twenty of them since 817. "
    "There are no covenants in the West Country, Devon and Cornwall, near "
    "the ruins of Sursum and Stellasper and the sites of Arthur.",
    "For most of its life the Tribunal was Blackthorn's. Few meetings were "
    "quorate, so Blackthorn could not be called to account, and at those that "
    "were it held most of the votes. Covenants had little to do with one "
    "another, and disputes were settled by certamen and Wizard's War. Julia "
    "of Voluntas worked for decades to break that hold; the meeting of 1194 "
    "failed so badly that Stonehenge sent no one to the Grand Tribunal of "
    "1195, and no one came at all in 1200. She brought Maximianus of "
    "Bonisagus, who founded Nigrasaxa, and in 1201 a second, quorate meeting "
    "was called with Voluntas, Schola Pythagoranis and Ungulus. Since then "
    "the Tribunal has met a year behind the rest of the Order, and no one "
    "covenant can rule it. It has nine active covenants now, all of good "
    "size.",
    "The meeting. Always at Blackthorn, whose Talion of Flambeau is Praeco; "
    "Blackthorn barred Immanola, then the eldest, as biased toward her own "
    "House, and since she entered Final Twilight in 1216 Talion is the "
    "eldest in any case. Iudicium of Guernicus, also of Blackthorn, presides. "
    "Each magus is called forward in turn to give his Hermetic name and "
    'covenant and show a sigil, and the presiding Quaesitor answers "Sic '
    'est"; then the meeting is declared quorate, twelve magi from at least '
    "four covenants. Business with the world outside comes first, then the "
    "apprentices are made magi, and the meeting is formally closed, until the "
    "youngest magus present protests that there are matters between sodales "
    "and asks for a new Tribunal, which the Praeco convenes on the spot: so "
    "every meeting is legally two, and either may be challenged alone. The "
    "custom dates from the Schism War. The Quaesitores do not vote, but each "
    "tells an unGifted Redcap how to cast his sigil, and the Praeco has done "
    "the same; unGifted Redcaps do not count toward the quorum. Meetings fell "
    "in 1201, 1208 and 1215, and the next is in 1222; the book gives no "
    "season, and summer is taken here.",
    "The Redcaps. Five unGifted Redcaps, all men, ride the Tribunal from "
    "Mercer House near Coventry, whose Hermes Portal reaches Harco. Each "
    "covenant is visited every other month, two days after the full moon, "
    "for three days: Blackthorn, Semitae, Schola Pythagoranis, Burnham and "
    "Ungulus one month, Cad Gadu, Libellus, Nigrasaxa and Voluntas the next. "
    "A covenant gives the visiting Redcap three purses of 28 pennies, on "
    "arrival, at noon on the second day and on leaving. A message waits for "
    "the next visit, one or two months; an urgent one costs a special "
    "journey, at least 28 pence. A Tribunal Summons must be delivered at "
    "least six months ahead, a rule kept strictly since the Tribunal called "
    "a meeting out of cycle.",
    "Its questions now: the feud of Voluntas and Blackthorn, a century old, "
    "and whether the Tribunal splits into two blocs; the covenants' "
    "accommodations with the mundane powers, and the Code; and a shortage of "
    "vis, as the plough takes the land and the Tribunal grows.",
)

SECRETS = paragraphs(
    "Blackthorn has faced charges of diabolism for generations; nothing has "
    "ever been proved, and the charge may be raised to distract from another, "
    "or may be true.",
    "Burnham's purpose is unknown to everyone outside it, and every covenant "
    "has its own theory.",
)

#: The Peripheral Code: (year, title, what it says).
RULINGS: tuple[tuple[int | None, str, str], ...] = (
    (
        1208,
        "Financial Matters",
        "No covenant may put more than a reasonable amount of magically made "
        "silver into circulation in a year: two pounds for each resident, "
        "magus or mundane. Blackthorn, Burnham, Voluntas and others had made "
        "so much silver late last century that its value halved in twenty "
        "years; the Tribunal judged it interference with the mundanes. A move "
        "to punish those responsible failed easily. Gold, not used as coin in "
        "England, is not covered, but magi now know that making too much of a "
        "thing lowers its worth.",
    ),
    (
        None,
        "The Praeco",
        "Immanola, Prima of Ex Miscellanea and then the eldest magus, was "
        "barred from the office as likely to favour her own House, at "
        "Blackthorn's urging; Talion of Blackthorn has held it since, and the "
        "Tribunal meets at Blackthorn. The other covenants dislike it, but none "
        "has acted.",
    ),
    (
        1201,
        "The meeting a year late",
        "The Tribunal meets a year after the rest of the Order, from the "
        "quorate meeting of 1201.",
    ),
)

#: The Tribunal's history (S9: the fallen covenants are entries here):
#: (year, season, title, details).
EVENTS: tuple[tuple[int, str, str, str], ...] = (
    (
        815,
        "Spring",
        "Pralix at Cad Gadu",
        "After the war on Damhan-Allaidh, Pralix founds the Ordo Miscellanea at Cad Gadu in North Wales.",
    ),
    (
        817,
        "Summer",
        "The Tribunal of Stonehenge",
        "The Ordo Miscellanea joins the Order as House Ex Miscellanea, and the Stonehenge Tribunal is born. The Nameless Covenant of House Diedne is founded on Anglesey.",
    ),
    (
        818,
        "Spring",
        "Blackthorn founded",
        "Magi of House Tremere found Blackthorn in the Black Mountains of south Wales.",
    ),
    (
        820,
        "Spring",
        "Rosalba founded",
        "Flavia of Jerbiton founds Rosalba in the Yorkshire Dales.",
    ),
    (
        821,
        "Spring",
        "Concordia founded",
        "Concordia, an attempt to weld the traditions of Ex Miscellanea together, is founded in the Lake District; it falls apart from its own tensions in 823.",
    ),
    (
        852,
        "Spring",
        "Castrum Antiquum founded",
        "A covenant in a Roman fort on Hadrian's Wall, which lasts until 1030 or 1031 and then vanishes without trace.",
    ),
    (
        863,
        "Spring",
        "Pralix vanishes",
        "Pralix disappears returning from a visit to her old domus magna (Houses of Hermes: Societates).",
    ),
    (
        866,
        "Spring",
        "Rector Maris",
        "A covenant on the Isle of Man that lasts six months.",
    ),
    (
        873,
        "Spring",
        "Diana against William",
        "Diana of Tremere of Blackthorn and William of Jerbiton of Rosalba fight a Wizard's War.",
    ),
    (
        875,
        "Spring",
        "Sursum founded",
        "A covenant in north Cornwall, which lasts until 931: Tytalus diabolism is found there, and King Athelstan destroys it.",
    ),
    (
        893,
        "Spring",
        "Occulta",
        "Newly Gauntleted magi found Occulta in the East Anglian fens; it fails to find resources and collapses in 897, its magi joining other covenants.",
    ),
    (
        896,
        "Spring",
        "The London Covenant",
        "A covenant in London, which lasts until about 952.",
    ),
    (
        899,
        "Spring",
        "Rosalba destroyed",
        "Blackthorn destroys Rosalba; its ruins are lost, and their defences are still active.",
    ),
    (
        915,
        "Spring",
        "Lux Draconis",
        "An undistinguished covenant in the Pennines that never has much of a summer and dies in 1100, unable to recruit.",
    ),
    (
        938,
        "Spring",
        "Rector Novus",
        "A second covenant on the Isle of Man, destroyed within a year.",
    ),
    (
        946,
        "Spring",
        "Roma Nova",
        "A covenant in Kent, destroyed by House Diedne in 1008.",
    ),
    (
        984,
        "Spring",
        "Ungulus founded",
        'Magi of House Flambeau found Ungulus, "the Claw", in the Lake District.',
    ),
    (
        998,
        "Spring",
        "Lumen",
        "An early victim of the Schism War, too poor to repel a Diedne assault in 1003.",
    ),
    (
        1011,
        "Spring",
        "The Nameless Covenant destroyed",
        "The Diedne covenant on Anglesey falls in the Schism War; its records are struck from the Code.",
    ),
    (
        1014,
        "Spring",
        "Tagelyn founded",
        "A covenant in caves near Blackthorn, which lasts until 1062.",
    ),
    (
        1025,
        "Spring",
        "Stellasper founded",
        "A Criamon covenant on the Isles of Scilly, destroyed in a storm in 1163.",
    ),
    (
        1060,
        "Summer",
        "Cad Gadu sacked",
        "Gruffydd ap Llewelyn, who besieged Blackthorn from 1058 to 1062, sacks Cad Gadu; Diedne were suspected, though it is now thought coincidence. Cad Gadu is refounded in its regio's higher levels in 1065.",
    ),
    (
        1062,
        "Autumn",
        "Blackthorn takes Tagelyn",
        "Blackthorn takes Tagelyn's caves and moves into them; Tagelyn's survivors flee to Hibernia and found Ashenrise.",
    ),
    (
        1066,
        "Autumn",
        "Harold's Vengeance",
        "Founded in the East Anglian fens to drive William the Conqueror from England; it breaks the Code so blatantly that it is Marched whole and destroyed in 1068.",
    ),
    (1083, "Spring", "Voluntas founded", "Norman magi found Voluntas in the north."),
    (
        1100,
        "Spring",
        "Lux Draconis claimed",
        "Blackthorn claims Lux Draconis's property, the start of its enmity with Voluntas.",
    ),
    (
        1104,
        "Spring",
        "Blackrose",
        "A covenant on the North York Moors, which lasts until 1107.",
    ),
    (
        1111,
        "Spring",
        "Magnantrum founded",
        "A covenant in a cave under Salisbury Plain, which disintegrates in 1187.",
    ),
    (
        1133,
        "Spring",
        "Natura Antiqua",
        "Nature magi found Natura Antiqua in the East Anglian fens; Geoffrey de Mandeville destroys it in the civil war, in 1143.",
    ),
    (
        1141,
        "Spring",
        "Burnham founded",
        "Burnham is founded in the far north-east, with a grant of immunity from King Stephen.",
    ),
    (
        1151,
        "Summer",
        "Semitae at the Tribunal",
        "The wandering covenant Semitae first appears at a meeting, led by Gerfallon of Criamon.",
    ),
    (
        1154,
        "Winter",
        "The Wild Hunt sealed",
        "Flumen of Tremere of Blackthorn leads the Wild Hunt into iron-bound caves near Blackthorn and shuts it in.",
    ),
    (
        1160,
        "Spring",
        "Servus Maris",
        'A third try at a Manx covenant, destroyed by a dragon within six months; one magus is let go home with the message, "Don\'t come back."',
    ),
    (
        1182,
        "Spring",
        "Schola Pythagoranis founded",
        "Jerbiton magi found Schola Pythagoranis at Cambridge.",
    ),
    (
        1187,
        "Spring",
        "Flumen's Final Twilight",
        "Flumen of Blackthorn passes into Final Twilight, and his filia Goliard takes his place; Magnantrum falls apart the same year.",
    ),
    (
        1194,
        "Summer",
        "A void meeting",
        "Blackthorn hosts, Voluntas and Burnham stay away and Semitae cannot be found: the meeting is not quorate, and Stonehenge sends no one to the Grand Tribunal of 1195.",
    ),
    (
        1195,
        "Spring",
        "Trutina joins Burnham",
        "Trutina the Quaesitor joins Burnham, and attends every meeting after.",
    ),
    (1200, "Summer", "No one comes", "No one attends the meeting of 1200."),
    (
        1201,
        "Summer",
        "The quorate meeting",
        "Maximianus of Bonisagus founds Nigrasaxa; with Voluntas, Schola Pythagoranis and Ungulus he calls a second meeting, quorate, at Blackthorn. The Tribunal meets a year late from now on, and the Redcaps' network is reorganised.",
    ),
    (
        1208,
        "Summer",
        "The silver ruling",
        "The meeting rules that no covenant may circulate more than two pounds of magical silver a resident a year.",
    ),
    (
        1210,
        "Spring",
        "Libellus founded",
        "Stephen Eruditus of Jerbiton founds Libellus with six young magi.",
    ),
    (
        1216,
        "Spring",
        "Immanola's Final Twilight",
        "Immanola, who has sat twelve years gazing into a pool at Cad Gadu, is declared to have entered Final Twilight; House Ex Miscellanea elects Ebroin Primus (Houses of Hermes: Societates).",
    ),
    (
        1220,
        "Spring",
        "William Fireheart killed",
        "William Fireheart of Flambeau, of Ungulus, loses a Wizard's War to a magus of Fudarus in the Normandy Tribunal, ending Ungulus's line of Flambeau magi.",
    ),
)


def build(records: Records) -> None:
    b = records.b
    records.tribunal = tribunal = b.tribunal(
        NAME,
        package=package.STONEHENGE.key,
        summary=SUMMARY,
        secrets=SECRETS,
        meets_every=7,
        next_year=1222,
        next_season="Summer",
        meeting_place=MEETING_PLACE,
        covenants_total=COVENANTS_TOTAL,
        magi_total=MAGI_TOTAL,
    )
    for year, title, says in RULINGS:
        b.ruling(tribunal, title, year, says)
    for year, season, title, details in EVENTS:
        b.event(tribunal, year, title, details, season=season)


def finish(records: Records) -> None:
    tribunal = records.tribunal
    assert tribunal is not None
    saga = records.b.saga
    praeco, quaesitor = records.magi.get("talion"), records.magi.get("iudicium")
    tribunal.praeco_id = praeco.id if praeco is not None else None
    tribunal.quaesitor_id = quaesitor.id if quaesitor is not None else None
    resident = [c for c in saga.covenants if c.tribunal_id == tribunal.id]
    ids = {c.id for c in resident}
    named = [m for m in saga.characters if m.type == "magus" and m.covenant_id in ids]
    tribunal.covenants_total = max(COVENANTS_TOTAL, len(resident))
    tribunal.magi_total = max(MAGI_TOTAL, len(named))
