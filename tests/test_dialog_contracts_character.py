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
from ars_magica_manager.rules import divine_state as ds
from ars_magica_manager.rules import merchants

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
        edits={"Name": "Bold", "Score": "3", "Temporary Sympathy Trait?": True},
        saved=lambda s: (
            character(s).personality_traits[0].name,
            character(s).personality_traits[0].score,
            character(s).personality_traits[0].type,
        ),
        expected=("Bold", 3, "Sympathy, temporary"),
        invalid={"Name": ""},
        shown={"#personality-traits-list": "Bold: +3 (Sympathy, temporary)"},
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
            "Height": "1.8",
            "Handedness": "left",
            "Biography": "Born in a storm.",
        },
        saved=lambda s: (
            character(s).background.player,
            character(s).background.year_born,
            character(s).description.height,
            character(s).description.handedness,
            character(s).description.biography,
        ),
        expected=("Sam", 1190, 1.8, "left", "Born in a storm."),
        # Age, from Year Born, is in the top panel, refreshed with it.
        shown={
            "#char-biographical-left": "Height: 1.8",
            "#char-info-left": "Age:            30",
        },
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
        edits={
            "House": "house_bonisagus",
            "Parens": "Trianoma",
            "Domus Magna": "Durenmar",
            "Age of Apprenticeship": "15",
        },
        saved=lambda s: (
            character(s).hermetic.house,
            character(s).hermetic.parens,
            character(s).hermetic.domus_magna,
            character(s).hermetic.age_of_apprenticeship,
        ),
        expected=("house_bonisagus", "Trianoma", "Durenmar", 15),
        invalid={"Age of Apprenticeship": "-"},  # crashed before
        shown={"#hermetic-background-left": "House: Bonisagus"},
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
    "add power": Contract(
        prefill={"Name": "", "Granted by": "Lesser Power", "Level": "0"},
        edits={
            "Name": "Wings of the Owl",
            "Granted by": "Greater Power",
            "Level": "30",
            "Penetration": "10",
        },
        saved=lambda s: [
            (p.name, p.virtue, p.level, p.penetration) for p in character(s).powers
        ],
        expected=[("Wings of the Owl", "Greater Power", 30, 10)],
        invalid=[{"Name": ""}, {"Name": "X", "Level": "lots"}],
        shown={"#char-powers-list": "Wings of the Owl"},
    ),
    "add agent": Contract(
        prefill={"Name": "", "Social Status": "free", "Impressed": False},
        edits={
            "Name": "Udo the Miller",
            "Social Status": "minor_virtue",
            "Serves a rival (+9)": True,
            "Resources": "the mill and its gossip",
        },
        saved=lambda s: [
            (a.name, a.status, a.modifiers, a.resistance, a.resources)
            for a in character(s).agents
        ],
        expected=[
            (
                "Udo the Miller",
                "minor_virtue",
                ["rival"],
                None,
                "the mill and its gossip",
            )
        ],
        invalid=[{"Name": ""}, {"Name": "X", "Bond score": "lots"}],
        live={"#fields-live": "Resistance 10 on the Agent Recruitment Table"},
        shown={
            "#char-agents-list": "Udo the Miller",
            "#char-agents-header": "Agents: 0 of",
        },
    ),
    "set agent task": Contract(
        prefill={"Task": "common", "Done": "weeks", "Risk to him": "none"},
        edits={"Task": "sensitive", "Done": "days", "Risk to him": "injury"},
        saved=lambda s: [a.name for a in character(s).agents],
        expected=["Sir Konrad", "Father Bertolf"],
        live={"#fields-live": "Ease Factor 10 (task 6 + haste 1 + risk 3"},
        shown={"#char-agents-list": "Sir Konrad"},
    ),
    "resolve agent task": Contract(
        prefill={"Task": "easy", "Ease Factor": "6", "Risk to him": "none"},
        edits={
            "What he does": "steal the ring",
            "Characteristic + Ability": "5",
            "Task": "hard",
        },
        saved=lambda s: character(s).diary[-1].name,
        expected="Sir Konrad's task: steal the ring",
        invalid=[{"Characteristic + Ability": "lots"}, {"Ease Factor": "-1"}],
        live={"#fields-live": "Ease Factor 12"},
        shown={"#char-agents-list": "Sir Konrad"},
    ),
    "spend agency xp": Contract(
        prefill={"Spend on": "resistance", "Agency experience": "6"},
        edits={"Agency experience": "3"},
        saved=lambda s: (character(s).agents[1].resistance, character(s).agency_xp),
        expected=(2, 7),
        invalid=[{"Agency experience": "0"}, {"Agency experience": "2"}],
        live={"#fields-live": "Resistance 3 to 2, for 3 Agency experience"},
        shown={"#char-agents-list": "2, impressed"},
    ),
    "labor from story": Contract(
        prefill={"Award": "subplot", "Seasons' worth": Select.NULL},
        edits={"The story": "The Doge's ring", "Award": "central"},
        saved=lambda s: (
            character(s).labor_points
            - 2
            * merchants.season_labor(
                character(s), "Profession: Merchant", "communication"
            ),
            character(s).diary[-1].name,
        ),
        expected=(40, "Labor Points from a story: The Doge's ring"),
        live={"#fields-live": "2 seasons' worth of Labor Points"},
        shown={"#char-season-content": "Labor Points"},
    ),
    "invest time or money": Contract(
        prefill={"Investment": "money", "Pounds spent": "0"},
        edits={"Investment": "speculation", "In what": "wool", "Labor Points": "20"},
        saved=lambda s: [(i.kind, i.name, i.lp) for i in character(s).investments],
        expected=[("speculation", "wool", 20)],
        invalid=[
            {"Investment": "speculation", "Labor Points": "5"},
            {"Investment": "speculation", "Labor Points": "50"},
        ],
        live={"#fields-live": "+2 a year"},
        shown={"#char-season-content": "Speculation (wool): 20 Labor Points"},
    ),
    "add constant effect": Contract(
        prefill={"Effect": "", "Realm": "Magic"},
        edits={"Effect": "Ring of Flight", "Realm": "Faerie"},
        saved=lambda s: [
            (e.name, e.realm, e.powerful) for e in character(s).constant_effects
        ],
        expected=[("Ring of Flight", "Faerie", False)],
        invalid=[{"Effect": ""}],
        shown={"#char-constant-effects-list": "Ring of Flight"},
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
        shown={"#fam-wounds-content": "Light Wounds:  2"},
    ),
    "reward or punish": Contract(
        prefill={"Reward or punishment": "improved_rations", "For how long": "A month"},
        edits={
            "Reward or punishment": "flogging",
            "Blows": "5",
            "Ordered by": "magus",
            "Just and in proportion": False,
            "Why": "asleep on watch",
        },
        saved=lambda s: (
            s.character("grog9").wounds.light,
            s.character("grog9").long_term_fatigue,
            [d.kind for d in s.character("grog9").discipline],
            [e.loyalty for e in s.covenant("cov1").diary if e.loyalty],
        ),
        expected=(2, 3, ["flogging"], [-12]),
        invalid={"Reward or punishment": "promotion", "His rank now": ""},
        live={
            "#fields-live": "5 blows: 2 Light Wounds and 3 Long-Term Fatigue levels."
        },
    ),
    "retire a grog": Contract(
        prefill={"He retires on": "pension"},
        edits={"He retires on": "rent", "Note": "keeps the gate"},
        saved=lambda s: (
            [(d.kind, d.note) for d in s.character("grog9").discipline],
            s.character("grog9").diary[-1].name,
        ),
        expected=([("retired", "rent")], "Retired, paying rent"),
    ),
    "craft by magic": Contract(
        prefill={
            "Technique": "Rego",
            "The work": "Average",
            "Precise Casting on the spell": "0",
        },
        edits={"The work": "Hard", "Work for one craftsman": "A season"},
        saved=lambda s: s.character("mag1").diary,
        expected=[],
        invalid={"Precise Casting on the spell": "x"},
        live={"#fields-live": "against 21"},
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
            "Work out the modified level": True,
            "Maintains concentration (+5)": True,
        },
        saved=lambda s: [
            (p.level, p.technique, p.form, p.worked_out, p.maintains_concentration)
            for p in familiar(s).bond_powers
            if p.name == "Mind link"
        ],
        expected=[(15, "Intellego", "Mentem", True, True)],
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
    # A craftsman's sale of his finished goods (City & Guild).
    "sell finished goods": Contract(
        prefill={"Customer": "typical", "Standard price (pence)": "0", "Die": ""},
        edits={
            "The goods": "8 shortswords",
            "Standard price (pence)": "200",
            "Die": "10",
        },
        saved=lambda s: character(s).diary[-1].name,
        expected="Sold: 8 shortswords",
        invalid=[{"Standard price (pence)": "0"}, {"Die": "11"}],
        live={"#fields-live": "against Ease Factor 9"},
    ),
    # Complexion, with Art & Academe's medicine.
    "edit biographical detail (complexion)": Contract(
        prefill={"Player": ""},
        edits={"Complexion": "sanguine-melancholic", "A touch of": "phlegmatic"},
        saved=lambda s: (
            character(s).description.complexion,
            character(s).description.complexion_minor,
        ),
        expected=("sanguine-melancholic", "phlegmatic"),
        shown={"#char-biographical-left": "Complexion: Sanguine, then melancholic"},
    ),
    # A young character's parent's vocation (Apprentices).
    "parent vocation": Contract(
        prefill={"Parent's vocation": "", "Parent's score": "0"},
        edits={"Parent's vocation": "Craft: Smith", "Parent's score": "6"},
        saved=lambda s: (
            character(s).creation_conditions.vocation,
            character(s).creation_conditions.vocation_score,
        ),
        expected=("Craft: Smith", 6),
        invalid=[{"Parent's score": "-1"}, {"Parent's score": "x"}],
    ),
    # Art & Academe's ligatures and the apothecary's store.
    "make a ligature": Contract(
        prefill={"For": "", "Die": ""},
        edits={"For": "a surgery roll", "Die": "10"},
        saved=lambda s: character(s).diary[-1].name,
        expected="Ligature: a surgery roll",
        invalid=[{"For": ""}, {"For": "a surgery roll", "Die": "-1"}],
        live={"#fields-live": "the Ligature Bonus Table"},
    ),
    "apothecary's store": Contract(
        prefill={"Ingredient": "", "Assistants": "0", "Die": ""},
        edits={"Ingredient": "henbane", "Die": "7"},
        saved=lambda s: character(s).diary[-1].name,
        expected="Searched for: henbane",
        invalid=[{"Ingredient": ""}, {"Ingredient": "henbane", "Assistants": "9"}],
        live={"#fields-live": "a month's search"},
    ),
    # The Theban Tribunal's Byzantine customs (The Sundered Eagle).
    "hermetic letter": Contract(
        prefill={"The letter": "compose", "Lore": "Mercere Lore"},
        edits={"The letter": "read", "Subtler than plain, by": "2"},
        saved=lambda s: character(s).diary,
        expected=[],
        invalid={"Subtler than plain, by": "x"},
        live={"#fields-live": "Against 8"},
    ),
    "invoke a broken oath": Contract(
        prefill={"The oath-breaker": Select.NULL, "Styx was named in the oath": False},
        edits={
            "The oath-breaker": "grog9",
            "Styx was named in the oath": True,
            "The witnessing spirit's Might": "50",
            "Its punishment, if heard": "vf_greater_malediction_toad_of_lies",
        },
        saved=lambda s: character(s).diary[-1].name,
        expected="Leandro invoked an oath broken by Hugo",
        invalid=[
            {"The witnessing spirit's Might": "x"},
            {
                "The oath-breaker": "grog9",
                "Its punishment, if heard": "vf_greater_malediction_toad_of_lies",
            },
        ],
        live={"#fields-live": "a Major Flaw"},
    ),
    "make greek fire": Contract(
        prefill={"Doses being made": "1"},
        edits={"Doses being made": "2", "The laboratory's Safety": "2"},
        saved=lambda s: character(s).diary[-1].name,
        expected="Made Greek Fire",
        invalid={"Doses being made": "0"},
        live={"#fields-live": "a reagent of level 15"},
    ),
    "paint an icon": Contract(
        prefill={"Depicting": "", "Kept at": "cologne"},
        edits={"Depicting": "St Ursula", "Seasons of Standard decoration": "1"},
        saved=lambda s: s.neighbour("cologne").details["relics"][-1]["name"],
        expected="An icon of St Ursula",
        invalid=[{"Depicting": ""}, {"Seasons of Standard decoration": "-1"}],
        live={"#fields-live": "Aesthetic Quality"},
    ),
    "venerate an icon": Contract(
        prefill={"In an emergency": False},
        edits={"In an emergency": True},
        saved=lambda s: character(s).fatigue_level,
        expected="winded",
        live={"#fields-live": "Presence + Concentration"},
    ),
    "a mother's curse": Contract(
        prefill={"His mother": "", "Area of expertise": "military"},
        edits={
            "His mother": "Maria",
            "Area of expertise": "academic",
            "What lifts it": "restore the family's honor",
        },
        saved=lambda s: [
            vf.params
            for vf in character(s).virtues_flaws
            if "mothers_curse" in vf.vf_id
        ],
        expected=[{"expertise": "academic"}],
        invalid={"His mother": ""},
        live={"#fields-live": "to every academic roll"},
    ),
    # Sin, tarnish and the Goetic Arts (RoP: The Infernal).
    "confidence through sin": Contract(
        prefill={"The sinful trait": "Cruel (Envious)", "How he sins": "season"},
        edits={"How he sins": "ceremony"},
        saved=lambda s: (
            s.character("mag1").background.confidence_points,
            s.character("mag1").aging.warping_realms,
        ),
        expected=(1, {"Infernal": 1}),
        live={"#fields-live": "Infernal Warping Point"},
    ),
    "infernal influence": Contract(
        prefill={
            "Influence": "person",
            "How": "season",
            "The trait awakened": "Envious",
        },
        edits={"The trait awakened": "Cruel"},
        saved=lambda s: s.character("mag1").diary[-1].name,
        expected="Infernal Influence",
        invalid={"The trait awakened": ""},
        live={"#fields-live": "Presence + Leadership"},
    ),
    "ars goetia": Contract(
        prefill={"Goetic Art": "Summoning", "The spirit's Might": "10"},
        edits={"The spirit's Might": "5"},
        saved=lambda s: s.character("mag1").diary,
        expected=[],
        invalid={"The spirit's Might": "x"},
        live={"#fields-live": "Against 10"},
    ),
    # An apprentice's magic and the Gauntlet (Apprentices).
    "turbulence": Contract(
        prefill={"Why": "botch", "Aegis of the Hearth he had no part in": "0"},
        edits={"Sympathetic multiplier": "1"},
        saved=lambda s: s.character("mag1").diary[-1].name,
        expected="Turbulence",
        invalid={"Confidence spent on incurring": "99"},
        live={"#fields-live": "Incurring"},
    ),
    "the gauntlet": Contract(
        prefill={"How it is decided": "story", "The parens' verdict": "pass"},
        edits={"The parens' verdict": "fail", "The test": "an owl's egg"},
        saved=lambda s: s.character("mag1").diary[-1].name,
        expected="The Gauntlet failed",
        live={"#fields-live": "Hermetic Magus replaces Apprentice"},
    ),
    "lose the gift": Contract(
        prefill={"The Gift is": "suppressed", "What happened": ""},
        edits={"What happened": "a laboratory accident"},
        saved=lambda s: (
            "vf_suppressed_gift"
            in {vf.vf_id for vf in s.character("mag1").virtues_flaws}
        ),
        expected=True,
        invalid={"What happened": ""},
        live={"#fields-live": "Suppressed Gift"},
    ),
    "learn a cantation": Contract(
        prefill={"Times cast spontaneously": "0"},
        edits={"The spell": "spell_ager_belli", "Times cast spontaneously": "10"},
        saved=lambda s: s.character("mag1").spells_known[-1].spell_id,
        expected="spell_ager_belli",
        invalid={"Times cast spontaneously": "0"},
        live={"#fields-live": "Ager Belli is level 10"},
    ),
    # Art & Academe's artists and scholars, between their seasons.
    "an artist's career": Contract(
        prefill={"Sponsor's Reputation": "0"},
        edits={"What": "deed", "Deed": "benefactor"},
        saved=lambda s: character(s).diary[-1].name,
        expected="Artist's deed: Gained a benefactor",
        invalid={"Sponsor's Reputation": "-1"},
        live={"#fields-live": "Gains and losses"},
    ),
    "a scholar's career": Contract(
        prefill={"A wealthy family's gift": "0"},
        edits={"What": "academic", "Deed": "tractatus"},
        saved=lambda s: character(s).diary[-1].name,
        expected="Academic deed: Wrote a tractatus",
        invalid={"A wealthy family's gift": "4"},
        live={"#fields-live": "Hermetic Arts earn none"},
    ),
    # Dealing with faeries (RoP: Faerie).
    "ars fabulosa": Contract(
        prefill={"Power": "(Faerie) Summoning", "The faerie's Might": "10"},
        edits={"The faerie's Might": "5"},
        saved=lambda s: character(s).diary[-1].name,
        expected="Ars Fabulosa: (Faerie) Summoning",
        invalid={"The faerie's Might": "11"},
        live={"#fields-live": "reach Might 10"},
    ),
    "a faerie bargain": Contract(
        prefill={"How it ended": "struck", "The faerie": ""},
        edits={"The faerie": "the Oak King"},
        saved=lambda s: character(s).diary[-1].name,
        expected="A Faerie Bargain",
        invalid={"The faerie": ""},
        live={"#fields-live": "binds the faerie"},
    ),
    "an offer to faerie": Contract(
        prefill={"His fable score": "1", "The threat it overcomes": "Serious"},
        edits={"The change he asks for": "a bridge of leaves"},
        saved=lambda s: character(s).diary[-1].name,
        expected="An Offer to Faerie",
        invalid={"His fable score": "0"},
        live={"#fields-live": "Accepted on 12"},
    ),
    # The lacuna and the pilgrim (HoH:S, The Church).
    "cast in a lacuna": Contract(
        prefill={"The city's Dominion": "3"},
        edits={"The city's Dominion": "4"},
        saved=lambda s: character(s).diary,
        expected=[],
        invalid={"The city's Dominion": "11"},
        live={"#fields-live": "Outside the lacuna, in the Dominion"},
    ),
    "pilgrimage": Contract(
        prefill={"Pilgrimage's name": ""},
        edits={"Pilgrimage's name": "Santiago", "Target Level": "30"},
        saved=lambda s: [
            (p.kind, p.name, p.target)
            for p in character(s).progress
            if p.kind == "pilgrimage"
        ],
        expected=[("pilgrimage", "Santiago", 30)],
        invalid={"Pilgrimage's name": ""},
        live={"#fields-live": "Target Level 30"},
    ),
    # Devotion and the saints (The Church, RoP: The Divine).
    "invoke a saint": Contract(
        prefill={"The saint": "The Magi", "A donation": "0"},
        edits={"In imminent peril (+2)": True, "Divine aura where he prays": "3"},
        saved=lambda s: character(s).diary[-1].name,
        expected="Invoked The Magi",
        invalid={"Divine aura where he prays": "x"},
        live={"#fields-live": "+ peril 2"},
    ),
    "threaten a saint": Contract(
        prefill={"The saint": "The Magi", "The saint's Divine Might": "25"},
        edits={"Exposing his bones (+1)": True},
        saved=lambda s: character(s).diary[-1].name,
        expected="Threatened The Magi",
        invalid={"Confidence Points spent": "99"},
        live={"#fields-live": "Against 14"},
    ),
    "devotion points": Contract(
        prefill={"How": "season", "Points gained (or lost)": "5"},
        edits={"The saint": "-another-", "Another saint's name": "Saint Nerius"},
        saved=lambda s: [
            (p.name, p.points) for p in character(s).progress if p.kind == "devotion"
        ],
        expected=[("Saint Nerius", 5)],
        invalid={"Points gained (or lost)": "x"},
        live={"#fields-live": "on Devotion Points alone"},
    ),
    "indulgence, vigil or fast": Contract(
        prefill={"The act": "vigil"},
        edits={"The virtuous task tomorrow": "the Tribunal's vote"},
        saved=lambda s: character(s).diary[-1].name,
        expected="Kept a vigil",
        invalid={"The virtuous task tomorrow": ""},
        live={"#fields-live": "1 Confidence Point"},
    ),
    # Holy influence and tempers (RoP: The Divine).
    "holy influence": Contract(
        prefill={
            "Influence": "person",
            "How": "season",
            "His authority over them": "spiritual",
        },
        edits={"The trait inspired": "Kind"},
        saved=lambda s: character(s).diary[-1].name,
        expected="Holy Influence",
        invalid={"The trait inspired": ""},
        live={"#fields-live": "Presence + Leadership"},
    ),
    # Mystic paths, God's aid, the Font and the Commanding Aura.
    "mystic path": Contract(
        prefill={"His path": "none"},
        edits={"His path": "Contemplative mysticism"},
        saved=lambda s: ds.path(character(s)),
        expected="Contemplative mysticism",
        invalid={"His path": "none"},
        live={"#fields-live": "Divine Form"},
    ),
    "spiritual path": Contract(
        prefill={"What": "count"},
        edits={"Quest Component": "quest"},
        saved=lambda s: [
            (p.name, p.points)
            for p in character(s).progress
            if p.kind == "spiritual path"
        ],
        expected=[("Premonitions", 6)],
        invalid={"What": "begin"},
        live={"#fields-live": "+6:"},
    ),
    "monistic revelation": Contract(
        prefill={"Warping Points the Ascent brought": "1"},
        edits={"Warping Points the Ascent brought": "2"},
        saved=lambda s: character(s).diary[-1].name,
        expected="Monistic Revelation",
        invalid={"Warping Points the Ascent brought": "0"},
        live={"#fields-live": "Intelligence + Concentration"},
    ),
    "invoke god's aid": Contract(
        prefill={"What he asks God's aid in": ""},
        edits={"What he asks God's aid in": "the duel"},
        saved=lambda s: character(s).diary[-1].name,
        expected="God's Aid",
        invalid={"What he asks God's aid in": ""},
        live={"#fields-live": "Communication + Dominion Lore"},
    ),
    "font of knowledge": Contract(
        prefill={"Times drawn on today": "0"},
        edits={"The untrained Ability": "Hunt", "Times drawn on today": "1"},
        saved=lambda s: character(s).diary[-1].name,
        expected="Font of Knowledge",
        invalid={"Times drawn on today": "x"},
        live={"#fields-live": "against 9"},
    ),
    "commanding aura": Contract(
        prefill={"Withdrawn until penance": False},
        edits={"Withdrawn until penance": True},
        saved=lambda s: ds.aura_withdrawn(character(s)),
        expected=True,
        live={"#fields-live": "Archbishop: Magic Resistance 10"},
    ),
    # House Verditius's Hubris and vendettas.
    "hubris": Contract(
        prefill={
            "What happened": "Selling (or making for pay) a charged item or an item "
            "of quality"
        },
        edits={"What happened": "Declaring a vendetta"},
        saved=lambda s: [
            (t.score, t.deeds)
            for t in character(s).personality_traits
            if t.name == "Hubris"
        ],
        expected=[(1, 1)],
        live={"#fields-live": "+1 Hubris experience"},
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
