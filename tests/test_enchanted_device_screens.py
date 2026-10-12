"""Enchanted Devices on the sheets: the section on the lab,
character and covenant sheets, and its keys -- a adds a device, i instils an
effect, e edits, A removes (after confirming), u uses a charge -- plus the
list sub-dialogs of the device form and the talisman on the Hermetic Magic
tab."""

from support import (
    build_all_tabs,
    everything_saga,
    menu,
    screen_lines,
    strip_markup,
    wait_until,
)
from textual.widgets import Button, Input, Select, Static, TabbedContent, TabPane, Tree

from ars_magica_manager import storage
from ars_magica_manager.models import CHARGED, LESSER, InstilledEffect, Saga
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    FieldsDialog,
    SelectableList,
    WorkspaceScreen,
)
from ars_magica_manager.tui.screens.pickers import ShapeMaterialPickerScreen
from ars_magica_manager.tui.screens.prompts import ListFieldScreen
from ars_magica_manager.tui.screens.widgets import section_stop

SECTIONS = {
    "laboratory": ("lab1", "section-lab-devices"),
    "character": ("mag1", "section-char-devices"),
    "covenant": ("cov1", "section-cov-devices"),
}


def _saved() -> Saga:
    return storage.load_saga("test_saga")


def _device(saga: Saga, device_id: str):
    return next(d for d in saga.enchanted_devices if d.id == device_id)


async def _open(pilot, app, kind: str):
    """Open `kind`'s sheet on its Enchanted Devices section."""
    holder_id, section_id = SECTIONS[kind]
    await pilot.press("enter")
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    workspace = app.screen
    tree = workspace.query_one("#nav-tree", Tree)

    def find_node():
        stack = [tree.root]
        while stack:
            node = stack.pop()
            if node.data == (kind, holder_id):
                return node
            stack.extend(node.children)
        return None

    assert await wait_until(pilot, lambda: find_node() is not None)
    tree.select_node(find_node())
    assert await wait_until(pilot, lambda: workspace._current_sheet_view() is not None)
    view = workspace._current_sheet_view()
    await build_all_tabs(pilot, view)
    section = view.query_one(f"#{section_id}")
    pane = next(a for a in section.ancestors if isinstance(a, TabPane))
    view.query_one(TabbedContent).active = pane.id
    await pilot.pause()
    section_stop(section).focus()
    assert await wait_until(pilot, lambda: workspace._active_section() == section_id)
    return workspace, view


async def _choose(pilot, view, kind: str, row: int) -> None:
    rows = view.query_one(f"#{SECTIONS[kind][1]}-list", SelectableList)
    rows.focus()
    await pilot.pause()
    rows.highlighted = row
    assert await wait_until(pilot, lambda: rows._marked == row)


async def _press(pilot, app, key: str, screen_type: type):
    await pilot.press(key)
    assert await wait_until(pilot, lambda: isinstance(app.screen, screen_type)), (
        f"{key!r} opened {type(app.screen).__name__}"
    )
    return app.screen


def _new_app(saga: Saga | None = None) -> ArsMagicaManagerApp:
    storage.save_saga(saga or everything_saga())
    return ArsMagicaManagerApp()


async def test_the_covenant_lists_its_devices():
    """The lab's and character's device lists are in the sheet-text golden;
    the covenant's is below the fold there."""
    app = _new_app()
    async with app.run_test(size=(140, 70)) as pilot:
        _, view = await _open(pilot, app, "covenant")
        rows = view.query_one(f"#{SECTIONS['covenant'][1]}-list", SelectableList)
        labels = [strip_markup(label) for _, label in rows._rows]
    assert labels == ["Potions  Charged   2/2 charges", "  Heal   CrCo 20"]


async def test_a_adds_a_device_held_by_the_sheet_on_show():
    app = _new_app()
    async with app.run_test(size=(140, 70)) as pilot:
        await _open(pilot, app, "character")
        dialog = await _press(pilot, app, "a", FieldsDialog)
        assert dialog.query_one("#fld-holder", Select).value == "character:mag1"
        dialog.query_one("#fld-name", Input).value = "Cloak of Shadows"
        dialog.query_one("#fld-type", Select).value = LESSER
        await pilot.pause()
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is not dialog)
        await pilot.pause()
    added = _saved().enchanted_devices[-1]
    assert (added.name, added.type, added.holder_kind, added.holder_id) == (
        "Cloak of Shadows",
        LESSER,
        "character",
        "mag1",
    )


