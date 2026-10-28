"""A stay as a guest at another covenant: Stay as Guest, the host's Guests
list, the aura his casting counts, the host's library open to him, and
Pay the Fee (DE pp. 381, 518; Guardians of the Forests p. 20)."""

from __future__ import annotations

from dataclasses import asdict

import pytest
from support import everything_saga

from ars_magica_manager import books, deletion, guest_stays
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import whereabouts
from ars_magica_manager.models import (
    FEE_NONE,
    FEE_SERVICE,
    FEE_SILVER,
    FEE_VIS,
    Character,
    GuestStay,
)
from ars_magica_manager.rules import hospitality, realms
from ars_magica_manager.rules.library import can_read


def _saga():
    """The sample saga: Severinus of Fengheld, with Vim vis and silver,
    and Keep (a Rhine covenant) with an aura of its own."""
    saga = everything_saga()
    guest = next(c for c in saga.characters if c.id == "mag_sketch")
    guest.raw_vis = {"vim": 5}
    guest.silver = 10
    host = saga.covenant("cov1")
    assert host is not None
    host.aura = 4
    home = saga.covenant("cov_sketch")
    assert home is not None
    home.aura = 1
    return saga, guest, host


def _values(form: Form, **changes: object) -> dict[str, object]:
    values = {f.key: f.value for f in form.fields()}
    values.update(changes)
    return values


def _stay(saga, guest: Character, **changes: object) -> list[str]:
    form = guest_stays.stay_form(saga, guest)
    assert isinstance(form, Form)
    values = _values(form, **changes)
    assert form.validate is not None
    problem = form.validate(values)
    assert problem is None, problem
    return form.apply(values)


def test_a_rhine_host_fills_in_the_peripheral_code_s_terms():
    saga, guest, host = _saga()
    form = guest_stays.stay_form(saga, guest)
    assert isinstance(form, Form)
    host_field = next(f for f in form.fields() if f.key == "host")
    assert host_field.fills is not None
    filled = host_field.fills({"host": host.id, "year": 1220})
    assert filled == {
        "fee_kind": FEE_VIS,
        "fee": 3,
        "laboratory": False,
        "until_year": 1222,
    }


def test_a_rhine_stay_is_three_to_seven_years():
    saga, guest, host = _saga()
    form = guest_stays.stay_form(saga, guest)
    assert isinstance(form, Form) and form.validate is not None
    year = saga.current_year
    short = _values(form, host=host.id, year=year, until_year=year + 1)
    assert "at least 3 years" in (form.validate(short) or "")
    long = _values(form, host=host.id, year=year, until_year=year + 7)
    assert "at most 7 years" in (form.validate(long) or "")
    assert form.validate(_values(form, host=host.id, until_year=year + 6)) is None


def test_another_tribunal_s_host_asks_no_terms():
    saga, guest, host = _saga()
    host.tribunal_id = "normandy"
    assert guest_stays.host_terms(saga, host) is None
    form = guest_stays.stay_form(saga, guest)
    assert isinstance(form, Form) and form.validate is not None
    values = _values(form, host=host.id, until_year=saga.current_year)
    assert form.validate(values) is None


def test_staying_writes_both_diaries_and_lists_the_guest():
    saga, guest, host = _saga()
    _stay(saga, guest, host=host.id, fee_kind=FEE_VIS, fee=3)
    assert guest.stay is not None and guest.stay.host_id == host.id
    assert guest_stays.guests(saga, host) == [guest]
    assert guest_stays.title(saga, host) == "Guests (1)"
    assert guest.diary[-1].name.startswith(f"A guest at {host.name}")
    assert host.diary[-1].name.startswith(f"{guest.name} came as a guest")
    row = guest_stays.grid(saga, host).rows[0]
    assert row[0] == guest.name and row[3] == "3 pawns of vis a year"
    assert row[4] == "Due"


def test_leaving_ends_the_stay_in_both_diaries():
    saga, guest, host = _saga()
    _stay(saga, guest, host=host.id)
    _stay(saga, guest, host=guest_stays.NOT_A_GUEST)
    assert guest.stay is None
    assert guest_stays.guests(saga, host) == []
    assert "Left" in guest.diary[-1].name
    assert "ended" in host.diary[-1].name


