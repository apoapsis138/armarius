"""Dialog contract tests for the forms of a laboratory's sheet.

Each form runs in one app session; dialog_contract_support.py has the
contract and the driver, dialog_openers.py how each form is reached."""

import pytest
from dialog_contract_support import Contract, device, laboratory, run_contract
from textual.widgets import Select

from ars_magica_manager.models import LabSpecialtyEntry, LabSpecialtyGrant

CONTRACTS: dict[str, Contract] = {
    "lab virtue choice": Contract(
        prefill={"Specialization": Select.NULL},
        edits={"Specialization": "Muto"},
        saved=lambda s: laboratory(s).virtues_flaws[-1].params,
        expected={"specialization": "Muto"},
        invalid={"Specialization": Select.NULL},
    ),
    "change lab virtue choice": Contract(
        prefill={"Specialization": "Creo"},
        edits={"Specialization": "Herbam"},
        saved=lambda s: [
            vf.params
            for vf in laboratory(s).virtues_flaws
            if vf.vf_id == "labvf_idyllic_surroundings"
        ],
        expected=[{"specialization": "Herbam"}],
        invalid={"Specialization": Select.NULL},
    ),
    "lab servant": Contract(
        # A grog of the saga, or the servant's Intelligence typed in.
        prefill={"Servant": Select.NULL, "Intelligence": ""},
        edits={"Servant": "grog9"},
        saved=lambda s: laboratory(s).virtues_flaws[-1].params,
        expected={"servant": "grog9"},
        invalid={"Servant": Select.NULL, "Intelligence": "clever"},
        shown={"#lab-vf-virtues-list": "Servant"},
    ),
    "edit lab identity": Contract(
        prefill={"Name": "Tower", "Covenant": "cov1", "Owner": "mag1"},
        edits={
            "Location": "Tower top",
            "Aura modifier": "1",
            "Sanctum marked": True,
            "Place": "drachenfels@2",
        },
        saved=lambda s: (
            laboratory(s).location,
            laboratory(s).aura_modifier,
            laboratory(s).sanctum_marked,
            laboratory(s).place_level,
        ),
        expected=("Tower top", 1, True, 2),
        invalid={"Name": ""},
        shown={"#lab-identity-right": "Sanctum?:     Yes"},
    ),
    "edit lab characteristics": Contract(
        prefill={"Size": "0", "Refinement": "0"},
        edits={"Refinement": "2", "Safety": "-1"},
        saved=lambda s: (
            laboratory(s).characteristics.refinement,
            laboratory(s).characteristics.safety,
        ),
        expected=(2, -1),
        invalid={"Safety": "-"},
        shown={"#lab-characteristics-right": "+2"},
    ),
    "add lab specialization source": Contract(
        prefill={"Points": "1", "Source": ""},
        edits={"Specialization": "Herbam", "Points": "-1", "Source": "Garden"},
        saved=lambda s: laboratory(s).specialties[-1],
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
            laboratory(s).features[0].name,
            laboratory(s).features[0].allocations,
            laboratory(s).features[0].focus,
            laboratory(s).features[0].focus_allocations,
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
        saved=lambda s: (
            laboratory(s).rooms[-1].name,
            laboratory(s).rooms[-1].description,
        ),
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
            (c.to, c.fixed, c.lasts, c.source) for c in laboratory(s).arcane_connections
        ],
        expected=[("a lock of hair", False, "until Summer 1222", "the Tribunal")],
        invalid={"Connection to": ""},
        shown={"#lab-connections-list": "a lock of hair"},
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
            laboratory(s).diary[-1].year,
            laboratory(s).diary[-1].activity,
            laboratory(s).diary[-1].name,
            laboratory(s).diary[-1].details,
        ),
        expected=(1221, "Study", "Moved in", "Boxes"),
        invalid={"Year": "-"},
        shown={"#lab-diary-list": "Moved in"},
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
            device(s, "dev-lab").name,
            device(s, "dev-lab").holder_kind,
            device(s, "dev-lab").holder_id,
            device(s, "dev-lab").maker_id,
            device(s, "dev-lab").pawns_opened,
            [e.id for e in device(s, "dev-lab").effects],
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
            for e in device(s, "dev-lab").effects[1:]
        ],
        expected=[("Ward", "Rego", "Vim", 20, "6", 4, "7 years")],
        invalid={"Name": "Ward", "Penetration": "3"},
    ),
    "add lab raw vis": Contract(
        prefill={"Art": Select.NULL, "Pawns": "1"},
        edits={"Art": "vim", "Pawns": "4"},
        saved=lambda s: laboratory(s).raw_vis,
        expected={"ignem": 2, "vim": 4},
        invalid=[{"Pawns": "2"}, {"Art": "vim", "Pawns": "-"}],
        shown={"#lab-raw-vis-list": "Vim: 4"},
    ),
    "edit lab raw vis": Contract(
        prefill={"Art": "ignem", "Pawns": "2"},
        edits={"Pawns": "5"},
        saved=lambda s: laboratory(s).raw_vis,
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
        saved=lambda s: (laboratory(s).diary[0].season, laboratory(s).diary[0].name),
        expected=("Summer", "Rebuilt"),
        invalid={"Year": "-"},
        shown={"#lab-diary-list": "Rebuilt"},
    ),
    "edit lab specialization source": Contract(
        prefill={"Specialization": "Ignem", "Points": "1", "Source": "Hearth spirit"},
        edits={"Points": "2"},
        saved=lambda s: laboratory(s).specialties[0],
        expected=LabSpecialtyEntry("Ignem", 2, "Hearth spirit"),
        invalid={"Points": "0"},
    ),
    "edit lab room": Contract(
        prefill={"Name": "Study", "Description": ""},
        edits={"Name": "Library", "Description": "Dusty"},
        saved=lambda s: (
            laboratory(s).rooms[0].name,
            laboratory(s).rooms[0].description,
        ),
        expected=("Library", "Dusty"),
        invalid={"Name": ""},
        shown={"#lab-rooms-list": "Library"},
    ),
}


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_form_contract(name):
    await run_contract(name, CONTRACTS[name])
