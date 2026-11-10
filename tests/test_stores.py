"""The Armarium and the Custodia Mirabilium (stores.py): every book and
device in the saga, held or unassigned; their filter, their Add, Edit and
Delete (forms/stores.py), and Give from nobody (giving.py)."""

from __future__ import annotations

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import books as bk
from ars_magica_manager import giving, stores, viewing
from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.forms import device as device_forms
from ars_magica_manager.forms import stores as store_forms
from ars_magica_manager.models import (
    Book,
    EnchantedDevice,
    InstilledEffect,
    Saga,
)

ARMARIUM = stores.STORES[stores.ARMARIUM]
CUSTODIA = stores.STORES[stores.CUSTODIA]


def _saga() -> Saga:
    saga = _sample_saga_with_covenant()
    # Only these: the sample's own books and devices aside.
    saga.books = [
        Book(
            id="b1",
            name="On Flames",
            type="Tractatus",
            owner_kind="covenant",
            owner_id="cov1",
        ),
        Book(id="b2", name="A Lost Summa", type="Art Summa", art="Ignem"),
    ]
    saga.codices = []
    saga.enchanted_devices = [
        EnchantedDevice(
            id="d1",
            name="Wand of Flames",
            holder_kind="character",
            holder_id=saga.characters[0].id,
            effects=[
                InstilledEffect(id="e1", name="Pilum of Fire"),
                InstilledEffect(id="e2", name="Ward against Heat"),
                InstilledEffect(id="e3", name="Light"),
            ],
        ),
        EnchantedDevice(
            id="d2", name="The Buried Ring", talisman=True, type="Invested Device"
        ),
    ]
    return saga


def _answer(form: Form, **chosen: object) -> dict[str, object]:
    return {f.key: chosen.get(f.key, f.value) for f in form.fields()}


def test_a_store_lists_every_item_with_its_holder_or_unassigned():
    saga = _saga()
    rows = stores.grid(saga, ARMARIUM, stores.shown(saga, ARMARIUM)).rows
    assert [(r[0], r[3]) for r in rows] == [
        ("On Flames", saga.covenants[0].name),
        ("A Lost Summa", "Unassigned"),
    ]
    devices = stores.grid(saga, CUSTODIA, stores.shown(saga, CUSTODIA)).rows
    # The first effect and how many more; a talisman says so.
    assert devices == [
        [
            "Wand of Flames",
            "Invested",
            "Pilum of Fire +2 more",
            saga.characters[0].name,
        ],
        ["The Buried Ring", "Talisman", "-", "Unassigned"],
    ]


def test_a_codex_volume_names_its_codex():
    saga = _saga()
    codex = bk.new_codex(saga, "The Red Codex")
    for book in saga.books:
        book.codex_id = codex.id
    names = [row[0] for row in stores.grid(saga, ARMARIUM, saga.books).rows]
    assert names == ["On Flames (in The Red Codex)", "A Lost Summa (in The Red Codex)"]


def test_the_filter_narrows_by_holder_unassigned_and_type():
    saga = _saga()
    cov = f"covenant:{saga.covenants[0].id}"
    assert [b.id for b in stores.shown(saga, ARMARIUM, stores.Filter(cov))] == ["b1"]
    unassigned = stores.Filter(stores.UNASSIGNED)
    assert [b.id for b in stores.shown(saga, ARMARIUM, unassigned)] == ["b2"]
    summae = stores.Filter(kind="Art Summa")
    assert [b.id for b in stores.shown(saga, ARMARIUM, summae)] == ["b2"]
    listed = stores.shown(saga, ARMARIUM, summae)
    assert stores.title(saga, ARMARIUM, listed) == "Books (1 of 2)"
    # Only those who hold something are offered.
    choices = stores.holder_choices(saga, ARMARIUM)
    assert choices == [
        ("All holders", ""),
        ("Unassigned", stores.UNASSIGNED),
        (f"Covenant: {saga.covenants[0].name}", cov),
    ]


