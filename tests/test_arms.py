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
    assert arms.blazon(Arms("Gules", charge="Crown", count=3)) == (
        "Gules, three crowns or"
    )
    assert arms.blazon(Arms("Or", charge="Eagle", charge_tincture="Sable")) == (
        "Or, an eagle sable"
    )
    assert arms.blazon(Arms("Azure", charge="Fleur-de-lis", count=2)) == (
        "Azure, two fleurs-de-lis or"
    )
    assert arms.blazon(
        Arms("Argent", charge="Cross", count=2, charge_tincture="Gules")
    ) == ("Argent, two crosses gules")
    knotted = Arms("Gules", charge="Lion, tail knotted")
    assert arms.blazon(knotted) == "Gules, a lion queue-nowed or"
    assert arms.blazon(Arms("Vert", charge="Lion, tail knotted", count=3)) == (
        "Vert, three lions queue-nowed or"
    )


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
    # The tower stands in the middle.
    left, top, side = arms.CHARGE_BOX
    assert arms.tincture_at(shield, left + 0.5 * side, top + 0.5 * side) == "Gules"
    # Every charge and division draws something of its own.
    for charge in arms.CHARGES:
        drawn = arms.pixels(Arms("Azure", charge=charge, charge_tincture="Or"), 20)
        assert any(cell == "Or" for row in drawn for cell in row), charge
    for division in arms.DIVISIONS[1:]:
        drawn = arms.pixels(Arms("Azure", division, "Or"), 20)
        assert any(cell == "Or" for row in drawn for cell in row), division


def test_ermine_a_bend_bendy_and_checky():
    assert arms.blazon(Arms("Ermine")) == "Ermine"
    assert arms.blazon(Arms("Or", "Checky", "Azure")) == "Checky or and azure"
    assert arms.blazon(Arms("Or", "Bendy", "Azure")) == "Bendy or and azure"
    assert arms.blazon(Arms("Azure", charge="Bend", charge_tincture="Argent")) == (
        "Azure, a bend argent"
    )
    # Ermine is painted argent with sable tails.
    ermine = {c for row in arms.pixels(Arms("Ermine"), 40) for c in row} - {None}
    assert ermine == {"Argent", "Sable"}
    # A fur is neither metal nor colour: the rule of tincture leaves it be.
    assert arms.warning(Arms("Ermine", charge="Bend", charge_tincture="Gules")) == ""
    assert arms.warning(Arms("Gules", charge="Lion", charge_tincture="Ermine")) == ""
    # A bend crosses the shield from its top left to its bottom right.
    bend = Arms("Azure", charge="Bend", charge_tincture="Argent")
    assert arms.tincture_at(bend, 0.1, 0.12) == "Argent"
    assert arms.tincture_at(bend, 0.75, 0.9) == "Argent"
    assert arms.tincture_at(bend, 0.9, 0.1) == "Azure"
    # An ordinary is borne once, whatever a save or the form says.
    assert Arms.from_dict({"field": "Azure", "charge": "Bend", "count": 3}).count == 1
    values = {"field": "Azure", "charge": "Bend", "count": "3"}
    assert arms.from_values(values) == Arms("Azure", charge="Bend")
    count = next(f for f in arms.arms_fields(None) if f.key == "count")
    assert count.show_if is not None and not count.show_if(values)


def _spots(drawn: list[list[str | None]], tincture: str) -> int:
    """How many separate runs of `tincture` its fullest row holds."""
    row = max(drawn, key=lambda r: r.count(tincture))
    return sum(
        1
        for i, cell in enumerate(row)
        if cell == tincture and (i == 0 or row[i - 1] != tincture)
    )


def test_two_or_three_charges_are_placed_as_heralds_place_them():
    one = arms.pixels(Arms("Azure", charge="Crown", count=1), 30)
    two = arms.pixels(Arms("Azure", charge="Crown", count=2), 30)
    three = arms.pixels(Arms("Azure", charge="Crown", count=3), 30)
    assert _spots(one, "Or") == 1 and _spots(two, "Or") == 2
    # Three: two above, and one below them in the middle.
    assert _spots(three, "Or") == 2
    rows = [r for r, row in enumerate(three) if "Or" in row]
    lower = three[rows[-1]]
    assert lower.index("Or") > 8 and len(lower) - 1 - lower[::-1].index("Or") < 22
    assert len(arms.charge_boxes(Arms(count=3))) == 3
    # A save without a count, or with a bad one, bears one charge.
    assert arms.Arms.from_dict({"field": "Azure", "charge": "Tower"}) == Arms(
        "Azure", charge="Tower"
    )
    assert arms.Arms.from_dict({"field": "Azure", "count": 7}).count == 1


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


def test_lords_towns_churches_and_factions_bear_arms():
    saga = everything_saga()
    kinds = {n.kind: arms.bears_arms(n) for n in saga.neighbours}
    assert kinds.get("lord") is True and kinds.get("town") is True
    assert kinds.get("church") is True
    assert kinds.get("threat", False) is False and kinds.get("place", False) is False
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
        "count": 3,
    }
    assert form.live is not None and form.picture is not None
    live = form.live(values)
    assert "Per pale azure and or, three towers gules" in live
    assert "colour on colour" in live
    # The motto is the bearer's own words: it leads, the blazon under it.
    assert live.index("Per aquas, lux") < live.index("Per pale azure")
    assert form.picture(values) == Arms(
        "Azure", "Per pale", "Or", "Tower", "Gules", "Per aquas, lux", 3
    )
    form.apply(values)
    assert keep.arms["motto"] == "Per aquas, lux" and keep.arms["count"] == 3
    # With no charge the count means nothing and is one.
    assert arms.from_values({**values, "charge": None}) == Arms(
        "Azure", "Per pale", "Or", "", "Gules", "Per aquas, lux"
    )
    # A blank field takes the arms away.
    form.apply({**values, "field": None})
    assert keep.arms == {} and arms.arms_of(keep) is None