async def test_instill_on_an_effect_row_instils_in_its_device():
    app = _new_app()
    async with app.run_test(size=(140, 70)) as pilot:
        _, view = await _open(pilot, app, "laboratory")
        await _choose(pilot, view, "laboratory", 1)  # the Pilum effect row
        await menu(pilot, app, "m", "Instill an Effect")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        dialog = app.screen
        assert dialog.title_text == "Instill an Effect in Wand"
        dialog.query_one("#fld-name", Input).value = "Ward"
        dialog.query_one("#fld-level", Input).value = "15"
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is not dialog)
        await pilot.pause()
        rows = view.query_one("#section-lab-devices-list", SelectableList)
        assert "Ward" in strip_markup(rows._rows[-1][1])
    assert [e.name for e in _device(_saved(), "dev-lab").effects] == ["Pilum", "Ward"]


async def test_instill_and_charge_show_only_on_rows_they_can_act_on():
    app = _new_app()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, "covenant")

        def enabled() -> tuple[bool, bool]:
            return (
                bool(workspace.check_action("instill_effect", ())),
                bool(workspace.check_action("use_charge", ())),
            )

        # The section took focus on its first row: a Charged Item.
        await _choose(pilot, view, "covenant", 0)
        assert enabled() == (False, True)
        # More has one thing to do there, so the footer names it.
        assert await wait_until(
            pilot, lambda: "m Use a Charge" in screen_lines(app)[-1]
        )
        footer = screen_lines(app)[-1]
        assert "Instill" not in footer and "q Quit" in footer
        assert "Set Date" not in footer
        await _choose(pilot, view, "covenant", 1)  # its effect
        assert enabled() == (False, False)
        assert not workspace.check_action("more", ())
        await pilot.press("m")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
    app = _new_app()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, "laboratory")
        await _choose(pilot, view, "laboratory", 1)  # an Invested Device's effect
        assert enabled() == (True, False)
        assert await wait_until(
            pilot, lambda: "m Instill an Effect" in screen_lines(app)[-1]
        )
        assert "q Quit" in screen_lines(app)[-1]


async def test_e_edits_the_chosen_effect_and_a_device_row_edits_the_device():
    app = _new_app()
    async with app.run_test(size=(140, 70)) as pilot:
        _, view = await _open(pilot, app, "laboratory")
        await _choose(pilot, view, "laboratory", 1)
        dialog = await _press(pilot, app, "e", FieldsDialog)
        assert dialog.title_text == "Edit an Effect of Wand"
        await pilot.press("escape")
        await pilot.pause()
        await _choose(pilot, view, "laboratory", 0)
        dialog = await _press(pilot, app, "e", FieldsDialog)
        assert dialog.title_text == "Edit an Enchanted Device"


async def test_d_deletes_an_effect_then_a_device_after_confirming():
    saga = everything_saga()
    wand = _device(saga, "dev-lab")
    wand.effects.append(
        InstilledEffect(id="eff9", name="Echo", linked_trigger=True, linked_to="eff1")
    )
    app = _new_app(saga)
    async with app.run_test(size=(140, 70)) as pilot:
        _, view = await _open(pilot, app, "laboratory")
        await _choose(pilot, view, "laboratory", 1)
        confirm = await _press(pilot, app, "d", ConfirmScreen)
        assert "Delete Pilum from Wand?" in confirm.message
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: [e.id for e in _device(_saved(), "dev-lab").effects] == ["eff9"],
        )
        # The effect it triggered forgets the link.
        assert _device(_saved(), "dev-lab").effects[0].linked_to == ""
        await _choose(pilot, view, "laboratory", 0)
        confirm = await _press(pilot, app, "d", ConfirmScreen)
        assert confirm.message == "Delete Wand and its 1 effect?"
        await pilot.press("y")
        assert await wait_until(
            pilot, lambda: all(d.id != "dev-lab" for d in _saved().enchanted_devices)
        )


async def test_use_a_charge_and_nothing_at_zero():
    saga = everything_saga()
    _device(saga, "dev-cov").charges_left = 1
    app = _new_app(saga)
    notices: list[str] = []
    async with app.run_test(size=(140, 70)) as pilot:
        _, view = await _open(pilot, app, "covenant")
        app.notify = lambda message, *a, **k: notices.append(str(message))  # type: ignore[method-assign]
        await _choose(pilot, view, "covenant", 0)
        await menu(pilot, app, "m", "Use a Charge")
        assert await wait_until(pilot, lambda: notices)
        assert notices[-1] == "Potions: 0 charges left."
        assert _device(_saved(), "dev-cov").charges_left == 0
        rows = view.query_one("#section-cov-devices-list", SelectableList)
        assert "0/2 charges" in strip_markup(rows._rows[0][1])
        await _choose(pilot, view, "covenant", 0)
        await menu(pilot, app, "m", "Use a Charge")
        assert await wait_until(pilot, lambda: len(notices) == 2)
        assert notices[-1] == "Potions has no charges left."
    assert _device(_saved(), "dev-cov").charges_left == 0


