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
from dialog_openers import contract_saga, new_app, open_dialog
from support import wait_until
from textual.widget import Widget
from textual.widgets import Button, Checkbox, Input, Label, Select, Static, TextArea

from ars_magica_manager import catalog, storage
from ars_magica_manager.models import (
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    BOON_HOOK_UNKNOWN,
    LabSpecialtyEntry,
    LabSpecialtyGrant,
    Possession,
    Saga,
)

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
    #: Label -> a value the dialog must refuse (None: nothing to refuse).
    invalid: dict[str, Any] | None = None
    #: Label -> widget id, for fields drawn without a label.
    aliases: dict[str, str] = field(default_factory=dict)


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
    "create saga": Contract(
        prefill={"Name": "", "Start Year": "1220", "Start Season": "Spring"},
        edits={"Name": "Second Saga", "Storyguide": "Ann"},
        saved=lambda _: sorted(
            (s.name, s.storyguide) for s in _all_sagas() if s.name == "Second Saga"
        ),
        expected=[("Second Saga", "Ann")],
        invalid={"Name": ""},
    ),
    "edit saga": Contract(
        prefill={"Name": "Matrix", "Storyguide": ""},
        edits={"Name": "Matrix II", "Storyguide": "Ann", "Description": "About"},
        saved=lambda s: (s.name, s.storyguide, s.description),
        expected=("Matrix II", "Ann", "About"),
        invalid={"Name": ""},
    ),
    "set date": Contract(
        prefill={"Season": "Spring", "Year": "1220"},
        edits={"Season": "Autumn", "Year": "1225"},
        saved=lambda s: (s.current_season, s.current_year),
        expected=("Autumn", 1225),
        invalid={"Year": "-"},
    ),
    "create covenant": Contract(
        prefill={"Name": ""},
        edits={"Name": "Harbour", "Notes": "By the sea"},
        saved=lambda s: [(c.name, c.notes) for c in s.covenants if c.name == "Harbour"],
        expected=[("Harbour", "By the sea")],
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
        invalid={"Name": "", "Size": "2"},
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
        invalid={"Name": ""},
    ),
    "edit covenant description": Contract(
        prefill={"Description": ""},
        edits={"Description": "An old keep."},
        saved=lambda s: _cov(s).notes,
        expected="An old keep.",
    ),
    "edit boon": Contract(
        prefill={"Detail": ""},
        edits={"Detail": "North tower", "Description": "Tall"},
        saved=lambda s: (
            _cov(s).boons_hooks[0].params.get(BOON_HOOK_DETAIL),
            _cov(s).boons_hooks[0].params.get(BOON_HOOK_DESCRIPTION),
        ),
        expected=("North tower", "Tall"),
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
    ),
    "edit character info": Contract(
        prefill={"Name": "Leandro", "Covenant": "cov1", "Assigned Laboratory": "lab1"},
        edits={"Setting": "Rhine", "Size": "1", "Confidence Score": "2"},
        saved=lambda s: (
            _char(s).background.setting,
            _char(s).background.size,
            _char(s).background.confidence_score,
        ),
        expected=("Rhine", 1, 2),
        invalid={"Name": ""},
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
    ),
    "edit fatigue": Contract(
        prefill={"Level": "fresh"},
        edits={"Level": "weary"},
        saved=lambda s: _char(s).fatigue_level,
        expected="weary",
    ),
    "edit hermetic background": Contract(
        prefill={"Domus Magna": "", "Age of Apprenticeship": ""},
        edits={"Domus Magna": "Durenmar", "Age of Apprenticeship": "15"},
        saved=lambda s: (
            _char(s).hermetic.domus_magna,
            _char(s).hermetic.age_of_apprenticeship,
        ),
        expected=("Durenmar", 15),
        invalid={"Age of Apprenticeship": "-"},  # crashed before (B3)
    ),
    "edit ability": Contract(
        prefill={"Level": "4", "XP": "0"},
        edits={"Level": "5", "Specialty": "Grammar"},
        saved=lambda s: (_char(s).abilities[0].level, _char(s).abilities[0].specialty),
        expected=(5, "Grammar"),
        invalid={"Level": "-"},
    ),
    "edit raw vis": Contract(
        prefill={"Art": "creo", "Pawns": "3"},
        edits={"Pawns": "5"},
        saved=lambda s: _char(s).raw_vis,
        expected={"creo": 5},
        invalid={"Pawns": "-"},
    ),
    "virtue parameters": Contract(
        prefill={"Subject": ""},
        edits={"Subject": "Latin"},
        saved=lambda s: _char(s).virtues_flaws[-1].params,
        expected={"subject": "latin"},  # parameters are stored lower-case
        invalid={"Subject": ""},
    ),
    "edit familiar info": Contract(
        prefill={"Name": "Corax", "Species": ""},
        edits={"Species": "Raven", "Year Bound": "1210", "Size": "-2"},
        saved=lambda s: (_fam(s).species, _fam(s).year_bound, _fam(s).size),
        expected=("Raven", 1210, -2),
        invalid={"Name": ""},
    ),
    "edit familiar binding": Contract(
        prefill={"Initial Binding Lab Total": "0"},
        edits={"Binding Technique": "Rego", "Initial Binding Lab Total": "30"},
        saved=lambda s: (_fam(s).binding_technique, _fam(s).binding_lab_total),
        expected=("Rego", 30),
    ),
    "edit familiar characteristics": Contract(
        prefill={"Intelligence": "0", "Base Soak": "0"},
        edits={"Intelligence": "-5", "Base Soak": "2"},
        saved=lambda s: (_fam(s).characteristics.intelligence, _fam(s).base_soak),
        expected=(-5, 2),
        invalid={"Intelligence": "-"},
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
            "Points": "5",
            "Aura modifier": "1",
            "Sanctum marked": True,
        },
        saved=lambda s: (
            _lab(s).location,
            _lab(s).build_points,
            _lab(s).aura_modifier,
            _lab(s).sanctum_marked,
        ),
        expected=("Tower top", 5, 1, True),
        invalid={"Name": ""},
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
    ),
    "add lab specialization source": Contract(
        prefill={"Points": "1", "Source": ""},
        edits={"Specialization": "Herbam", "Points": "-1", "Source": "Garden"},
        saved=lambda s: _lab(s).specialties[-1],
        expected=LabSpecialtyEntry("Herbam", -1, "Garden"),
        invalid={"Points": "0"},
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
    ),
    "add lab diary entry": Contract(
        prefill={"Year": "1220", "Season": "Spring", "Name": ""},
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
    ),
}


