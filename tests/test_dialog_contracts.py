"""Contract tests for the app's form dialogs, keyed by what the user sees.

Each dialog is opened the way the app opens it (dialog_openers.py) and
driven by its field labels, never by widget ids, so the same tests hold
before and after a dialog is rebuilt (e.g. as a FieldsDialog). For each:

- the form is pre-filled with the record's current values;
- Cancel after editing leaves the saved saga untouched;
- an invalid entry keeps the dialog open with an error and saves nothing;
- a valid edit, saved, lands in the saved saga.

A field is found by the text of its label (a prefix match, ignoring a
trailing colon), or -- for the few fields drawn without a label -- by an
alias to its widget id. A Checkbox may also be found by its own label.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import pytest
from dialog_openers import contract_saga, new_app, open_dialog, reopen_dialog
from support import build_all_tabs, strip_markup, wait_until
from textual.widget import Widget
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    Input,
    Label,
    Select,
    Static,
    TextArea,
)

from ars_magica_manager import catalog, storage
from ars_magica_manager import players as pl
from ars_magica_manager.models import (
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    BOON_HOOK_UNKNOWN,
    LabSpecialtyEntry,
    LabSpecialtyGrant,
    LabTextAccess,
    Possession,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.screens import SelectableList

SAGA_ID = contract_saga().id

#: The button that completes a dialog (whatever its label says).
SAVE_BUTTON_IDS = ("btn-save", "btn-create", "btn-confirm")


@dataclass
class Contract:
    #: Label -> the value shown when the dialog opens.
    prefill: dict[str, Any]
    #: Label -> a new value (text for inputs, a value for selects, a bool for
    #: checkboxes); saved, then `saved` must return `expected`.
    edits: dict[str, Any]
    saved: Callable[[Saga], Any]
    expected: Any
    #: Label -> a value the dialog must refuse, or several such entries,
    #: each refused on its own (None: nothing to refuse).
    invalid: dict[str, Any] | list[dict[str, Any]] | None = None
    #: Selector -> text the screen shows there once the edit is saved (the
    #: sheet, panel or tree refreshed): a Collapsible's title, a list's rows
    #: or a Static's text, markup stripped.
    shown: dict[str, str] = field(default_factory=dict)
    #: Label -> widget id, for fields drawn without a label.
    aliases: dict[str, str] = field(default_factory=dict)
    #: Selector -> text the dialog itself shows once `edits` are typed,
    #: before saving (a live line worked out from them).
    live: dict[str, str] = field(default_factory=dict)


#: A self-initiation into Affinity with Ignem, with a Major Ordeal.
_INITIATION = {
    "Activity": "undergo_initiation",
    "Script bonus": "12",
    "Mystagogue's Lore": "Mercere Lore",
    "Virtue initiated": VirtueFlawInstance("vf_affinity_with_art", {"art": "ignem"}),
    "Ordeal Flaw": VirtueFlawInstance("vf_deficient_technique", {"technique": "creo"}),
    "Ordeal size": "Major",
}

#: A Resolved Story Event linked to the covenant's Hidden Resources Boon.
_HIDDEN_STORY = {
    "Category": "Story Event",
    "Name": "Past the guardian",
    "Status": "Resolved",
    "Linked Boon/Hook": "bh-hr",
}

#: The same, linked to its Illusory Resources Hook.
_ILLUSORY_STORY = {**_HIDDEN_STORY, "Linked Boon/Hook": "bh-ir"}


def _char(saga: Saga):
    return next(c for c in saga.characters if c.id == "mag1")


def _fam(saga: Saga):
    return saga.familiars[0]


def _lab(saga: Saga):
    return saga.laboratories[0]


def _cov(saga: Saga):
    return saga.covenants[0]


def _gear(possessions: list[Possession], kind: str) -> tuple:
    """The last weapon's (or armor's) name, book entry, Quality and
    figures."""
    item = [p for p in possessions if p.kind == kind][-1]
    head = (item.name, item.gear_id, item.gear_quality)
    if kind == "armor":
        return (*head, item.gear_type, item.armor_protection, item.load)
    figures = (item.weapon_init, item.weapon_attack, item.weapon_defense)
    return (*head, *figures, item.weapon_damage, item.load)


def _all_sagas() -> list[Saga]:
    return [storage.load_saga(saga_id) for saga_id in storage.list_sagas()]


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
            [(x.step, x.target, x.xp) for x in _char(s).creation_xp],
            [a.specialty for a in _char(s).abilities if a.name == "Area Lore: Rhine"],
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
        saved=lambda s: [(x.target, x.xp) for x in _char(s).creation_xp],
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
        saved=lambda s: [(x.step, x.target, x.xp) for x in _char(s).creation_xp],
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
            _char(s).creation_conditions.lab_seasons,
            _char(s).creation_conditions.aura,
        ),
        expected=(6, 5),
        invalid=[{"Seasons of lab work": "-1"}, {"Aura": "x"}],
    ),
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
    "native language": Contract(
        prefill={"Language": ""},
        edits={"Language": "German"},
        saved=lambda s: [(x.target, x.xp, x.note) for x in _char(s).creation_xp],
        expected=[("Living Language: German", 75, "native")],
        invalid={"Language": ""},
    ),
    "create saga": Contract(
        prefill={"Name": "", "Start Year": "1220", "Start Season": "Spring"},
        edits={"Name": "Second Saga", "Storyguide": "Ann"},
        saved=lambda _: sorted(
            (s.name, s.storyguide) for s in _all_sagas() if s.name == "Second Saga"
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
    "create character": Contract(
        prefill={"Name": "", "Type": "magus", "Covenant": "cov1"},
        edits={"Name": "Ulla", "Type": "companion"},
        saved=lambda s: [
            (c.type, c.covenant_id) for c in s.characters if c.name == "Ulla"
        ],
        expected=[("companion", "cov1")],
        invalid={"Name": ""},
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
            "Tribunal": "Rhine",
            "Year Founded": "1100",
            "Aura": "3",
            "Covenant Season": "Summer",
        },
        saved=lambda s: (
            _cov(s).name,
            _cov(s).tribunal,
            _cov(s).year_founded,
            _cov(s).aura,
            _cov(s).covenant_season,
        ),
        expected=("Keep II", "Rhine", 1100, 3, "Summer"),
        invalid=[{"Name": ""}, {"Name": "  "}],
        shown={"#cov-info-right": "Rhine", "#cov-info-left": "1100"},
    ),
    "edit covenant description": Contract(
        prefill={"Description": ""},
        edits={"Description": "An old keep."},
        saved=lambda s: _cov(s).notes,
        expected="An old keep.",
        shown={"#cov-description-content": "An old keep."},
    ),
    "edit boon": Contract(
        prefill={"Detail": ""},
        edits={"Detail": "North tower", "Description": "Tall"},
        saved=lambda s: (
            _cov(s).boons_hooks[0].params.get(BOON_HOOK_DETAIL),
            _cov(s).boons_hooks[0].params.get(BOON_HOOK_DESCRIPTION),
        ),
        expected=("North tower", "Tall"),
        shown={"#cov-boons-list": "North tower"},
    ),
    "edit hook": Contract(
        prefill={"Unknown": False, "Detail": ""},
        edits={"Unknown": True, "Detail": "The mill"},
        saved=lambda s: (
            _cov(s).boons_hooks[1].params.get(BOON_HOOK_DETAIL),
            _cov(s).boons_hooks[1].params.get(BOON_HOOK_UNKNOWN),
        ),
        expected=("The mill", "yes"),
    ),
    "edit personality trait": Contract(
        prefill={"Name": "Brave", "Score": "2"},
        edits={"Name": "Bold", "Score": "3"},
        saved=lambda s: (
            _char(s).personality_traits[0].name,
            _char(s).personality_traits[0].score,
        ),
        expected=("Bold", 3),
        invalid={"Name": ""},
        shown={"#personality-traits-list": "Bold: +3"},
    ),
    # Choosing a book weapon fills in its figures; a typed name stays.
    "edit covenant weapon": Contract(
        prefill={"Name": "A weapon", "Weapon": Select.NULL, "Init": "0", "Load": "0"},
        edits={"Weapon": "weapon_long_sword"},
        saved=lambda s: _gear(_cov(s).possessions, "weapon"),
        expected=("A weapon", "weapon_long_sword", "Expensive", 2, 4, 1, 6, 1),
        invalid={"Quantity": "0"},
    ),
    "edit covenant armor": Contract(
        prefill={"Name": "A armor", "Material": Select.NULL, "Protection": "0"},
        edits={"Material": "armor_metal_scale", "Type": "Full armor"},
        saved=lambda s: _gear(_cov(s).possessions, "armor"),
        expected=("A armor", "armor_metal_scale", "Standard", "Full armor", 7, 7),
        # Heavy Leather only comes as partial armor.
        invalid={"Material": "armor_heavy_leather", "Type": "Full armor"},
    ),
    "add personal weapon": Contract(
        prefill={"Name": "", "Weapon": Select.NULL, "Attack": "0"},
        edits={"Weapon": "weapon_short_bow"},
        saved=lambda s: _gear(_char(s).inventory, "weapon"),
        # A blank name becomes the weapon's.
        expected=("Short Bow", "weapon_short_bow", "Standard", -1, 3, 0, 6, 2),
        invalid={"Name": ""},
    ),
    "edit natural weapon": Contract(
        prefill={"Name": "Beak", "Natural Weapon": Select.NULL},
        edits={"Natural Weapon": "natural_teeth"},
        saved=lambda s: _gear(_fam(s).natural_weapons, "weapon"),
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
            _char(s).background.setting,
            _char(s).background.size,
            _char(s).background.confidence_score,
            _char(s).background.faith_points,
        ),
        expected=("Rhine", 1, 2, 3),
        invalid={"Name": ""},
        shown={"#char-info-left": "Rhine"},
    ),
    "edit characteristics": Contract(
        prefill={"Intelligence": "0", "Quickness": "0"},
        edits={"Intelligence": "3", "Quickness": "-2"},
        saved=lambda s: (
            _char(s).characteristics.intelligence,
            _char(s).characteristics.quickness,
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
            _char(s).background.player,
            _char(s).background.year_born,
            _char(s).description.handedness,
            _char(s).description.biography,
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
            _char(s).aging.decrepitude,
            _char(s).aging.effects,
            _char(s).aging.warping_score,
            _char(s).aging.warping_points,
        ),
        expected=(1, "Limp", 2, 5),
        invalid={"Decrepitude": "-"},
        shown={"#aging-content": "Decrepitude: 1"},
    ),
    "edit wounds": Contract(
        prefill={"Soak": "0", "Light Wounds": "0", "Incapacitated": False},
        edits={"Soak": "3", "Light Wounds": "1", "Incapacitated": True},
        saved=lambda s: (
            _char(s).wounds.soak,
            _char(s).wounds.light,
            _char(s).wounds.incapacitated,
        ),
        expected=(3, 1, True),
        invalid={"Soak": "-"},
        shown={"#wounds-content": "Incapacitated: yes"},
    ),
    "edit fatigue": Contract(
        prefill={"Level": "fresh"},
        edits={"Level": "weary"},
        saved=lambda s: _char(s).fatigue_level,
        expected="weary",
        shown={"#fatigue-content": "Weary"},
    ),
    "edit hermetic background": Contract(
        prefill={"Domus Magna": "", "Age of Apprenticeship": ""},
        edits={"Domus Magna": "Durenmar", "Age of Apprenticeship": "15"},
        saved=lambda s: (
            _char(s).hermetic.domus_magna,
            _char(s).hermetic.age_of_apprenticeship,
        ),
        expected=("Durenmar", 15),
        invalid={"Age of Apprenticeship": "-"},  # crashed before
        shown={"#hermetic-background-left": "Durenmar"},
    ),
    "edit ability": Contract(
        prefill={"XP": "50"},
        edits={"XP": "75", "Specialty": "Grammar"},
        saved=lambda s: (_char(s).abilities[0].level, _char(s).abilities[0].specialty),
        expected=(5, "Grammar"),
        invalid={"XP": "-5"},
        live={"#fields-live": "Latin: Score 5 · Score 6 at 105 xp"},
        # the score and xp are in columns
        shown={"#abilities-list": "Latin (Grammar)           5       75/105"},
    ),
    "edit raw vis": Contract(
        prefill={"Art": "creo", "Pawns": "3"},
        edits={"Pawns": "5"},
        saved=lambda s: _char(s).raw_vis,
        expected={"creo": 5},
        invalid={"Pawns": "-"},
    ),
    "move raw vis": Contract(
        prefill={"Pawns": "3", "To": Select.NULL},
        edits={"Pawns": "2", "To": "laboratory:lab1"},
        saved=lambda s: (
            _char(s).raw_vis,
            _lab(s).raw_vis,
            _char(s).diary[-1].name,
            _lab(s).diary[-1].name,
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
            _char(s).breakthroughs[-1].name,
            _char(s).breakthroughs[-1].kind,
            _char(s).breakthroughs[-1].target,
            _char(s).breakthroughs[-1].grant_kind,
            _char(s).breakthroughs[-1].grant,
        ),
        expected=("Piercing the Aegis", "Major", 45, "Ability", "Aegis Lore"),
        invalid=[{"Goal": ""}, {"Goal": "X", "Target": "0"}],
        shown={"#research-goals-list": "Piercing the Aegis (Major): 0/45"},
    ),
    "lab virtue choice": Contract(
        prefill={"Specialization": Select.NULL},
        edits={"Specialization": "Muto"},
        saved=lambda s: _lab(s).virtues_flaws[-1].params,
        expected={"specialization": "Muto"},
        invalid={"Specialization": Select.NULL},
    ),
    "virtue parameters": Contract(
        prefill={"Subject": ""},
        edits={"Subject": "Latin"},
        saved=lambda s: _char(s).virtues_flaws[-1].params,
        expected={"subject": "latin"},  # parameters are stored lower-case
        invalid={"Subject": ""},
    ),
    "virtue ability choice": Contract(
        # An {ability} is picked from a list, not typed.
        prefill={"Ability": Select.NULL},
        edits={"Ability": "magic theory"},
        saved=lambda s: _char(s).virtues_flaws[-1].params,
        expected={"ability": "magic theory"},
        invalid={"Ability": Select.NULL},
    ),
    "edit familiar info": Contract(
        prefill={"Name": "Corax", "Species": ""},
        edits={"Species": "Raven", "Year Bound": "1210", "Size": "-2"},
        saved=lambda s: (_fam(s).species, _fam(s).year_bound, _fam(s).size),
        expected=("Raven", 1210, -2),
        invalid={"Name": ""},
        shown={"#fam-info-content": "Raven"},
    ),
    "edit familiar binding": Contract(
        prefill={"Initial Binding Lab Total": "0"},
        edits={"Binding Technique": "Rego", "Initial Binding Lab Total": "30"},
        saved=lambda s: (_fam(s).binding_technique, _fam(s).binding_lab_total),
        expected=("Rego", 30),
        shown={"#fam-binding-content": "Rego"},
    ),
    "edit spell mastery": Contract(
        prefill={"Score": "0", "XP": "0"},
        edits={"Score": "2", "XP": "10"},
        saved=lambda s: (
            _char(s).spells_known[0].mastery_score,
            _char(s).spells_known[0].mastery_xp,
        ),
        expected=(2, 10),
        invalid=[{"Score": "-"}, {"XP": "x"}],
    ),
    "edit familiar characteristics": Contract(
        prefill={"Intelligence": "0", "Base Soak": "0"},
        edits={"Intelligence": "-5", "Base Soak": "2", "Magic Resistance": "4"},
        saved=lambda s: (
            _fam(s).characteristics.intelligence,
            _fam(s).base_soak,
            _fam(s).magic_resistance,
        ),
        expected=(-5, 2, 4),
        invalid={"Intelligence": "-"},
        shown={"#fam-characteristics-content": "Base Soak: 2"},
    ),
    "edit familiar wounds": Contract(
        prefill={"Light Wounds": "0", "Dead": False},
        edits={"Light Wounds": "2", "Dead": True},
        saved=lambda s: (_fam(s).wounds.light, _fam(s).wounds.dead),
        expected=(2, True),
        invalid={"Light Wounds": "-"},
    ),
    "edit lab identity": Contract(
        prefill={"Name": "Tower", "Covenant": "cov1", "Owner": "mag1"},
        edits={
            "Location": "Tower top",
            "Aura modifier": "1",
            "Sanctum marked": True,
        },
        saved=lambda s: (
            _lab(s).location,
            _lab(s).aura_modifier,
            _lab(s).sanctum_marked,
        ),
        expected=("Tower top", 1, True),
        invalid={"Name": ""},
        shown={"#lab-identity-right": "Sanctum?:     Yes"},
    ),
    "edit lab characteristics": Contract(
        prefill={"Size": "0", "Refinement": "0"},
        edits={"Refinement": "2", "Safety": "-1"},
        saved=lambda s: (
            _lab(s).characteristics.refinement,
            _lab(s).characteristics.safety,
        ),
        expected=(2, -1),
        invalid={"Safety": "-"},
        shown={"#lab-characteristics-right": "+2"},
    ),
    "add lab specialization source": Contract(
        prefill={"Points": "1", "Source": ""},
        edits={"Specialization": "Herbam", "Points": "-1", "Source": "Garden"},
        saved=lambda s: _lab(s).specialties[-1],
        expected=LabSpecialtyEntry("Herbam", -1, "Garden"),
        invalid={"Points": "0"},
        shown={"#lab-specialties-list": "Garden"},
    ),
    "edit lab feature": Contract(
        prefill={
            "Name": "Big windows",
            "Point 1": "Intellego",
            "Point 2": "Intellego",
            "Point 3": "Auram",
            "Focus": True,
            "Focus point 1": "Imaginem",
            "Focus point 4": "Imaginem",
        },
        edits={"Name": "Skylight", "Point 3": "Imaginem", "Focus": False},
        saved=lambda s: (
            _lab(s).features[0].name,
            _lab(s).features[0].allocations,
            _lab(s).features[0].focus,
            _lab(s).features[0].focus_allocations,
        ),
        expected=(
            "Skylight",
            [LabSpecialtyGrant("Intellego", 2), LabSpecialtyGrant("Imaginem", 1)],
            False,
            [],
        ),
        invalid={"Name": ""},
    ),
    "add lab room": Contract(
        prefill={"Name": ""},
        edits={"Name": "Vault", "Description": "Cold"},
        saved=lambda s: (_lab(s).rooms[-1].name, _lab(s).rooms[-1].description),
        expected=("Vault", "Cold"),
        invalid={"Name": ""},
        shown={"#lab-rooms-list": "Vault"},
    ),
    "add arcane connection": Contract(
        prefill={"Connection to": "", "Fixed": False, "Lasts": ""},
        edits={
            "Connection to": "a lock of hair",
            "Lasts": "until Summer 1222",
            "Where from": "the Tribunal",
        },
        saved=lambda s: [
            (c.to, c.fixed, c.lasts, c.source) for c in _lab(s).arcane_connections
        ],
        expected=[("a lock of hair", False, "until Summer 1222", "the Tribunal")],
        invalid={"Connection to": ""},
        shown={"#lab-connections-list": "a lock of hair"},
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
    "add lab diary entry": Contract(
        prefill={"Year": "1220", "Season": "Autumn", "Name": ""},
        edits={
            "Year": "1221",
            "Activity Type": "Study",
            "Name": "Moved in",
            "Details": "Boxes",
        },
        saved=lambda s: (
            _lab(s).diary[-1].year,
            _lab(s).diary[-1].activity,
            _lab(s).diary[-1].name,
            _lab(s).diary[-1].details,
        ),
        expected=(1221, "Study", "Moved in", "Boxes"),
        invalid={"Year": "-"},
        shown={"#lab-diary-list": "Moved in"},
    ),
    "plan a season": Contract(
        prefill={"Activity": "exposure", "Months lost": "0", "Notes": ""},
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
        prefill={"Activity": "exposure", "Months lost": "0", "Notes": ""},
        edits=_INITIATION,
        saved=lambda s: [
            (
                p.activity,
                p.title,
                p.other_modifier,
                p.effect_id,
                p.effect_params,
                p.device_id,
                p.ordeal_params,
                p.research_kind,
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
                "Major",
            )
        ],
        invalid=[
            {**_INITIATION, "Virtue initiated": None},
            {**_INITIATION, "Ordeal size": "Minor"},
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
            _char(s).diary[-1].year,
            _char(s).diary[-1].activity,
            _char(s).diary[-1].name,
            _char(s).diary[-1].details,
        ),
        expected=(1221, "Practice", "Latin lessons", "At the abbey"),
        invalid={"Year": "-"},
        shown={"#char-diary-list": "Latin lessons"},
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
            _cov(s).diary[-1].year,
            _cov(s).diary[-1].category,
            _cov(s).diary[-1].name,
            _cov(s).diary[-1].pounds,
            _cov(s).diary[-1].loyalty,
        ),
        expected=(1221, "Purchases & Sales", "Bought a mill", -12.0, 3),
        invalid={"Pounds": "lots"},
        shown={"#cov-diary-list": "Bought a mill"},
    ),
    "add hidden resources story event": Contract(
        prefill={"Year": "1220", "Season": "Autumn", "Name": ""},
        edits={**_HIDDEN_STORY, "Build Points unlocked": "120"},
        saved=lambda s: (
            _cov(s).diary[-1].category,
            _cov(s).diary[-1].boon_hook_id,
            _cov(s).diary[-1].build_points,
        ),
        expected=("Story Event", "bh-hr", 120),
        invalid=[
            {**_HIDDEN_STORY, "Build Points unlocked": "251"},
            {**_HIDDEN_STORY, "Build Points unlocked": "0"},
        ],
        shown={
            "#cov-boons-list": "Hidden Resources (120/250 BP)",
            "#cov-diary-list": "Past the guardian  \\[Resolved]  120 Build Points",
        },
    ),
    "add illusory resources story event": Contract(
        prefill={"Year": "1220", "Season": "Autumn", "Name": ""},
        edits={**_ILLUSORY_STORY, "Build Points found illusory": "60"},
        saved=lambda s: (
            _cov(s).diary[-1].boon_hook_id,
            _cov(s).diary[-1].build_points,
        ),
        expected=("bh-ir", 60),
        invalid=[
            {**_ILLUSORY_STORY, "Build Points found illusory": "251"},
            {**_ILLUSORY_STORY, "Build Points found illusory": "-5"},
        ],
        shown={"#cov-hooks-list": "Illusory Resources (60/250 BP)"},
    ),
    "edit enchanted device": Contract(
        prefill={
            "Name": "Wand",
            "Type": "Invested Device",
            "Holder": "laboratory:lab1",
            "Pawns opened": "4",
        },
        edits={
            "Name": "Rowan Wand",
            "Holder": "covenant:cov1",
            "Maker": "mag1",
            "Pawns opened": "3",
        },
        saved=lambda s: (
            _device(s, "dev-lab").name,
            _device(s, "dev-lab").holder_kind,
            _device(s, "dev-lab").holder_id,
            _device(s, "dev-lab").maker_id,
            _device(s, "dev-lab").pawns_opened,
            [e.id for e in _device(s, "dev-lab").effects],
        ),
        expected=("Rowan Wand", "covenant", "cov1", "mag1", 3, ["eff1"]),
        invalid={"Name": ""},
    ),
    "instill effect": Contract(
        prefill={"Name": "", "Effect level": "0", "Uses per day": "1"},
        edits={
            "Name": "Ward",
            "Technique": "Rego",
            "Form": "Vim",
            "Effect level": "20",
            "Uses per day": "6",
            "Penetration": "4",
            "Effect Expiry": "7 years",
        },
        saved=lambda s: [
            (e.name, e.technique, e.form, e.level, e.uses_per_day, e.penetration)
            + (e.expiry,)
            for e in _device(s, "dev-lab").effects[1:]
        ],
        expected=[("Ward", "Rego", "Vim", 20, "6", 4, "7 years")],
        invalid={"Name": "Ward", "Penetration": "3"},
    ),
    "edit charged item effect": Contract(
        prefill={"Name": "Heal", "Technique": "Creo", "Effect level": "20"},
        edits={"Name": "Mend", "Effect level": "15", "Known": False},
        saved=lambda s: (
            _device(s, "dev-cov").effects[0].name,
            _device(s, "dev-cov").effects[0].level,
            _device(s, "dev-cov").effects[0].known,
        ),
        expected=("Mend", 15, False),
        invalid={"Effect level": "-5"},
    ),
    # -- forms that only had bespoke tests --
    "edit covenant reputation": Contract(
        prefill={"Name": "Fair dealing", "Score": "2"},
        edits={"Score": "3"},
        saved=lambda s: _cov(s).reputations[0].score,
        expected=3,
        invalid=[{"Score": "4"}, {"Score": "-4"}],
        shown={"#cov-reputations-list": "Fair dealing: +3"},
    ),
    "add boon": Contract(
        prefill={"Detail": "", "Description": ""},
        edits={"Detail": "North tower", "Description": "Tall"},
        saved=lambda s: (
            _cov(s).boons_hooks[-1].vf_id,
            _cov(s).boons_hooks[-1].params.get(BOON_HOOK_DETAIL),
            _cov(s).boons_hooks[-1].params.get(BOON_HOOK_DESCRIPTION),
        ),
        expected=("covbh_boon_minor_edifice", "North tower", "Tall"),
        shown={"#cov-boons-list": "Edifice - North tower"},
    ),
    "add property": Contract(
        prefill={"Name": "", "Dimensions": ""},
        edits={"Name": "Mill", "Dimensions": "40 acres"},
        saved=lambda s: [
            (p.name, p.dimensions) for p in _cov(s).possessions if p.name == "Mill"
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
            for p in _cov(s).possessions
            if p.name == "Study"
        ],
        expected=[("Free", 3, 15, "Standard (2 Seasons)")],
        invalid={"Name": ""},
        shown={"#pos-sanctum-list": "Study"},
    ),
    "add covenant item": Contract(
        prefill={"Name": "", "Quantity": "1"},
        edits={"Name": "Lens", "Quantity": "5"},
        saved=lambda s: [p.quantity for p in _cov(s).possessions if p.name == "Lens"],
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
            for p in _cov(s).possessions
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
            for p in _cov(s).possessions
            if p.name == "Cask"
        ],
        expected=[("Vim", 9, "laboratory", "lab1", "Top shelf")],
        invalid=[{"Name": ""}, {"Name": "Cask"}],
        shown={"#pos-vis_store-list": "Cask"},
    ),
    "edit wealth": Contract(
        prefill={"Wealth": "0"},
        edits={"Wealth": "2525"},
        saved=lambda s: _cov(s).economics.wealth,
        expected=2525,
        invalid={"Wealth": "lots"},
        shown={"#eco-wealth-left": "2525"},
    ),
    "add income source": Contract(
        prefill={"Name": "", "Type": "Typical", "Current Income": ""},
        edits={"Name": "Toll bridge", "Type": "Greater"},
        saved=lambda s: [
            (i.type, i.income)
            for i in _cov(s).economics.income_sources
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
        saved=lambda s: _cov(s).economics.income_sources[0].income,
        expected=55,
        invalid={"Current Income": "lots"},
        shown={"#eco-income-list": "55"},
    ),
    "edit expenditure row": Contract(
        prefill={"Notes": ""},
        edits={"Notes": "Old roof"},
        saved=lambda s: _cov(s).economics.notes.get("buildings"),
        expected="Old roof",
        shown={"#eco-expenditure-list": "Old roof"},
    ),
    "edit tithes": Contract(
        prefill={"Amount": "0", "Notes": ""},
        edits={"Amount": "12"},
        saved=lambda s: _cov(s).economics.tithes,
        expected=12,
        invalid={"Amount": "lots"},
    ),
    "edit sundry": Contract(
        prefill={"Amount": "1"},
        edits={"Amount": "3"},
        saved=lambda s: _cov(s).economics.sundry,
        expected=3,
        invalid={"Amount": "0"},  # at least 1
    ),
    "edit magic savings": Contract(
        prefill={"Savings": "0"},
        edits={"Savings": "20"},
        saved=lambda s: _cov(s).economics.magic_savings,
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
            _cov(s).loyalty.governance,
            _cov(s).loyalty.money,
            _cov(s).loyalty.familiarity,
        ),
        expected=("Council", "Generous salary", 2),
        invalid={"Familiarity": "lots"},
    ),
    "edit population": Contract(
        prefill={"Other People": "0"},
        edits={"Other People": "7"},
        saved=lambda s: _cov(s).population.other_people,
        expected=7,
        invalid={"Other People": "lots"},
    ),
    "edit miscellaneous": Contract(
        prefill={"Aging for Magi": "0", "Magic Turbula": "0"},
        edits={"Aging for Magi": "1", "Magic Turbula": "2"},
        saved=lambda s: (
            _cov(s).population.aging_magi,
            _cov(s).population.magic_turbula,
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
            for i in _cov(s).inhabitants
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
            (i.kind, i.quantity) for i in _cov(s).inhabitants if i.name == "Guards"
        ],
        expected=[("turb", 3)],
        invalid=[{"Name": ""}, {"Name": "Guards", "Quantity": "0"}],
        shown={"#section-inh-turb": "(4)"},  # the headcount adds the quantity
    ),
    "add covenfolk member": Contract(
        prefill={"Name": "", "Covenant Role": Select.NULL, "Quantity": "1"},
        edits={"Name": "Old Marta", "Covenant Role": "Dependent", "Year Born": "1180"},
        saved=lambda s: [
            (i.role, i.year_born) for i in _cov(s).inhabitants if i.name == "Old Marta"
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
            for i in _cov(s).inhabitants
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
            for i in _cov(s).inhabitants
            if i.name == "Ponies"
        ],
        expected=[("horse", 4, None)],
        invalid={"Quantity": "0"},
        shown={"#inh-horse-list": "Ponies"},
    ),
    "edit book": Contract(
        prefill={"Name": "Summa", "Type": "Art Summa", "Owner": "covenant:cov1"},
        edits={
            "Art": "Ignem",
            "Level": "10",
            "Quality": "12",
            "Owner": "laboratory:lab1",
        },
        saved=lambda s: [
            (b.owner_kind, b.owner_id) for b in s.books if b.id == "b-cov"
        ],
        expected=[("laboratory", "lab1")],
        invalid={"Name": ""},
    ),
    "add book": Contract(
        prefill={"Name": "", "Type": Select.NULL, "Owner": "covenant:cov1"},
        edits={
            "Name": "Scrolls",
            "Type": "Tractatus",
            "Subject": "Art",
            "Art": "Ignem",
            "Quality": "7",
            "Language": "Greek",
        },
        saved=lambda s: [
            (b.type, b.language, b.owner_kind, b.owner_id)
            for b in s.books
            if b.name == "Scrolls"
        ],
        expected=[("Tractatus", "Greek", "covenant", "cov1")],
        invalid=[
            {"Name": ""},
            # A templated Ability needs its detail.
            {
                "Name": "Lore",
                "Type": "Ability Summa",
                "Ability": "Area Lore: {region}",
            },
        ],
        shown={"#section-lib-books-list": "Scrolls"},
    ),
    "add book into a codex": Contract(
        prefill={"Name": "", "Codex": Select.NULL, "Owner": "covenant:cov1"},
        edits={
            "Name": "Scrolls",
            "Type": "Tractatus",
            "Subject": "Art",
            "Art": "Ignem",
            "Quality": "7",
            "Codex": "__new__",
            "New codex's name": "Bound Fire",
            "Palimpsest": True,
        },
        saved=lambda s: [
            (c.name, c.palimpsest, [b.name for b in s.books if b.codex_id == c.id])
            for c in s.codices
        ],
        expected=[("Bound Fire", True, ["Scrolls"])],
        invalid={"Name": ""},
        shown={"#section-lib-books-list": "│ Scrolls"},
    ),
    "add commentary": Contract(
        prefill={"Name": "", "Physical form": Select.NULL},
        edits={
            "Name": "Glosses",
            "Type": "Tractatus",
            "Subject": "Art",
            "Art": "Ignem",
            "Quality": "7",
            "Opus": "Commentary",
            "Commentary on": "b-cov",
            "Physical form": "Exemplar",
        },
        saved=lambda s: [
            (b.opus, b.commentary_on, b.physical_form)
            for b in s.books
            if b.name == "Glosses"
        ],
        expected=[("Commentary", "b-cov", "Exemplar")],
        invalid={"Name": ""},
        shown={"#section-lib-books-list": "Glosses"},
    ),
    "book craftsmanship": Contract(
        prefill={"Skilled scribe (+1)": False, "Resonant materials": Select.NULL},
        edits={
            "Skilled scribe (+1)": True,
            "Skilled illuminator (+1)": True,
            "Resonant materials": "story_resonance",
        },
        saved=lambda s: [b.craft for b in s.books if b.id == "b-cov"],
        expected=[["scribe", "illuminator", "story_resonance"]],
        invalid={"Name": ""},
    ),
    "enchant a book": Contract(
        prefill={"Epitome": Select.NULL},
        edits={
            "Art": "Ignem",
            "Level": "10",
            "Quality": "12",
            "Epitome": "__new_epitome__",
        },
        saved=lambda s: [
            (d.name, d.holder_kind, d.holder_id)
            for b in s.books
            if b.id == "b-cov"
            for d in s.enchanted_devices
            if d.id == b.device_id
        ],
        expected=[("Summa", "covenant", "cov1")],
        invalid={"Name": ""},
    ),
    "research bonuses": Contract(
        prefill={"Ignem": "0"},
        edits={"Ignem": "3"},
        saved=lambda s: s.covenants[0].library_research,
        expected={"Ignem": 3},
        shown={"#lib-summary-right": "1 subject"},
    ),
    # Lab Texts
    "add lab text": Contract(
        prefill={"Name": "", "Type": Select.NULL, "Owner": "laboratory:lab1"},
        edits={
            "Name": "Ring of Warmth",
            "Type": "Lab Text",
            "Kind": "Enchantment",
            "Technique": "Creo",
            "Form": "Ignem",
            "Level": "10",
            "Range / Duration / Target": "Touch / Sun / Individual",
            "Device": "Lesser Enchantment",
            "Author's sheet": "mag2",
            "Raw (author's shorthand)": True,
        },
        saved=lambda s: [
            (
                b.text_kind,
                b.technique,
                b.form,
                b.level,
                b.effect_rdt,
                b.device_type,
                b.author_id,
                b.author,
                b.raw,
                b.spell_id,
            )
            for b in s.books
            if b.name == "Ring of Warmth"
        ],
        expected=[
            (
                "Enchantment",
                "Creo",
                "Ignem",
                10,
                "Touch / Sun / Individual",
                "Lesser Enchantment",
                "mag2",
                "Brother Oda",
                True,
                None,
            )
        ],
        # A spell's text needs its spell; any other kind needs its level.
        invalid=[
            {"Name": "Text", "Type": "Lab Text"},
            {"Name": "Text", "Type": "Lab Text", "Kind": "Other"},
        ],
        shown={"#section-lab-texts-list": "Ring of Warmth"},
    ),
    "perform ritual again": Contract(
        prefill={"Vis": "Creo", "Vis from": "laboratory"},
        edits={"Vis from": "character"},
        saved=lambda s: (
            _char(s).raw_vis,
            _char(s).aging.longevity_modifier,
            _lab(s).diary[-1].name,
        ),
        # Level 20 / 5; 2 of his 3 pawns of Creo vis.
        expected=({"creo": 1}, 4, "Longevity Ritual performed again: Leandro"),
        # The laboratory has no Creo vis; he has no Vim.
        invalid=[
            {"Vis from": "laboratory"},
            {"Vis": "Vim", "Vis from": "character"},
        ],
    ),
    "lab texts read": Contract(
        prefill={"Author": Select.NULL, "Reads to level": "0"},
        edits={"Author": "mag2", "Reads to level": "20", "How": "decoded"},
        saved=lambda s: _char(s).lab_text_access,
        expected={"mag2": LabTextAccess(20, "decoded")},
        # No author; not a number.
        invalid=[
            {"Reads to level": "5"},
            {"Author": "mag2", "Reads to level": "-"},
        ],
        shown={"#hermetic-background-right": "Brother Oda to 20 (decoded)"},
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
    "add ability": Contract(
        prefill={"XP": "0", "Specialty": ""},
        edits={"XP": "30", "Specialty": "Running"},
        saved=lambda s: [
            (a.category, a.xp, a.specialty)
            for a in _char(s).abilities
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
        saved=lambda s: (_char(s).arts["creo"].xp, _char(s).arts["vim"].xp),
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
        saved=lambda s: _fam(s).fatigue_level,
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
            for p in _fam(s).bond_powers
            if p.name == "Mind link"
        ],
        expected=[(15, "Intellego", "Mentem")],
        invalid={"Level": "lots"},
        shown={"#fam-bond-powers-list": "Mind link"},
    ),
    "edit bond power": Contract(
        prefill={"Power Name": "Speak", "Uses/Day": "0"},
        edits={"Power Name": "Speech"},
        saved=lambda s: _fam(s).bond_powers[0].name,
        expected="Speech",
        invalid={"Level": "lots"},
        shown={"#fam-bond-powers-list": "Speech"},
    ),
    "add lab raw vis": Contract(
        prefill={"Art": Select.NULL, "Pawns": "1"},
        edits={"Art": "vim", "Pawns": "4"},
        saved=lambda s: _lab(s).raw_vis,
        expected={"ignem": 2, "vim": 4},
        invalid=[{"Pawns": "2"}, {"Art": "vim", "Pawns": "-"}],
        shown={"#lab-raw-vis-list": "Vim: 4"},
    ),
    "edit lab raw vis": Contract(
        prefill={"Art": "ignem", "Pawns": "2"},
        edits={"Pawns": "5"},
        saved=lambda s: _lab(s).raw_vis,
        expected={"ignem": 5},
        invalid={"Pawns": "-"},
        shown={"#lab-raw-vis-list": "Ignem: 5"},
    ),
    "edit lab diary entry": Contract(
        prefill={
            "Year": "1220",
            "Season": "Spring",
            "Activity Type": Select.NULL,
            "Name": "Built",
        },
        edits={"Name": "Rebuilt", "Season": "Summer"},
        saved=lambda s: (_lab(s).diary[0].season, _lab(s).diary[0].name),
        expected=("Summer", "Rebuilt"),
        invalid={"Year": "-"},
        shown={"#lab-diary-list": "Rebuilt"},
    ),
    "edit lab specialization source": Contract(
        prefill={"Specialization": "Ignem", "Points": "1", "Source": "Hearth spirit"},
        edits={"Points": "2"},
        saved=lambda s: _lab(s).specialties[0],
        expected=LabSpecialtyEntry("Ignem", 2, "Hearth spirit"),
        invalid={"Points": "0"},
    ),
    "edit lab room": Contract(
        prefill={"Name": "Study", "Description": ""},
        edits={"Name": "Library", "Description": "Dusty"},
        saved=lambda s: (_lab(s).rooms[0].name, _lab(s).rooms[0].description),
        expected=("Library", "Dusty"),
        invalid={"Name": ""},
        shown={"#lab-rooms-list": "Library"},
    ),
}


def _device(saga: Saga, device_id: str):
    return next(d for d in saga.enchanted_devices if d.id == device_id)


# -- finding and setting fields by label --

_INPUTS = (Input, Select, TextArea, Checkbox)


def _is_input(widget: Widget) -> bool:
    """A field's widget: an input, or a "picker" field's button."""
    return isinstance(widget, _INPUTS) or (
        isinstance(widget, Button) and widget.has_class("fd-picker")
    )


def _text(widget: Widget) -> str:
    return str(widget.render()).strip().rstrip(":").strip()


def field_widget(dialog, label: str, aliases: dict[str, str]) -> Widget:
    """The input widget for the field labelled `label` in `dialog`."""
    widgets = list(dialog.query("*"))
    for position, widget in enumerate(widgets):
        if isinstance(widget, Checkbox) and str(widget.label).startswith(label):
            return widget
        if type(widget) in (Label, Static) and _text(widget).startswith(label):
            following = next((w for w in widgets[position + 1 :] if _is_input(w)), None)
            if following is not None:
                return following
    if label in aliases:
        return dialog.query_one(f"#{aliases[label]}")
    raise AssertionError(f"no field labelled {label!r}")


def field_value(widget: Widget) -> Any:
    if isinstance(widget, Button):  # a picker field: what it holds
        return widget.screen._picked.get((widget.id or "").removeprefix("fld-"))
    if isinstance(widget, (Input, Select)):
        return widget.value
    if isinstance(widget, TextArea):
        return widget.text
    assert isinstance(widget, Checkbox)
    return widget.value


def set_field(widget: Widget, value: Any) -> None:
    if isinstance(widget, Button):  # a picker field: as if it were chosen
        dialog = widget.screen
        dialog._picked[(widget.id or "").removeprefix("fld-")] = value
        dialog._react()
        return
    if isinstance(widget, (Input, Select)):
        widget.value = value
    elif isinstance(widget, TextArea):
        widget.text = value
    else:
        assert isinstance(widget, Checkbox)
        widget.value = value


def save_button(dialog) -> Button:
    return next(b for b in dialog.query(Button) if b.id in SAVE_BUTTON_IDS)


def cancel_button(dialog) -> Button:
    return dialog.query_one("#btn-cancel", Button)


def error_text(dialog) -> str:
    """Any error message the dialog shows."""
    return " ".join(
        _text(w)
        for w in dialog.query("Static, Label")
        if w.id and w.id.endswith("error") and _text(w)
    )


def _saved_file() -> str:
    return storage.saga_path(SAGA_ID).read_text(encoding="utf-8")


async def _fill(pilot, dialog, contract: Contract, values: dict[str, Any]) -> None:
    for label, value in values.items():
        set_field(field_widget(dialog, label, contract.aliases), value)
    await pilot.pause()


# -- the contracts --


def _invalid_entries(contract: Contract) -> list[dict[str, Any]]:
    if contract.invalid is None:
        return []
    if isinstance(contract.invalid, dict):
        return [contract.invalid]
    return contract.invalid


def shown_text(screen, selector: str) -> str:
    """What `screen` shows at `selector`: a Collapsible's title, a list's
    rows (one per line) or a Static's text, markup stripped."""
    widget = screen.query_one(selector)
    if isinstance(widget, Collapsible):
        text = widget.title
    elif isinstance(widget, SelectableList):
        text = "\n".join(label for _, label in widget._rows)
    else:
        text = str(widget.render())
    return strip_markup(text)