async def test_i_and_u_only_in_a_devices_section():
    app = _new_app()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, view = await _open(pilot, app, "laboratory")
        await _choose(pilot, view, "laboratory", 0)
        assert workspace.check_action("instill_effect", ())
        section_stop(view.query_one("#section-lab-items")).focus()
        assert await wait_until(
            pilot, lambda: workspace._active_section() == "section-lab-items"
        )
        assert not workspace.check_action("instill_effect", ())
        assert not workspace.check_action("use_charge", ())


async def test_components_are_edited_in_a_sub_dialog():
    app = _new_app()
    async with app.run_test(size=(140, 70)) as pilot:
        await _open(pilot, app, "laboratory")
        dialog = await _press(pilot, app, "a", FieldsDialog)
        dialog.query_one("#fld-name", Input).value = "Staff"
        dialog.query_one("#fld-components", Button).press()
        editor = await _wait_for(pilot, app, ListFieldScreen)
        editor.action_add()
        part = await _wait_for(pilot, app, FieldsDialog, not_=dialog)
        part.query_one("#fld-description", Input).value = "oak staff"
        part.query_one("#fld-material", Select).value = "wood"
        part.query_one("#fld-size", Select).value = "large"
        await pilot.pause()
        assert "Capacity: 8 pawns" in str(
            part.query_one("#fields-live", Static).render()
        )
        part.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is editor)
        editor.query_one("#btn-done", Button).press()
        assert await wait_until(pilot, lambda: app.screen is dialog)
        await pilot.pause()
        button = str(dialog.query_one("#fld-components", Button).label)
        assert button == "oak staff: wood, large (8 pawns)"
        live = str(dialog.query_one("#fields-live", Static).render())
        assert "Capacity: 8 pawns (wood x large = 2 x 4)" in live
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is not dialog)
        await pilot.pause()
    staff = _saved().enchanted_devices[-1]
    assert [(c.description, c.material, c.size) for c in staff.components] == [
        ("oak staff", "wood", "large")
    ]


async def test_a_bonus_is_picked_from_des_table():
    app = _new_app()
    async with app.run_test(size=(140, 70)) as pilot:
        await _open(pilot, app, "laboratory")
        dialog = await _press(pilot, app, "a", FieldsDialog)
        dialog.query_one("#fld-name", Input).value = "Agate Charm"
        dialog.query_one("#fld-bonuses", Button).press()
        editor = await _wait_for(pilot, app, ListFieldScreen)
        editor.action_add()
        bonus = await _wait_for(pilot, app, FieldsDialog, not_=dialog)
        bonus.query_one("#fld-catalog", Button).press()
        picker = await _wait_for(pilot, app, ShapeMaterialPickerScreen)
        picker.query_one("#picker-search", Input).value = "Agate protection from s"
        assert await wait_until(pilot, lambda: len(picker._by_item_id) == 1)
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: app.screen is bonus)
        await pilot.pause()
        assert bonus.query_one("#fld-bonus", Input).value == "5"
        assert (
            bonus.query_one("#fld-applies_to", Input).value == "protection from storms"
        )
        assert bonus.query_one("#fld-shape", Input).value == "Agate"
        bonus.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is editor)
        editor.query_one("#btn-done", Button).press()
        assert await wait_until(pilot, lambda: app.screen is dialog)
        dialog.query_one("#btn-save").press()
        assert await wait_until(pilot, lambda: app.screen is not dialog)
        await pilot.pause()
    [saved] = _saved().enchanted_devices[-1].bonuses
    assert (saved.bonus, saved.applies_to, saved.shape) == (
        5,
        "protection from storms",
        "Agate",
    )


async def test_changing_a_multi_effect_device_to_one_effect_type_is_refused():
    saga = everything_saga()
    _device(saga, "dev-lab").effects.append(InstilledEffect(id="eff9", name="Echo"))
    app = _new_app(saga)
    async with app.run_test(size=(140, 70)) as pilot:
        _, view = await _open(pilot, app, "laboratory")
        await _choose(pilot, view, "laboratory", 0)
        dialog = await _press(pilot, app, "e", FieldsDialog)
        dialog.query_one("#fld-type", Select).value = CHARGED
        await pilot.pause()
        dialog.query_one("#btn-save").press()
        await pilot.pause()
        error = str(dialog.query_one("#fields-error", Static).render())
        assert "has exactly one effect" in error
        assert app.screen is dialog


async def _wait_for(pilot, app, screen_type: type, not_=None):
    assert await wait_until(
        pilot,
        lambda: isinstance(app.screen, screen_type) and app.screen is not not_,
    ), type(app.screen).__name__
    await pilot.pause()
    return app.screen
