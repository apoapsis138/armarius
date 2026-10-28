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
    AnimalForm,
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
    "companion template": Contract(
        # The Definitive Edition's quick Martial companion.
        prefill={
            "Martial Ability": Select.NULL,
            "Major Flaw": Select.NULL,
            "Social Status": "vf_covenfolk",
        },
        edits={"Martial Ability": "single weapon", "Major Flaw": "vf_dark_secret"},
        saved=lambda s: [
            (c.type, c.in_creation, [vf.vf_id for vf in c.virtues_flaws])
            for c in s.characters
            if c.name == "Ulla"
        ],
        expected=[
            (
                "companion",
                True,
                [
                    "vf_covenfolk",
                    "vf_warrior",
                    "vf_puissant_ability",
                    "vf_affinity_with_ability",
                    "vf_dark_secret",
                ],
            )
        ],
        invalid=[
            {"Martial Ability": "single weapon"},
            {
                "Martial Ability": "single weapon",
                "Major Flaw": "vf_dark_secret",
                "Social Status": "vf_knight",
            },
        ],
        live={"#fields-live": "3 Virtue points, 3 Flaw points (of 10)"},
    ),
    "mythic companion template": Contract(
        # The Definitive Edition's Faerie Doctor, its Dutybound swapped for
        # another Minor Flaw and the book's minimum Abilities left out.
        prefill={
            "Faerie Friend": "vf_faerie_friend",
            "Dutybound": "vf_dutybound",
            "The book's minimum Abilities": True,
            "Social Status": "vf_wise_one",
        },
        edits={"Dutybound": "vf_reckless", "The book's minimum Abilities": False},
        saved=lambda s: [
            (c.type, c.in_creation, [vf.vf_id for vf in c.virtues_flaws], c.abilities)
            for c in s.characters
            if c.name == "Ulla"
        ],
        expected=[
            (
                "mythic companion",
                True,
                [
                    "vf_wise_one",
                    "vf_faerie_doctor",
                    "vf_dowsing",
                    "vf_curse_throwing",
                    "vf_faerie_friend",
                    "vf_reckless",
                ],
                [],
            )
        ],
        invalid={"First Virtue": VirtueFlawInstance("vf_tough")},
        aliases={"First Virtue": "fld-virtue_0"},
        live={"#fields-live": "5 Virtue points of 5 allowed, 2 Flaw points (of 10)"},
    ),
    "companion sample": Contract(
        # The Church's Anne, a Holy Hermit, without her Visions and Small
        # Frame (3 + 1 points of Flaws), so a Virtue must go too.
        prefill={
            "Guardian Angel": True,
            "Visions": True,
            "The book's Characteristics": True,
            "The book's Abilities": True,
            "Social Status": "vf_religious",
        },
        edits={"Visions": False, "Small Frame": False, "Guardian Angel": False},
        saved=lambda s: [
            (
                c.type,
                c.in_creation,
                s.current_year - (c.background.year_born or 0),
                [vf.vf_id for vf in c.virtues_flaws],
                bool(c.abilities),
            )
            for c in s.characters
            if c.name == "Ulla"
        ],
        expected=[
            (
                "companion",
                True,
                28,
                [
                    "vf_religious",
                    "vf_strong_willed",
                    "vf_missing_eye",
                    "vf_poor_eyesight",
                    "vf_vow",
                ],
                True,
            )
        ],
        invalid={"Visions": False},
    ),
    "grog template as companion": Contract(
        # The Animal Trainer's Madoc as a companion: a Major Story Flaw
        # (which no grog may take) makes him one.
        prefill={
            "Character": "0",
            "Social Status": "vf_covenfolk",
            "Cursed Guile": True,
        },
        edits={"First Flaw": VirtueFlawInstance("vf_dark_secret")},
        saved=lambda s: [
            (c.type, c.in_creation, [vf.vf_id for vf in c.virtues_flaws])
            for c in s.characters
            if c.name == "Ulla"
        ],
        expected=[
            (
                "companion",
                True,
                [
                    "vf_covenfolk",
                    "vf_puissant_ability",
                    "vf_improved_characteristics",
                    "vf_cursed_guile",
                    "vf_judged_unfairly",
                    "vf_dark_secret",
                ],
            )
        ],
        invalid={"Cursed Guile": False},
        aliases={"First Flaw": "fld-flaw_0"},
        live={"#fields-live": "Flaw points (of 10)"},
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
    # The book's Dog, whose list leaves no names blank: saving makes
    # the grog, an animal with its free Flaws.
    "animal template": Contract(
        prefill={"Age": "0", "Social Status": "vf_domestic_animal"},
        edits={"Age": "1", "Social Status": "vf_companion_animal"},
        saved=lambda s: [
            (
                c.in_creation,
                s.current_year - (c.background.year_born or 0),
                c.animal,
                [vf.vf_id for vf in c.virtues_flaws],
            )
            for c in s.characters
            if c.name == "Rex"
        ],
        expected=[
            (
                True,
                4,
                AnimalForm("clawed", "Dog", "Dog"),
                [
                    "vf_companion_animal",
                    "vf_restricted_learning",
                    "vf_no_hands",
                    "vf_mute",
                ],
            )
        ],
        invalid=[{"First Virtue": VirtueFlawInstance("vf_educated")}],
        aliases={"First Virtue": "fld-virtue_0"},
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
    "add story event concerning a character": Contract(
        prefill={"Year": "1220", "Season": "Autumn", "Name": ""},
        edits={
            "Category": "Story Event",
            "Name": "A salamander in the lab",
            "Concerns": "characters:mag1",
        },
        saved=lambda s: (covenant(s).diary[-1].status, covenant(s).diary[-1].concerns),
        expected=("Open", "characters:mag1"),
        invalid={"Name": ""},
        shown={"#cov-diary-list": "A salamander in the lab"},
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
        # No cap: a Major Prestige Boon's Reputation is 9 (DE p. 184).
        edits={"Score": "9"},
        saved=lambda s: covenant(s).reputations[0].score,
        expected=9,
        invalid=[{"Score": "lots"}],
        shown={"#cov-reputations-list": "Fair dealing: +9"},
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
    "add covenant manor": Contract(
        prefill={"Name": "", "Acres": "600"},
        edits={"Name": "Kohlergrund", "Held as an allod": True},
        saved=lambda s: covenant(s).manors["manor_list"][-1]["allod"],
        expected=True,
        invalid={"Name": ""},
        shown={"#manors-list": "Kohlergrund"},
    ),
    "edit manor check": Contract(
        prefill={"Agriculture source": Select.NULL, "Livestock source": Select.NULL},
        edits={"Agriculture source": "inc1"},
        saved=lambda s: covenant(s).manors["agriculture_source"],
        expected="inc1",
        shown={"#manor-check-text": "Mill"},
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
    "edit charter": Contract(
        prefill={"Name": "", "Year": "", "Ratified by a Quaesitor": False},
        edits={
            "Name": "The Keep's Accord",
            "Sworn in": "Summer",
            "Year": "1190",
            "Preamble": "We swear to hold the Keep together.",
            "Ratified by a Quaesitor": True,
        },
        saved=lambda s: (
            covenant(s).charter_of_covenant.name,
            covenant(s).charter_of_covenant.season,
            covenant(s).charter_of_covenant.year,
            covenant(s).charter_of_covenant.preamble,
            covenant(s).charter_of_covenant.ratified,
        ),
        expected=(
            "The Keep's Accord",
            "Summer",
            1190,
            "We swear to hold the Keep together.",
            True,
        ),
        invalid=[{"Name": ""}, {"Year": "long ago"}],
        shown={
            "#section-cov-charter": "The Keep's Accord",
            "#cov-charter-text": "Low Crime",
        },
    ),
    "add clause": Contract(
        # A new clause is agreed in the saga's present season and year.
        prefill={"Number or title": "", "Agreed in": "Autumn", "Year": "1220"},
        edits={
            "Number or title": "Apprentices",
            "Section": "Membership",
            "Text": "No apprentice without the council's leave.",
        },
        saved=lambda s: [
            (c.number, c.section, c.season, c.year, c.status)
            for c in covenant(s).charter_of_covenant.clauses
            if c.number == "Apprentices"
        ],
        expected=[("Apprentices", "Membership", "Autumn", 1220, "In force")],
        invalid=[
            {"Number or title": "", "Text": "Words."},
            {"Number or title": "8", "Text": ""},
        ],
        shown={
            "#section-cov-clauses": "Clauses (2 in force of 2)",
            "#cov-clauses-list": "Membership",
        },
        live={"#fields-live": "Apprentices"},
    ),
    "edit clause": Contract(
        prefill={
            "Number or title": "1",
            "Text": "All vis is shared.",
            "Agreed in": "Spring",
            "Year": "1200",
            "Status": "In force",
        },
        edits={
            "Status": "Amended",
            "Since": "Winter",
            "How": "The Aegis's vis comes first.",
        },
        saved=lambda s: [
            (c.status, c.since_season, c.note)
            for c in covenant(s).charter_of_covenant.clauses
        ],
        expected=[("Amended", "Winter", "The Aegis's vis comes first.")],
        invalid={"Text": ""},
        shown={"#cov-clauses-list": "Amended Winter"},
        live={"#fields-live": "Amended"},
    ),
    "pay the fee": Contract(
        prefill={"Pawns": "3"},
        edits={"Pawns": "2"},
        saved=lambda s: (
            next(c for c in s.characters if c.id == "mag_sketch").raw_vis,
            next(c for c in s.characters if c.id == "mag_sketch").stay.paid,
        ),
        expected=({"vim": 3}, [1220]),
        invalid={"Pawns": "9"},
        shown={"#section-cov-guests": "Guests (1)", "#cov-guests-list": "Paid"},
    ),
    "break clause": Contract(
        prefill={"Season": "Autumn", "Year": "1220", "How it was broken": ""},
        edits={"How it was broken": "Leandro kept the Vim vis."},
        saved=lambda s: [
            (c.status, c.since_season, c.since_year, c.note)
            for c in covenant(s).charter_of_covenant.clauses
        ],
        expected=[("Broken", "Autumn", 1220, "Leandro kept the Vim vis.")],
        invalid=[{"How it was broken": ""}, {"Year": "soon"}],
        shown={
            "#section-cov-clauses": "Clauses (0 in force of 1)",
            "#cov-clauses-list": "Broken Autumn 1220",
        },
        # The note typed in the many-line field reaches the inspector.
        live={"#fields-live": "Leandro kept the Vim vis."},
    ),
    "seal charter": Contract(
        prefill={"Leandro": False, "Brother Oda": False},
        edits={"Leandro": True, "Sealed in": "Spring", "Year": "1219"},
        saved=lambda s: [
            (seal.character_id, seal.season, seal.year)
            for seal in covenant(s).charter_of_covenant.seals
        ],
        expected=[("mag1", "Spring", 1219)],
        invalid={"Leandro": True, "Year": "soon"},
        shown={"#cov-charter-text": "Sealed by: Leandro (Spring 1219)"},
        live={"#fields-live": "Not yet sworn: Brother Oda"},
    ),
    # A covenant's ships (Hermetic Projects; City & Guild).
    "add ship": Contract(
        prefill={"Name": "", "Size": "5", "Cargo (tons)": "20", "Crew": "8"},
        edits={"Name": "Möwe", "Kind": "Knarr", "Damage levels lost": "1"},
        saved=lambda s: [
            (p.name, p.ship.kind_name, p.ship.damage_lost)
            for p in covenant(s).possessions
            if p.ship is not None
        ],
        expected=[("Möwe", "Knarr", 1)],
        invalid=[{"Name": ""}, {"Name": "Möwe", "Damage levels lost": "9"}],
        shown={"#pos-ship-list": "Möwe"},
        live={"#fields-live": "Damage levels: 3 of 4"},
    ),
    "ship stress check": Contract(
        prefill={"Weather": "fair", "Repaired before (-1)": False},
        edits={"Weather": "severe"},
        saved=lambda s: covenant(s).diary[-1].name,
        expected="Stress Check: Seehund",
        shown={"#pos-ship-list": "Seehund"},
        live={"#fields-live": "against 15"},
    ),
    "ship combat": Contract(
        prefill={"We mean to": "board", "Our crew's experience (0 to +3)": "0"},
        edits={"We mean to": "escape"},
        saved=lambda s: covenant(s).diary[-1].name,
        expected="Ship Combat: Seehund",
        invalid={"Our crew's experience (0 to +3)": "4"},
        shown={"#pos-ship-list": "Seehund"},
        live={"#fields-live": "slip away"},
    ),
    "sunk or taken": Contract(
        prefill={"What became of her": "afloat"},
        edits={"What became of her": "Sunk"},
        saved=lambda s: next(
            p.ship.fate for p in covenant(s).possessions if p.id == "seehund"
        ),
        expected="Sunk",
    ),
    # Shaping the land by magic (Transforming Mythic Europe pp. 54-77).
    "shape land": Contract(
        prefill={
            "Name": "",
            "Wall height (paces)": "30",
            "Grassland over the island": True,
        },
        edits={"Name": "Insula", "Across (miles)": "30"},
        saved=lambda s: [(p.name, p.across_miles) for p in covenant(s).land_projects],
        expected=[("Insula", 30.0)],
        invalid=[{"Name": ""}, {"Name": "Insula", "Across (miles)": "0"}],
        # A 30-mile island: a level 35 wall and a level 40 fill (TME p. 59).
        live={"#fields-live": "The fill: CrTe 40 Ritual"},
    ),
    "settle new land": Contract(
        prefill={"Manors to settle (of 7 left)": "7", "Named": "Insula"},
        edits={"Manors to settle (of 7 left)": "2"},
        saved=lambda s: [
            m["name"]
            for m in covenant(s).manors.get("manor_list", [])
            if m["name"].startswith("Insula")
        ],
        expected=["Insula 1", "Insula 2"],
        invalid=[
            {"Manors to settle (of 7 left)": "8"},
            {"Manors to settle (of 7 left)": "0"},
        ],
        live={"#fields-live": "40 pounds a year"},
    ),
    # A covenant's Hermetic Projects (Hermetic Projects pp. 36-41).
    "begin project": Contract(
        prefill={"Name": "", "Kind": "Great Tower", "Year": "1220"},
        edits={"Name": "The Spire", "Innovation": "2"},
        saved=lambda s: [(p.name, p.innovation) for p in covenant(s).hermetic_projects],
        expected=[("The Spire", 2)],
        invalid=[{"Name": ""}, {"Name": "The Spire", "Innovation": "4"}],
    ),
    "edit project": Contract(
        prefill={"Name": "The Schattenbach Spire", "Raw Materials": "0"},
        edits={"Name": "The Spire", "Raw Materials": "3"},
        saved=lambda s: [
            (p.name, p.raw_materials) for p in covenant(s).hermetic_projects
        ],
        expected=[("The Spire", 3)],
        invalid={"Raw Materials": "5"},
        shown={"#cov-projects-list": "The Spire"},
    ),
    "add work": Contract(
        prefill={"Work": "", "Levels added": "0"},
        edits={"Work": "Gregor builds", "Levels added": "2", "Quality": "Superior"},
        saved=lambda s: [
            (w.name, w.levels, w.quality)
            for w in covenant(s).hermetic_projects[0].works[2:]
        ],
        expected=[("Gregor builds", 2, "Superior")],
        invalid={"Levels added": "-1"},
        shown={"#cov-tower-works-list": "Gregor builds"},
    ),
    "add device": Contract(
        prefill={"Device": "", "Effect": ""},
        edits={"Device": "True Falsework", "Effect": "ReHe 30"},
        saved=lambda s: [d.name for d in covenant(s).hermetic_projects[0].devices],
        expected=["The Arms of Hercules", "True Falsework"],
        invalid={"Device": ""},
        shown={"#cov-tower-devices-list": "True Falsework"},
    ),
    "tower stress check": Contract(
        prefill={"How severe": "0", "Previously repaired": False},
        edits={"How severe": "-2"},
        saved=lambda s: covenant(s).hermetic_projects[0].works[-1].kind,
        expected="stress",
        invalid={"How severe": "x"},
        live={"#fields-live": "against 15"},
    ),
    "conjure levels": Contract(
        prefill={"Ritual": "heights", "Year": "1220"},
        edits={"Season": "Winter"},
        saved=lambda s: [
            (w.kind, w.levels, w.season)
            for w in covenant(s).hermetic_projects[0].works[2:]
        ],
        expected=[("ritual", 4, "Winter")],
        invalid={"Ritual": "conjuring"},
        live={"#fields-live": "Botch dice: 5"},
    ),
    # A covenant's Menagerie (Hermetic Projects pp. 119-142).
    "add beast": Contract(
        prefill={"Name": "", "Kind": "Beast of Virtue", "How many": "1"},
        edits={
            "Name": "Basilisk",
            "Kind": "Beast of Legend",
            "Magic Might (grown)": "20",
        },
        saved=lambda s: [
            (b.name, b.kind, b.might)
            for b in covenant(s).hermetic_projects[0].beasts[3:]
        ],
        expected=[("Basilisk", "Beast of Legend", 20)],
        invalid=[
            {"Name": ""},
            {"Name": "Dog", "Kind": "Transformed Animal", "Magic Might (grown)": "5"},
        ],
        shown={"#cov-menagerie-beasts-list": "Basilisk"},
    ),
    "breed a pair": Contract(
        prefill={"Male": "bock", "Female": "geiss", "Year": "1220"},
        edits={"Season": "Winter"},
        saved=lambda s: [
            (b.pair, b.season) for b in covenant(s).hermetic_projects[0].breedings[1:]
        ],
        expected=[("Bock × Geiß", "Winter")],
        invalid={"Ligature (0 to +3)": "4"},
        live={"#fields-live": "against 9"},
    ),
    "edit breeding": Contract(
        prefill={"Pair": "Bock × Geiß", "Young born": "0"},
        edits={"Result": "Two kids", "Young born": "2"},
        saved=lambda s: [
            (b.result, b.young) for b in covenant(s).hermetic_projects[0].breedings
        ],
        expected=[("Two kids", 2)],
        invalid={"Young born": "-1"},
        shown={"#cov-menagerie-breedings-list": "Two kids"},
    ),
    "tame a beast": Contract(
        prefill={"Tamed by": "comp1", "Year": "1220"},
        edits={"Season": "Summer"},
        saved=lambda s: [
            (p.activity, p.title, p.season)
            for p in s.season_plans
            if p.character_id == "comp1" and p.title == "Hare of Virtue"
        ],
        expected=[("tame_animal", "Hare of Virtue", "Summer")],
        invalid={"Year": "x"},
        live={"#fields-live": "taming points"},
    ),
    # The guides' gaps, round two.
    "build a ship": Contract(
        prefill={"Like": "buss", "Built by": "shipwright"},
        edits={"Her name": "The Hermes", "Built by": "creo_ritual"},
        saved=lambda s: covenant(s).diary[-1].name,
        expected="Build a Ship: The Hermes",
        live={"#fields-live": "Opened as her hull alone"},
    ),
    "suggest a story": Contract(
        prefill={},
        edits={"The story": "The wyrm wakes", "Year": "1222"},
        saved=lambda s: (
            covenant(s).diary[-1].name,
            covenant(s).diary[-1].status,
            s.calendar[-1].year,
        ),
        expected=("The wyrm wakes", "Open", 1222),
        invalid={"Year": "x"},
    ),
    "menagerie reputation award": Contract(
        prefill={"Visitors this year": "0"},
        edits={"Visitors this year": "50"},
        saved=lambda s: next(
            r.score
            for r in s.character("comp1").reputations
            if r.name == "Keeper of Beasts"
        ),
        expected=1,
        invalid={"Visitors this year": "x"},
        live={"#fields-live": "experience toward"},
    ),
    # A staged Hermetic Project (Hermetic Projects pp. 9-118).
    "add project stage": Contract(
        prefill={"Stage": "", "Done": False},
        edits={"Stage": "Woo the fire spirit"},
        saved=lambda s: covenant(s).hermetic_projects[0].stages[-1].name,
        expected="Woo the fire spirit",
        invalid={"Stage": ""},
        shown={"#cov-staged-stages-list": "Woo the fire spirit"},
    ),
    "add stage work": Contract(
        prefill={"Seasons spent": "1"},
        edits={"Work": "Vulcan's Glass", "Seasons spent": "2"},
        saved=lambda s: [
            (w.name, w.seasons, p.stages[0].id == w.stage)
            for p in covenant(s).hermetic_projects[:1]
            for w in p.works
        ],
        expected=[("Vulcan's Glass", 2, True)],
        invalid=[{"Seasons spent": "x"}, {"Seasons spent": "-1"}],
        shown={"#cov-staged-works-list": "Vulcan's Glass"},
    ),
    "warning bell": Contract(
        prefill={},
        edits={},
        saved=lambda s: covenant(s).diary[-1].name,
        expected="Warning Bell: Vulcan's Hearth",
        live={"#fields-live": "A stress die of days"},
    ),
    "gather a connection": Contract(
        prefill={"Gathered from": "blood"},
        edits={"Or by name": "Brother Oda", "Gathered from": "breath"},
        saved=lambda s: [
            c.lasts
            for lab in s.laboratories
            for c in lab.arcane_connections
            if c.to.startswith("Brother Oda")
        ],
        expected=["Hours or days"],
        invalid={"Or by name": ""},
        live={"#fields-live": "hours or days"},
    ),
    "lower an aegis": Contract(
        prefill={"Its level": "30"},
        edits={"Its level": "40", "Or an Aegis of level": "20"},
        saved=lambda s: [e for e in covenant(s).diary if e.name.startswith("Lower")],
        expected=[],
        invalid={"Its level": "x"},
        live={"#fields-live": "Guttering of the Home-Fires 40"},
    ),
    "death roll": Contract(
        prefill={"The saga's power": "Medium"},
        edits={"Days dead before animated": "2"},
        saved=lambda s: [
            e.name
            for c in s.characters
            for e in c.diary
            if e.name == "Death Roll: Vulcan's Hearth"
        ],
        expected=["Death Roll: Vulcan's Hearth"],
        invalid={"Days dead before animated": "x"},
    ),
}


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_form_contract(name):
    await run_contract(name, CONTRACTS[name])
