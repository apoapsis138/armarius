"""The covenant Diary tab (STORY-406): entries, their rows and details, the
Loyalty points they add, and the tab's a/A/e keys."""

from support import strip_markup, wait_until
from textual.widgets import Static, TabbedContent, Tree

from ars_magica_manager import covenant_diary as cd
from ars_magica_manager import inhabitants as inh
from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Covenant,
    CovenantDiaryEntry,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.screens import ConfirmScreen, FieldsDialog, WorkspaceScreen

HOOK_ID = "covbh_hook_minor_contested_resource"


def _covenant() -> Covenant:
    covenant = Covenant(
        id="cov1",
        saga_id="s",
        name="Dammerstein",
        boons_hooks=[VirtueFlawInstance(vf_id=HOOK_ID, id="bh1")],
        diary=[
            CovenantDiaryEntry(
                1221,
                "Winter",
                "Bought a mill",
                category="Purchases & Sales",
                pounds=-12,
            ),
            CovenantDiaryEntry(
                1220,
                "Autumn",
                "Saltworks dispute",
                category="Story Event",
                status="Open",
                boon_hook_id="bh1",
                loyalty=-3,
            ),
            CovenantDiaryEntry(
                1221, "Spring", "Vis harvest", vis_pawns=4, vis_art="Vim"
            ),
            CovenantDiaryEntry(
                1222,
                "Spring",
                "Saltworks settled",
                category="Story Event",
                status="Resolved",
                boon_hook_id="bh1",
            ),
        ],
    )
    covenant.loyalty.actions_and_events = 2
    return covenant


def test_old_saves_load_with_an_empty_diary_and_boon_hook_ids():
    covenant = Covenant.from_dict(
        {
            "id": "c",
            "saga_id": "s",
            "name": "C",
            "boons_hooks": [{"vf_id": HOOK_ID, "params": {}}],
        }
    )
    assert covenant.diary == []
    assert covenant.boons_hooks[0].id  # Story Events link to it by id


def test_rows_are_in_date_order_with_amounts_and_status():
    rows = [
        (i, strip_markup(label).replace("\\[", "["))
        for i, label in cd.rows(_covenant().diary)
    ]
    assert [i for i, _ in rows] == [1, 2, 0, 3]
    assert rows[0][1].startswith("1220 Autumn  Story Event")
    assert rows[0][1].endswith("Saltworks dispute  [Open]  -3 Loyalty")
    assert rows[1][1].endswith("Vis harvest  +4 Vi")
    assert rows[2][1].endswith("Bought a mill  -12 £")


def test_diary_loyalty_adds_into_actions_and_events():
    covenant = _covenant()
    assert cd.diary_loyalty(covenant) == -3
    assert cd.actions_and_events(covenant) == -1  # -3 from the Diary, +2 manual
    saga = Saga(id="s", name="S", covenants=[covenant])
    without = Covenant(id="c2", saga_id="s", name="C2")
    without.loyalty.actions_and_events = 2
    assert inh.total_modifiers(saga, covenant) == inh.total_modifiers(saga, without) - 3
    text = strip_markup(inh.loyalty_right_text(saga, covenant))
    assert "(Diary -3, manual +2)" in text


def test_details_count_the_stories_against_a_linked_hook():
    covenant = _covenant()
    text = strip_markup(cd.info_text(covenant, 3))
    assert "Status: Resolved" in text
    assert "Linked to: Contested Resource (Hook)" in text
    assert "2nd story against this Hook; a Minor Hook takes about 6 to overcome" in (
        text
    )
    covenant.boons_hooks.clear()
    assert "Linked to: (no longer attached)" in strip_markup(cd.info_text(covenant, 3))


def _walk(node):
    yield node
    for child in node.children:
        yield from _walk(child)


async def test_the_diary_tab_adds_edits_and_removes_entries():
    storage.save_saga(Saga(id="s", name="S", covenants=[_covenant()]))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.press("enter")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        ws = app.screen
        tree = ws.query_one("#nav-tree", Tree)
        tree.select_node(
            next(n for n in _walk(tree.root) if n.data == ("covenant", "cov1"))
        )
        await wait_until(pilot, lambda: ws._covenant_sheet_view is not None)
        view = ws._covenant_sheet_view
        await wait_until(pilot, lambda: view.initial_tab_seen)
        await pilot.pause()
        view.query_one(TabbedContent).active = "tab-cov-diary"
        await wait_until(pilot, lambda: ws._active_section() == "tab-cov-diary")

        await pilot.press("a")
        await wait_until(
            pilot,
            lambda: isinstance(app.screen, FieldsDialog) and app.screen.is_mounted,
        )
        await pilot.press("escape")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

        await pilot.press("A")  # nothing chosen: asks which, in date order
        await wait_until(pilot, lambda: not isinstance(app.screen, WorkspaceScreen))
        await pilot.press("enter")  # the first listed: 1220 Autumn
        await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

        saved = storage.load_saga("s").covenants[0]
        assert [e.name for e in saved.diary] == [
            "Bought a mill",
            "Vis harvest",
            "Saltworks settled",
        ]
        loyalty = str(ws.query_one("#inh-loyalty-right", Static).render())
        assert "Diary" not in loyalty  # the -3 went with the removed entry
