"""Deleting covenants, characters and laboratories (STORY-108): what goes with
them, what's left behind unassigned, and the workspace's confirmed
d key."""

from support import wait_until
from textual.widgets import Tree

from ars_magica_manager import deletion, storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Book,
    Character,
    Covenant,
    Familiar,
    Inhabitant,
    KnownSpell,
    Laboratory,
    Possession,
    Saga,
    Spell,
)
from ars_magica_manager.screens import ConfirmScreen, WorkspaceScreen


def _saga() -> Saga:
    """A covenant with a magus (Familiar, lab, a book, two invented spells --
    one known by a companion), a grog assigned as a Turb member, and a
    covenant book."""
    covenant = Covenant(
        id="cov1",
        saga_id="s",
        name="Dammerstein",
        inhabitants=[
            Inhabitant(id="i1", kind="magus", character_id="magus1", role="Autocrat"),
            Inhabitant(id="i2", kind="turb", name="Hugo", character_id="grog1"),
        ],
        possessions=[
            Possession(id="p1", kind="sanctum", lab_id="lab1", quality=2),
            Possession(id="p2", kind="item", name="Cart"),
        ],
    )
    magus = Character(
        id="magus1",
        name="Aelric",
        type="magus",
        covenant_id="cov1",
        assigned_lab_id="lab1",
        invented_spells=[
            Spell(id="inv1", name="Used Spell", technique="Creo", form="Ignem"),
            Spell(id="inv2", name="Private Spell", technique="Muto", form="Aquam"),
        ],
        spells_known=[KnownSpell(spell_id="inv1"), KnownSpell(spell_id="inv2")],
    )
    companion = Character(
        id="comp1",
        name="Brother Anselm",
        type="companion",
        covenant_id="cov1",
        spells_known=[KnownSpell(spell_id="inv1")],
    )
    grog = Character(id="grog1", name="Hugo", type="grog", covenant_id="cov1")
    lab = Laboratory(id="lab1", covenant_id="cov1", name="Tower", owner_id="magus1")
    return Saga(
        id="s",
        name="Saga",
        covenants=[covenant],
        characters=[magus, companion, grog],
        laboratories=[lab],
        familiars=[Familiar(id="fam1", character_id="magus1", name="Ashwing")],
        books=[
            Book(
                id="b1",
                name="Notes",
                type="Other",
                owner_kind="character",
                owner_id="magus1",
            ),
            Book(
                id="b2",
                name="Lab Journal",
                type="Other",
                owner_kind="laboratory",
                owner_id="lab1",
            ),
            Book(
                id="b3",
                name="Charter",
                type="Other",
                owner_kind="covenant",
                owner_id="cov1",
            ),
        ],
    )


# ------------------------------------------------------------------ character


def test_deleting_a_magus_takes_their_familiar_and_frees_their_lab():
    saga = _saga()
    deletion.delete_character(saga, saga.characters[0])

    assert [c.id for c in saga.characters] == ["comp1", "grog1"]
    assert saga.familiars == []
    assert saga.laboratories[0].owner_id is None


def test_deleting_a_character_unassigns_their_books():
    saga = _saga()
    deletion.delete_character(saga, saga.characters[0])

    book = saga.books[0]
    assert (book.owner_kind, book.owner_id) == (None, None)


def test_deleting_a_magus_drops_their_covenant_extras():
    saga = _saga()
    deletion.delete_character(saga, saga.characters[0])

    assert [r.id for r in saga.covenants[0].inhabitants] == ["i2"]


def test_deleting_a_grog_keeps_their_inhabitant_entry_unlinked():
    saga = _saga()
    deletion.delete_character(saga, saga.character("grog1"))

    record = saga.covenants[0].inhabitants[1]
    assert (record.name, record.character_id) == ("Hugo", None)


def test_invented_spells_someone_else_knows_move_to_the_saga():
    saga = _saga()
    deletion.delete_character(saga, saga.characters[0])

    assert [s.id for s in saga.spells] == ["inv1"]


