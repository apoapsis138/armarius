"""New covenfolk dilute Familiarity, then grow used to the Gift
(Covenants pp. 37, 40); Recruit and Depart keep each line's arrivals."""

from dataclasses import asdict

from ars_magica_manager import inhabitants as inh
from ars_magica_manager.forms import inhabitant as forms
from ars_magica_manager.models import Arrival, Covenant, Inhabitant, Saga
from ars_magica_manager.rules import covenfolk


def _saga(year: int = 1220) -> tuple[Saga, Covenant]:
    covenant = Covenant("cov1", "s1", "Fengheld", year_founded=1180)
    covenant.inhabitants = [
        Inhabitant(id="m", kind="magus", name="Gifted", gift="The Gift"),
        Inhabitant(id="t", kind="turb", name="Turb", quantity=10),
    ]
    return Saga("s1", "Test", current_year=year, covenants=[covenant]), covenant


def _turb(saga: Saga, covenant: Covenant) -> covenfolk.InhabitantEntry:
    return covenfolk.entries_for_kind(saga, covenant, "turb")[0]


def test_an_old_household_has_its_full_familiarity():
    saga, covenant = _saga()
    assert inh.familiarity(saga, covenant) == 30  # capped at the Gift's -30


def test_doubling_the_covenfolk_halves_it():
    saga, covenant = _saga()
    covenant.inhabitants[1].quantity = 20
    covenant.inhabitants[1].arrivals = [Arrival(10, 1220)]
    assert inh.familiarity(saga, covenant) == 15
    assert inh.newcomers(saga, covenant) == (10, 20)


def test_newcomers_grow_used_to_the_gift_two_a_year():
    saga, covenant = _saga(1225)
    covenant.inhabitants[1].quantity = 20
    covenant.inhabitants[1].arrivals = [Arrival(10, 1220)]
    assert inh.familiarity(saga, covenant) == 20  # (10 x 30 + 10 x 10) / 20
    saga.current_year = 1235
    assert inh.familiarity(saga, covenant) == 30
    assert inh.newcomers(saga, covenant) == (0, 20)


def test_recruit_adds_an_arrival_and_the_inspector_lists_them():
    saga, covenant = _saga()
    form = forms.recruit_form(saga, covenant, _turb(saga, covenant))
    form.apply({"count": 2, "year": 1220, "note": "From the village"})
    record = covenant.inhabitants[1]
    assert (record.quantity, record.arrivals) == (12, [Arrival(2, 1220)])
    text = inh.arrival_text(saga, covenant, _turb(saga, covenant))
    assert "10 here since the founding (1180)" in text
    assert "2 joined 1220, still growing used to the Gift (0 of 30" in text
    assert covenant.diary[-1].category == "Inhabitants"


def test_depart_takes_from_the_group_chosen():
    saga, covenant = _saga()
    record = covenant.inhabitants[1]
    record.quantity, record.arrivals = 12, [Arrival(2, 1220)]
    form = forms.depart_form(saga, covenant, _turb(saga, covenant))
    assert form.validate is not None
    assert form.validate({"group": "0", "count": 3, "why": ""})  # only 2 came then
    form.apply({"group": "founding", "count": 1, "why": "Died of old age"})
    assert (record.quantity, record.arrivals) == (11, [Arrival(2, 1220)])
    form = forms.depart_form(saga, covenant, _turb(saga, covenant))
    form.apply({"group": "0", "count": 2, "why": "Ran off"})
    assert (record.quantity, record.arrivals) == (9, [])


def test_a_line_everyone_leaves_is_removed():
    saga, covenant = _saga()
    covenant.inhabitants[1].quantity = 1
    form = forms.depart_form(saga, covenant, _turb(saga, covenant))
    form.apply({"group": "founding", "count": 1, "why": ""})
    assert [r.kind for r in covenant.inhabitants] == ["magus"]


def test_quantity_cannot_drop_below_the_recorded_arrivals():
    saga, covenant = _saga()
    covenant.inhabitants[1].arrivals = [Arrival(4, 1220)]
    form = forms.inhabitant_form(covenant, "turb", _turb(saga, covenant))
    assert form.validate is not None
    assert "Depart" in (form.validate({"quantity": 3}) or "")


def test_arrivals_survive_a_save():
    covenant = Covenant("cov1", "s1", "F")
    covenant.inhabitants = [
        Inhabitant(id="t", kind="turb", quantity=3, arrivals=[Arrival(1, 1220)])
    ]
    loaded = Covenant.from_dict(asdict(covenant))
    assert loaded.inhabitants[0].arrivals == [Arrival(1, 1220)]
