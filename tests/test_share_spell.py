"""Making a magus's invented spell available to the saga (STORY-608)."""

from __future__ import annotations

from support import wait_until
from test_list_flows import ListCase, _open

from ars_magica_manager import spells as spl
from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import Book, Character, Covenant, KnownSpell, Saga
from ars_magica_manager.screens import ConfirmScreen


def _saga() -> tuple[Saga, Character]:
    saga = Saga(
        id="test_saga",
        name="Saga",
        covenants=[Covenant(id="cov1", saga_id="test_saga", name="Keep")],
    )
    magus = Character(id="mag1", name="Leandro", type="magus", covenant_id="cov1")
    saga.characters.append(magus)
    spark = spl.add_invented_spell(saga, magus, "Spark of Wit", "Creo", "Mentem")
    spark.level = 10
    magus.spells_known.append(KnownSpell(spell_id=spark.id))
    # A design he hasn't finished inventing: not his to share yet.
    spl.add_invented_spell(saga, magus, "Half an Idea", "Muto", "Vim")
    saga.books.append(Book(id="b1", name="Notes", type="Lab Text", spell_id=spark.id))
    return saga, magus


def test_only_invented_spells_the_magus_knows_can_be_shared():
    _, magus = _saga()
    assert [s.name for s in spl.shareable_spells(magus)] == ["Spark of Wit"]


def test_sharing_moves_the_spell_to_the_saga_and_keeps_every_link():
    saga, magus = _saga()
    [spark] = spl.shareable_spells(magus)
    spl.share_invented_spell(saga, magus, spark)
    assert [s.name for s in magus.invented_spells] == ["Half an Idea"]
    assert [s.name for s in saga.spells] == ["Spark of Wit"]
    assert spark.source == "Invented by Leandro"
    # Same id: he still knows it, and his Lab Text still points at it.
    assert spl.find_spell(saga, magus.spells_known[0].spell_id) is spark
    assert spl.find_spell(saga, saga.books[0].spell_id) is spark
    assert spl.is_own(saga, spark)
    assert spl.shareable_spells(magus) == []


async def test_s_on_known_spells_shares_the_spell_after_asking():
    saga, _ = _saga()
    storage.save_saga(saga)
    case = ListCase(
        ("character", "mag1"),
        "section-known-spells",
        "section-known-spells-list",
        lambda s: s.characters[0].spells_known,
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, _ = await _open(pilot, app, case)
        assert workspace.check_action("share_spell", ())
        await pilot.press("s")  # one shareable spell: no picker
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("n")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert storage.load_saga("test_saga").spells == []
        await pilot.press("s")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: (
                [s.name for s in storage.load_saga("test_saga").spells]
                == ["Spark of Wit"]
            ),
        )
        # Nothing left to share: the key is off again.
        assert await wait_until(
            pilot, lambda: not workspace.check_action("share_spell", ())
        )
    saved = storage.load_saga("test_saga")
    assert [k.spell_id for k in saved.characters[0].spells_known] == [
        saved.spells[0].id
    ]
