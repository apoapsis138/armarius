"""Give: what one record holds handed to another, with both Diaries'
lines; gear and silver never go to a laboratory."""

from __future__ import annotations

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import books as bk
from ars_magica_manager import giving, vis
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.models import Character, EnchantedDevice, Possession


def _answer(form: Form, **chosen):
    return {f.key: chosen.get(f.key, f.value) for f in form.fields()}


def _saga():
    saga = _sample_saga_with_covenant()
    saga.characters.append(Character(id="comp1", name="Hugo", type="companion"))
    return saga


def test_gear_splits_when_only_some_is_given():
    saga = _saga()
    magus, companion = saga.characters[0], saga.characters[1]
    magus.inventory = [Possession(id="g1", kind="weapon", name="Spear", quantity=3)]
    form = giving.give(saga, giving.GEAR, magus, magus.inventory[0])
    assert isinstance(form, Form)
    assert form.title == "Give 3 × Spear"
    targets = dict(next(f for f in form.fields() if f.key == "to").options or [])
    # No laboratory takes gear.
    assert not any(value.startswith("laboratory:") for value in targets.values())
    assert form.validate is not None
    assert form.validate(_answer(form, count=4)) == "Leandro has only 3."
    form.apply(_answer(form, count=1, to="character:comp1"))
    assert [(g.name, g.quantity) for g in magus.inventory] == [("Spear", 2)]
    assert [(g.name, g.quantity) for g in companion.inventory] == [("Spear", 1)]
    assert companion.inventory[0].id != "g1"
    assert magus.diary[-1].name == "Gave 1 × Spear to Hugo"
    assert companion.diary[-1].name == "Received 1 × Spear from Leandro"


def test_silver_goes_from_a_purse_into_the_covenants_wealth():
    saga = _saga()
    magus, covenant = saga.characters[0], saga.covenants[0]
    magus.silver = 10
    wealth = covenant.economics.wealth
    form = giving.give(saga, giving.SILVER, magus)
    assert isinstance(form, Form) and form.title == "Give Silver"
    form.apply(_answer(form, count=4, to="covenant:cov1"))
    assert magus.silver == 6
    assert covenant.economics.wealth == wealth + 4
    entry = covenant.diary[-1]
    assert entry.name == "Received 4 pounds of silver from Leandro"
    assert entry.category == "Purchases & Sales" and entry.pounds == 4


def test_a_purse_without_silver_has_none_to_give():
    saga = _saga()
    found = giving.give(saga, giving.SILVER, saga.characters[0])
    assert isinstance(found, Refuse)
    assert giving.blocked(saga, giving.SILVER, saga.characters[0]) is not None


def test_a_book_changes_owner_wherever_it_is_listed():
    saga = _saga()
    book = bk.add_book(saga, "On Flames", "Tractatus")
    book.owner_kind, book.owner_id = "covenant", "cov1"
    gift = giving.gift(saga, giving.BOOK, saga.laboratories[0], book)
    # Listed on a laboratory's page, it is still the covenant's to give.
    assert gift is not None and gift.source is saga.covenants[0]
    form = giving.give_gift(saga, gift)
    assert isinstance(form, Form) and form.title == "Give On Flames"
    form.apply(_answer(form, to="character:comp1"))
    assert (book.owner_kind, book.owner_id) == ("character", "comp1")
    assert saga.covenants[0].diary[-1].category == "Library"


def test_a_device_and_its_epitome_go_together():
    saga = _saga()
    device = EnchantedDevice(
        id="d1", name="Ring of Warmth", holder_kind="character", holder_id="char1"
    )
    saga.enchanted_devices.append(device)
    epitome = bk.add_book(saga, "Epitome of the Ring", "Lab Text")
    epitome.owner_kind, epitome.owner_id = "character", "char1"
    epitome.device_id = "d1"
    gift = giving.gift(saga, giving.DEVICE, None, device)
    assert gift is not None
    form = giving.give_gift(saga, gift)
    assert isinstance(form, Form)
    form.apply(_answer(form, to="laboratory:lab1"))
    assert (device.holder_kind, device.holder_id) == ("laboratory", "lab1")
    assert (epitome.owner_kind, epitome.owner_id) == ("laboratory", "lab1")


def test_vis_goes_only_to_magi_and_places():
    saga = _saga()
    magus = saga.characters[0]
    magus.raw_vis = {"creo": 3}
    held = vis.held(magus)[0]
    takers = giving.receivers(saga, giving.VIS, magus)
    assert saga.characters[1] not in takers
    form = giving.give(saga, giving.VIS, magus, held)
    assert isinstance(form, Form)
    form.apply(_answer(form, count=2, to="laboratory:lab1"))
    assert magus.raw_vis == {"creo": 1}
    assert saga.laboratories[0].raw_vis.get("creo") == 2