def test_a_guest_casts_in_the_host_s_aura_unless_he_is_elsewhere():
    saga, guest, host = _saga()
    assert realms.present_aura(saga, guest) == (1, "Magic")
    _stay(saga, guest, host=host.id)
    assert realms.present_aura(saga, guest)[0] == realms.aura_of(host)[0]
    assert whereabouts.where_line(saga, guest).startswith(f"A guest at {host.name}")
    guest.away_aura, guest.away_realm = 2, "Faerie"
    assert realms.present_aura(saga, guest) == (2, "Faerie")
    # His home, for seasons, aging and warping, is still his own covenant.
    assert realms.home_aura(saga, guest)[0] == 1


def test_the_host_s_library_opens_to_a_guest_with_its_use():
    saga, guest, host = _saga()
    book = next(b for b in saga.books if b.id == "b-cov")
    assert not can_read(saga, guest, book)
    _stay(saga, guest, host=host.id, library=False)
    assert not can_read(saga, guest, book)
    _stay(saga, guest, host=host.id, library=True)
    assert can_read(saga, guest, book)
    assert book in books.studyable_books(saga, guest)


def test_paying_the_fee_in_vis_gives_it_to_the_host():
    saga, guest, host = _saga()
    _stay(saga, guest, host=host.id, fee_kind=FEE_VIS, fee=3)
    assert guest_stays.can_pay(saga, host, 0)
    form = guest_stays.pay_form(saga, host, 0)
    assert isinstance(form, Form)
    values = _values(form)
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    assert guest.raw_vis.get("vim") == 2
    stay = guest.stay
    assert stay is not None and saga.current_year in stay.paid
    assert not guest_stays.can_pay(saga, host, 0)
    assert guest_stays.grid(saga, host).rows[0][4] == "Paid"
    assert isinstance(guest_stays.pay_form(saga, host, 0), Refuse)


def test_a_fee_he_can_t_cover_is_refused():
    saga, guest, host = _saga()
    _stay(saga, guest, host=host.id, fee_kind=FEE_SILVER, fee=30)
    form = guest_stays.pay_form(saga, host, 0)
    assert isinstance(form, Form) and form.validate is not None
    assert "only 10" in (form.validate(_values(form)) or "")
    guest.raw_vis = {}
    _stay(saga, guest, host=host.id, fee_kind=FEE_VIS, fee=3)
    assert isinstance(guest_stays.pay_form(saga, host, 0), Refuse)


def test_service_is_written_in_both_diaries():
    saga, guest, host = _saga()
    _stay(saga, guest, host=host.id, fee_kind=FEE_SERVICE, fee=1)
    form = guest_stays.pay_form(saga, host, 0)
    assert isinstance(form, Form)
    form.apply({"service": "Warded the granary"})
    assert "Warded the granary" in guest.diary[-1].name
    assert "Warded the granary" in host.diary[-1].name
    assert guest.stay is not None and guest.stay.paid == [saga.current_year]


def test_no_fee_is_never_due():
    stay = GuestStay("cov1", year=1220, fee_kind=FEE_NONE)
    assert not hospitality.due(stay, 1220)
    assert hospitality.fee_words(stay) == "No fee"


def test_a_fee_is_due_only_in_the_years_of_the_stay():
    stay = GuestStay("cov1", year=1220, until_year=1222, fee_kind=FEE_VIS, fee=3)
    assert not hospitality.due(stay, 1219)
    assert hospitality.due(stay, 1222)
    assert not hospitality.due(stay, 1223)


def test_a_stay_saves_and_loads():
    stay = GuestStay("cov1", 1220, "Spring", 1222, FEE_VIS, 3, True, False, "", [1220])
    assert GuestStay.from_dict(asdict(stay)) == stay


def test_a_bad_stay_in_a_save_is_reported():
    with pytest.raises(ValueError, match="kind of fee"):
        GuestStay.from_dict({"host_id": "cov1", "fee_kind": "goats"})
    with pytest.raises(ValueError, match="no host"):
        GuestStay.from_dict({"fee": 3})


def test_deleting_the_host_ends_the_stay():
    saga, guest, host = _saga()
    _stay(saga, guest, host=host.id)
    deletion.delete_covenant(saga, host)
    assert guest.stay is None
