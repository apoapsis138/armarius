"""User-made catalog entries kept with the saga."""

from __future__ import annotations

from dataclasses import asdict

import pytest
from support import strip_markup, wait_until
from textual.widgets import Collapsible, Select, Static, TabbedContent, Tree

from ars_magica_manager import catalog, storage
from ars_magica_manager import house_rules as hr
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Character,
    Covenant,
    Laboratory,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.screens import (
    ConfirmScreen,
    FieldsDialog,
    SelectableList,
    WorkspaceScreen,
)
from ars_magica_manager.screens.workspace.base import NodeKind


def _saga() -> Saga:
    return Saga(
        id="test_saga",
        name="Saga",
        covenants=[Covenant(id="cov1", saga_id="test_saga", name="Keep")],
        characters=[Character(id="c1", name="Ana", type="companion")],
        laboratories=[Laboratory(id="lab1", covenant_id="cov1", name="Tower")],
    )


def _values(name: str, entry_type: str, tier: str = "Minor", **more) -> dict:
    return {"name": name, "type": entry_type, "tier": tier, **more}


def test_points_follow_the_tier_and_flaws_and_hooks_give_them():
    assert hr.cost("Virtue", "Minor") == 1
    assert hr.cost("Flaw", "Major") == -3
    assert hr.cost("Boon", "Free") == 0
    assert hr.cost("Hook", "Minor") == -1
    assert hr.points_text("Flaw", "Minor") == "Minor Flaw: gives 1 point"
    assert hr.points_text("Boon", "Major") == "Major Boon: costs 3 points"
    assert hr.points_text("Virtue", "Free") == "Free Virtue: no points"


def test_entries_join_the_catalogs_of_the_saga_in_use():
    saga = _saga()
    shared = len(catalog.load_virtue_flaw_catalog())
    virtue = hr.add(saga, hr.CHARACTER, _values("Storm-Touched", "Virtue"))
    flaw = hr.add(saga, hr.LABORATORY, _values("Leaky Roof", "Flaw", "Free"))
    hook = hr.add(
        saga, hr.COVENANT, _values("Feuding Abbot", "Hook", "Major", category="Site")
    )
    assert (virtue.id, virtue.cost, virtue.category, virtue.source) == (
        "custom_vf_storm_touched",
        1,
        "General",
        "",
    )
    assert (flaw.cost, flaw.category) == (0, "Structure")
    assert (hook.cost, hook.category) == (-3, "Site")
    # Adding registers them: every lookup and picker now sees them.
    assert len(catalog.load_virtue_flaw_catalog()) == shared + 1
    assert catalog.load_virtue_flaw_catalog_by_id()[virtue.id] is virtue
    assert catalog.load_lab_virtue_flaw_catalog_by_id()[flaw.id] is flaw
    assert catalog.load_covenant_boon_hook_catalog()[-1] is hook
    held = VirtueFlawInstance(virtue.id)
    assert (
        catalog.describe_virtue_flaw(held, catalog.load_virtue_flaw_catalog_by_id())
        == "Storm-Touched"
    )
    # With no saga in use, only the shared catalogs.
    catalog.use_saga(None)
    assert virtue.id not in catalog.load_virtue_flaw_catalog_by_id()
    assert len(catalog.load_virtue_flaw_catalog()) == shared


def test_names_are_needed_and_cant_repeat_within_a_kind():
    saga = _saga()
    first = hr.add(saga, hr.CHARACTER, _values("Storm-Touched", "Virtue"))
    assert hr.form_problem(saga, hr.CHARACTER, _values(" ", "Virtue")) == (
        "Name is required."
    )
    assert hr.form_problem(saga, hr.CHARACTER, _values("storm-touched", "Virtue")) == (
        "There is already a Minor Virtue called Storm-Touched."
    )
    # Another tier, another kind, or the entry being edited itself is fine.
    assert hr.form_problem(saga, hr.CHARACTER, _values("Storm-Touched", "Flaw")) is None
    assert (
        hr.form_problem(saga, hr.LABORATORY, _values("Storm-Touched", "Virtue")) is None
    )
    assert (
        hr.form_problem(saga, hr.CHARACTER, _values("Storm-Touched", "Virtue"), first)
        is None
    )
    # Two of a name get different ids.
    second = hr.add(saga, hr.CHARACTER, _values("Storm-Touched", "Flaw"))
    assert second.id != first.id


def test_an_entry_in_use_keeps_its_id_through_an_edit():
    saga = _saga()
    virtue = hr.add(saga, hr.CHARACTER, _values("Storm-Touched", "Virtue"))
    hook = hr.add(saga, hr.COVENANT, _values("Feuding Abbot", "Hook"))
    saga.characters[0].virtues_flaws.append(VirtueFlawInstance(virtue.id))
    saga.covenants[0].boons_hooks.append(VirtueFlawInstance(hook.id))
    assert hr.used_by(saga, hr.CHARACTER, virtue) == ["Ana"]
    assert hr.used_by(saga, hr.COVENANT, hook) == ["Keep"]
    hr.update(
        saga,
        hr.CHARACTER,
        virtue,
        _values("Storm-Born", "Virtue", "Major", description="Born in a *storm*."),
    )
    assert (virtue.id, virtue.name, virtue.cost) == (
        "custom_vf_storm_touched",
        "Storm-Born",
        3,
    )
    held = saga.characters[0].virtues_flaws[0]
    assert (
        catalog.describe_virtue_flaw(held, catalog.load_virtue_flaw_catalog_by_id())
        == "Storm-Born"
    )
    detail = strip_markup(hr.detail_text(saga, (hr.CHARACTER, virtue)))
    assert "Points: Major Virtue: costs 3 points" in detail
    assert "Held by: Ana" in detail and "Born in a storm." in detail
    assert strip_markup(hr.row_label(hr.COVENANT, hook)).split() == [
        "Feuding",
        "Abbot",
        "Covenant",
        "Hook",
        "Minor",
        "-1",
    ]