# -- finding and setting fields by label --

_INPUTS = (Input, Select, TextArea, Checkbox)


def _text(widget: Widget) -> str:
    return str(widget.render()).strip().rstrip(":").strip()


def field_widget(dialog, label: str, aliases: dict[str, str]) -> Widget:
    """The input widget for the field labelled `label` in `dialog`."""
    widgets = list(dialog.query("*"))
    for position, widget in enumerate(widgets):
        if isinstance(widget, Checkbox) and str(widget.label).startswith(label):
            return widget
        if type(widget) in (Label, Static) and _text(widget).startswith(label):
            following = next(
                (w for w in widgets[position + 1 :] if isinstance(w, _INPUTS)), None
            )
            if following is not None:
                return following
    if label in aliases:
        return dialog.query_one(f"#{aliases[label]}")
    raise AssertionError(f"no field labelled {label!r}")


def field_value(widget: Widget) -> Any:
    if isinstance(widget, (Input, Select)):
        return widget.value
    if isinstance(widget, TextArea):
        return widget.text
    assert isinstance(widget, Checkbox)
    return widget.value


def set_field(widget: Widget, value: Any) -> None:
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


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_prefills_the_current_values(name):
    contract = CONTRACTS[name]
    app = new_app()
    async with app.run_test(size=(140, 70)) as pilot:
        _, dialog = await open_dialog(pilot, app, name)
        shown = {
            label: field_value(field_widget(dialog, label, contract.aliases))
            for label in contract.prefill
        }
        assert shown == contract.prefill


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_cancel_saves_nothing(name):
    contract = CONTRACTS[name]
    app = new_app()
    before = _saved_file()
    async with app.run_test(size=(140, 70)) as pilot:
        _, dialog = await open_dialog(pilot, app, name)
        await _fill(pilot, dialog, contract, contract.edits)
        cancel_button(dialog).press()
        assert await wait_until(pilot, lambda: app.screen is not dialog)
        await pilot.pause()
    assert _saved_file() == before
    if name == "create saga":
        assert storage.list_sagas() == [SAGA_ID]


@pytest.mark.parametrize(
    "name", [name for name, c in CONTRACTS.items() if c.invalid is not None]
)
async def test_refuses_an_invalid_entry(name):
    contract = CONTRACTS[name]
    assert contract.invalid is not None
    app = new_app()
    before = _saved_file()
    async with app.run_test(size=(140, 70)) as pilot:
        _, dialog = await open_dialog(pilot, app, name)
        await _fill(pilot, dialog, contract, contract.invalid)
        save_button(dialog).press()
        assert await wait_until(pilot, lambda: error_text(dialog) != "")
        assert app.screen is dialog
    assert _saved_file() == before


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_save_stores_the_edit(name):
    contract = CONTRACTS[name]
    app = new_app()
    async with app.run_test(size=(140, 70)) as pilot:
        _, dialog = await open_dialog(pilot, app, name)
        await _fill(pilot, dialog, contract, contract.edits)
        save_button(dialog).press()
        assert await wait_until(pilot, lambda: app.screen is not dialog), (
            f"still open: {error_text(dialog)!r}"
        )
        await pilot.pause()
    assert contract.saved(storage.load_saga(SAGA_ID)) == contract.expected


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_fits_a_small_terminal(name):
    """At 120x45 the whole dialog, and its Save and Cancel buttons, are on
    screen (a long form scrolls between them)."""
    app = new_app()
    async with app.run_test(size=(120, 45)) as pilot:
        _, dialog = await open_dialog(pilot, app, name)
        await pilot.pause()
        for button in (save_button(dialog), cancel_button(dialog)):
            region = button.region
            assert region.height > 0, button.id
            assert region.x >= 0 and region.right <= 120, (button.id, region)
            assert region.y >= 0 and region.bottom <= 45, (button.id, region)


# -- which book tables each weapon form offers (STORY-709) --


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