def test_an_invented_spell_on_a_lab_text_moves_to_the_saga():
    saga = _saga()
    saga.books.append(Book(id="b9", name="Text", type="Lab Text", spell_id="inv2"))
    deletion.delete_character(saga, saga.characters[0])

    assert [s.id for s in saga.spells] == ["inv1", "inv2"]


def test_character_consequences_say_what_happens():
    saga = _saga()
    assert deletion.character_consequences(saga, saga.characters[0]) == [
        "Their Familiar, Ashwing, is deleted too.",
        "Tower no longer has an owner.",
        "1 book they own becomes unassigned.",
        "1 invented spell still in use moves to the saga's own spells.",
    ]


# ----------------------------------------------------------------- laboratory


def test_deleting_a_laboratory_frees_its_owner_books_and_sanctum_entry():
    saga = _saga()
    deletion.delete_laboratory(saga, saga.laboratories[0])

    assert saga.laboratories == []
    assert saga.characters[0].assigned_lab_id is None
    assert (saga.books[1].owner_kind, saga.books[1].owner_id) == (None, None)
    assert [p.id for p in saga.covenants[0].possessions] == ["p2"]


def test_laboratory_consequences_say_what_happens():
    saga = _saga()
    assert deletion.laboratory_consequences(saga, saga.laboratories[0]) == [
        "Aelric no longer has a laboratory.",
        "1 book kept there becomes unassigned.",
    ]


# ------------------------------------------------------------------- covenant


def test_deleting_a_covenant_leaves_its_characters_labs_and_books_unassigned():
    saga = _saga()
    deletion.delete_covenant(saga, saga.covenants[0])

    assert saga.covenants == []
    assert {c.covenant_id for c in saga.characters} == {None}
    assert saga.laboratories[0].covenant_id is None
    assert (saga.books[2].owner_kind, saga.books[2].owner_id) == (None, None)
    # Books its members own stay theirs.
    assert saga.books[0].owner_id == "magus1"
    assert saga.books[1].owner_id == "lab1"


def test_covenant_consequences_say_what_happens():
    saga = _saga()
    assert deletion.covenant_consequences(saga, saga.covenants[0]) == [
        "3 characters become unassigned.",
        "1 laboratory becomes unassigned.",
        "1 book it owns becomes unassigned.",
        "Its Inhabitants, Possessions and Economics entries are deleted with it.",
    ]


# ------------------------------------------------------------------ workspace


async def _open(pilot, app, data) -> None:
    await pilot.press("enter")  # picker -> workspace
    await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    tree = app.screen.query_one("#nav-tree", Tree)
    node = next(n for n in _walk(tree.root) if n.data == data)
    tree.select_node(node)
    await wait_until(pilot, lambda: app.screen.selected_kind == data[0])
    await pilot.pause()


def _walk(node):
    yield node
    for child in node.children:
        yield from _walk(child)


async def test_d_deletes_the_selected_character_after_confirming():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open(pilot, app, ("character", "magus1"))
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        await wait_until(pilot, lambda: app.screen.selected_kind == "saga")

        saved = storage.load_saga("s")
        assert [c.id for c in saved.characters] == ["comp1", "grog1"]
        assert saved.familiars == []
        tree = app.screen.query_one("#nav-tree", Tree)
        assert not any(n.data == ("character", "magus1") for n in _walk(tree.root))


async def test_answering_no_keeps_the_covenant():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open(pilot, app, ("covenant", "cov1"))
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("n")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

        assert [c.id for c in storage.load_saga("s").covenants] == ["cov1"]


async def test_deleting_is_only_offered_for_covenants_characters_and_laboratories():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open(pilot, app, ("familiar", "fam1"))
        assert app.screen.check_action("delete_record", ()) is False
        await _select(app, pilot, ("laboratory", "lab1"))
        assert app.screen.check_action("delete_record", ()) is True


async def _select(app, pilot, data) -> None:
    tree = app.screen.query_one("#nav-tree", Tree)
    tree.select_node(next(n for n in _walk(tree.root) if n.data == data))
    await wait_until(pilot, lambda: app.screen.selected_kind == data[0])
    await pilot.pause()
