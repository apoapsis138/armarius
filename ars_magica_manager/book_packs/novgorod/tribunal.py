"""The Novgorod Tribunal itself: the record and its summary (a young
Tribunal of six covenants in the Russian principalities and Poland,
kept small by its own caution and split by House Bjornaer's quarrel over
Thousand Caves), the Peripheral Code with its three rulings (N4), the
history the book dates in the Diary, and the docket for 1221 (N5): the
charge against Pripet Maior for the raid of 1217, the charge that
Thousand Caves meddles with mundanes, and Lelya Danichev's motion (build);
then the Praeco and the chief Quaesitor and the Tribunal's totals
(finish).

Keys: the Praeco is magi["miya"] (N2, the eldest magus, inferred) and the
chief Quaesitor magi["andrei"] (covenants)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...tribunal_packages import novgorod as package
from ..builder import paragraphs, titled

if TYPE_CHECKING:
    from ..records import Records

NAME = "The Novgorod Tribunal"
#: Six covenants, four of them described (p. 109).
COVENANTS_TOTAL = 6
MEETING_PLACE = "Three Lakes"

SUMMARY = paragraphs(
    "The Order's Tribunal of the Russian principalities and the Kingdom of "
    "Poland, from Novgorod and the northern lakes to Galicia and the "
    "steppe, and from Silesia to the Urals. It is young, barely two "
    "centuries old, and small: six covenants in a vast land of forest, "
    "marsh and river, where faerie vis is rich and the faeries dangerous, "
    "and where the Volkhvy, the Slavs' pagan priest-wizards, kept the "
    "Order out until the princes turned Christian.",
    "Its founders were three covenants sponsored by Thebes, the Rhine and "
    "Transylvania, which refused to fight one another in the Schism War, "
    "on the urging of the Hibernian quaesitor Patrick of Dunderry, and "
    "made themselves the New Slavonic Tribunal in 1008; it took the name "
    "of Novgorod in 1053. Patrick is still its patron saint. Since then "
    "it has grown slowly, ejecting foreign magi from its lands, keeping "
    "away from the princes, and holding off the Rhine's claim to Poland.",
    "Now it is split. Pripet Maior, the oldest covenant, a nest of "
    "ancient Bjornaer sinking into their heart-beasts, guards its marsh "
    "against settlers by raid and haunting; Thousand Caves in the Urals "
    "lives among pagan tribes, finds heart-beasts in mundanes, and seeks "
    "with the Volkhvy a way to temper auras and bring the god Hermes "
    "back. At the meeting of 1214 the quarrel broke into the open, and in "
    "1217 Pripet Maior raided Thousand Caves without declaring Wizard's "
    "War. The magi have not yet been brought to judgement.",
    "The meeting. The Tribunal meets every seven years at Three Lakes, "
    "which Pripet Maior ceded the privilege to more than forty years ago; "
    "the book dates meetings to 1214 and 1221 but gives no season, and "
    "summer is taken here. The Grand Tribunal of 1228 looms over it: the "
    "Rhine will use any scandal to press its claim to Poland.",
    "Officers. The chief Quaesitor, Andrei Soitkchin of Three Lakes, "
    "chairs the meeting; Pavel Chedyav is his junior. The book names no "
    "Praeco: by the rule it is the eldest magus, Miya Cossuri of Pripet "
    "Maior, at a hundred and fifty-three, who seldom leaves her reed "
    "palace.",
)

SECRETS = [
    titled(
        "Thousand Caves' real purpose",
        "Malincka Capcek hid her real purpose when she asked for Thousand "
        "Caves' charter in 1185: not a wilderness covenant but a way to "
        "blend Volkhv ritual with Hermetic magic, temper an aura with "
        "mundane worship and a faerie god, and make Hermes that god.",
    ),
    titled(
        "Zashya Miyovna's child",
        "Zashya Miyovna of Three Lakes, daughter of the Praeco, bore a child "
        "to a prince of the House of Rurik before the Royal Embargo; her "
        "granddaughter is Nastassia Baramov of Thousand Caves.",
    ),
]

#: The Peripheral Code: (year or None, title, what it says).
RULINGS: tuple[tuple[int | None, str, str], ...] = (
    (
        1039,
        "The settlement of new covenants",
        "The Tribunal's council has formal authority over the settlement of "
        "every new covenant in the Slavic lands. Pushed through after the "
        "fall of Grand Silesia, when the Rhine's first attempt to move the "
        "border was only narrowly defeated at Grand Tribunal; it has been "
        "used several times since to eject trespassing bands of foreign "
        "magi, and some now say it has slowed the Tribunal's growth.",
    ),
    (
        1132,
        "The Royal Embargo",
        "No member of the Tribunal may reveal himself to any member of the "
        "Russian royal house. Made after the death of Mstislav the Great, "
        "when every alliance with a prince had ended in disaster; Yury "
        "Beslav of Three Lakes shaped it. Later extended to the Polish "
        "royal house. Leczyca and Pavel Chedyav resent it.",
    ),
    (
        1190,
        "Leczyca's fine",
        "Leczyca was found guilty of serious breaches of the Royal Embargo "
        "for giving Silesian nobles magically gained word of German raids, "
        "and paid a heavy fine in vis. The book dates it about thirty years "
        "before 1220.",
    ),
)

#: The Diary: (year, season, title, details).
EVENTS: tuple[tuple[int, str, str, str], ...] = (
    (
        942,
        "Spring",
        "Michael of Amastris's expedition",
        "With Princess Olga driving off the Volkhvy, a Byzantine expedition "
        "under Michael of Amastris tries to found a covenant in the "
        "Drevlianian lands. Two magi are lost in Arcadia, one is killed by "
        "Volkhvy and one stoned in Kiev.",
    ),
    (
        962,
        "Spring",
        "Michael withdraws",
        "Sviatoslav, a pagan who cares only for war, lets Olga's policy "
        "lapse; the Volkhvy return in force and Michael flees to "
        "Constantinople before they strike.",
    ),
    (
        992,
        "Spring",
        "Rodnya founded",
        "The Theban Tribunal founds Rodnya on the Dnieper, about eighty "
        "miles south of Kiev.",
    ),
    (
        993,
        "Spring",
        "Grand Silesia and Pripet Maior founded",
        "The Rhine founds Grand Silesia between the Oder and the Warta, "
        "heavily backed by Crintera; Transylvania founds Pripet Maior in "
        "the Pripet marshes (the book's sidebar says 994).",
    ),
    (
        1006,
        "Autumn",
        "Patrick of Dunderry refuses",
        "Ordered by Thebes to join a strike on a Carpathian covenant, the "
        "quaesitor Patrick of Dunderry refuses and denounces the order as "
        "diabolical madness; Rodnya backs him, and the three covenants "
        "begin a quiet reconciliation.",
    ),
    (
        1008,
        "Spring",
        "The New Slavonic Tribunal",
        "The three covenants shed their sponsors and declare themselves a "
        "Tribunal; the Grand Tribunal after the Schism War ratifies it.",
    ),
    (
        1009,
        "Spring",
        "Rodnya abandoned",
        "Attacked by Thebans and Transylvanians alike, Rodnya is abandoned; "
        "Patrick leads its magi north. Grand Silesia is damaged and its "
        "refugees flee to Pripet Maior.",
    ),
    (
        1012,
        "Autumn",
        "Three Lakes founded",
        "Between lakes Onega, Beloe and Ilmen, equidistant from Novgorod, "
        "Beloozero and Ladoga.",
    ),
    (
        1039,
        "Spring",
        "Grand Silesia destroyed",
        "Resettled in 1013, Grand Silesia is destroyed by anti-pagan "
        "knights when Casimir the Restorer returns to power; the Rhine "
        "makes its first attempt on the border.",
    ),
    (
        1052,
        "Autumn",
        "Leczyca founded",
        "Once Casimir has driven the Czechs from Silesia, Grand Silesia's "
        "survivors found Leczyca between the Vistula and the Warta; many "
        "stay at Pripet Maior, the root of its bond with House Bjornaer.",
    ),
    (
        1053,
        "Spring",
        "The Novgorod Tribunal",
        "The Tribunal drops 'New' from its name and takes Novgorod's.",
    ),
    (
        1069,
        "Spring",
        "Vseslav in Kiev",
        "Vseslav of Polotsk, a prince and a Volkhv, takes Kiev; the "
        "Tribunal, as in 1054, chooses to do nothing, and he is soon "
        "driven out. He dies in 1101, having written his dangerous lore "
        "in six great tomes of black serpent skin.",
    ),
    (
        1132,
        "Spring",
        "The Royal Embargo",
        "After the death of Mstislav the Great the Tribunal forbids its "
        "members to reveal themselves to the Russian royal house.",
    ),
    (
        1147,
        "Spring",
        "Roslav Lavickovich Primus",
        "Roslav of Pripet Maior is summoned to Crintera to become Primus of "
        "House Bjornaer, which he is for almost thirty years.",
    ),
    (
        1185,
        "Summer",
        "Thousand Caves chartered",
        "On the urging of Malincka Capcek, the Tribunal grants a charter "
        "for a covenant in a gorge of the western Urals; Nastassia Baramov "
        "passes her Gauntlet at Three Lakes the day before.",
    ),
    (
        1190,
        "Summer",
        "Leczyca fined",
        "Leczyca pays a heavy vis fine for aiding Silesian nobles against "
        "German raids.",
    ),
    (
        1194,
        "Winter",
        "Pripet Maior's bicentenary",
        "The oldest covenant of the Tribunal marks two hundred years.",
    ),
    (
        1206,
        "Spring",
        "Yannes Kolski's great Twilight",
        "The Criamon Yannes Kolski of Leczyca spends at least two weeks in "
        "Twilight, prophesying; his words, the Yannes Discourse, are kept "
        "at Leczyca. He never works magic again.",
    ),
    (
        1212,
        "Autumn",
        "Three Lakes' bicentenary",
        "A special council finds that no apprentice has passed a Gauntlet "
        "at Three Lakes in thirty-five years; four apprentices are taken in "
        "the five years after.",
    ),
    (
        1214,
        "Summer",
        "The meeting dismissed",
        "Thousand Caves and Pripet Maior trade accusations; Malincka speaks "
        "for hours on how the Volkhvy temper auras. The Quaesitores confer "
        "in private, then dismiss the meeting, announcing a delegation to "
        "both covenants. They are also asked whether Yannes Kolski has "
        "passed into Final Twilight.",
    ),
    (
        1215,
        "Spring",
        "The delegation",
        "A quaesitorial delegation backed by magi of every covenant visits "
        "Pripet Maior and Thousand Caves over 1215 and 1216, and finds both "
        "in breach of the Code.",
    ),
    (
        1216,
        "Summer",
        "Yannes vanishes",
        "After a disruptive visit to Thousand Caves, Yannes Kolski is lost "
        "near Vladimir-in-Suzdalia while its magi escort him back.",
    ),
    (
        1217,
        "Spring",
        "The raid on Thousand Caves",
        "Pripet Maior strikes Thousand Caves without declaring Wizard's "
        "War. It fails: the local animals stay loyal, two attackers fall "
        "into Twilight, and Otto Rattstein drives off Casimi Ljech as he "
        "is about to kill Nastassia Baramov.",
    ),
    (
        1218,
        "Spring",
        "Zashya at Crintera",
        "Zashya Miyovna complains of Pripet Maior to the elders at "
        "Crintera, who summon Pripet to judgement but promise nothing to "
        "make it come.",
    ),
)


def build(records: Records) -> None:
    b = records.b
    records.tribunal = tribunal = b.tribunal(
        NAME,
        package=package.NOVGOROD.key,
        summary=SUMMARY,
        secrets=SECRETS,
        meets_every=7,
        next_year=1221,
        next_season="Summer",
        meeting_place=MEETING_PLACE,
        covenants_total=COVENANTS_TOTAL,
    )
    for year, title, says in RULINGS:
        b.ruling(tribunal, title, year, says)
    for year, season, title, details in EVENTS:
        b.event(tribunal, year, title, details, season=season)
    when = {"filed_year": 1218, "filed_season": "Spring"}
    b.case(
        tribunal,
        "The raid on Thousand Caves",
        brought_by="The Quaesitores (Andrei Soitkchin)",
        against="Pripet Maior (Casimi Ljech above all)",
        charge="An undeclared assault on a covenant of the Tribunal in the "
        "spring of 1217, meant to wreck its laboratories and kill its magi, "
        "with neither Wizard's War nor Wizard's March. Pripet Maior has "
        "ignored every summons; Casimi, who led it, is all but "
        "ungovernable, and too many magi have old ties to Pripet for "
        "punishment to be easy.",
        notice_given=True,
        evidence="The delegation's report; Thousand Caves' magi and "
        "animals; Otto Rattstein, who fought Casimi but will not lay "
        "charges before Crintera.",
        **when,
    )
    b.case(
        tribunal,
        "Meddling with mundanes at Thousand Caves",
        brought_by="Pripet Maior, with magi who were outraged in 1214",
        against="Thousand Caves (Malincka Capcek)",
        charge="Thousand Caves leads a confederation of pagan tribes, "
        "teaches them a revived cult of Hermes and wakes heart-beasts in "
        "mundanes; the charge is interfering with the mundanes and "
        "endangering the Order. It is hard to prove harm, as the tribes "
        "are pagans hundreds of miles from any Christian authority.",
        evidence="The delegation found Thousand Caves in breach of the Code "
        "in 1215-1216.",
        **when,
    )
    b.case(
        tribunal,
        "Lelya Danichev's motion on the Volkhvy",
        kind="motion",
        brought_by="Lelya Danichev of Thousand Caves",
        against="(the Tribunal)",
        charge="That the Tribunal condemn the Order's treatment of the "
        "Volkhvy. Lelya also means to force Pripet Maior to a formal "
        "apology for the raid, and has practised certamen for three years "
        "to do it.",
        filed_year=1221,
        filed_season="Summer",
    )


def finish(records: Records) -> None:
    tribunal = records.tribunal
    assert tribunal is not None
    saga = records.b.saga
    praeco, quaesitor = records.magi.get("miya"), records.magi.get("andrei")
    tribunal.praeco_id = praeco.id if praeco is not None else None
    tribunal.quaesitor_id = quaesitor.id if quaesitor is not None else None
    resident = [c for c in saga.covenants if c.tribunal_id == tribunal.id]
    ids = {c.id for c in resident}
    named = [m for m in saga.characters if m.type == "magus" and m.covenant_id in ids]
    tribunal.covenants_total = max(COVENANTS_TOTAL, len(resident))
    tribunal.magi_total = len(named) + sum(c.unnamed_magi for c in resident)