async def _close(pilot, app, dialog, button: Button) -> None:
    button.press()
    assert await wait_until(pilot, lambda: app.screen is not dialog), (
        f"still open: {error_text(dialog)!r}"
    )
    await pilot.pause()


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_form_contract(name):
    """One app session per form, at 120x45 (the smallest size the user
    works at):

    - the whole dialog, and its Save and Cancel buttons, are on screen (a
      long form scrolls between them);
    - it's pre-filled with the record's current values;
    - Cancel after editing saves nothing;
    - each invalid entry is refused with an error, the dialog staying open
      and nothing saved;
    - a valid edit, saved, lands in the saved saga and the screen shows it.
    """
    contract = CONTRACTS[name]
    app = new_app()
    before = _saved_file()
    async with app.run_test(size=(120, 45)) as pilot:
        base, dialog = await open_dialog(pilot, app, name)
        for button in (save_button(dialog), cancel_button(dialog)):
            region = button.region
            assert region.height > 0, button.id
            assert region.x >= 0 and region.right <= 120, (button.id, region)
            assert region.y >= 0 and region.bottom <= 45, (button.id, region)

        prefilled = {
            label: field_value(field_widget(dialog, label, contract.aliases))
            for label in contract.prefill
        }
        assert prefilled == contract.prefill

        await _fill(pilot, dialog, contract, contract.edits)
        await _close(pilot, app, dialog, cancel_button(dialog))
        assert _saved_file() == before

        for entry in _invalid_entries(contract):
            dialog = await reopen_dialog(pilot, app, base, name)
            await _fill(pilot, dialog, contract, entry)
            save_button(dialog).press()
            assert await wait_until(pilot, lambda d=dialog: error_text(d) != ""), entry
            assert app.screen is dialog, entry
            await _close(pilot, app, dialog, cancel_button(dialog))
            assert _saved_file() == before, entry
        if name == "create saga":
            assert storage.list_sagas() == [SAGA_ID]

        dialog = await reopen_dialog(pilot, app, base, name)
        view = getattr(base, "_current_sheet_view", lambda: None)()
        if contract.shown and view is not None:
            # Build every tab now, so the save has to refresh what's shown.
            await build_all_tabs(pilot, view)
        await _fill(pilot, dialog, contract, contract.edits)
        for selector, text in contract.live.items():
            assert await wait_until(
                pilot, lambda s=selector, t=text, d=dialog: t in shown_text(d, s)
            ), (selector, shown_text(dialog, selector))
        await _close(pilot, app, dialog, save_button(dialog))
        # The screen shows the saved values (its sheet was refreshed).
        for selector, text in contract.shown.items():
            assert await wait_until(
                pilot, lambda s=selector, t=text: t in shown_text(base, s)
            ), (selector, shown_text(base, selector))
    assert contract.saved(storage.load_saga(SAGA_ID)) == contract.expected


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
