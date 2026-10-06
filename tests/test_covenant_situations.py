"""Covenant Situations and the Poverty Hook."""

from __future__ import annotations

from support import wait_until
from textual.widgets import Button, ListView, OptionList, Static, Tree

from ars_magica_manager import catalog, covenants, sourcebooks, storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Covenant,
    IncomeSource,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation as rules
from ars_magica_manager.screens import ConfirmScreen, WorkspaceScreen
from ars_magica_manager.screens.creation_worksheet import CreationWorksheetScreen
from ars_magica_manager.screens.pickers import RemovalPickerScreen
from ars_magica_manager.screens.workspace.base import NodeKind

BY_ID = catalog.load_covenant_boon_hook_catalog_by_id()


def _covenant(*vf_ids: str) -> Covenant:
    covenant = Covenant(id="cov1", saga_id="test_saga", name="Keep", in_creation=True)
    covenant.boons_hooks = [VirtueFlawInstance(vf_id) for vf_id in vf_ids]
    return covenant


def test_every_situation_uses_catalog_boons_and_hooks_from_a_known_book():
    situations = catalog.load_covenant_situation_catalog()
    assert len(situations) == 24
    assert len({s.id for s in situations}) == 24
    for situation in situations:
        assert situation.description and situation.entries, situation.id
        assert situation.source in sourcebooks.SOURCEBOOKS, situation.id
        for entry in situation.entries:
            assert entry["vf_id"] in BY_ID, (situation.id, entry)
    # The core book's six balance exactly.
    for situation in situations:
        if situation.source == "DE":
            hooks, boons = covenants.situation_points(situation, BY_ID)
            assert hooks == boons, situation.id


def test_a_situation_adds_each_entry_as_often_as_it_is_taken():
    situations = {s.id: s for s in catalog.load_covenant_situation_catalog()}
    added = covenants.situation_instances(situations["situation_de_winter_ruins"])
    ids = [bh.vf_id for bh in added]
    assert ids.count("covbh_hook_minor_contested_resource") == 3
    assert ids.count("covbh_boon_minor_hidden_resources") == 3
    assert len(added) == 12 and len({bh.id for bh in added}) == 12
    keep = covenants.situation_instances(situations["situation_cov_autumn_power"])
    details = {bh.vf_id: bh.params.get("detail") for bh in keep}
    assert details["covbh_boon_major_curtain_walls_and_mural_towers"] == "Hall Keep"


def test_minor_poverty_excludes_wealth_and_secondary_income():
    covenant = _covenant("covbh_hook_minor_poverty", "covbh_boon_minor_wealth")
    assert covenants.boon_hook_problems(covenant, BY_ID) == [
        "Poverty (Minor Hook) can't be taken with Wealth (Minor Boon)."
    ]
    saga = Saga(id="test_saga", name="S", covenants=[covenant])
    found = {c.detail: c.status for c in rules.checks(saga, covenant, "boons_hooks")}
    assert (
        found["Poverty (Minor Hook) can't be taken with Wealth (Minor Boon)."] == "warn"
    )
    assert (
        covenants.boon_hook_problems(_covenant("covbh_hook_minor_poverty"), BY_ID) == []
    )


def test_poverty_limits_the_covenants_income():
    minor = _covenant("covbh_hook_minor_poverty")
    minor.economics.income_sources = [IncomeSource(id="i1", name="Mill", type="Lesser")]
    assert covenants.boon_hook_problems(minor, BY_ID) == []
    minor.economics.income_sources.append(IncomeSource(id="i2", name="Toll"))
    [problem] = covenants.boon_hook_problems(minor, BY_ID)
    assert problem.startswith("Poverty (Minor Hook): the covenant has one Lesser")
    assert "Toll (Typical)" in problem
    major = _covenant("covbh_hook_major_poverty")
    major.economics.income_sources = [IncomeSource(id="i1", name="Mill")]
    [problem] = covenants.boon_hook_problems(major, BY_ID)
    assert problem.startswith("Poverty (Major Hook): the covenant has no source")


def test_boons_may_cost_less_than_the_hooks_give_but_not_more():
    covenant = _covenant("covbh_hook_minor_rival")
    saga = Saga(id="test_saga", name="S", covenants=[covenant])

    def found():
        return {
            c.label: (c.status, c.detail)
            for c in rules.checks(saga, covenant, "boons_hooks")
        }

    assert found()["Boons cost no more than the Hooks give"][0] == "pass"
    assert found()["Hook points spent"] == ("advice", "1 unspent")
    covenant.boons_hooks += [
        VirtueFlawInstance("covbh_boon_minor_aura"),
        VirtueFlawInstance("covbh_boon_minor_edifice"),
    ]
    assert found()["Boons cost no more than the Hooks give"] == (
        "warn",
        "2 Boon, 1 Hook points, 1 too many",
    )


async def test_the_worksheet_adds_a_covenant_situation_and_the_sheet_warns():
    covenant = _covenant("covbh_boon_minor_wealth")
    saga = Saga(id="test_saga", name="S", covenants=[covenant], books_in_play=[])
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        tree = workspace.query_one("#nav-tree", Tree)

        def node():
            stack = [tree.root]
            while stack:
                n = stack.pop()
                if n.data == (NodeKind.COVENANT, "cov1"):
                    return n
                stack.extend(n.children)
            return None

        assert await wait_until(pilot, lambda: node() is not None)
        tree.select_node(node())
        assert await wait_until(
            pilot, lambda: workspace._covenant_sheet_view is not None
        )
        view = workspace._covenant_sheet_view
        workspace.query_one("#btn-worksheet", Button).press()
        assert await wait_until(
            pilot, lambda: isinstance(app.screen, CreationWorksheetScreen)
        )
        await pilot.pause()  # let the worksheet mount and choose its first step
        screen = app.screen
        screen.query_one("#ws-steps", OptionList).highlighted = 2
        assert await wait_until(pilot, lambda: screen.step == "boons_hooks")

        def button():
            return next(
                (
                    b
                    for b in screen.query("#ws-actions Button")
                    if str(b.label) == "Use a Covenant Situation"
                ),
                None,
            )

        assert await wait_until(pilot, lambda: button() is not None)
        button().press()
        assert await wait_until(
            pilot, lambda: isinstance(app.screen, RemovalPickerScreen)
        )
        # Only the core book's six are offered with no supplements in play.
        assert len(app.screen.labels) == 6
        # Winter Ruins, the last of them: it has Poverty (Minor).
        options = app.screen.query_one("#removal-picker-list", ListView)
        assert await wait_until(pilot, lambda: len(options.children) == 6)
        options.index = 5
        await pilot.pause()
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: len(storage.load_saga("test_saga").covenants[0].boons_hooks) == 13,
        )
        # Its Poverty doesn't go with the Wealth the covenant already had.
        assert await wait_until(
            pilot,
            lambda: (
                "Poverty (Minor Hook) can't be taken with Wealth (Minor Boon)."
                in str(view.query_one("#cov-bh-warnings", Static).render())
            ),
        )
