"""Dialog contract tests for the forms of a covenant's sheet and a sketch covenant's.

Each form runs in one app session; dialog_contract_support.py has the
contract and the driver, dialog_openers.py how each form is reached."""

import pytest
from dialog_contract_support import (
    HIDDEN_STORY,
    ILLUSORY_STORY,
    Contract,
    covenant,
    device,
    last_gear,
    run_contract,
    sketch_covenant,
)
from textual.widgets import Select

from ars_magica_manager.models import (
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    BOON_HOOK_UNKNOWN,
    VirtueFlawInstance,
)

CONTRACTS: dict[str, Contract] = {
    "power level": Contract(
        prefill={"Power Level": Select.NULL},
        edits={
            "Power Level": "Medium",
            "Build Points": "600",
            "Magi without a laboratory": "1",
            "Year Founded": "1200",
        },
        saved=lambda s: (
            s.covenants[0].power_level,
            s.covenants[0].build_points_budget,
            s.covenants[0].magi_without_lab,
            s.covenants[0].year_founded,
        ),
        expected=("Medium", 600, 1, 1200),
        invalid=[
            {"Power Level": Select.NULL},
            {"Year Founded": "soon"},
            {"Power Level": "Low", "Build Points": "400"},
            {"Magi without a laboratory": "-1"},
        ],
    ),
    "buy specialist": Contract(
        prefill={
            "Name": "",
            "A teacher": False,
            "Ability used for the covenant": None,
            "Its score": "1",
        },
        edits={
            "Name": "Master Odo",
            "A teacher": True,
            "Ability used for the covenant": "Artes Liberales",
            "Its score": "5",
            "Communication": "2",
            "Teaching": "4",
        },
        saved=lambda s: [
            (
                i.kind,
                i.name,
                i.linked_ability,
                i.specialist_score,
                i.teacher_communication,
                i.teacher_teaching,
            )
            for i in s.covenants[0].inhabitants
            if i.name == "Master Odo"
        ],
        expected=[("specialist", "Master Odo", "Artes Liberales", 5, 2, 4)],
        invalid=[
            {"Name": "", "Ability used for the covenant": "Brawl"},
            {
                "Name": "Odo",
                "Ability used for the covenant": "Brawl",
                "Its score": "-1",
            },
        ],
    ),
    "create character": Contract(
        prefill={"Name": "", "Type": "magus", "Covenant": "cov1"},
        edits={"Name": "Ulla", "Type": "companion"},
        saved=lambda s: [
            (c.type, c.covenant_id) for c in s.characters if c.name == "Ulla"
        ],
        expected=[("companion", "cov1")],
        invalid={"Name": ""},
    ),
    "grog template": Contract(
        # The Animal Trainer's first sample, Madoc, whose list leaves no
        # names blank: saving makes the grog.
        prefill={
            "Character": "0",
            "Age": "0",
            "Social Status": "vf_covenfolk",
            "Puissant Animal Handling": True,
            "Cursed Guile": True,
        },
        edits={"Improved Characteristics": False, "Cursed Guile": False},
        saved=lambda s: [
            (
                c.in_creation,
                s.current_year - (c.background.year_born or 0),
                [vf.vf_id for vf in c.virtues_flaws],
            )
            for c in s.characters
            if c.name == "Ulla"
        ],
        expected=[
            (True, 15, ["vf_covenfolk", "vf_puissant_ability", "vf_judged_unfairly"])
        ],
        invalid=[
            {"First Virtue": VirtueFlawInstance("vf_tough")},
            {
                "First Flaw": VirtueFlawInstance("vf_carefree"),
                "Second Flaw": VirtueFlawInstance("vf_clumsy"),
            },
        ],
        aliases={
            "First Virtue": "fld-virtue_0",
            "First Flaw": "fld-flaw_0",
            "Second Flaw": "fld-flaw_1",
        },
        live={"#fields-live": "1 Virtue point, 1 Flaw point (1 of 3 Minor Flaws)"},
    ),
    "create laboratory": Contract(
        prefill={"Name": "", "Size": "0", "Covenant": "cov1"},
        edits={"Name": "Cellar", "Size": "2"},
        saved=lambda s: [
            (lab.covenant_id, lab.characteristics.size)
            for lab in s.laboratories
            if lab.name == "Cellar"
        ],
        expected=[("cov1", 2)],
        invalid=[{"Name": "", "Size": "2"}, {"Name": "Cellar", "Size": "big"}],
    ),
    "bind familiar": Contract(
        prefill={"Name": ""},
        edits={"Name": "Mouse", "Magus Partner": "mag2"},
        saved=lambda s: [f.character_id for f in s.familiars if f.name == "Mouse"],
        expected=["mag2"],
        invalid={"Name": "", "Magus Partner": "mag2"},
    ),
    "edit covenant": Contract(
        prefill={"Name": "Keep", "Aura": "0", "Covenant Season": "Spring"},
        edits={
            "Name": "Keep II",
            "Tribunal": Select.NULL,
            "Year Founded": "1100",
            "Aura": "3",
            "Covenant Season": "Summer",
        },
        saved=lambda s: (
            covenant(s).name,
            covenant(s).tribunal_id,
            covenant(s).year_founded,
            covenant(s).aura,
            covenant(s).covenant_season,
        ),
        expected=("Keep II", None, 1100, 3, "Summer"),
        invalid=[{"Name": ""}, {"Name": "  "}],
        shown={"#cov-info-right": "(not set)", "#cov-info-left": "1100"},
    ),
    "edit sketch covenant": Contract(
        prefill={"Name": "Fengheld", "Unnamed magi": "2"},
        edits={
            "Name": "Fengheld II",
            "Unnamed magi": "3",
            "In the Saga": "Old rivals.",
            "Vassal of": "cov1",
            "The oath's duties": "Ten pawns of Aquam a year.",
        },
        saved=lambda s: (
            sketch_covenant(s).name,
            sketch_covenant(s).unnamed_magi,
            sketch_covenant(s).summary,
            sketch_covenant(s).liege_id,
            sketch_covenant(s).oath,
        ),
        expected=(
            "Fengheld II",
            3,
            "Old rivals.",
            "cov1",
            "Ten pawns of Aquam a year.",
        ),
        invalid=[{"Name": ""}, {"Unnamed magi": "-1"}],
        shown={
            "#cov-info-right": "4 (1 named, 3 unnamed)",
            "#cov-summary": "Old rivals.",
            "#cov-info-left": "Vassal of",
        },
    ),
    "covenant arms": Contract(
        prefill={"Motto": ""},
        edits={
            "Field": "Azure",
            "Division": "Per pale",
            "Second tincture": "Or",
            "Charge": "Tower",
            "How many": "2",
            "Charge tincture": "Gules",
            "Motto": "Per aquas, lux",
        },
        saved=lambda s: s.covenants[0].arms,
        expected={
            "field": "Azure",
            "division": "Per pale",
            "second": "Or",
            "charge": "Tower",
            "charge_tincture": "Gules",
            "motto": "Per aquas, lux",
            "count": 2,
        },
        live={
            "#fields-live": "Per pale azure and or, two towers gules",
        },
        shown={"#cov-info-right": "Arms"},
    ),
    "what matters": Contract(
        prefill={"What Matters": "Vis: the ford, 3 Aquam a year"},
        edits={"What Matters": "Library: strong in Rego"},
        saved=lambda s: sketch_covenant(s).what_matters,
        expected="Library: strong in Rego",
        shown={"#cov-what-matters": "Library: strong in Rego"},
    ),
    "add reason": Contract(
        prefill={"Toward": "cov1", "Change": "1", "Year": "1220", "Season": "Autumn"},
        edits={"What happened": "Shared the vis", "Change": "2"},
        saved=lambda s: [
            (r.what, r.change) for r in sketch_covenant(s).attitudes[0].reasons
        ],
        expected=[("Claimed the ford", -1), ("Shared the vis", 2)],
        invalid=[{"What happened": ""}, {"What happened": "x", "Change": "0"}],
        shown={"#attitude-list": "Shared the vis"},
    ),
    "add favour": Contract(
        prefill={"What for": "", "Year": "1220", "Season": "Autumn"},
        edits={"What for": "Lent a book", "Owed by": "Keep", "Owed to": "Fengheld"},
        saved=lambda s: [(f.what, f.owed_by) for f in sketch_covenant(s).favours],
        expected=[("Hid a grog", "Fengheld"), ("Lent a book", "Keep")],
        invalid={"What for": ""},
        shown={"#favours-list": "Keep owes Fengheld: Lent a book"},
    ),
    "add sketch magus": Contract(
        prefill={"Name": "", "Detail": "Line"},
        edits={"Name": "Ulla", "Detail": "Sketch", "In the Saga": "Votes with him."},
        saved=lambda s: [
            (c.detail, c.summary, c.in_creation)
            for c in s.characters
            if c.name == "Ulla"
        ],
        expected=[("Sketch", "Votes with him.", False)],
        invalid={"Name": ""},
        shown={"#cov-magi-list": "Ulla"},
    ),
    "edit covenant description": Contract(
        prefill={"Description": ""},
        edits={"Description": "An old keep."},
        saved=lambda s: covenant(s).notes,
        expected="An old keep.",
        shown={"#cov-description-content": "An old keep."},
    ),
    "edit boon": Contract(
        prefill={"Detail": ""},
        edits={"Detail": "North tower", "Description": "Tall"},
        saved=lambda s: (
            covenant(s).boons_hooks[0].params.get(BOON_HOOK_DETAIL),
            covenant(s).boons_hooks[0].params.get(BOON_HOOK_DESCRIPTION),
        ),
        expected=("North tower", "Tall"),
        shown={"#cov-boons-list": "North tower"},
    ),
    "edit hook": Contract(
        prefill={"Unknown": False, "Detail": ""},
        edits={"Unknown": True, "Detail": "The mill"},
        saved=lambda s: (
            covenant(s).boons_hooks[1].params.get(BOON_HOOK_DETAIL),
            covenant(s).boons_hooks[1].params.get(BOON_HOOK_UNKNOWN),
        ),
        expected=("The mill", "yes"),
    ),
    # Choosing a book weapon fills in its figures; a typed name stays.
    "edit covenant weapon": Contract(
        prefill={"Name": "A weapon", "Weapon": Select.NULL, "Init": "0", "Load": "0"},
        edits={"Weapon": "weapon_long_sword"},
        saved=lambda s: last_gear(covenant(s).possessions, "weapon"),
        expected=("A weapon", "weapon_long_sword", "Expensive", 2, 4, 1, 6, 1),
        invalid={"Quantity": "0"},
    ),
    "edit covenant armor": Contract(
        prefill={"Name": "A armor", "Material": Select.NULL, "Protection": "0"},
        edits={"Material": "armor_metal_scale", "Type": "Full armor"},
        saved=lambda s: last_gear(covenant(s).possessions, "armor"),
        expected=("A armor", "armor_metal_scale", "Standard", "Full armor", 7, 7),
        # Heavy Leather only comes as partial armor.
        invalid={"Material": "armor_heavy_leather", "Type": "Full armor"},
    ),
    "add covenant diary entry": Contract(
        prefill={"Year": "1220", "Season": "Autumn", "Name": ""},
        edits={
            "Year": "1221",
            "Category": "Purchases & Sales",
            "Name": "Bought a mill",
            "Pounds": "-12",
            "Loyalty points": "3",
        },
        saved=lambda s: (
            covenant(s).diary[-1].year,
            covenant(s).diary[-1].category,
            covenant(s).diary[-1].name,
            covenant(s).diary[-1].pounds,
            covenant(s).diary[-1].loyalty,
        ),
        expected=(1221, "Purchases & Sales", "Bought a mill", -12.0, 3),
        invalid={"Pounds": "lots"},
        shown={"#cov-diary-list": "Bought a mill"},
    ),
    "add hidden resources story event": Contract(
        prefill={"Year": "1220", "Season": "Autumn", "Name": ""},
        edits={**HIDDEN_STORY, "Build Points unlocked": "120"},
        saved=lambda s: (
            covenant(s).diary[-1].category,
            covenant(s).diary[-1].boon_hook_id,
            covenant(s).diary[-1].build_points,
        ),
        expected=("Story Event", "bh-hr", 120),
        invalid=[
            {**HIDDEN_STORY, "Build Points unlocked": "251"},
            {**HIDDEN_STORY, "Build Points unlocked": "0"},
        ],
        shown={
            "#cov-boons-list": "Hidden Resources (120/250 BP)",
            "#cov-diary-list": "Past the guardian  \\[Resolved]  120 Build Points",
        },
    ),
    "add illusory resources story event": Contract(
        prefill={"Year": "1220", "Season": "Autumn", "Name": ""},
        edits={**ILLUSORY_STORY, "Build Points found illusory": "60"},
        saved=lambda s: (
            covenant(s).diary[-1].boon_hook_id,
            covenant(s).diary[-1].build_points,
        ),
        expected=("bh-ir", 60),
        invalid=[
            {**ILLUSORY_STORY, "Build Points found illusory": "251"},
            {**ILLUSORY_STORY, "Build Points found illusory": "-5"},
        ],
        shown={"#cov-hooks-list": "Illusory Resources (60/250 BP)"},
    ),
    "edit charged item effect": Contract(
        prefill={"Name": "Heal", "Technique": "Creo", "Effect level": "20"},
        edits={"Name": "Mend", "Effect level": "15", "Known": False},
        saved=lambda s: (
            device(s, "dev-cov").effects[0].name,
            device(s, "dev-cov").effects[0].level,
            device(s, "dev-cov").effects[0].known,
        ),
        expected=("Mend", 15, False),
        invalid={"Effect level": "-5"},
    ),
    "edit covenant reputation": Contract(
        prefill={"Name": "Fair dealing", "Score": "2"},
        edits={"Score": "3"},
        saved=lambda s: covenant(s).reputations[0].score,
        expected=3,
        invalid=[{"Score": "4"}, {"Score": "-4"}],
        shown={"#cov-reputations-list": "Fair dealing: +3"},
    ),
    "add boon": Contract(
        prefill={"Detail": "", "Description": ""},
        edits={"Detail": "North tower", "Description": "Tall"},
        saved=lambda s: (
            covenant(s).boons_hooks[-1].vf_id,
            covenant(s).boons_hooks[-1].params.get(BOON_HOOK_DETAIL),
            covenant(s).boons_hooks[-1].params.get(BOON_HOOK_DESCRIPTION),
        ),
        expected=("covbh_boon_minor_edifice", "North tower", "Tall"),
        shown={"#cov-boons-list": "Edifice - North tower"},
    ),
    "add property": Contract(
        prefill={"Name": "", "Dimensions": ""},
        edits={"Name": "Mill", "Dimensions": "40 acres"},
        saved=lambda s: [
            (p.name, p.dimensions) for p in covenant(s).possessions if p.name == "Mill"
        ],
        expected=[("Mill", "40 acres")],
        invalid={"Name": ""},
        shown={"#pos-property-list": "Mill"},
    ),
    "add sanctum": Contract(
        prefill={"Name": "", "Owner": "Free", "Usage": "Standard (2 Seasons)"},
        edits={"Name": "Study", "Quality": "3", "Build Points": "15"},
        saved=lambda s: [
            (p.owner, p.quality, p.build_points, p.usage)
            for p in covenant(s).possessions
            if p.name == "Study"
        ],
        expected=[("Free", 3, 15, "Standard (2 Seasons)")],
        invalid={"Name": ""},
        shown={"#pos-sanctum-list": "Study"},
    ),
    "add covenant item": Contract(
        prefill={"Name": "", "Quantity": "1"},
        edits={"Name": "Lens", "Quantity": "5"},
        saved=lambda s: [
            p.quantity for p in covenant(s).possessions if p.name == "Lens"
        ],
        expected=[5],
        invalid=[{"Name": ""}, {"Name": "Lens", "Quantity": "0"}],
        shown={"#pos-item-list": "Lens"},
    ),
    "add vis source": Contract(
        prefill={"Name": "", "Art": Select.NULL, "Season harvested": Select.NULL},
        edits={
            "Name": "Well",
            "Art": "Vim",
            "Season harvested": "Winter",
            "Pawns": "3",
            "Location": "Chapel",
        },
        saved=lambda s: [
            (p.art, p.season, p.pawns, p.location)
            for p in covenant(s).possessions
            if p.name == "Well"
        ],
        expected=[("Vim", "Winter", 3, "Chapel")],
        # Name, Art and Season are required, and at least one pawn.
        invalid=[
            {"Name": ""},
            {"Name": "Well"},
            {"Name": "Well", "Art": "Vim"},
            {"Name": "Well", "Art": "Vim", "Season harvested": "Winter", "Pawns": "0"},
        ],
        shown={"#pos-vis_source-list": "Well"},
    ),
    "add vis store": Contract(
        prefill={
            "Name": "",
            "Art": Select.NULL,
            "Pawns": "1",
            "Kept at": "covenant:cov1",
        },
        edits={
            "Name": "Cask",
            "Art": "Vim",
            "Pawns": "9",
            "Kept at": "laboratory:lab1",
            "Location": "Top shelf",
        },
        saved=lambda s: [
            (p.art, p.pawns, p.location_kind, p.location_id, p.location)
            for p in covenant(s).possessions
            if p.name == "Cask"
        ],
        expected=[("Vim", 9, "laboratory", "lab1", "Top shelf")],
        invalid=[{"Name": ""}, {"Name": "Cask"}],
        shown={"#pos-vis_store-list": "Cask"},
    ),
    "edit wealth": Contract(
        prefill={"Wealth": "0"},
        edits={"Wealth": "2525"},
        saved=lambda s: covenant(s).economics.wealth,
        expected=2525,
        invalid={"Wealth": "lots"},
        shown={"#eco-wealth-left": "2525"},
    ),
    "add income source": Contract(
        prefill={"Name": "", "Type": "Typical", "Current Income": ""},
        edits={"Name": "Toll bridge", "Type": "Greater"},
        saved=lambda s: [
            (i.type, i.income)
            for i in covenant(s).economics.income_sources
            if i.name == "Toll bridge"
        ],
        # A blank income is the type's usual one.
        expected=[("Greater", None)],
        invalid={"Name": ""},
        shown={"#eco-income-list": "Toll bridge"},
    ),
    "edit income source": Contract(
        prefill={"Name": "Mill", "Type": "Typical", "Current Income": ""},
        edits={"Current Income": "55"},
        saved=lambda s: covenant(s).economics.income_sources[0].income,
        expected=55,
        invalid={"Current Income": "lots"},
        shown={"#eco-income-list": "55"},
    ),
    "edit expenditure row": Contract(
        prefill={"Notes": ""},
        edits={"Notes": "Old roof"},
        saved=lambda s: covenant(s).economics.notes.get("buildings"),
        expected="Old roof",
        shown={"#eco-expenditure-list": "Old roof"},
    ),
    "edit tithes": Contract(
        prefill={"Amount": "0", "Notes": ""},
        edits={"Amount": "12"},
        saved=lambda s: covenant(s).economics.tithes,
        expected=12,
        invalid={"Amount": "lots"},
    ),
    "edit sundry": Contract(
        prefill={"Amount": "1"},
        edits={"Amount": "3"},
        saved=lambda s: covenant(s).economics.sundry,
        expected=3,
        invalid={"Amount": "0"},  # at least 1
    ),
    "edit magic savings": Contract(
        prefill={"Savings": "0"},
        edits={"Savings": "20"},
        saved=lambda s: covenant(s).economics.magic_savings,
        expected=20,
        invalid={"Savings": "lots"},
    ),
    "edit loyalty": Contract(
        prefill={
            "Type of Governance": "",
            "Equipment": "Standard",
            "Money": "Standard salary",
            "Familiarity": "0",
        },
        edits={
            "Type of Governance": "Council",
            "Money": "Generous salary",
            "Familiarity": "2",
        },
        saved=lambda s: (
            covenant(s).loyalty.governance,
            covenant(s).loyalty.money,
            covenant(s).loyalty.familiarity,
        ),
        expected=("Council", "Generous salary", 2),
        invalid={"Familiarity": "lots"},
    ),
    "edit population": Contract(
        prefill={"Other People": "0"},
        edits={"Other People": "7"},
        saved=lambda s: covenant(s).population.other_people,
        expected=7,
        invalid={"Other People": "lots"},
    ),
    "edit miscellaneous": Contract(
        prefill={"Aging for Magi": "0", "Magic Turbula": "0"},
        edits={"Aging for Magi": "1", "Magic Turbula": "2"},
        saved=lambda s: (
            covenant(s).population.aging_magi,
            covenant(s).population.magic_turbula,
        ),
        expected=(1, 2),
        invalid={"Magic Turbula": "lots"},
    ),
    "add magus": Contract(
        prefill={
            "Name": "",
            "House": Select.NULL,
            "Year Born": "",
            "Gift": Select.NULL,
        },
        edits={"Name": "Tytalus NPC", "House": "house_tytalus", "Gift": "Blatant"},
        saved=lambda s: [
            (i.kind, i.house, i.gift, i.year_born)
            for i in covenant(s).inhabitants
            if i.name == "Tytalus NPC"
        ],
        # A blank Year Born stays unknown.
        expected=[("magus", "house_tytalus", "Blatant", None)],
        invalid={"Name": ""},
        shown={"#inh-magus-list": "Tytalus NPC", "#section-inh-magus": "Magi (3)"},
    ),
    "add turb": Contract(
        prefill={"Name": "", "Year Born": "", "Quantity": "1"},
        edits={"Name": "Guards", "Quantity": "3"},
        saved=lambda s: [
            (i.kind, i.quantity) for i in covenant(s).inhabitants if i.name == "Guards"
        ],
        expected=[("turb", 3)],
        invalid=[{"Name": ""}, {"Name": "Guards", "Quantity": "0"}],
        shown={"#section-inh-turb": "(4)"},  # the headcount adds the quantity
    ),
    "add covenfolk member": Contract(
        prefill={"Name": "", "Covenant Role": Select.NULL, "Quantity": "1"},
        edits={"Name": "Old Marta", "Covenant Role": "Dependent", "Year Born": "1180"},
        saved=lambda s: [
            (i.role, i.year_born)
            for i in covenant(s).inhabitants
            if i.name == "Old Marta"
        ],
        expected=[("Dependent", 1180)],
        invalid=[{"Name": ""}, {"Name": "Old Marta"}],  # the role is required
        shown={"#inh-inhabitant-list": "Old Marta"},
    ),
    "add craftsperson": Contract(
        prefill={
            "Name": "",
            "Value of Crafting Skill": "0",
            "Field of Work": "None",
            "Linked Ability": "",
        },
        edits={
            "Name": "Smith",
            "Value of Crafting Skill": "6",
            "Field of Work": "Weapons and Armor",
            "Linked Ability": "Craft: Smith",
        },
        saved=lambda s: [
            (i.skill_value, i.field_of_work, i.linked_ability)
            for i in covenant(s).inhabitants
            if i.name == "Smith"
        ],
        expected=[(6, "Weapons and Armor", "Craft: Smith")],
        invalid={"Name": ""},
        shown={"#inh-craftsperson-list": "Smith"},
    ),
    "add horses": Contract(
        prefill={"Name": "", "Year Born": "", "Quantity": "1"},
        edits={"Name": "Ponies", "Quantity": "4"},
        saved=lambda s: [
            (i.kind, i.quantity, i.year_born)
            for i in covenant(s).inhabitants
            if i.name == "Ponies"
        ],
        expected=[("horse", 4, None)],
        invalid={"Quantity": "0"},
        shown={"#inh-horse-list": "Ponies"},
    ),
}


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_form_contract(name):
    await run_contract(name, CONTRACTS[name])
