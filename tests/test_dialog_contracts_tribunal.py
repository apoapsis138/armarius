"""Dialog contract tests for the forms of a tribunal's sheet and the places, neighbours and
factions of its region.

Each form runs in one app session; dialog_contract_support.py has the
contract and the driver, dialog_openers.py how each form is reached."""

import pytest
from dialog_contract_support import Contract, run_contract
from dialog_openers import contract_saga
from textual.widgets import Select

from ars_magica_manager import neighbour_filter

CONTRACTS: dict[str, Contract] = {
    "add faction": Contract(
        prefill={"Name": "", "Ruler or leader": None, "Detail": "Sketch"},
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
    "edit secrets": Contract(
        prefill={"Secrets": "He owes the Archbishop more than he can pay."},
        edits={"Secrets": "He has sold the mill to the Archbishop in secret."},
        saved=lambda s: s.neighbour("gottfried").secrets,
        expected="He has sold the mill to the Archbishop in secret.",
        shown={"#secrets-text": "He has sold the mill to the Archbishop in secret."},
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
        shown={"#nb-gratitude-list": "A manor; 20 for baron of the king"},
    ),
    "add battle": Contract(
        prefill={"Battle": "", "First army": "neighbour:gottfried"},
        edits={
            "Battle": "Siege of Soest",
            "Second army": "neighbour:mark",
            "Second army's combat groups": "30",
        },
        saved=lambda s: [
            (b.sides[0].neighbour_id, b.sides[1].neighbour_id, b.sides[1].groups)
            for b in s.battles
            if b.name == "Siege of Soest"
        ],
        expected=[("gottfried", "mark", 30)],
        invalid=[
            {"Battle": ""},
            {"Second army's combat groups": "-1"},
            {"Second army": "neighbour:gottfried"},
        ],
        shown={"#nb-battles-list": "Siege of Soest", "#section-nb-battles": "(2)"},
    ),
    "battle event": Contract(
        prefill={"Maneuver": "Defend", "Size": "Even", "How it went": "beaten"},
        # One "How it went" a Maneuver: the Defend one shown.
        aliases={"How it went": "fld-condition_Defend"},
        edits={"Leading the event": "comp1", "Size": "Outnumbered"},
        saved=lambda s: (
            s.battles[0].sides[1].groups,
            s.neighbour("gottfried").details["diary"][-1]["text"][:13],
        ),
        expected=(16, "The ford at W"),
        shown={"#nb-battles-list": "2 won, 0 lost"},
        live={"#fields-live": "Advantage or Setback, Ease Factor 12"},
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
    "add charter lord": Contract(
        prefill={"Lord": "", "Kind": "Noble", "Holds it": "Sole"},
        edits={"Lord": "Archbishop of Cologne", "Kind": "Church"},
        saved=lambda s: s.neighbour("soest").details["charter_lords"][-1]["kind"],
        expected="Church",
        invalid=[{"Lord": ""}, {"Since (year)": "soon"}],
        shown={
            "#nb-charter-lords-list": "Archbishop of Cologne",
            "#nb-charter-gives-text": "4 within the walls",
        },
    ),
    "edit charter terms": Contract(
        prefill={"Charter family": "", "Granted (year)": ""},
        edits={"Charter family": "Soest", "Granted (year)": "1120", "Salvage": True},
        saved=lambda s: s.neighbour("soest").details["charter_terms"]["family"],
        expected="Soest",
        invalid={"Granted (year)": "long ago"},
        shown={"#nb-charter-terms-facts": "Soest"},
    ),
    "edit charter gives": Contract(
        prefill={"Pawns of vis in it": ""},
        edits={"Pawns of vis in it": "2"},
        saved=lambda s: s.neighbour("soest").details["charter_terms"]["pawns"],
        expected=2,
        invalid={"Pawns of vis in it": "-1"},
        shown={"#nb-charter-gives-text": "2 pawns of Rego vis"},
    ),
    "add citizen": Contract(
        prefill={"Came to live here (season)": "Autumn"},
        edits={"Character": "comp1", "Came to live here (year)": "1218"},
        saved=lambda s: s.neighbour("soest").details["citizens"][-1]["character_id"],
        expected="comp1",
        invalid={"Came to live here (year)": "once"},
        shown={"#nb-citizens-list": "+1 multiplier"},
    ),
    "edit town people": Contract(
        prefill={"Population": "5000", "Council (seats)": "12"},
        edits={"Burgesses": "300", "A city by right": True},
        saved=lambda s: s.neighbour("soest").details["burgesses"],
        expected=300,
        invalid={"Burgesses": "-1"},
        shown={"#nb-town-people-facts": "5,000 (city)"},
    ),
    "add guild member": Contract(
        prefill={"Guild": "Weavers", "Rank": "apprentice"},
        edits={"Character": "comp1", "Rank": "master"},
        saved=lambda s: s.neighbour("soest").details["guild_members"][-1]["rank"],
        expected="master",
        shown={"#nb-guild-members-list": "Master"},
    ),
    "add court case": Contract(
        prefill={"Accused": "", "Court": "Town"},
        edits={"Accused": "Hartmut", "Charge": "Theft", "Verdict": "Guilty"},
        saved=lambda s: s.neighbour("soest").details["court_cases"][-1]["accused"],
        expected="Hartmut",
        invalid={"Accused": ""},
        shown={"#nb-court-cases-list": "Guilty"},
    ),
    "court roll": Contract(
        prefill={"Law argued": "civil"},
        edits={"Who pleads": "comp1", "He truly is innocent": True},
        saved=lambda s: bool(s.neighbour("soest").details["court_cases"][0]["verdict"]),
        expected=True,
        live={"#fields-live": "Against 3 = 6 -3 truly innocent"},
        shown={"#nb-court-cases-list": "Hartmut"},
    ),
    "add manor": Contract(
        prefill={"Name": "", "Acres": "600", "Farmed as": "Large fields"},
        edits={"Name": "Hagen", "Demesne (acres)": "200", "A mill by custom": True},
        saved=lambda s: s.neighbour("gottfried").details["manor_list"][-1]["demesne"],
        expected=200,
        invalid=[{"Name": ""}, {"Demesne (acres)": "900"}],
        shown={"#manors-list": "Hagen", "#section-manors": "(1)"},
    ),
    "add establishment": Contract(
        prefill={"Kind": "Stables", "Quality": "Standard"},
        edits={"Kind": "Mews", "Quality": "Superior", "Animals": "7"},
        saved=lambda s: s.neighbour("gottfried").details["establishments"][-1][
            "animals"
        ],
        expected=7,
        invalid={"Animals": "-1"},
        shown={"#establishments-list": "Mews"},
    ),
    "edit household": Contract(
        prefill={"Household (people)": "", "Mesnie": ""},
        edits={"Household (people)": "28", "Mesnie": "6 knights"},
        saved=lambda s: s.neighbour("gottfried").details["household"]["retinue"],
        expected=28,
        invalid={"Household (people)": "-3"},
        shown={"#household-facts": "28: 6 knights"},
    ),
    "buy manor": Contract(
        prefill={"Name": "", "Price (pounds)": "800"},
        edits={"Name": "Hagen", "Price (pounds)": "700"},
        saved=lambda s: s.neighbour("gottfried").details["manor_list"][-1]["name"],
        expected="Hagen",
        invalid=[{"Name": ""}, {"Price (pounds)": "0"}],
        live={"#fields-live": "35 times"},
        shown={"#manors-list": "Hagen"},
    ),
    "assart": Contract(
        prefill={"Laborers": "1", "Months": "1"},
        edits={"Laborers": "4", "Months": "6"},
        saved=lambda s: s.neighbour("gottfried").details["manor_list"][0]["waste"],
        expected=36,
        invalid={"Laborers": "100"},
        live={"#fields-live": "24 acres"},
        shown={"#manors-list": "224"},
    ),
    "winter roll": Contract(
        prefill={"With": "profession"},
        edits={"Who rolls": "comp1"},
        saved=lambda s: (
            "die" in s.neighbour("gottfried").details["establishments"][0]["roll"]
        ),
        expected=True,
        live={"#fields-live": "against 9"},
        shown={"#establishments-list": "Stables"},
    ),
    "settle inheritance": Contract(
        prefill={"Heir": "", "By": "Primogeniture"},
        edits={"Heir": "Heinrich"},
        saved=lambda s: s.neighbour("gottfried").ruler,
        expected="Heinrich",
        invalid={"Heir": ""},
        shown={"#nb-info-left": "Heinrich"},
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
        prefill={"Relic": "", "Faith score": "1"},
        edits={"Relic": "A finger of St. Ursula", "Faith score": "2"},
        saved=lambda s: s.neighbour("cologne").details["relics"][-1]["faith"],
        expected=2,
        invalid=[{"Relic": ""}, {"Faith score": "-1"}],
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
        edits={
            "Aura": "6",
            "Status": "Claimed",
            "Tethers": "A dragon's skull",
            "Alignment": "Ignem",
        },
        saved=lambda s: (
            s.neighbour("drachenfels").details["aura"],
            s.neighbour("drachenfels").details["alignment"],
        ),
        expected=(6, "Ignem"),
        invalid=[{"Name": ""}, {"Aura": "-1"}],
        shown={"#nb-kind-facts": "aligned with Ignem"},
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
            "Alignment": "Healing",
            "To enter it": "Pre + Music against 9",
        },
        saved=lambda s: (
            s.neighbour("drachenfels").details["levels"][-1]["aura"],
            s.neighbour("drachenfels").details["levels"][-1]["alignment"],
        ),
        expected=(8, "Healing"),
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
    "tie trigger": Contract(
        prefill={"Trigger": "", "Comes": "Once"},
        edits={
            "Trigger": "Abnoba's due",
            "Comes": "Each year",
            "Season": "Winter",
            "Moves a threat": "crown",
            "Failing moves it (steps)": "2",
        },
        saved=lambda s: (
            s.neighbour("drachenfels").details["triggers"][-1]["threat_id"],
            s.neighbour("drachenfels").details["triggers"][-1]["steps"],
        ),
        expected=("crown", 2),
        invalid=[{"Comes": "Whenever", "What happens": "The hunt rides"}],
        shown={"#nb-triggers-list": "Failing it moves The Hollow Crown 2 steps"},
    ),
    "grow story": Contract(
        prefill={"Threat": "A salamander in the lab", "Begin it now": "now"},
        edits={"Threat": "The Salamander's Hunger", "Antagonist": "A salamander"},
        saved=lambda s: (
            s.covenants[0].diary[-1].status,
            s.neighbour(s.covenants[0].diary[-1].threat_id or "").name,
        ),
        expected=("Grown into a threat", "The Salamander's Hunger"),
        invalid={"Threat": ""},
        shown={"#region-threats-list": "The Salamander's Hunger"},
    ),
    "delay threat": Contract(
        prefill={"Seasons later": "1", "Why": ""},
        edits={"Seasons later": "2", "Why": "The bridge was burned"},
        saved=lambda s: s.neighbour("crown").details["delay"],
        expected=2,
        invalid=[{"Why": ""}, {"Seasons later": "0"}],
        shown={"#nb-kind-facts": "2 seasons later"},
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
    # Close (the cancel) records nothing; Set Out writes the traveller's
    # Diary and the arrival on Ahead.
    "travel set out": Contract(
        prefill={"Measured": "direct", "By": "foot", "Travellers": "0", "Who goes": []},
        edits={
            "Who goes": ["mag1"],
            "Miles": "180",
            "By": "barge_down",
            "Cargo, in tons": "2",
        },
        saved=lambda s: (
            s.calendar[-1].title,
            s.character("mag1").diary[-1].name,
            len(s.calendar) - len(contract_saga().calendar),
        ),
        expected=("Leandro arrives", "Travel", 1),
        invalid=[
            {"Miles": "-5", "Who goes": ["mag1"]},
            {"Travellers": "many"},
            {"Miles": "180"},
        ],
        live={"#fields-live": "Days: 23"},
        shown={"#ahead-list": "Leandro arrives"},
    ),
    # Closing a forced march records nothing either; set out, it costs
    # Leandro a Long-Term Fatigue level a day.
    "travel close": Contract(
        prefill={"Measured": "direct", "Travel quickly": False},
        edits={
            "Who goes": ["mag1"],
            "Measured": "route",
            "Miles": "40",
            "By": "foot",
            "Travel quickly": True,
        },
        saved=lambda s: (
            s.character("mag1").long_term_fatigue,
            s.character("mag1").fatigue_level,
        ),
        expected=(2, "weary"),
        live={"#fields-live": "Forced march"},
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
    "add faction diary entry": Contract(
        prefill={"Year": "1220"},
        edits={"What happened": "The coven courted the Count."},
        saved=lambda s: s.neighbour("coven").details["diary"][-1]["text"],
        expected="The coven courted the Count.",
        invalid={"What happened": ""},
        shown={"#nb-place-diary-list": "The coven courted"},
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
        prefill={"Keep: all present": True, "Fengheld: proxies": "1"},
        edits={
            "Keep: all present": False,
            "Brother Oda": False,
            "Fengheld: proxies": "2",
        },
        saved=lambda s: (
            s.tribunals[0].meeting["attendance"]["cov1"]["present"],
            s.tribunals[0].meeting["attendance"]["cov_sketch"]["proxies"],
        ),
        expected=(["mag1"], 2),
        invalid={"Fengheld: proxies": "-1"},
        shown={"#meeting-business": "✓ held"},
    ),
    "open the meeting": Contract(
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
        prefill={"Fengheld: all present": True, "Fengheld: proxies": "1"},
        edits={
            "Fengheld: all present": False,
            "Fengheld: unnamed magi present": "1",
            "Fengheld: proxies": "2",
            "Fengheld: Quaesitor": "Set aside",
        },
        saved=lambda s: {
            k: v
            for k, v in s.tribunals[0].meeting["attendance"]["cov_sketch"].items()
            if k in ("present", "unnamed", "proxies", "ruling")
        },
        expected={
            "present": ["mag_sketch"],
            "unnamed": 1,
            "proxies": 2,
            "ruling": "Set aside",
        },
        invalid={
            "Fengheld: all present": False,
            "Fengheld: unnamed magi present": "-1",
        },
        shown={"#meeting-attendance": "2 (set aside)"},
    ),
    "hold the debate": Contract(
        prefill={
            "Settled in private": False,
            "Prosecutor": "mag_sketch",
            "Defender": "mag1",
            "Rounds": "5",
        },
        edits={
            "Defender": "mag2",
            "Defender: debates as": "Formidable",
            "Levels lost (for)": "0",
            "Levels lost (against)": "3",
        },
        saved=lambda s: (
            s.tribunals[0].cases[0].defender,
            s.tribunals[0].meeting["debates"][s.tribunals[0].cases[0].id]["lost"],
        ),
        expected=("Brother Oda", [0, 3]),
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
        prefill={
            "Fengheld v. Keep: written from": "",
            "Fengheld v. Keep: into the Code": False,
        },
        edits={
            "Fengheld v. Keep: the ruling": "Keep pays",
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
        prefill={"Case": "", "Kind": "charge", "Filed (year)": "1220", "Victim": ""},
        edits={
            "Case": "Keep v. Fengheld",
            "Kind": "appeal",
            "Against": "Fengheld",
            "Victim": "Alys",
            "Notice given": True,
        },
        saved=lambda s: [
            (c.title, c.kind, c.against, c.victim, c.notice_given)
            for c in s.tribunals[0].cases
            if c.title == "Keep v. Fengheld"
        ],
        expected=[("Keep v. Fengheld", "appeal", "Fengheld", "Alys", True)],
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
        prefill={"Gild": "", "Agenda": "", "Keep": False, "Fengheld": False},
        edits={"Gild": "Mercantile", "Fengheld": True},
        saved=lambda s: s.tribunals[0].package_data["rhine"]["gilds"][-1],
        expected={
            "name": "Mercantile",
            "agenda": "",
            "leader_ids": [],
            "magi": [],
            "members": ["cov_sketch"],
        },
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
    "edit ostracism": Contract(
        prefill={"Meeting (year)": "1214", "Sherds against him": "30"},
        edits={"Sherds cast": "100", "Exile ends (year)": "1230"},
        saved=lambda s: s.tribunal("alps").package_data["alps"]["ostracised"][0][
            "until"
        ],
        expected=1230,
        invalid={"Sherds cast": "200"},
        shown={"#trib-ostracism-list": "to 1230"},
    ),
    "add tribunal diary entry": Contract(
        prefill={"Year": "1220", "Entry": "", "Numbers": ""},
        edits={"Entry": "Gild dues raised", "Numbers": "12 votes"},
        saved=lambda s: [(e.title, e.margin) for e in s.tribunals[0].diary],
        expected=[("The Tribunal of 1221", ""), ("Gild dues raised", "12 votes")],
        invalid={"Entry": ""},
        shown={"#trib-diary": "12 votes"},
    ),
    # The Theban treasury's loans of vis.
    "lend vis": Contract(
        prefill={
            "Art": "Vim",
            "Pawns": "0",
            "Repaid by (year)": "1225",
            "Repayment plan": "",
            "For an emergency": False,
            "Into the magus's own vis": True,
        },
        edits={"Art": "Creo", "Pawns": "4", "Repayment plan": "a pawn a year"},
        saved=lambda s: (
            s.tribunal("thebes").treasury[-1].amount,
            s.tribunal("thebes").treasury[-1].art,
            s.character("mag1").raw_vis.get("creo", 0),
        ),
        expected=(4, "Creo", 7),
        invalid=[{"Pawns": "0"}, {"Pawns": "11"}],
        shown={"#trib-treasury": "4 pawns of Creo"},
    ),
    # The Rhine's ranks and its meeting's rite.
    "mark of approval": Contract(
        prefill={
            "Applicant": "mag1",
            "Mark given by": "mag_sketch",
            "Asked of him": "",
        },
        edits={
            "Applicant": "mag1",
            "Mark given by": "mag_sketch",
            "Asked of him": "a tract",
        },
        saved=lambda s: s.tribunal("rhine").package_data["rhine"]["marks"]["mag1"][0][
            "sponsor_id"
        ],
        expected="mag_sketch",
        # Brother Oda is of Severinus's House.
        invalid={"Applicant": "mag2"},
        live={"#fields-live": "1 of 3 marks: Severinus"},
    ),
    "archmage's challenge": Contract(
        prefill={
            "Challenger": "mag_sketch",
            "Archmage": "arch1",
            "Contest": "",
            "Has invented a spell of 7th magnitude": False,
            "Great deed": "",
            "Outcome": "Lost",
        },
        edits={
            "Challenger": "mag_sketch",
            "Archmage": "arch1",
            "Contest": "defeat him in certamen",
            "Has invented a spell of 7th magnitude": True,
            "Great deed": "Bound the wyrm",
            "Outcome": "Won",
        },
        saved=lambda s: (
            [vf.vf_id for vf in s.character("mag_sketch").virtues_flaws][-1],
            s.tribunal("rhine").package_data["rhine"]["challenges"]["arch1"]["contest"],
        ),
        expected=("vf_archmage_rhine_tribunal", "defeat him in certamen"),
        invalid=[
            {
                "Challenger": "mag_sketch",
                "Archmage": "arch1",
                "Contest": "certamen",
                "Great deed": "Bound the wyrm",
            },
            {
                "Challenger": "mag_sketch",
                "Archmage": "arch1",
                "Has invented a spell of 7th magnitude": True,
                "Great deed": "Bound the wyrm",
            },
        ],
    ),
    "rhine rite": Contract(
        prefill={"Confer: Severinus (Master)": True, "Sigil of": ""},
        edits={"Sigil of": "Notatus"},
        saved=lambda s: (
            s.tribunal("rhine").package_data["rhine"]["entrusted"],
            s.tribunal("rhine").proxies["cov_sketch"],
        ),
        expected=({"mag_sketch": ["Notatus"]}, 2),
        shown={"#meeting-business": "✓ held"},
    ),
    # Transylvania's promissory notes (Against the Dark p. 19).
    "add promissory note": Contract(
        prefill={"Held by": "", "Redeemed": False, "Note": ""},
        edits={"Held by": "Old Histria", "Amount": "4", "Art": "Vim"},
        saved=lambda s: [
            (e.kind, e.who, e.amount, e.art, e.paid)
            for e in s.tribunal("transylvania").treasury
        ],
        expected=[("note", "Old Histria", 4, "Vim", False)],
        invalid=[{"Held by": ""}, {"Amount": ""}],
        shown={"#trib-treasury": "outstanding"},
    ),
    # The hunt and Area Lore, on a manor and on the road (LoM pp. 48-58,
    # C&G p. 83): the dice decide the outcome, so the Diary's entry is checked.
    "hunt on a manor": Contract(
        prefill={
            "Hunt": "hounds",
            "Native to the ground": True,
            "Lay a relay": True,
            "Hours of daylight": "11",
        },
        edits={"Hunters, who ride": ["comp1"]},
        saved=lambda s: s.character("comp1").diary[-1].name.startswith("The Hunt"),
        expected=True,
        invalid={"Hours of daylight": "0"},
        live={"#fields-live": "Pursuit"},
        shown={"#manors-list": "Hagen"},
    ),
    "area lore on a manor": Contract(
        prefill={"Looking for": "free_goods", "He lives": "home"},
        edits={"Who asks": "comp1", "Looking for": "major_inn"},
        saved=lambda s: s.character("comp1").diary[-1].name.startswith("Area Lore"),
        expected=True,
        invalid={"Looking for": "other", "Ease Factor": "-1"},
        live={"#fields-live": "Ease Factor 6"},
        shown={"#manors-list": "Hagen"},
    ),
    "hunt on the road": Contract(
        prefill={"Hunt": "hounds", "In a lord's chase, warren or forest": False},
        edits={"Hunters, who ride": ["mag1"]},
        saved=lambda s: s.character("mag1").diary[-1].name.startswith("The Hunt"),
        expected=True,
        invalid={"Hours of daylight": "0", "Hunters, who ride": ["mag1"]},
        live={"#fields-live": "First find a hunting spot"},
    ),
    "area lore on the road": Contract(
        prefill={"Looking for": "free_goods"},
        edits={"Who asks": "mag1", "Looking for": "route_inns"},
        saved=lambda s: s.character("mag1").diary[-1].name.startswith("Area Lore"),
        expected=True,
        live={"#fields-live": "Ease Factor 12"},
    ),
    # Hermetic law on the docket (HoH:S, HoH:TL).
    "add wizard's war": Contract(
        prefill={"Case": "", "Kind": "charge"},
        edits={
            "Case": "Leandro declares on Severinus",
            "Kind": "war",
            "Brought by": "Leandro",
            "Against": "Severinus",
            "Arrived at the full moon of month": "2",
        },
        saved=lambda s: [
            (c.kind, c.month, c.served, c.notice_given)
            for c in s.tribunals[0].cases
            if c.title == "Leandro declares on Severinus"
        ],
        expected=[("war", 2, "redcap", True)],
        invalid=[{"Kind": "war"}, {"Kind": "war", "Against": "Fengheld"}],
        shown={"#trib-cases": "Leandro declares"},
    ),
    # A place's Tomb tab (Lands of the Nile pp. 32-46).
    "edit tomb": Contract(
        prefill={"Kind": "lesser_royal", "Centuries the burial ground": "3"},
        edits={"Points of Hooks": "4", "Boons": "Seclusion"},
        saved=lambda s: s.neighbour("drachenfels").details["tomb_boons"],
        expected="Seclusion",
        invalid={"Points of Hooks": "11"},
        live={"#fields-live": "100 Build Points"},
        shown={"#nb-tomb-facts": "Boons: Seclusion"},
    ),
    "add tomb curse": Contract(
        prefill={"Name": "", "Kind": "Hermetic effect"},
        edits={
            "Name": "He Shall Have No Successors",
            "Art": "PeCo",
            "Level": "35",
            "Condition": "Whoever breaks the seal",
        },
        saved=lambda s: [
            (c["name"], c["level"])
            for c in s.neighbour("drachenfels").details["tomb_curses"][1:]
        ],
        expected=[("He Shall Have No Successors", 35)],
        invalid=[
            {"Name": ""},
            {"Name": "Seth", "Condition": "Whoever", "Kind": "Greater Malediction"}
            | {"Level": "25"},
        ],
        live={"#fields-live": "14 Build Points"},
        shown={"#nb-tomb-curses-list": "He Shall Have No Successors"},
    ),
    "edit tomb ward": Contract(
        prefill={"Name": "Turn the Interloper", "Kind": "Ward", "Level": "30"},
        edits={"Level": "35"},
        saved=lambda s: s.neighbour("drachenfels").details["tomb_wards"][0]["level"],
        expected=35,
        invalid={"Level": "0"},
        live={"#fields-live": "Ease Factor 16"},
        shown={"#nb-tomb-wards-list": "EF 16, 14 BP"},
    ),
    "add tomb trap": Contract(
        prefill={"Name": "", "What it does": "scare", "Ease Factor to avoid": "3"},
        edits={
            "Name": "Head Wires",
            "What it does": "minor",
            "Ease Factor to avoid": "15",
        },
        saved=lambda s: [
            (t["name"], t["ease"])
            for t in s.neighbour("drachenfels").details["tomb_traps"][1:]
        ],
        expected=[("Head Wires", 15)],
        invalid={"Name": ""},
        live={"#fields-live": "15 Build Points"},
        shown={"#nb-tomb-traps-list": "Head Wires"},
    ),
    # Roll asks before writing the outcome in the place's diary: the form
    # alone writes nothing.
    "overcome trap": Contract(
        prefill={"Harder or easier": "0", "His roll": "Qik + Athletics"},
        edits={"Who acts": "mag1", "Harder or easier": "-3"},
        saved=lambda s: s.neighbour("drachenfels").details["diary"][-1]["text"],
        expected="Leandro found the path backwards.",
        live={"#fields-live": "adjusted to 9"},
    ),
    # The Rhine's Great Library at Durenmar (Guardians of the Forests).
    "search the great library": Contract(
        prefill={
            "Magus": "mag1",
            "Looking for": "art",
            "Art, Ability or spell": "",
            "Level wanted": "15",
        },
        edits={"Looking for": "tractatus", "Art, Ability or spell": "Ignem"},
        saved=lambda s: [
            (e["sought"], e["subject"], e["outcome"], e["credit_taken"])
            for e in s.tribunal("rhine").package_data["rhine"]["library_searches"][1:]
        ],
        expected=[("tractatus", "Ignem", "found", True)],
        # Severinus has no credit there.
        invalid=[
            {"Art, Ability or spell": ""},
            {"Magus": "mag_sketch", "Looking for": "tractatus"},
        ],
        live={"#fields-live": "No roll to find one"},
        shown={"#trib-library-searches-list": "Ignem tractatus"},
    ),
    "contribute to the great library": Contract(
        prefill={"Magus": "mag1", "Gives": "book", "Seasons of credit": "2"},
        edits={"Gives": "vis", "What": "4 pawns of Vim", "Seasons of credit": "2"},
        saved=lambda s: s.tribunal("rhine").package_data["rhine"]["library_credit"][0][
            "given"
        ][-1]["what"],
        expected="4 pawns of Vim",
        invalid={"Gives": "vis", "What": ""},
        live={"#fields-live": "Taken, never acknowledged"},
        shown={"#trib-library-credit-list": "4 seasons"},
    ),
    "edit library credit": Contract(
        prefill={"Seasons granted besides": "0", "Seasons used": "0", "Note": ""},
        edits={"Seasons used": "1", "Note": "Read the Vim tractatus"},
        saved=lambda s: s.tribunal("rhine").package_data["rhine"]["library_credit"][0][
            "used"
        ],
        expected=1,
        invalid={"Seasons used": "-1"},
        shown={"#trib-library-credit-list": "1 season"},
    ),
    "edit library search": Contract(
        prefill={"Art, Ability or spell": "Vim", "Result": "found", "Quality": "7"},
        edits={"Result": "certamen"},
        saved=lambda s: s.tribunal("rhine").package_data["rhine"]["library_searches"][
            0
        ]["outcome"],
        expected="certamen",
        invalid={"Art, Ability or spell": ""},
        shown={"#trib-library-searches-list": "Certamen"},
    ),
    # A lord's marriages (Lords of Men pp. 10-11; DE pp. 148, 512-513).
    "arrange marriage": Contract(
        prefill={
            "Season": "Autumn",
            "It stands": "betrothed",
            "Her parents' children": "1",
        },
        edits={
            "Bride's name": "Adelheid of Sayn",
            "Groom": "neighbour:gottfried",
            "Her parents' land (manors)": "6",
            "Her parents' children": "2",
        },
        saved=lambda s: s.marriages[-1].groom_ref,
        expected="neighbour:gottfried",
        invalid=[{"Bride's name": ""}, {"Her parents' children": "0"}],
        live={"#fields-live": "6 manors / 2"},
        shown={
            "#nb-marriages-list": "Adelheid of Sayn",
            "#section-nb-marriages": "(1)",
        },
    ),
    "edit marriage": Contract(
        prefill={"Bride's name": "Adelheid of Sayn", "It stands": "married"},
        edits={"Note": "A love match"},
        saved=lambda s: s.marriages[0].note,
        expected="A love match",
        invalid={"Bride's name": ""},
        shown={"#nb-marriages-list": "Married"},
    ),
    "edit marriage terms": Contract(
        prefill={"Her parents' land (manors)": "4"},
        edits={"Custom for the dowry": "england"},
        saved=lambda s: s.marriages[0].custom,
        expected="england",
        invalid=[
            {"Her parents' land (manors)": "-1"},
            # With a patrimony the eldest son comes out of the division too.
            {"The eldest son's patrimony, kept out (French custom)": "1"},
        ],
        shown={"#nb-marriage-facts": "England"},
    ),
    "end marriage": Contract(
        prefill={"It ends": "husband", "Season": "Autumn"},
        edits={"It ends": "part"},
        saved=lambda s: s.marriages[0].ended,
        expected="part",
        live={"#fields-live": "feud"},
        shown={"#nb-marriages-list": "Separated"},
    ),
    # Polemic and Charter Strength (Transforming Mythic Europe pp. 27-36).
    "add argument": Contract(
        prefill={"Argument": "", "It concerns": "tribunal", "It backs": "for"},
        edits={"Argument": "Covenants may hold charters", "It concerns": "covenant"},
        saved=lambda s: [(a.topic, a.reach) for a in s.tribunal("rhine").arguments],
        expected=[("Covenants may hold charters", "covenant")],
        invalid={"Argument": ""},
        shown={
            "#trib-arguments": "Covenant 6",
            "#section-trib-arguments": "(1)",
        },
    ),
    "edit argument": Contract(
        prefill={"Argument": "Covenants may hold charters", "Its ideal": "Charters"},
        edits={"Last debate": "won"},
        saved=lambda s: s.tribunal("rhine").arguments[0].outcome,
        expected="won",
        invalid={"Argument": ""},
        shown={"#trib-argument-text": "won: its bonus carries"},
    ),
    "add text": Contract(
        prefill={"Kind": "polemic", "Circulated to": "tribunal"},
        edits={"Book": "b-polemic", "Seasons spent circulating": "1"},
        saved=lambda s: [
            (t.kind, t.book_id, t.author_id, t.seasons_spent)
            for t in s.tribunal("rhine").arguments[0].texts
        ],
        expected=[("polemic", "b-polemic", "mag1", 1)],
        invalid={"Seasons spent circulating": "-1"},
        shown={
            "#trib-argument-texts": "Summa, Code of Hermes L4 Q11",
            "#section-trib-argument-texts": "(1)",
        },
    ),
    "circulate text": Contract(
        prefill={"Seasons spent so far (+1 each)": "0", "To": "tribunal"},
        edits={"Seasons spent so far (+1 each)": "1"},
        saved=lambda s: s.tribunal("rhine").arguments[0].texts[0].seasons_spent,
        expected=2,
        invalid={"Seasons spent so far (+1 each)": "x"},
        live={"#fields-live": "+ 1 for seasons spent"},
        shown={"#trib-argument-texts": "Circulat"},
    ),
    "draft charter": Contract(
        prefill={
            "Drawn up for": "subordinate",
            "Other notaries (−1 botch die each)": "0",
        },
        edits={"Other notaries (−1 botch die each)": "2", "In England": True},
        saved=lambda s: (
            isinstance(
                s.neighbour("soest")
                .details["charter_lords"][0]
                .get("subordinate_strength"),
                int,
            ),
            s.neighbour("soest").details["charter_lords"][0].get("in_england"),
        ),
        expected=(True, True),
        invalid={"Other notaries (−1 botch die each)": "-1"},
        live={"#fields-live": "1 botch dice"},
    ),
    "seek loophole": Contract(
        prefill={"Searching for": "subordinate", "Season": "Autumn"},
        edits={"Year": "1221"},
        saved=lambda s: s.neighbour("soest").details["charter_lords"][0][
            "superior_strength"
        ],
        expected=0,
        invalid={"Searching for": "superior"},
        live={"#fields-live": "Charter Strength 0"},
    ),
    # The guides' gaps, round two.
    "war's end": Contract(
        prefill={"How it ended": "ran_out"},
        edits={"How it ended": "peace"},
        saved=lambda s: next(
            (c.status, c.outcome)
            for c in s.tribunals[0].cases
            if c.id == "war-contract"
        ),
        expected=("decided", "They made peace before it was fought"),
    ),
    "cross the threshold": Contract(
        prefill={"From": "0"},
        edits={"Arcadian Travel charm": "30"},
        saved=lambda s: (
            s.neighbour("drachenfels")
            .details["diary"][-1]["text"]
            .startswith("Cross the Threshold")
        ),
        expected=True,
        invalid={"Arcadian Travel charm": "x"},
        live={"#fields-live": "Threshold points against a strength of 24"},
    ),
}


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_form_contract(name):
    await run_contract(name, CONTRACTS[name])
