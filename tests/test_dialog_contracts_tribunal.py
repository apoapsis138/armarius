"""Dialog contract tests for the forms of a tribunal's sheet and the places, neighbours and
factions of its region.

Each form runs in one app session; dialog_contract_support.py has the
contract and the driver, dialog_openers.py how each form is reached."""

import pytest
from dialog_contract_support import Contract, run_contract
from textual.widgets import Select

from ars_magica_manager import neighbour_filter

CONTRACTS: dict[str, Contract] = {
    "add faction": Contract(
        prefill={"Name": "", "Ruler or leader": "", "Detail": "Sketch"},
        edits={"Name": "The Soest wool merchants", "Ruler or leader": "Hanno"},
        saved=lambda s: [(n.name, n.kind, n.ruler) for n in s.neighbours][-1],
        expected=("The Soest wool merchants", "faction", "Hanno"),
        invalid={"Name": ""},
        shown={"#region-factions-list": "The Soest wool merchants"},
    ),
    "filter neighbours": Contract(
        prefill={"Region": "siebengebirge"},
        edits={"Kind": "church"},
        saved=lambda s: neighbour_filter.current(s),
        expected=neighbour_filter.Filter(region="siebengebirge", kind="church"),
        shown={
            "#region-lords-list": "None match the filter.",
            "#region-info-right": "Church, in The Siebengebirge",
        },
    ),
    "edit neighbour": Contract(
        prefill={
            "Name": "Gottfried of Arnsberg",
            "Kind": "lord",
            "Title": "count",
            "Manors": "50",
            "Answers to": "cologne",
        },
        edits={
            "Realm": "Divine",
            "Answers to": Select.NULL,
            "Detail": "Full",
            "Manors": "60",
        },
        saved=lambda s: (
            s.neighbours[0].realm,
            s.neighbours[0].answers_to,
            s.neighbours[0].details["manors"],
        ),
        expected=("Divine", None, 60),
        invalid=[{"Name": ""}, {"Manors": "-1"}],
        shown={
            "#nb-info-right": "Divine",
            "#nb-info-left": "Full",
            "#nb-kind-facts": "1200 pounds a year",
        },
    ),
    "add castle": Contract(
        prefill={"Name": "", "Garrison": ""},
        edits={"Name": "Wildshausen", "Garrison": "2 knights"},
        saved=lambda s: s.neighbours[0].details["castles"][-1]["garrison"],
        expected="2 knights",
        invalid={"Name": ""},
        shown={"#nb-castles-list": "Wildshausen", "#section-nb-castles": "(2)"},
    ),
    "add gratitude": Contract(
        prefill={"Owed to": "mag1", "Points": "1"},
        edits={"Owed to": "comp1", "Points": "10", "For": "Broke the siege"},
        saved=lambda s: s.neighbours[0].details["gratitude"][-1]["points"],
        expected=10,
        invalid={"Points": "-2"},
        shown={"#nb-gratitude-list": "A manor; 20 for a barony"},
    ),
    "edit guild": Contract(
        prefill={"Trade": "Weavers", "Dean": "Heinrich", "Masters": "9"},
        edits={"Journeymen": "14"},
        saved=lambda s: s.neighbour("soest").details["guilds"][0]["journeymen"],
        expected=14,
        invalid=[{"Trade": ""}, {"Apprentices": "-1"}],
        shown={"#nb-guilds-list": "14"},
    ),
    "edit fair": Contract(
        prefill={"Name": "St. Patroclus' fair", "Season": "Autumn", "Size": "Lesser"},
        edits={"Size": "Typical"},
        saved=lambda s: s.neighbour("soest").details["fairs"][0]["band"],
        expected="Typical",
        invalid=[{"Name": ""}, {"Income (pounds a year)": "-5"}],
        shown={"#nb-fairs-list": "100 pounds"},
    ),
    "edit church": Contract(
        prefill={
            "Church": "Archbishop's cathedral",
            "Order": "The secular clergy",
            "Worship since (year)": "1180",
        },
        edits={"Church": "Monastery or nunnery", "Order": "Benedictine"},
        saved=lambda s: s.neighbour("cologne").details["order"],
        expected="Benedictine",
        invalid=[{"Name": ""}, {"Abandoned in (year)": "1100"}],
        shown={"#nb-kind-facts": "Monastery or nunnery"},
    ),
    "add relic": Contract(
        prefill={"Relic": "", "Faith Points": "1"},
        edits={"Relic": "A finger of St. Ursula", "Faith Points": "2"},
        saved=lambda s: s.neighbour("cologne").details["relics"][-1]["faith"],
        expected=2,
        invalid=[{"Relic": ""}, {"Faith Points": "-1"}],
        shown={"#nb-relics-list": "A finger of St. Ursula"},
    ),
    "add faculty": Contract(
        prefill={"Faculty": "Arts"},
        edits={"Faculty": "Medicine", "Rector": "Master Hugo", "Endowed chairs": "6"},
        saved=lambda s: s.neighbour("studium").details["faculties"][-1]["rector"],
        expected="Master Hugo",
        invalid={"Endowed chairs": "-1"},
        shown={
            "#nb-faculties-list": "Master Hugo",
            "#nb-kind-facts": "Doctor in Medicine",
        },
    ),
    "edit master": Contract(
        prefill={"Name": "Master Gerard", "Licence": "Doctor", "Faculty": "Theology"},
        edits={"Licence": "Magister in Artibus", "Faculty": "Arts"},
        saved=lambda s: s.neighbour("studium").details["masters"][0]["licence"],
        expected="Magister in Artibus",
        invalid={"Name": ""},
        shown={"#nb-masters-list": "Magister in Artibus"},
    ),
    "edit faction": Contract(
        prefill={"Faction": "Hedge coven", "Members": "7"},
        edits={
            "Decides by": "A council",
            "Offers": "Herb-lore",
            "Tradition": "trad_folk_witches",
        },
        saved=lambda s: (
            s.neighbour("coven").details["offers"],
            s.neighbour("coven").details["tradition"],
        ),
        expected=("Herb-lore", "trad_folk_witches"),
        invalid={"Members": "-3"},
        shown={"#nb-kind-facts": "Folk Witches"},
    ),
    "add stage": Contract(
        prefill={"Stage": "", "What became of it": "Pending"},
        edits={"Stage": "The king is crowned", "Year": "1221", "Season": "Summer"},
        saved=lambda s: s.neighbour("crown").details["stages"][-1]["season"],
        expected="Summer",
        invalid={"Stage": ""},
        shown={"#nb-stages-list": "Summer 1221"},
    ),
    "edit stage": Contract(
        prefill={"Stage": "The ford floods", "Year": "1220", "Season": "Winter"},
        edits={"What became of it": "Stopped", "If stopped": "The mill is saved"},
        saved=lambda s: s.neighbour("crown").details["stages"][1]["outcome"],
        expected="Stopped",
        invalid={"Stage": ""},
        shown={"#nb-stages-list": "Stopped", "#nb-kind-facts": "The crowning"},
    ),
    "edit place": Contract(
        prefill={"Name": "The Drachenfels", "Aura": "5", "Inside": "siebengebirge"},
        edits={"Aura": "6", "Status": "Claimed", "Tethers": "A dragon's skull"},
        saved=lambda s: s.neighbour("drachenfels").details["aura"],
        expected=6,
        invalid=[{"Name": ""}, {"Aura": "-1"}],
        shown={"#nb-kind-facts": "Magic 6"},
    ),
    "found covenant": Contract(
        prefill={
            "Name": "The Drachenfels",
            "Aura realm": "Magic",
            "Take Winter Ruins": True,
        },
        edits={"Name": "Drachenhort", "Season": "Winter"},
        saved=lambda s: [
            (
                c.place_id,
                c.covenant_season,
                bool(c.boons_hooks),
                s.neighbour("drachenfels").details["ruined"],
            )
            for c in s.covenants
            if c.name == "Drachenhort"
        ],
        expected=[("drachenfels", "Winter", True, False)],
        invalid={"Name": ""},
    ),
    "add regio level": Contract(
        prefill={"Name": "", "Realm": "Magic"},
        edits={
            "Name": "The Hall of Stones",
            "Aura": "8",
            "To enter it": "Pre + Music against 9",
        },
        saved=lambda s: s.neighbour("drachenfels").details["levels"][-1]["aura"],
        expected=8,
        invalid=[{"Name": ""}, {"Aura": "-2"}],
        shown={"#nb-levels-list": "The Hall of Stones"},
    ),
    "edit place effect": Contract(
        prefill={"Effect": "lab_total", "Amount": "2", "Art or realm": "Herbam"},
        edits={"Amount": "3"},
        saved=lambda s: s.neighbour("drachenfels").details["effects"][0]["amount"],
        expected=3,
        invalid={"Art or realm": "Lettuce"},
        shown={"#nb-effects-list": "+3 Herbam"},
    ),
    "add trigger": Contract(
        prefill={"Trigger": "", "Comes": "Once"},
        edits={
            "Trigger": "Level 3 opens",
            "Season": "Summer",
            "Year": "1221",
            "What happens": "The Hall of Stones can be reached",
        },
        saved=lambda s: s.neighbour("drachenfels").details["triggers"][-1]["year"],
        expected=1221,
        invalid=[{"Trigger": ""}, {"Year": ""}],
        shown={"#nb-triggers-list": "Level 3 opens"},
    ),
    "edit looking ahead": Contract(
        prefill={"Looking ahead": "2", "Show": "Everything"},
        edits={"Looking ahead": "3", "Show": "Places"},
        saved=lambda s: (s.ahead_span, s.ahead_show),
        expected=(3, "Places"),
        shown={"#section-ahead": "Looking Ahead: 3 years · Places"},
    ),
    "add calendar entry": Contract(
        prefill={"What": "", "Year": "1220", "Season": "Autumn", "Comes": "Once"},
        edits={"What": "Vis lease ends", "Year": "1221", "Season": "Spring"},
        saved=lambda s: (s.calendar[-1].title, s.calendar[-1].year),
        expected=("Vis lease ends", 1221),
        invalid=[{"What": ""}, {"Comes": "Every N years"}],
        shown={"#ahead-list": "Vis lease ends"},
    ),
    "edit roll table": Contract(
        prefill={"Table": "Who walks the Mist Wood", "Die": "Simple die"},
        edits={"Rows": "1-9: No one\n10: The king"},
        saved=lambda s: s.neighbour("drachenfels").details["tables"][0]["rows"],
        expected="1-9: No one\n10: The king",
        invalid=[{"Table": ""}, {"Rows": "a stag"}],
        shown={"#nb-tables-list": "Who walks the Mist Wood"},
    ),
    "add place diary entry": Contract(
        prefill={"Year": "1220"},
        edits={"What happened": "The mist lifted for a day."},
        saved=lambda s: s.neighbour("drachenfels").details["diary"][-1]["text"],
        expected="The mist lifted for a day.",
        invalid={"What happened": ""},
        shown={"#nb-place-diary-list": "The mist lifted"},
    ),
    "edit tribunal": Contract(
        prefill={
            "Name": "Rhine",
            "Next meeting (year)": "1228",
            "Meeting place": "Durenmar",
            "Praeco": "mag_sketch",
        },
        edits={"Name": "The Rhine", "Magi in all": "40", "Praeco": "mag1"},
        saved=lambda s: (s.tribunals[0].name, s.tribunals[0].magi_total),
        expected=("The Rhine", 40),
        invalid=[{"Name": ""}, {"Meets every (years)": "-1"}],
        shown={
            "#section-trib-info": "The Rhine",
            "#trib-info-right": "Leandro",
        },
    ),
    "edit proxies": Contract(
        prefill={"Proxies held": "1"},
        edits={"Proxies held": "3"},
        saved=lambda s: s.tribunals[0].proxies,
        expected={"cov_sketch": 3},
        invalid={"Proxies held": "-1"},
        shown={"#trib-roster": "3 held", "#trib-info-right": "Your votes"},
    ),
    "hold tribunal": Contract(
        prefill={"Held at": "Durenmar", "Days": "3", "Fengheld v. Keep": "1"},
        edits={"Days": "4", "Gild dues": "2"},
        saved=lambda s: (
            s.tribunals[0].meeting["days"],
            s.tribunals[0].meeting["day_of"][s.tribunals[0].cases[1].id],
        ),
        expected=(4, 2),
        invalid=[{"Days": "0"}, {"Fengheld v. Keep": "9"}],
        shown={"#meeting-business": "The Fourth Day"},
    ),
    "attendance and proxies": Contract(
        prefill={"Keep: absent": "0", "Fengheld: proxies": "1"},
        edits={
            "Keep: absent": "1",
            "Fengheld: proxies": "2",
            "Fengheld: Quaesitor": "Set aside",
        },
        saved=lambda s: s.tribunals[0].meeting["attendance"]["cov_sketch"],
        expected={"absent": 0, "proxies": 2, "ruling": "Set aside"},
        invalid={"Keep: absent": "-1"},
        shown={"#meeting-attendance": "2 (set aside)"},
    ),
    "hold the debate": Contract(
        prefill={"Prosecutor": "Severinus", "Defender": "Keep", "Rounds": "5"},
        edits={
            "Defender": "Leandro",
            "Levels lost (for)": "0",
            "Levels lost (against)": "3",
        },
        saved=lambda s: (
            s.tribunals[0].cases[0].defender,
            s.tribunals[0].meeting["debates"][s.tribunals[0].cases[0].id]["lost"],
        ),
        expected=("Leandro", [0, 3]),
        invalid=[
            {"Rounds": "11"},
            {"Levels lost (for)": "1", "Levels lost (against)": ""},
        ],
        shown={"#meeting-vote": "brings it", "#meeting-business": "✓ held"},
    ),
    "hold the vote": Contract(
        prefill={"Keep: leans": "Against", "Fengheld: leans": "For"},
        edits={"Keep: leans": "Undecided"},
        saved=lambda s: s.tribunals[0].meeting["votes"][s.tribunals[0].cases[0].id][
            "leanings"
        ]["cov1"],
        expected="Undecided",
        shown={"#meeting-tally": "2 undecided"},
    ),
    "hold the rulings": Contract(
        prefill={"Fengheld v. Keep": "", "Fengheld v. Keep: into the Code": False},
        edits={
            "Fengheld v. Keep": "Keep pays",
            "Fengheld v. Keep: fine": "3",
            "Fengheld v. Keep: fine in": "Aquam",
            "Fengheld v. Keep: into the Code": True,
        },
        saved=lambda s: {
            k: v
            for k, v in s.tribunals[0]
            .meeting["rulings"][s.tribunals[0].cases[0].id]
            .items()
            if k in ("outcome", "fine", "art", "code")
        },
        expected={"outcome": "Keep pays", "fine": 3.0, "art": "Aquam", "code": True},
        invalid={"Fengheld v. Keep: fine": "0"},
        shown={"#meeting-step-info": "fine 3 pawns of Aquam"},
    ),
    "add case": Contract(
        prefill={"Case": "", "Kind": "charge", "Filed (year)": "1220"},
        edits={
            "Case": "Keep v. Fengheld",
            "Kind": "appeal",
            "Against": "Fengheld",
            "Notice given": True,
        },
        saved=lambda s: [
            (c.title, c.kind, c.against, c.notice_given)
            for c in s.tribunals[0].cases
            if c.title == "Keep v. Fengheld"
        ],
        expected=[("Keep v. Fengheld", "appeal", "Fengheld", True)],
        invalid={"Case": ""},
        shown={"#trib-cases": "Keep v. Fengheld", "#section-trib-cases": "(3)"},
    ),
    "edit case": Contract(
        prefill={"Case": "Fengheld v. Keep", "Against": "Keep", "Status": "open"},
        edits={"Status": "decided", "Outcome": "Fengheld keeps the ford"},
        saved=lambda s: (
            s.tribunals[0].cases[0].status,
            s.tribunals[0].cases[0].outcome,
        ),
        expected=("decided", "Fengheld keeps the ford"),
        invalid={"Case": ""},
        shown={"#trib-past": "Fengheld keeps the ford", "#trib-cases": "Gild dues"},
    ),
    "add ruling": Contract(
        prefill={"Ruling": "", "Year": "1220"},
        edits={"Ruling": "Ford sources", "What it says": "A source moves with it."},
        saved=lambda s: [r.title for r in s.tribunals[0].rulings],
        expected=["Gild membership", "Ford sources"],
        invalid={"Ruling": ""},
        shown={"#trib-code": "Ford sources"},
    ),
    "edit treasury loan": Contract(
        prefill={"To whom": "Fengheld", "Amount": "10", "Due (year)": "1229"},
        edits={"Repaid": True},
        saved=lambda s: s.tribunals[0].treasury[2].paid,
        expected=True,
        invalid=[{"To whom": ""}, {"Amount": ""}],
        shown={"#trib-treasury": "repaid", "#trib-balance": "Silver in hand: 40"},
    ),
    "add gild": Contract(
        prefill={"Gild": "", "Dues": "", "Keep": False, "Fengheld": False},
        edits={"Gild": "Mercantile", "Fengheld": True},
        saved=lambda s: s.tribunals[0].package_data["rhine"]["gilds"][-1],
        expected={"name": "Mercantile", "dues": "", "members": ["cov_sketch"]},
        invalid={"Gild": ""},
        shown={"#trib-gilds-list": "Mercantile", "#trib-roster": "Hermetic, Mercan"},
    ),
    "add tokens": Contract(
        prefill={
            "Status": "polites",
            "Tokens": "0",
            "Shards": "0",
            "Services": "0",
            "Ostracised until (year)": "",
        },
        edits={"Magus": "mag1", "Tokens": "3", "Services": "2"},
        saved=lambda s: s.tribunal("thebes").package_data["theban"]["magi"][-1][
            "tokens"
        ],
        expected=3,
        invalid=[{"Shards": "-1"}, {"Status": "metoikos", "Tokens": "1"}],
        shown={"#trib-tokens-list": "3"},
    ),
    "add privilege": Contract(
        prefill={"Office": ""},
        edits={"Magus": "mag_sketch", "Privilege": "socii", "Office": "Polemarch"},
        saved=lambda s: s.tribunal("transylvania").package_data["transylvania"][
            "members"
        ][-1],
        expected={
            "character_id": "mag_sketch",
            "privilege": "socii",
            "office": "Polemarch",
        },
        invalid=[{"Magus": "mag1"}],
        shown={"#trib-privileges-list": "Socii (Domostron)"},
    ),
    "add ambassador": Contract(
        prefill={"Faction": "", "Ambassador": ""},
        edits={"Faction": "The Fir Bolg", "Ambassador": "Ainid"},
        saved=lambda s: s.tribunal("hibernia").package_data["hibernia"]["ambassadors"][
            -1
        ]["name"],
        expected="Ainid",
        invalid={"Faction": ""},
        shown={"#trib-ambassadors-list": "The Fir Bolg"},
    ),
    "edit treaty": Contract(
        prefill={"Treaty": "The Treaty of the Ford", "Year": "1210"},
        edits={"Witnessed by": "Quaesitor Áed"},
        saved=lambda s: s.tribunal("hibernia").package_data["hibernia"]["treaties"][0][
            "witness"
        ],
        expected="Quaesitor Áed",
        invalid={"Treaty": ""},
        shown={"#trib-treaties-list": "The Treaty of the Ford"},
    ),
    "add tenure": Contract(
        prefill={"Vis source": "", "Until (year)": "", "Notes": ""},
        edits={
            "Vis source": "The Grey Stone",
            "Tenure": "legacy",
            "Until (year)": "1227",
        },
        saved=lambda s: s.tribunal("normandy").package_data["normandy"]["tenures"][-1][
            "tenure"
        ],
        expected="legacy",
        invalid={"Vis source": ""},
        shown={"#trib-tenure-list": "The Grey Stone"},
    ),
    "edit tourney result": Contract(
        prefill={"Year": "1220", "Team": "Visitors of Iberia", "Points": "30"},
        edits={"Points": "50"},
        saved=lambda s: s.tribunal("normandy").package_data["normandy"]["tourney"][2][
            "points"
        ],
        expected=50,
        invalid={"Points": "-1"},
        shown={"#trib-tourney-list": "50"},
    ),
    "edit office": Contract(
        prefill={"Office": "Polemarch"},
        edits={"Held by": "mag1", "Term ends (year)": "1232"},
        saved=lambda s: s.tribunal("thebes").package_data["theban"]["archai"][1][
            "holder_id"
        ],
        expected="mag1",
        invalid={"Office": ""},
        shown={"#trib-archai-list": "to 1232"},
    ),
    "add tribunal diary entry": Contract(
        prefill={"Year": "1220", "Entry": "", "Numbers": ""},
        edits={"Entry": "Gild dues raised", "Numbers": "12 votes"},
        saved=lambda s: [(e.title, e.margin) for e in s.tribunals[0].diary],
        expected=[("The Tribunal of 1221", ""), ("Gild dues raised", "12 votes")],
        invalid={"Entry": ""},
        shown={"#trib-diary": "12 votes"},
    ),
}


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_form_contract(name):
    await run_contract(name, CONTRACTS[name])
