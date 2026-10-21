"""Dialog contract tests for the forms of a character's and a familiar's sheets (and the Creation
Worksheet's character steps).

Each form runs in one app session; dialog_contract_support.py has the
contract and the driver, dialog_openers.py how each form is reached."""

import pytest
from dialog_contract_support import (
    INITIATION,
    Contract,
    character,
    familiar,
    laboratory,
    last_gear,
    run_contract,
)
from dialog_openers import new_app, open_dialog
from textual.widgets import Select

from ars_magica_manager import catalog
from ars_magica_manager.models import AnimalForm

CONTRACTS: dict[str, Contract] = {
    # Creation Worksheet
    "spend creation xp": Contract(
        prefill={"Ability or Art": Select.NULL, "Pool xp": "5"},
        edits={
            "Ability or Art": "Area Lore: {region}",
            "Which one": "Rhine",
            "Pool xp": "15",
            "Specialty": "rivers",
        },
        saved=lambda s: (
            [(x.step, x.target, x.xp) for x in character(s).creation_xp],
            [
                a.specialty
                for a in character(s).abilities
                if a.name == "Area Lore: Rhine"
            ],
        ),
        expected=([("childhood", "Area Lore: Rhine", 15)], ["rivers"]),
        invalid=[
            {"Ability or Art": "Brawl", "Pool xp": "0"},
            {"Ability or Art": "Area Lore: {region}", "Pool xp": "5"},
        ],
        shown={"#abilities-list": "Area Lore: Rhine (rivers)"},
        live={
            "#fields-live": "Area Lore: Rhine: gains 15 xp\n"
            "Score 2 · Score 3 at 30 xp (15 more pool xp)"
        },
    ),
    "childhood blanks": Contract(
        prefill={"Area": "", "Second area": "", "Language": ""},
        edits={"Area": "Rhine", "Second area": "Alps", "Language": "French"},
        saved=lambda s: [(x.target, x.xp) for x in character(s).creation_xp],
        expected=[
            ("Area Lore: Rhine", 5),
            ("Area Lore: Alps", 5),
            ("Folk Ken", 15),
            ("Living Language: French", 5),
            ("Survival", 15),
        ],
        invalid={"Area": ""},
    ),
    "general spell level": Contract(
        prefill={"Level": "5"},
        edits={"Level": "20"},
        saved=lambda s: [(x.step, x.target, x.xp) for x in character(s).creation_xp],
        expected=[("apprenticeship_spells", "spell_aegis_of_the_hearth", 20)],
        invalid=[{"Level": "0"}, {"Level": "-"}],
    ),
    "gauntlet conditions": Contract(
        prefill={
            "Seasons of lab work": "0",
            "Aura": "3",
            "Lab quality": "0",
            "Living Conditions": "1",
        },
        edits={"Seasons of lab work": "6", "Aura": "5"},
        saved=lambda s: (
            character(s).creation_conditions.lab_seasons,
            character(s).creation_conditions.aura,
        ),
        expected=(6, 5),
        invalid=[{"Seasons of lab work": "-1"}, {"Aura": "x"}],
    ),
    "grogs aging chart": Contract(
        prefill={"Aging": "average", "Take the chart's crises": False},
        edits={"Aging": "harsh", "Move the Ability cap": True},
        saved=lambda s: (
            (c := s.character("grog9")).creation_conditions.aging_chart,
            c.creation_conditions.aging_chart_cap,
            c.creation_conditions.aged_to,
            c.aging.decrepitude_points,
        ),
        expected=("harsh", 1, 44, 6),
        live={"#fields-live": "Total: 6 Aging Point(s)."},
    ),
    "native language": Contract(
        prefill={"Language": ""},
        edits={"Language": "German"},
        saved=lambda s: [(x.target, x.xp, x.note) for x in character(s).creation_xp],
        expected=[("Living Language: German", 75, "native")],
        invalid={"Language": ""},
    ),
    "animal form": Contract(
        prefill={"Kind": "person"},
        edits={"Kind": "clawed", "Species": "Dog", "Size": "-1"},
        saved=lambda s: [
            (
                c.animal,
                c.background.size,
                [vf.vf_id for vf in c.virtues_flaws],
            )
            for c in s.characters
            if c.id == "grog9"
        ],
        expected=[
            (
                AnimalForm("clawed", "Dog", "Dog"),
                -1,
                ["vf_restricted_learning", "vf_no_hands", "vf_mute"],
            )
        ],
        invalid=[
            {"Kind": "clawed", "Species": ""},
            {"Kind": "clawed", "Species": "Dog", "Average lifespan": "0"},
        ],
    ),
    "edit personality trait": Contract(
        prefill={"Name": "Brave", "Score": "2"},
        edits={"Name": "Bold", "Score": "3"},
        saved=lambda s: (
            character(s).personality_traits[0].name,
            character(s).personality_traits[0].score,
        ),
        expected=("Bold", 3),
        invalid={"Name": ""},
        shown={"#personality-traits-list": "Bold: +3"},
    ),
    # Choosing a book weapon fills in its figures; a typed name stays.
    "add personal weapon": Contract(
        prefill={"Name": "", "Weapon": Select.NULL, "Attack": "0"},
        edits={"Weapon": "weapon_short_bow"},
        saved=lambda s: last_gear(character(s).inventory, "weapon"),
        # A blank name becomes the weapon's.
        expected=("Short Bow", "weapon_short_bow", "Standard", -1, 3, 0, 6, 2),
        invalid={"Name": ""},
    ),
    "edit natural weapon": Contract(
        prefill={"Name": "Beak", "Natural Weapon": Select.NULL},
        edits={"Natural Weapon": "natural_teeth"},
        saved=lambda s: last_gear(familiar(s).natural_weapons, "weapon"),
        expected=("Beak", "natural_teeth", "Standard", 0, 3, 1, 1, 0),
        invalid={"Quantity": "0"},
        shown={"#fam-natural-weapons-list": "Beak"},
    ),
    "edit character info": Contract(
        prefill={"Name": "Leandro", "Covenant": "cov1", "Assigned Laboratory": "lab1"},
        edits={
            "Setting": "Rhine",
            "Size": "1",
            "Confidence Score": "2",
            "Faith Points": "3",
        },
        saved=lambda s: (
            character(s).background.setting,
            character(s).background.size,
            character(s).background.confidence_score,
            character(s).background.faith_points,
        ),
        expected=("Rhine", 1, 2, 3),
        invalid={"Name": ""},
        shown={"#char-info-left": "Rhine"},
    ),
    "edit characteristics": Contract(
        prefill={"Intelligence": "0", "Quickness": "0"},
        edits={"Intelligence": "3", "Quickness": "-2"},
        saved=lambda s: (
            character(s).characteristics.intelligence,
            character(s).characteristics.quickness,
        ),
        expected=(3, -2),
        invalid={"Intelligence": "-"},
        shown={"#char-characteristics-content": "Int: +3"},
    ),
    "edit biographical detail": Contract(
        prefill={"Player": "", "Handedness": "right"},
        edits={
            "Player": "Sam",
            "Year Born": "1190",
            "Handedness": "left",
            "Biography": "Born in a storm.",
        },
        saved=lambda s: (
            character(s).background.player,
            character(s).background.year_born,
            character(s).description.handedness,
            character(s).description.biography,
        ),
        expected=("Sam", 1190, "left", "Born in a storm."),
        shown={"#char-biographical-left": "Sam"},
    ),
    "edit aging": Contract(
        prefill={"Decrepitude": "0", "Effects of Aging": ""},
        edits={
            "Decrepitude": "1",
            "Effects of Aging": "Limp",
            "Warping Score": "2",
            "Warping Points": "5",
        },
        saved=lambda s: (
            character(s).aging.decrepitude,
            character(s).aging.effects,
            character(s).aging.warping_score,
            character(s).aging.warping_points,
        ),
        expected=(1, "Limp", 2, 5),
        invalid={"Decrepitude": "-"},
        shown={"#aging-content": "Decrepitude: 1"},
    ),
    "edit wounds": Contract(
        prefill={"Soak": "0", "Light Wounds": "0", "Incapacitated": False},
        edits={"Soak": "3", "Light Wounds": "1", "Incapacitated": True},
        saved=lambda s: (
            character(s).wounds.soak,
            character(s).wounds.light,
            character(s).wounds.incapacitated,
        ),
        expected=(3, 1, True),
        invalid={"Soak": "-"},
        shown={"#wounds-content": "Incapacitated: yes"},
    ),
    "edit fatigue": Contract(
        prefill={"Level": "fresh"},
        edits={"Level": "weary"},
        saved=lambda s: character(s).fatigue_level,
        expected="weary",
        shown={"#fatigue-content": "Weary"},
    ),
    "edit hermetic background": Contract(
        prefill={"Domus Magna": "", "Age of Apprenticeship": ""},
        edits={"Domus Magna": "Durenmar", "Age of Apprenticeship": "15"},
        saved=lambda s: (
            character(s).hermetic.domus_magna,
            character(s).hermetic.age_of_apprenticeship,
        ),
        expected=("Durenmar", 15),
        invalid={"Age of Apprenticeship": "-"},  # crashed before
        shown={"#hermetic-background-left": "Durenmar"},
    ),
    "edit ability": Contract(
        prefill={"XP": "50"},
        edits={"XP": "75", "Specialty": "Grammar"},
        saved=lambda s: (
            character(s).abilities[0].level,
            character(s).abilities[0].specialty,
        ),
        expected=(5, "Grammar"),
        invalid={"XP": "-5"},
        live={"#fields-live": "Latin: Score 5 · Score 6 at 105 xp"},
        # the score and xp are in columns
        shown={"#abilities-list": "Latin (Grammar)           5       75/105"},
    ),
    "edit raw vis": Contract(
        prefill={"Art": "creo", "Pawns": "3"},
        edits={"Pawns": "5"},
        saved=lambda s: character(s).raw_vis,
        expected={"creo": 5},
        invalid={"Pawns": "-"},
    ),
    "give raw vis": Contract(
        prefill={"Pawns": "3", "To": Select.NULL},
        edits={"Pawns": "2", "To": "laboratory:lab1"},
        saved=lambda s: (
            character(s).raw_vis,
            laboratory(s).raw_vis,
            character(s).diary[-1].name,
            laboratory(s).diary[-1].name,
        ),
        expected=(
            {"creo": 1},
            {"ignem": 2, "creo": 2},
            "Moved 2 pawns of Creo vis to Tower",
            "Received 2 pawns of Creo vis from Leandro",
        ),
        # More than he has; none; nowhere to send it.
        invalid=[
            {"Pawns": "4", "To": "laboratory:lab1"},
            {"Pawns": "0", "To": "laboratory:lab1"},
            {"Pawns": "2"},
        ],
        shown={"#raw-vis-list-hermetic": "Creo: 1 pawn(s)"},
    ),
    "add research goal": Contract(
        prefill={"Goal": "", "Breakthrough": "Minor", "Target": "30"},
        edits={
            "Goal": "Piercing the Aegis",
            "Breakthrough": "Major",
            "Reaching it grants": "Ability",
            "Ability": "Aegis Lore",
        },
        saved=lambda s: (
            character(s).breakthroughs[-1].name,
            character(s).breakthroughs[-1].kind,
            character(s).breakthroughs[-1].target,
            character(s).breakthroughs[-1].grant_kind,
            character(s).breakthroughs[-1].grant,
        ),
        expected=("Piercing the Aegis", "Major", 45, "Ability", "Aegis Lore"),
        invalid=[{"Goal": ""}, {"Goal": "X", "Target": "0"}],
        shown={"#research-goals-list": "Piercing the Aegis (Major): 0/45"},
    ),
    "add secret research goal": Contract(
        prefill={"Goal": "", "Target": "30"},
        edits={"Goal": "Range: Horizon", "Keep the target secret": True},
        saved=lambda s: (
            character(s).breakthroughs[-1].name,
            character(s).breakthroughs[-1].hidden_target,
        ),
        expected=("Range: Horizon", True),
        shown={
            "#research-goals-list": "Range: Horizon (Minor): 0 points (target kept "
            "by the storyguide)"
        },
    ),
    "add integration goal": Contract(
        prefill={"Goal": "", "Target": "30"},
        edits={"Integration": "Hermetic Rune Magic"},
        saved=lambda s: (
            character(s).breakthroughs[-1].name,
            character(s).breakthroughs[-1].kind,
            character(s).breakthroughs[-1].target,
            character(s).breakthroughs[-1].grant_kind,
            character(s).breakthroughs[-1].grant,
        ),
        expected=(
            "Hermetic Rune Magic",
            "Major",
            45,
            "Virtue",
            "vf_hermetic_rune_magic",
        ),
        shown={"#research-goals-list": "Hermetic Rune Magic (Major): 0/45"},
    ),
    "add tradition effect": Contract(
        prefill={"Name": "", "Kind": "spell", "Cast or made by": "Rune script"},
        edits={
            "Name": "Wealth Rune",
            "Kind": "rune script",
            "Uses": "Fehu",
            "Level": "10",
        },
        saved=lambda s: (
            character(s).tradition_effects[-1].name,
            character(s).tradition_effects[-1].tradition,
            character(s).tradition_effects[-1].uses,
            character(s).tradition_effects[-1].level,
        ),
        expected=("Wealth Rune", "trad_vitkir", ["Fehu"], 10),
        invalid=[{"Name": ""}, {"Name": "X", "Level": "-5"}],
        shown={"#trad-trad_vitkir-effects": "Wealth Rune (rune script, level 10)"},
    ),
    "add bound being": Contract(
        prefill={"Name": "", "Bonus": "0", "Bonus adds to": "none"},
        edits={"Name": "Huginn", "Bonus": "2", "Bonus adds to": "lab"},
        saved=lambda s: (
            character(s).bound_beings[-1].name,
            character(s).bound_beings[-1].tradition,
            character(s).bound_beings[-1].bonus,
            character(s).bound_beings[-1].applies_to,
        ),
        expected=("Huginn", "trad_vitkir", 2, "lab"),
        invalid=[{"Name": ""}, {"Name": "X", "Bonus": "2", "Bonus adds to": "none"}],
        shown={"#trad-trad_vitkir-bonds": "Huginn: +2 to Lab Totals"},
    ),
    "virtue parameters": Contract(
        prefill={"Subject": ""},
        edits={"Subject": "Latin"},
        saved=lambda s: character(s).virtues_flaws[-1].params,
        expected={"subject": "latin"},  # parameters are stored lower-case
        invalid={"Subject": ""},
    ),
    "virtue ability choice": Contract(
        # An {ability} is picked from a list, not typed.
        prefill={"Ability": Select.NULL},
        edits={"Ability": "magic theory"},
        saved=lambda s: character(s).virtues_flaws[-1].params,
        expected={"ability": "magic theory"},
        invalid={"Ability": Select.NULL},
    ),
    "change virtue choice": Contract(
        # Edit on a Virtue changes only what it names, in place.
        prefill={"Ability": "magic theory"},
        edits={"Ability": "finesse"},
        saved=lambda s: [
            vf.params
            for vf in character(s).virtues_flaws
            if vf.vf_id == "vf_puissant_ability"
        ],
        expected=[{"ability": "finesse"}],
        invalid={"Ability": Select.NULL},
        shown={"#vf-virtues-list": "Puissant Finesse"},
    ),
    "edit familiar info": Contract(
        prefill={"Name": "Corax", "Species": ""},
        edits={"Species": "Raven", "Year Bound": "1210", "Size": "-2"},
        saved=lambda s: (familiar(s).species, familiar(s).year_bound, familiar(s).size),
        expected=("Raven", 1210, -2),
        invalid={"Name": ""},
        shown={"#fam-info-content": "Raven"},
    ),
    "edit familiar binding": Contract(
        prefill={"Initial Binding Lab Total": "0"},
        edits={"Binding Technique": "Rego", "Initial Binding Lab Total": "30"},
        saved=lambda s: (familiar(s).binding_technique, familiar(s).binding_lab_total),
        expected=("Rego", 30),
        shown={"#fam-binding-content": "Rego"},
    ),
    "edit spell mastery": Contract(
        prefill={"Score": "0", "XP": "0"},
        edits={"Score": "2", "XP": "10"},
        saved=lambda s: (
            character(s).spells_known[0].mastery_score,
            character(s).spells_known[0].mastery_xp,
        ),
        expected=(2, 10),
        invalid=[{"Score": "-"}, {"XP": "x"}],
    ),
    "edit familiar characteristics": Contract(
        prefill={"Intelligence": "0", "Base Soak": "0"},
        edits={"Intelligence": "-5", "Base Soak": "2", "Magic Resistance": "4"},
        saved=lambda s: (
            familiar(s).characteristics.intelligence,
            familiar(s).base_soak,
            familiar(s).magic_resistance,
        ),
        expected=(-5, 2, 4),
        invalid={"Intelligence": "-"},
        shown={"#fam-characteristics-content": "Base Soak: 2"},
    ),
    "edit familiar wounds": Contract(
        prefill={"Light Wounds": "0", "Dead": False},
        edits={"Light Wounds": "2", "Dead": True},
        saved=lambda s: (familiar(s).wounds.light, familiar(s).wounds.dead),
        expected=(2, True),
        invalid={"Light Wounds": "-"},
    ),
    "grog yearly update": Contract(
        prefill={"Vocational xp": "7", "Story awards this year": "0"},
        edits={
            "Vocational training": "Single Weapon",
            "Practice (4 xp)": "Brawl",
            "Exposure (2 xp)": "Awareness",
            "Story awards this year": "1",
        },
        saved=lambda s: (
            s.character("grog9").grog_year.vocational,
            s.character("grog9").grog_year.practice,
            s.character("grog9").grog_year.exposure,
            s.character("grog9").grog_year.story_awards,
        ),
        expected=("Single Weapon", "Brawl", "Awareness", 1),
        invalid={"Vocational xp": "x"},
    ),
    "plan a season": Contract(
        prefill={"Activity": None, "Months lost": "0", "Notes": ""},
        edits={
            "Activity": "practice",
            "Experience in": "ability:Latin",
            "Notes": "Reading aloud",
        },
        saved=lambda s: [
            (p.activity, [a.subject for a in p.allocations], p.details)
            for p in s.season_plans
        ],
        expected=[("practice", ["ability:Latin"], "Reading aloud")],
        invalid={"Months lost": "-"},
    ),
    "plan an initiation": Contract(
        prefill={"Activity": None, "Months lost": "0", "Notes": ""},
        edits=INITIATION,
        saved=lambda s: [
            (
                p.activity,
                p.title,
                p.other_modifier,
                p.effect_id,
                p.effect_params,
                p.device_id,
                p.ordeal_params,
                p.ordeal_kind,
            )
            for p in s.season_plans
        ],
        expected=[
            (
                "undergo_initiation",
                "Mercere Lore",
                12,
                "vf_affinity_with_art",
                {"art": "ignem"},
                "vf_deficient_technique",
                {"technique": "creo"},
                "gain",
            )
        ],
        invalid=[
            {**INITIATION, "Virtue initiated": None},
            {**INITIATION, "Ordeal": "raise"},
        ],
    ),
    "add character diary entry": Contract(
        prefill={"Year": "1220", "Season": "Autumn", "Name": ""},
        edits={
            "Year": "1221",
            "Activity Type": "Practice",
            "Name": "Latin lessons",
            "Details": "At the abbey",
        },
        saved=lambda s: (
            character(s).diary[-1].year,
            character(s).diary[-1].activity,
            character(s).diary[-1].name,
            character(s).diary[-1].details,
        ),
        expected=(1221, "Practice", "Latin lessons", "At the abbey"),
        invalid={"Year": "-"},
        shown={"#char-diary-list": "Latin lessons"},
    ),
    "add ability": Contract(
        prefill={"XP": "0", "Specialty": ""},
        edits={"XP": "30", "Specialty": "Running"},
        saved=lambda s: [
            (a.category, a.xp, a.specialty)
            for a in character(s).abilities
            if a.name == "Athletics"
        ],
        expected=[("General", 30, "Running")],
        invalid={"XP": "-5"},
        live={"#fields-live": "Athletics: Score 3 · Score 4 at 50 xp"},
        shown={"#abilities-list": "Athletics (Running)"},
    ),
    "edit arts": Contract(
        prefill={"Creo": "0", "Vim": "0"},
        edits={"Creo": "55", "Vim": "6"},
        saved=lambda s: (character(s).arts["creo"].xp, character(s).arts["vim"].xp),
        expected=(55, 6),
        invalid={"Creo": "lots"},
        live={
            "#art-score-creo": "10       66 xp",
            "#art-score-vim": "3        10 xp",
        },
    ),
    "edit familiar fatigue": Contract(
        prefill={"Level": "fresh"},
        edits={"Level": "weary"},
        saved=lambda s: familiar(s).fatigue_level,
        expected="weary",
        shown={"#fam-fatigue-content": "Weary"},
    ),
    "add bond power": Contract(
        prefill={"Power Name": "", "Level": "0"},
        edits={
            "Power Name": "Mind link",
            "Level": "15",
            "Technique": "Intellego",
            "Form": "Mentem",
        },
        saved=lambda s: [
            (p.level, p.technique, p.form)
            for p in familiar(s).bond_powers
            if p.name == "Mind link"
        ],
        expected=[(15, "Intellego", "Mentem")],
        invalid={"Level": "lots"},
        shown={"#fam-bond-powers-list": "Mind link"},
    ),
    "edit bond power": Contract(
        prefill={"Power Name": "Speak", "Uses/Day": "0"},
        edits={"Power Name": "Speech"},
        saved=lambda s: familiar(s).bond_powers[0].name,
        expected="Speech",
        invalid={"Level": "lots"},
        shown={"#fam-bond-powers-list": "Speech"},
    ),
    "edit character traditions": Contract(
        prefill={"Vitkir (HMRE)": True},
        edits={"Vitkir (HMRE)": False},
        saved=lambda s: s.character("mag1").traditions,
        expected=[],
    ),
}


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_form_contract(name):
    await run_contract(name, CONTRACTS[name])


# -- which book tables each weapon form offers --


@pytest.mark.parametrize(
    ("name", "tables"),
    [
        ("edit covenant weapon", ("melee", "missile")),
        ("add personal weapon", ("melee", "missile")),
        ("edit natural weapon", ("natural",)),
    ],
)
async def test_weapon_forms_offer_the_books_tables_for_their_sheet(name, tables):
    app = new_app()
    async with app.run_test(size=(140, 70)) as pilot:
        _, dialog = await open_dialog(pilot, app, name)
        [book] = [f for f in dialog.fields if f.key == "gear_id"]
    assert [value for _, value in book.options] == [
        w.id for w in catalog.load_weapon_catalog(tables=tables)
    ]
