"""Arms: the blazon written from the five choices, the rule of tincture,
the shield's pixels, keeping arms with the saga, and the form."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import arms, storage
from ars_magica_manager.arms import Arms
from ars_magica_manager.commands import Form


def test_the_blazon_is_written_from_the_choices():
    assert arms.blazon(Arms("Azure", "Per bend", "Argent", "Tower", "Or")) == (
        "Per bend azure and argent, a tower or"
    )
    assert arms.blazon(Arms("Gules")) == "Gules"
    assert arms.blazon(Arms("Vert", charge="Key", charge_tincture="Argent")) == (
        "Vert, a key argent"
    )
    assert arms.blazon(Arms("Sable", "Quarterly", "Or")) == "Quarterly sable and or"


def test_colour_on_colour_is_warned_of_but_allowed():
    said = arms.warning(Arms("Azure", "Per pale", "Or", "Tower", "Gules"))
    assert (
        said
        == "Gules on azure is colour on colour: heralds would frown, but it's allowed."
    )
    assert arms.warning(Arms("Argent", charge="Star", charge_tincture="Or")) == (
        "Or on argent is metal on metal: heralds would frown, but it's allowed."
    )
    assert "is lost against the field" in arms.warning(
        Arms("Or", charge="Crown", charge_tincture="Or")
    )
    assert arms.warning(Arms("Azure", charge="Tower", charge_tincture="Or")) == ""
    assert arms.warning(Arms("Azure", "Per fess", "Azure")) == (
        "Divided azure and azure is a plain field."
    )


def test_the_shield_is_drawn_from_its_divisions_and_charge():
    shield = Arms("Azure", "Per pale", "Or", "Tower", "Gules")
    grid = arms.pixels(shield, 20)
    assert len(grid) == 24 and all(len(row) == 20 for row in grid)
    # The upper corners are on the shield, the lower ones off it.
    assert grid[0][0] == "Azure" and grid[0][19] == "Or"
    assert grid[23][0] is None and grid[23][19] is None
    # The tower stands in the middle, its door cut out of it.
    assert any(cell == "Gules" for row in grid for cell in row)
    left, top, side = arms.CHARGE_BOX
    door = arms.tincture_at(shield, left + 0.5 * side, top + 0.9 * side)
    assert door in ("Azure", "Or")
    # Every charge and division draws something of its own.
    for charge in arms.CHARGES:
        drawn = arms.pixels(Arms("Azure", charge=charge, charge_tincture="Or"), 20)
        assert any(cell == "Or" for row in drawn for cell in row), charge
    for division in arms.DIVISIONS[1:]:
        drawn = arms.pixels(Arms("Azure", division, "Or"), 20)
        assert any(cell == "Or" for row in drawn for cell in row), division


def test_arms_are_kept_with_the_saga():
    saga = everything_saga()
    keep = saga.covenant("cov1")
    assert keep is not None and arms.arms_of(keep) is None
    keep.arms = Arms(
        "Azure", "Per bend", "Argent", "Tower", "Or", "Per aquas, lux"
    ).to_dict()
    storage.save_saga(saga)
    loaded = storage.load_saga(saga.id)
    found = arms.arms_of(loaded.covenant("cov1"))
    assert found == Arms("Azure", "Per bend", "Argent", "Tower", "Or", "Per aquas, lux")


def test_lords_towns_and_factions_bear_arms():
    saga = everything_saga()
    kinds = {n.kind: arms.bears_arms(n) for n in saga.neighbours}
    assert kinds.get("lord") is True and kinds.get("town") is True
    assert kinds.get("church", False) is False and kinds.get("threat", False) is False
    assert all(arms.bears_arms(c) for c in saga.covenants)


def test_the_form_writes_the_blazon_as_the_choices_are_made():
    saga = everything_saga()
    keep = saga.covenant("cov1")
    form = arms.arms_form(keep)
    assert isinstance(form, Form) and form.title == "Arms of Keep"
    values = {
        "field": "Azure",
        "division": "Per pale",
        "second": "Or",
        "charge": "Tower",
        "charge_tincture": "Gules",
        "motto": " Per aquas, lux ",
    }
    assert form.live is not None and form.picture is not None
    live = form.live(values)
    assert "Per pale azure and or, a tower gules" in live
    assert "colour on colour" in live
    assert form.picture(values) == Arms(
        "Azure", "Per pale", "Or", "Tower", "Gules", "Per aquas, lux"
    )
    form.apply(values)
    assert keep.arms["motto"] == "Per aquas, lux"
    # A blank field takes the arms away.
    form.apply({**values, "field": None})
    assert keep.arms == {} and arms.arms_of(keep) is None