def test_add_makes_an_item_with_no_holder():
    saga = _saga()
    ops = store_forms.store_ops(saga, ARMARIUM, lambda: saga.books)
    assert ops.add is not None
    form = ops.add()
    assert isinstance(form, Form)
    owner = next(f for f in form.fields() if f.key == "owner")
    assert owner.value == ""
    form.apply(_answer(form, name="Found in the Tower", type="Tractatus"))
    assert bk.is_unassigned(saga, saga.books[-1])

    devices = store_forms.store_ops(saga, CUSTODIA, lambda: saga.enchanted_devices)
    assert devices.add is not None
    form = devices.add()
    assert isinstance(form, Form)
    holder = next(f for f in form.fields() if f.key == "holder")
    assert holder.value == ""
    assert (device_forms.NO_HOLDER, "") in (holder.options or [])
    form.apply(_answer(form, name="A Wand Nobody Holds"))
    assert saga.enchanted_devices[-1].holder_kind is None


def test_edit_to_no_holder_sets_an_item_down():
    saga = _saga()
    ops = store_forms.store_ops(saga, CUSTODIA, lambda: saga.enchanted_devices)
    assert ops.edit is not None
    form = ops.edit(0)
    assert isinstance(form, Form)
    form.apply(_answer(form, holder=""))
    wand = saga.enchanted_devices[0]
    assert (wand.holder_kind, wand.holder_id) == (None, None)
    # Nothing is written in anyone's Diary.
    assert not saga.characters[0].diary


def test_delete_names_the_holder_of_a_held_item():
    saga = _saga()
    ops = store_forms.store_ops(saga, CUSTODIA, lambda: saga.enchanted_devices)
    assert ops.remove is not None
    held = ops.remove(0)
    assert isinstance(held, Confirm)
    assert held.question == (
        f"Delete Wand of Flames, held by {saga.characters[0].name} and its 3 effects?"
    )
    loose = ops.remove(1)
    assert isinstance(loose, Confirm) and loose.question == "Delete The Buried Ring?"
    loose.apply()
    assert [d.id for d in saga.enchanted_devices] == ["d1"]


def test_give_from_nobody_writes_only_the_receivers_diary():
    saga = _saga()
    ring = saga.enchanted_devices[1]
    found = giving.gift(saga, giving.DEVICE, None, ring)
    assert found is not None and found.source is None
    form = giving.give_gift(saga, found)
    assert isinstance(form, Form)
    shown = {f.key: f.value for f in form.fields()}
    assert shown["_what"] == "Unassigned (The Buried Ring)"
    magus = saga.characters[0]
    form.apply(_answer(form, to=f"character:{magus.id}"))
    assert (ring.holder_kind, ring.holder_id) == ("character", magus.id)
    # A talisman keeps its mark.
    assert ring.talisman
    assert magus.diary[-1].name == "Received The Buried Ring"


def test_giving_one_volume_moves_its_codex_and_says_so():
    saga = _saga()
    codex = bk.new_codex(saga, "The Red Codex")
    for book in saga.books:
        book.codex_id = codex.id
        book.owner_kind, book.owner_id = None, None
    form = giving.give_gift(saga, giving.gift(saga, giving.BOOK, None, saga.books[0]))
    assert isinstance(form, Form)
    shown = {f.key: f.value for f in form.fields()}
    assert shown["_codex"] == "Bound in The Red Codex: its 2 books go together."
    covenant = saga.covenants[0]
    form.apply(_answer(form, to=f"covenant:{covenant.id}"))
    assert {(b.owner_kind, b.owner_id) for b in saga.books} == {
        ("covenant", covenant.id)
    }
    assert covenant.diary[-1].name == "Received On Flames"


def test_the_stores_are_the_storyguides_alone():
    saga = _saga()
    assert viewing.reads(part=ARMARIUM.section)
    viewing.use(viewing.TABLE_VIEWER, saga)
    assert not viewing.reads(part=ARMARIUM.section)
    assert not viewing.reads(part=CUSTODIA.section)
