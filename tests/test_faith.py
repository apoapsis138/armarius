"""True Faith Score and Faith Points (STORY-210)."""

from support import wait_until
from textual.widgets import Input, Static

from ars_magica_manager import faith, storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import Character, Saga, VirtueFlawInstance
from ars_magica_manager.screens import FieldsDialog, WorkspaceScreen


def _believer(**background) -> Character:
    character = Character(
        id="c1",
        name="Brother Anselm",
        type="companion",
        virtues_flaws=[VirtueFlawInstance(vf_id=faith.TRUE_FAITH_ID)],
    )
    for key, value in background.items():
        setattr(character.background, key, value)
    return character


def test_old_saves_load_with_no_faith():
    character = Character.from_dict({"id": "c", "name": "C", "type": "grog"})
    assert (
        character.background.true_faith_score,
        character.background.faith_points,
    ) == (0, 0)


def test_the_sheet_shows_faith_for_the_virtue_or_any_points():
    assert faith.shows_faith(_believer())
    grog = Character(id="g", name="Hugo", type="grog")
    assert not faith.shows_faith(grog)
    grog.background.faith_points = 1  # from a pilgrimage
    assert faith.shows_faith(grog)


def test_warnings():
    believer = _believer()
    assert faith.faith_warnings(believer, 1, "companion") == []
    assert faith.faith_warnings(believer, 2, "companion") == [
        "A True Faith Score of 2 or more is for a Mythic Companion."
    ]
    assert faith.faith_warnings(believer, 3, "mythic companion") == []
    grog = Character(id="g", name="Hugo", type="grog")
    assert faith.faith_warnings(grog, 1, "grog") == [
        "Only a character with the True Faith Virtue has a Score."
    ]
    assert faith.faith_warnings(grog, 0, "grog") == []


async def test_edit_warns_but_saves_and_the_sheet_shows_it():
    saga = Saga(id="s", name="S", characters=[_believer(true_faith_score=1)])
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.press("enter")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        tree = app.screen.query_one("#nav-tree")
        node = next(
            n for n in tree.root.children[0].children if n.data == ("character", "c1")
        )
        tree.select_node(node)
        await wait_until(pilot, lambda: app.screen._character_sheet_view is not None)
        await pilot.pause()
        info = app.screen._character_sheet_view
        assert "True Faith Score" in str(
            info.query_one("#char-info-right", Static).render()
        )

        app.screen._edit_character_info()
        await wait_until(
            pilot,
            lambda: isinstance(app.screen, FieldsDialog) and app.screen.is_mounted,
        )
        await pilot.pause()
        app.screen.query_one("#fld-true_faith_score", Input).value = "2"
        await pilot.pause()
        live = str(app.screen.query_one("#fields-live", Static).render())
        assert "Mythic Companion" in live
        app.screen.query_one("#btn-save").press()
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

        assert storage.load_saga("s").characters[0].background.true_faith_score == 2
