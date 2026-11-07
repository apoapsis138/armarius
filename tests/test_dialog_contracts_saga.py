"""Dialog contract tests for the forms of the saga picker, the saga itself, Saga Content and the bestiary.

Each form runs in one app session; dialog_contract_support.py has the
contract and the driver, dialog_openers.py how each form is reached."""

import pytest
from dialog_contract_support import Contract, all_sagas, run_contract
from textual.widgets import Select

from ars_magica_manager import armies, catalog
from ars_magica_manager import house_rules as hr
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
    "hide from the players": Contract(
        prefill={"Which": "lords", "In the lands of": Select.NULL},
        edits={"Which": "characters"},
        saved=lambda s: sorted(c.id for c in s.characters if not c.known),
        expected=["comp1", "grog9", "mag1", "mag2", "mag_sketch"],
        live={"#fields-live": "5 records known now would be hidden."},
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
                b.sides[0].groups
                == armies.army_groups(s.neighbour("gottfried"), at_home=False),
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
        prefill={"Maneuver": "Defend", "Fighting for": "0", "How it went": "beaten"},
        # One "How it went" a Maneuver: the Defend one shown.
        aliases={"How it went": "fld-condition_Defend"},
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
    "hire mercenaries": Contract(
        prefill={"Side": "0", "Knights": "0"},
        edits={"Knights": "2", "Levies": "3"},
        saved=lambda s: (
            s.battles[0].sides[0].mix,
            s.battles[0].sides[0].groups,
        ),
        expected=({"knights": 2, "levies": 3}, 45),
        # The Count's Average budget is 100 pounds (Lords of Men p. 103).
        invalid={"Knights": "7"},
        live={"#fields-live": "Cost 33 pounds"},
    ),
    "end of the day": Contract(
        prefill={"How the day ends": "won", "That Reputation": "Victorious commander"},
        edits={"How the day ends": "truce"},
        saved=lambda s: s.battles[0].ended.startswith("A truce"),
        expected=True,
    ),
    "combat options": Contract(
        prefill={"Option": "charge", "Combat Ability": "Single Weapon"},
        edits={"Option": "crowd"},
        saved=lambda s: len(s.fights),
        expected=1,
        live={"#fields-live": "At most 6 attack one man"},
    ),
    "change deployments": Contract(
        prefill={"Besiegers at the North": "1", "Garrison at the West": "2"},
        edits={"Garrison at the North": "0"},
        saved=lambda s: s.sieges[0].garrison_walls,
        expected=[0, 2, 2, 2],
        invalid={"Garrison at the West": "many"},
        live={"#fields-live": "Undefended: North"},
    ),
    "supplies story": Contract(
        prefill={"What happens": "blockade"},
        edits={"What happens": "relief"},
        saved=lambda s: (s.sieges[0].supplies, s.sieges[0].events[-1].kind),
        expected=("Superior", "story"),
    ),
    "castle taken": Contract(
        prefill={"Its governor": "", "What becomes of it": ""},
        edits={"Its governor": "Sir Odo"},
        saved=lambda s: (s.sieges[0].ended, "Sir Odo" in s.sieges[0].events[-1].text),
        expected=("Taken", True),
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
    "add good": Contract(
        prefill={"Name": "", "Priced": "commodity", "Class": "bulk", "Sold by": "ton"},
        edits={
            "Name": "Amber",
            "Class": "luxury",
            "Standard": "500",
            "Superior": "1,000",
            "Bought in bulk at": "the Baltic; Hungary",
        },
        saved=lambda s: [
            (g.id, g.commodity_class, g.prices, g.sources) for g in s.custom_goods
        ],
        expected=[
            (
                "custom_good_amber",
                "luxury",
                ("", "500", "1,000", ""),
                ("the Baltic", "Hungary"),
            )
        ],
        invalid=[{"Name": ""}, {"Name": "Amber", "Standard": "lots"}],
        shown={"#section-content-goods": "Goods (78)"},
    ),
    "add purity": Contract(
        prefill={"Purity": "", "Metal content, %": ""},
        edits={"Purity": "Coin", "Metal content, %": "50"},
        saved=lambda s: [(p.good_id, p.label, p.percent) for p in s.good_purities],
        expected=[("good_silver", "Coin", 50.0)],
        invalid=[
            {"Purity": "Coin", "Metal content, %": "150"},
            {"Purity": "", "Metal content, %": "50"},
        ],
        shown={"#content-goods-info": "Coin, 50% 1,210"},
    ),
    "move to source": Contract(
        prefill={"Move to": "HR", "Ours (Character, no source)": False},
        edits={"Ours (Character, no source)": True},
        saved=lambda s: [(e.name, e.source) for _, e in hr.all_entries(s)],
        expected=[("Ours", "HR")],
        # Nothing ticked: nothing to move.
        invalid={"Ours (Character, no source)": False},
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
        # Every tradition of the books in play is offered until turned off.
        prefill={"Vitkir (HMRE)": True, "Folk Witches (HMRE)": True},
        edits={"Folk Witches (HMRE)": False},
        saved=lambda s: s.traditions_off,
        expected=["trad_folk_witches"],
        shown={
            "#section-traditions": (
                f"Traditions Offered ({len(catalog.load_tradition_catalog()) - 1}"
                f" of {len(catalog.load_tradition_catalog())})"
            )
        },
    ),
    # A saga's own Abilities in House Rules (HoH:S pp. 103-106).
    "add house rule ability": Contract(
        prefill={"For": "character", "Name": ""},
        edits={
            "For": "ability",
            "Name": "Call the Tide",
            "Ability category": "Supernatural",
            "Realm": "Faerie",
            "Rolls with": "Stamina",
        },
        aliases={"Ability category": "fld-category_ability"},
        live={"#fields-live": "Casting Total: Stamina + Call the Tide"},
        saved=lambda s: (
            [
                (a.id, a.category, a.realm, a.characteristic, a.xp_table, a.source)
                for a in s.custom_abilities
            ],
            [(v.name, v.tier, v.category, v.cost) for v in s.custom_virtues_flaws],
        ),
        expected=(
            [
                (
                    "custom_ability_call_the_tide",
                    "Supernatural",
                    "Faerie",
                    "Stamina",
                    "ability",
                    "",
                )
            ],
            [("Call the Tide", "Major", "Supernatural", 3)],
        ),
        invalid=[
            {"For": "ability", "Name": ""},
            {"For": "ability", "Name": "Athletics"},
        ],
        shown={"#house-rules-list": "Call the Tide"},
    ),
    "edit house rule ability": Contract(
        prefill={
            "Name": "Speak with Ravens",
            "Realm": "Magic",
            "Rolls with": "Communication",
        },
        edits={"Name": "Raven Tongue", "Realm": "Faerie"},
        saved=lambda s: [(a.id, a.name, a.realm) for a in s.custom_abilities],
        expected=[("custom_ability_speak_with_ravens", "Raven Tongue", "Faerie")],
        invalid={"Name": ""},
        shown={"#house-rules-list": "Raven Tongue"},
    ),
    # Saga Content's Mystery Cults (The Mysteries Revised Edition pp. 13-19).
    "add mystery cult": Contract(
        prefill={"Name": "", "Realm": "Magic", "Initiation uses": "Presence"},
        edits={
            "Name": "The Seventh Wave",
            "Its Lore (a new Ability)": "Seventh Wave Lore",
            "Realm": "Faerie",
            "Founded in": "1218",
        },
        saved=lambda s: [(c.id, c.lore, c.realm, c.founded) for c in s.custom_cults],
        expected=[
            ("custom_cult_the_seventh_wave", "Seventh Wave Lore", "Faerie", 1218)
        ],
        invalid=[
            {"Name": ""},
            {"Name": "X", "Its Lore (a new Ability)": "Magic Theory"},
            {"Name": "X", "Its Lore (a new Ability)": ""},
        ],
        shown={"#section-content-cults": "The Saga's Mystery Cults (1)"},
    ),
    "edit mystery cult": Contract(
        prefill={"Name": "The Spinner's Thread", "Realm": "Faerie"},
        edits={"Name": "The Thread", "Initiation uses": "Communication"},
        saved=lambda s: [(c.name, c.characteristic) for c in s.custom_cults],
        expected=[("The Thread", "Communication")],
        invalid={"Name": ""},
        shown={"#section-content-cult": "The Thread"},
    ),
    "add cult degree": Contract(
        prefill={"Degree": ""},
        edits={"Degree": "Weaver", "Mystery Virtue": "vf_faerie_magic"},
        saved=lambda s: [(d.name, d.virtue_id) for d in s.custom_cults[0].degrees],
        expected=[("Spinner", "vf_second_sight"), ("Weaver", "vf_faerie_magic")],
        invalid=[
            {"Degree": ""},
            {"Degree": "Again", "Mystery Virtue": "vf_second_sight"},
        ],
        shown={"#section-content-cult-degrees": "Degrees (2)"},
    ),
    "edit cult script": Contract(
        prefill={
            "Script": "The Silk Hall",
            "Quests (+3 each)": "1",
            "Ordeal": "minor",
            "Its Flaw": "vf_visions",
        },
        edits={"Quests (+3 each)": "2", "Sympathy (−5 to +5)": "1"},
        saved=lambda s: s.custom_cults[0].degrees[0].script.bonus,
        expected=14,
        invalid=[
            {"Script": ""},
            {"Something of great value (0, +3 to +6)": "2"},
            {"Sympathy (−5 to +5)": "6"},
        ],
        live={"#fields-live": "= +14"},
        shown={"#section-content-cult-scripts": "The Silk Hall: +14"},
    ),
    "add cult component": Contract(
        prefill={"Kind": "quest", "What it is": ""},
        edits={"Kind": "unique_quest", "What it is": "The head of the Minotaur"},
        saved=lambda s: [
            (c.key, c.bonus, c.note)
            for c in s.custom_cults[0].degrees[0].script.components
        ][-1],
        expected=("unique_quest", 6, "The head of the Minotaur"),
        invalid={"Kind": "place"},
        shown={"#content-cult-scripts-list": "The head of the Minotaur"},
    ),
    # Fleet battles (Tales of Power pp. 106-110).
    "edit fleet battle": Contract(
        prefill={
            "Fought": "sea",
            "Seehund, coastal buss, 8 men": True,
            "Second army's other ships": "2",
        },
        edits={"Möwe, coastal buss, 8 men": False, "Second army's other ships": "3"},
        saved=lambda s: (
            s.battles[0].sides[0].ships,
            s.battles[0].sides[1].other_ships,
        ),
        expected=(["seehund"], 3),
        invalid=[
            {"Second army's other ships": "-1"},
            {"Second army's other ships": "0"},
        ],
        live={"#fields-live": "1 ship against 3"},
        shown={"#conflicts-info-panel": "Ships: Seehund (8 men)."},
    ),
    "fleet battle event": Contract(
        prefill={"Event": "cut", "Engaged: Seehund": True, "Engaged: Möwe": True},
        edits={
            "Event": "board",
            "Engaged: Möwe": False,
            "Engaged: Second army's others": "1",
            "Leading the event": "comp1",
        },
        saved=lambda s: [
            (e.deed, e.engaged_ships, e.engaged_other) for e in s.battles[0].events
        ],
        expected=[("board", ["seehund"], [0, 1])],
        invalid={"Engaged: Second army's others": "3"},
        live={"#fields-live": "Engaged: 1 against 1"},
        shown={"#conflict-battles-list": "Off Terschelling"},
    ),
}


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_form_contract(name):
    await run_contract(name, CONTRACTS[name])