def test_entries_are_saved_with_the_saga():
    saga = _saga()
    hr.add(saga, hr.CHARACTER, _values("Storm-Touched", "Virtue", repeatable=True))
    hr.add(saga, hr.LABORATORY, _values("Leaky Roof", "Flaw"))
    hr.add(saga, hr.COVENANT, _values("Feuding Abbot", "Hook"))
    storage.save_saga(saga)
    loaded = storage.load_saga("test_saga")
    assert asdict(loaded.custom_virtues_flaws[0]) == asdict(
        saga.custom_virtues_flaws[0]
    )
    assert [(k, e.name) for k, e in hr.all_entries(loaded)] == [
        ("character", "Storm-Touched"),
        ("laboratory", "Leaky Roof"),
        ("covenant", "Feuding Abbot"),
    ]
    assert loaded.custom_virtues_flaws[0].repeatable
    # An older saga has none.
    old = asdict(saga)
    for key in (
        "custom_virtues_flaws",
        "custom_lab_virtues_flaws",
        "custom_boons_hooks",
    ):
        del old[key]
    assert hr.all_entries(Saga.from_dict(old)) == []


def _node(tree: Tree, data: tuple):
    pending = [tree.root]
    while pending:
        node = pending.pop()
        if node.data == data:
            return node
        pending.extend(node.children)
    return None


@pytest.mark.parametrize("size", [(140, 60), (120, 45)])
async def test_house_rules_are_added_edited_and_removed_from_their_node(size):  # noqa: PLR0915
    saga = _saga()
    hr.add(saga, hr.CHARACTER, _values("Storm-Touched", "Virtue"))
    saga.characters[0].virtues_flaws.append(
        VirtueFlawInstance(saga.custom_virtues_flaws[0].id)
    )
    storage.save_saga(saga)
    catalog.use_saga(None)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=size) as pilot:
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        # Opening the saga puts its entries in the catalogs.
        assert "custom_vf_storm_touched" in catalog.load_virtue_flaw_catalog_by_id()
        tree = workspace.query_one("#nav-tree", Tree)
        assert await wait_until(
            pilot, lambda: _node(tree, (NodeKind.SAGA_CONTENT,)) is not None
        )
        tree.select_node(_node(tree, (NodeKind.SAGA_CONTENT,)))
        assert await wait_until(pilot, lambda: workspace._saga_content_view)
        view = workspace._saga_content_view
        assert await wait_until(pilot, lambda: view.initial_tab_seen)
        view.query_one(TabbedContent).active = "tab-content-house-rules"
        assert await wait_until(
            pilot, lambda: bool(workspace.query("#house-rules-list"))
        )
        assert await wait_until(
            pilot, lambda: workspace._active_section() == "section-house-rules"
        )
        rows = workspace.query_one("#house-rules-list", SelectableList)
        assert workspace._active_section() == "section-house-rules"
        # 'a': a Major Hook for covenants.
        await pilot.press("a")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-kind")))
        dialog = app.screen
        region = dialog.query_one("#fields-dialog").region
        assert region.bottom <= size[1] and region.right <= size[0]
        dialog.query_one("#fld-kind", Select).value = hr.COVENANT
        await pilot.pause()
        assert dialog.query_one("#fdw-bh_type").display
        assert not dialog.query_one("#fdw-vf_type").display
        dialog.query_one("#fld-name").value = "Feuding Abbot"
        dialog.query_one("#fld-bh_type", Select).value = "Hook"
        dialog.query_one("#fld-tier", Select).value = "Major"
        await pilot.pause()
        live = str(dialog.query_one("#fields-live", Static).render())
        assert "Major Hook: gives 3 points" in live
        dialog.query_one("#btn-save").press()
        assert await wait_until(
            pilot,
            lambda: (
                [h.name for h in storage.load_saga("test_saga").custom_boons_hooks]
                == ["Feuding Abbot"]
            ),
        )
        assert await wait_until(pilot, lambda: app.screen is workspace)
        section = workspace.query_one("#section-house-rules", Collapsible)
        assert await wait_until(pilot, lambda: section.title == "House Rules (2)")
        hook_id = workspace.saga.custom_boons_hooks[0].id
        assert hook_id in catalog.load_covenant_boon_hook_catalog_by_id()
        # An entry someone holds can't be deleted.
        rows.focus()
        rows.highlighted = 0
        await pilot.pause()
        await pilot.press("enter")
        panel = workspace.query_one("#house-rules-panel", Static)
        assert await wait_until(pilot, lambda: "Held by: Ana" in str(panel.render()))
        await pilot.press("d")
        await pilot.pause()
        assert app.screen is workspace
        assert len(storage.load_saga("test_saga").custom_virtues_flaws) == 1
        # The Hook no one holds can.
        rows.highlighted = 1
        await pilot.pause()
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: "Feuding Abbot" in str(panel.render()))
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(
            pilot, lambda: storage.load_saga("test_saga").custom_boons_hooks == []
        )
        assert hook_id not in catalog.load_covenant_boon_hook_catalog_by_id()
