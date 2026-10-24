"""Dialog contract tests for the forms of the saga picker, the saga itself, Saga Content and the bestiary.

Each form runs in one app session; dialog_contract_support.py has the
contract and the driver, dialog_openers.py how each form is reached."""

import pytest
from dialog_contract_support import Contract, all_sagas, run_contract
from textual.widgets import Select

from ars_magica_manager import armies, catalog
from ars_magica_manager import players as pl

CONTRACTS: dict[str, Contract] = {
    "create saga": Contract(
        prefill={"Name": "", "Start Year": "1220", "Start Season": "Spring"},
        edits={"Name": "Second Saga", "Storyguide": "Ann"},
        saved=lambda _: sorted(
            (s.name, s.storyguide) for s in all_sagas() if s.name == "Second Saga"
        ),
        expected=[("Second Saga", "Ann")],
        invalid=[{"Name": ""}, {"Name": "Second Saga"}],
    ),
    "edit saga": Contract(
        prefill={"Name": "Matrix", "Storyguide": ""},
        edits={"Name": "Matrix II", "Storyguide": "Ann", "Description": "About"},
        saved=lambda s: (s.name, s.storyguide, s.description),
        expected=("Matrix II", "Ann", "About"),
        invalid=[{"Name": ""}, {"Name": "  "}, {"Storyguide": ""}],
    ),
    "set date": Contract(
        prefill={"Season": "Autumn", "Year": "1220"},
        edits={"Season": "Winter", "Year": "1225"},
        saved=lambda s: (s.current_season, s.current_year),
        expected=("Winter", 1225),
        invalid=[{"Year": "-"}, {"Year": ""}],
    ),
    "create covenant": Contract(
        prefill={"Name": "", "Season": "Spring", "Aura realm": "Magic"},
        edits={
            "Name": "Harbour",
            "Notes": "By the sea",
            "Season": "Winter",
            "Aura realm": "Faerie",
        },
        saved=lambda s: [
            (c.name, c.notes, c.covenant_season, c.aura_realm, c.aura)
            for c in s.covenants
            if c.name == "Harbour"
        ],
        expected=[("Harbour", "By the sea", "Winter", "Faerie", 3)],
        invalid={"Name": ""},
    ),
    "create tribunal": Contract(
        prefill={"Name": "", "Meets every (years)": "7"},
        edits={
            "Name": "Provence",
            "Next meeting (year)": "1227",
            "Meeting place": "Avignon",
        },
        saved=lambda s: [
            (t.name, t.next_year, t.meeting_place, t.meets_every)
            for t in s.tribunals
            if t.name == "Provence"
        ],
        expected=[("Provence", 1227, "Avignon", 7)],
        invalid=[{"Name": ""}, {"Meets every (years)": "0"}, {"Magi in all": "-2"}],
    ),
    "create creature": Contract(
        prefill={"Name": "", "Size": "0", "Realm": Select.NULL},
        edits={
            "Name": "Boglin",
            "Realm": "Faerie",
            "Might Score": "5",
            "Might Form": "Aquam",
            "Size": "-2",
        },
        saved=lambda s: [
            (c.name, c.realm, c.might, c.might_form, c.size)
            for c in s.creatures
            if c.name == "Boglin"
        ],
        expected=[("Boglin", "Faerie", 5, "Aquam", -2)],
        invalid=[{"Name": ""}, {"Size": "big"}],
    ),
    "add battle (conflicts)": Contract(
        prefill={"Battle": "", "Season": "Autumn", "First army": ""},
        edits={
            "Battle": "Lippe",
            "First army": "neighbour:gottfried",
            "Second army": "neighbour:mark",
        },
        saved=lambda s: [
            (
                b.sides[0].neighbour_id,
                b.sides[1].neighbour_id,
                b.sides[0].groups == armies.army_groups(s.neighbour("gottfried")),
            )
            for b in s.battles
            if b.name == "Lippe"
        ],
        expected=[("gottfried", "mark", True)],
        invalid=[{"Battle": ""}, {"Second army": "neighbour:gottfried"}],
        shown={"#conflict-battles-list": "Lippe", "#section-conflict-battles": "(2)"},
    ),
    "edit battle (conflicts)": Contract(
        prefill={"Battle": "The ford at Werl", "First army": "neighbour:gottfried"},
        edits={"Where": "by the Lippe"},
        saved=lambda s: s.battles[0].place,
        expected="by the Lippe",
        invalid={"Battle": ""},
    ),
    "battle event (conflicts)": Contract(
        prefill={"Maneuver": "Defend", "Fighting for": "0", "How it went": "won"},
        edits={"Leading the event": "comp1", "Size": "Outnumbered"},
        saved=lambda s: (s.battles[0].sides[1].groups, len(s.battles[0].events)),
        expected=(16, 2),
        shown={"#conflict-battles-list": "2 won, 0 lost"},
    ),
    "add fight": Contract(
        prefill={"Fight": "", "Season": "Autumn", "Year": "1220"},
        edits={"Fight": "Skirmish", "First side": "Us", "Second side": "Them"},
        saved=lambda s: [
            (f.name, [side.name for side in f.sides])
            for f in s.fights
            if f.name == "Skirmish"
        ],
        expected=[("Skirmish", ["Us", "Them"])],
        invalid=[{"Fight": ""}, {"Year": "soon"}],
        shown={"#fights-list": "Skirmish", "#section-fights": "(2)"},
    ),
    "edit fight": Contract(
        prefill={"Fight": "The Fray at the Ford", "Where": "below the mill"},
        edits={"Where": "at the bridge"},
        saved=lambda s: s.fights[0].place,
        expected="at the bridge",
        invalid={"Fight": ""},
        shown={"#conflicts-info-panel": "at the bridge"},
    ),
    "add siege": Contract(
        prefill={"Siege": "", "Garrison (combat groups)": "", "Defenses": "Standard"},
        edits={
            "Siege": "Siege of Burg B",
            "Castle": "Burg B",
            "Garrison (combat groups)": "25",
        },
        saved=lambda s: [
            (x.name, x.castle, x.garrison) for x in s.sieges if x.castle == "Burg B"
        ],
        expected=[("Siege of Burg B", "Burg B", 25)],
        invalid=[{"Siege": ""}, {"Garrison (combat groups)": "-1"}],
        shown={"#sieges-list": "Burg B"},
    ),
    "edit siege": Contract(
        prefill={"Siege": "The Siege of Falkenstein", "Castle": "Burg Falkenstein"},
        edits={"Supplies": "Superior"},
        saved=lambda s: s.sieges[0].supplies,
        expected="Superior",
        invalid={"Siege": ""},
        shown={"#sieges-list": "Superior"},
    ),
    "add combatant": Contract(
        prefill={"Side": "0", "Drawn from": "character"},
        edits={"Character and weapon": "mag2|"},
        saved=lambda s: [c.name for c in s.fights[0].sides[0].combatants],
        expected=["Leandro", "Brother Oda"],
    ),
    "form a group": Contract(
        prefill={"Side": "0"},
        edits={"Side": "1", "Group": "Bandits", "Bandit 1": True, "Bandit 2": True},
        saved=lambda s: [(g.name, g.members) for g in s.fights[0].sides[1].groups],
        expected=[("Bandits", ["c-bandit1", "c-bandit2"])],
        invalid={"Side": "1"},
    ),
    "next blow": Contract(
        prefill={"Action": "Attack"},
        edits={"Action": "Wait"},
        saved=lambda s: (s.fights[0].round, len(s.fights[0].log)),
        expected=(1, 2),
    ),
    "next siege event": Contract(
        prefill={"Event": "Bombard a wall"},
        edits={"Event": "Keep the stockade"},
        saved=lambda s: (s.sieges[0].days, [e.text for e in s.sieges[0].events]),
        expected=(1, ["The stockade holds."]),
    ),
    "edit creature": Contract(
        prefill={"Name": "Aeolus", "Realm": "Magic", "Might Score": "8", "Size": "2"},
        edits={
            "Might Score": "12",
            "Many of a kind": True,
            "How many": "A herd",
            "Age": "200 (40)",
        },
        saved=lambda s: (
            s.creatures[0].might,
            s.creatures[0].many,
            s.creatures[0].how_many,
            s.creatures[0].age,
        ),
        expected=(12, True, "A herd", "200 (40)"),
        invalid={"Name": ""},
        shown={"#cr-info-left": "Magic Might 12 (Animal)"},
    ),
    "edit creature characteristics": Contract(
        prefill={"Soak": "3", "Fatigue levels": "OK, 0, -1, -3, -5, Unconscious"},
        edits={"Soak": "5", "Cunning, not Intelligence": True, "Encumbrance": "0 (0)"},
        saved=lambda s: (
            s.creatures[0].soak,
            s.creatures[0].cunning,
            s.creatures[0].encumbrance,
        ),
        expected=(5, True, "0 (0)"),
        invalid={"Soak": "hard"},
        shown={"#cr-characteristics-content": "Cun"},
    ),
    "add creature attack": Contract(
        prefill={"Attack": "", "Init": "0"},
        edits={"Attack": "Bite", "Init": "1", "Damage (blank = n/a)": "7"},
        saved=lambda s: [(a.name, a.init, a.damage) for a in s.creatures[0].attacks],
        expected=[("Kick", 4, 5), ("Bite", 1, 7)],
        invalid={"Attack": ""},
        shown={"#cr-attacks-list": "Bite", "#section-cr-attacks": "(2)"},
    ),
    "add creature power": Contract(
        prefill={"Power": "", "Might Point cost": "0"},
        edits={"Power": "Gallop on the Wind", "Might Point cost": "1", "Form": "Auram"},
        saved=lambda s: [(p.name, p.might_cost, p.form) for p in s.creatures[0].powers][
            -1
        ],
        expected=("Gallop on the Wind", 1, "Auram"),
        invalid={"Power": ""},
        shown={"#cr-powers-list": "Gallop on the Wind"},
    ),
    "add creature vis": Contract(
        prefill={"Pawns": "1", "Where in the body": ""},
        edits={"Pawns": "3", "Art": "Auram", "Where in the body": "in its mane"},
        saved=lambda s: [(v.pawns, v.art, v.where) for v in s.creatures[0].vis][-1],
        expected=(3, "Auram", "in its mane"),
        invalid={"Pawns": "0"},
        shown={"#cr-vis-list": "3 pawns of Auram, in its mane"},
    ),
    # House Rules
    "add house rule": Contract(
        prefill={"For": "character", "Name": "", "Tier": "Minor"},
        edits={
            "For": "laboratory",
            "Name": "Leaky Roof",
            "Type": "Flaw",
            "Tier": "Major",
            "Can be taken more than once": True,
        },
        saved=lambda s: [
            (e.id, e.type, e.tier, e.cost, e.category, e.repeatable, e.source)
            for e in s.custom_lab_virtues_flaws
        ],
        expected=[
            ("custom_labvf_leaky_roof", "Flaw", "Major", -3, "Structure", True, "")
        ],
        invalid={"Name": ""},
    ),
    # Players who sign in from a browser
    "add player": Contract(
        prefill={"Name": "", "Role": "player", "Passcode": ""},
        edits={"Name": "Ana", "Role": "storyguide", "Passcode": "rosemary"},
        saved=lambda s: [
            (
                p.id,
                p.name,
                p.role,
                pl.passcode_matches(p, "rosemary"),
                p.passcode_hash != "rosemary",
            )
            for p in s.players
        ],
        expected=[("ana", "Ana", "storyguide", True, True)],
        invalid=[{"Name": ""}, {"Name": "Ana", "Passcode": ""}],
        shown={"#section-players": "Players (1)"},
    ),
    "add spell": Contract(
        prefill={"Name": "", "Technique": Select.NULL, "Level": ""},
        edits={
            "Name": "Lamp of Tobias",
            "Technique": "Creo",
            "Form": "Ignem",
            "Level": "10",
            "Requisites": "Rego",
            "Range": "Touch",
            "Duration": "Sun",
            "Target": "Individual",
        },
        saved=lambda s: [
            (sp.technique, sp.form, sp.level, sp.requisites)
            for sp in s.spells
            if sp.name == "Lamp of Tobias"
        ],
        expected=[("Creo", "Ignem", 10, ["Rego"])],
        invalid=[
            {"Name": ""},
            {
                "Name": "Lamp",
                "Technique": "Creo",
                "Form": "Ignem",
                "Requisites": "Nope",
            },
        ],
        shown={"#spell-list": "Lamp of Tobias"},
    ),
    "edit spell": Contract(
        prefill={"Name": "Own Spell", "Technique": "Creo", "Level": "5"},
        edits={
            "Name": "Own Spell II",
            "Level": "15",
            "Range": "Touch",
            "Duration": "Sun",
            "Target": "Individual",
        },
        saved=lambda s: (s.spells[0].name, s.spells[0].level),
        expected=("Own Spell II", 15),
        invalid={"Name": ""},
    ),
    # Saga Content
    "add saga source": Contract(
        prefill={"Abbreviation": "", "Title": ""},
        edits={"Abbreviation": "HR", "Title": "Our house rules"},
        saved=lambda s: (
            [(x.abbreviation, x.title) for x in s.sources],
            s.books_in_play,
        ),
        expected=([("HR", "Our house rules")], None),
        # Blank; a sourcebook's abbreviation, or one of its other spellings;
        # the ; that separates the books an entry cites.
        invalid=[
            {"Abbreviation": ""},
            {"Abbreviation": "Covenants"},
            {"Abbreviation": "ArM5"},
            {"Abbreviation": "A;B"},
        ],
        shown={"#section-saga-sources": "Saga Sources (1)"},
    ),
    "edit saga source": Contract(
        prefill={"Abbreviation": "HR", "Title": "House rules"},
        edits={"Abbreviation": "OHR", "Title": "Our house rules"},
        saved=lambda s: [(x.abbreviation, x.title) for x in s.sources],
        expected=[("OHR", "Our house rules")],
        invalid={"Abbreviation": "DE"},
        shown={"#content-sources-list": "OHR"},
    ),
    "edit catalog": Contract(
        prefill={"Offered in this saga": True},
        edits={"Offered in this saga": False},
        saved=lambda s: s.hidden_catalogs,
        expected=["spells"],
        shown={"#content-catalogs-list": "Spells"},
    ),
    # Saving picks the catalog; the entry is chosen next (test_saga_content).
    "hide catalog entry": Contract(
        prefill={"Catalog": "virtues_flaws"},
        edits={"Catalog": "abilities"},
        saved=lambda s: s.hidden_entries,
        expected={},
    ),
    "edit traditions offered": Contract(
        prefill={"Vitkir (HMRE)": True, "Folk Witches (HMRE)": False},
        edits={"Folk Witches (HMRE)": True},
        saved=lambda s: s.traditions,
        expected=["trad_folk_witches", "trad_vitkir"],
        shown={
            "#section-traditions": (
                f"Traditions Offered (2 of {len(catalog.load_tradition_catalog())})"
            )
        },
    ),
}


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_form_contract(name):
    await run_contract(name, CONTRACTS[name])
