"""The covenant's Economics tab, Emergency Savings and the year's end."""

import re

from screen_helpers import (
    _cov_view,
    _fill,
    _inh_labels,
    _is_form,
    _open_inh_section,
    _open_workspace,
    _plain_title,
    _saga_with_people,
    _save_dialog,
    _select_covenant,
    _wait_for_screen,
)
from support import build_all_tabs, menu, wait_until
from textual.widgets import (
    Button,
    Collapsible,
    Input,
    Label,
    ListView,
    Select,
    Static,
    TabbedContent,
)

from ars_magica_manager import economics as eco
from ars_magica_manager import storage
from ars_magica_manager.models import IncomeSource, Inhabitant, Saga
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    AdvanceSeasonScreen,
    ConfirmScreen,
    FieldsDialog,
    SagaPickerScreen,
    SelectableList,
    WorkspaceScreen,
)
from ars_magica_manager.tui.screens.widgets import section_stop


def _saga_for_economics() -> Saga:
    """Corvinus (magus) and Alys (companion) plus six turb and three laborers:
    17 points of inhabitants, one source of income."""
    saga = _saga_with_people()
    cov = saga.covenants[0]
    cov.inhabitants = [
        Inhabitant(id="t", kind="turb", name="Guards", quantity=6),
        Inhabitant(
            id="l", kind="inhabitant", name="Laborers", role="Laborer", quantity=3
        ),
    ]
    cov.economics.income_sources = [
        IncomeSource(
            id="a", name="Salt Mine", type="Typical", description="A **rich** seam."
        )
    ]
    return saga


async def _show_economics_tab(pilot, app) -> None:
    view = app.screen._covenant_sheet_view
    await wait_until(pilot, lambda: view.initial_tab_seen)
    await pilot.pause()
    view.query_one(TabbedContent).active = "tab-cov-economics"
    await pilot.pause()


async def _open_eco_section(pilot, app, which: str) -> None:
    """Focus an Economics section (so its a / e / d keys apply)."""
    await _show_economics_tab(pilot, app)
    view = app.screen._covenant_sheet_view
    section_stop(view.query_one(f"#section-eco-{which}", Collapsible)).focus()
    await pilot.pause()
    await wait_until(
        pilot, lambda: app.screen._active_section() == f"section-eco-{which}"
    )


async def _select_eco_row(pilot, app, which: str, row: int) -> None:
    await _show_economics_tab(pilot, app)
    rows = app.screen._covenant_sheet_view.query_one(
        f"#eco-{which}-list", SelectableList
    )
    rows.focus()
    await pilot.pause()
    rows.highlighted = row
    await pilot.pause()


def _eco_panel(app) -> str:
    return str(_cov_view(app).query_one("#eco-panel", Static).render())


def _eco_labels(app, which: str) -> list[str]:
    view = _cov_view(app)
    summary = eco.summarize(view.saga, view.covenant)
    return [re.sub(r"\s+", " ", label) for _, label in view._eco_rows(which, summary)]


def _eco_wealth(app) -> str:
    view = _cov_view(app)
    return "\n".join(
        str(view.query_one(f"#eco-wealth-{side}", Static).render())
        for side in ("left", "right")
    )


def _saved_economics():
    return storage.load_saga("test_saga").covenants[0].economics


async def test_economics_tab_shows_calculated_wealth_and_all_its_sections():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _show_economics_tab(pilot, app)
        view = _cov_view(app)

        sections = [
            view.query_one(f"#section-eco-{k}", Collapsible)
            for k in ("wealth", "income", "expenditure", "savings")
        ]
        assert [_plain_title(x) for x in sections] == [
            "Wealth",
            "Sources of Income (1)",
            "Yearly Expenditure",
            "Cost Savings",
        ]
        assert all(not x.collapsed for x in sections)

        wealth = _eco_wealth(app)
        # 5 (magus) + 3 (companion) + 6 turb + 3 laborers
        assert re.search(r"Points of Inhabitants:\s+17\b", wealth)
        assert re.search(r"Points of Laboratories:\s+0\b", wealth)
        assert re.search(r"Points of Weapons and Armor:\s+0\b", wealth)
        assert re.search(r"Wealth:\s+0\b", wealth)
        assert re.search(r"Total Income:\s+100\b", wealth)
        # 2 + 4 + 9 + 4 + 1 writing + 1 sundry (the minimum) = 21; laborers save 3
        assert re.search(r"Expenditure \(Before Cost Savings\):\s+21\b", wealth)
        assert re.search(r"Cost Savings:\s+3\b", wealth)
        assert re.search(r"Total Expenditure:\s+18\b", wealth)

        names = lambda which: [x.split(" ")[0] for x in _eco_labels(app, which)]
        assert names("expenditure") == [
            "Buildings",
            "Consumables",
            "Laboratories",
            "Provisions",
            "Wages",
            "Weapons",
            "Writing",
            "Tithes",
            "Inflation",
            "Sundry",
        ]
        assert names("savings") == ["Laborers", "Craftspeople", "Magic", "Emergency"]
        headers = [str(w.render()) for w in view.query(".eco-header").results(Static)]
        assert "Type" in headers[0] and "Income" in headers[0]  # income source header
        assert "Cost" in headers[1] and "Quantity" in headers[2]
        assert "Savings" in headers[1] and "Notes" in headers[1]
        assert _eco_labels(app, "income") == ["Salt Mine Typical 100"]
        assert "Select a source" in _eco_panel(app)


async def _add_income(pilot, app, **values) -> None:
    before = len(_eco_labels(app, "income"))
    await _open_eco_section(pilot, app, "income")
    await pilot.press("a")
    await _wait_for_screen(pilot, app, FieldsDialog)
    assert isinstance(app.screen, FieldsDialog)
    _fill(app, **values)
    await _save_dialog(pilot, app)
    await wait_until(pilot, lambda: len(_eco_labels(app, "income")) > before)


async def test_a_new_income_source_takes_its_income_from_its_type_unless_typed_over():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_eco_section(pilot, app, "income")
        await pilot.press("a")
        await pilot.pause()
        assert app.screen.query_one("#fld-type", Select).value == "Typical"
        assert app.screen.query_one("#fld-income", Input).value == ""  # follows type
        types = app.screen.query_one("#fld-type", Select)
        assert [v for _, v in types._options if isinstance(v, str)] == [
            "None",
            "Lesser",
            "Typical",
            "Greater",
            "Legendary",
        ]
        await _save_dialog(pilot, app)
        assert isinstance(app.screen, FieldsDialog)  # a name is required
        assert "Name is required" in str(app.screen.query_one("#fields-error").render())
        _fill(app, name="Old Quarry", type="Legendary")
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_eco_labels(app, "income")) == 2)

        await _add_income(pilot, app, name="Toll", type="Lesser", income=55)
        await _add_income(pilot, app, name="Idle Land", type="None")
        assert _eco_labels(app, "income") == [
            "Salt Mine Typical 100",
            "Old Quarry Legendary 1000",
            "Toll Lesser 55",
            "Idle Land None 0",
        ]
        # 100 + 1000 + 55 + 0
        assert re.search(r"Total Income:\s+1155\b", _eco_wealth(app))

    sources = _saved_economics().income_sources
    assert [s.income for s in sources] == [None, None, 55, None]  # only typed ones kept


async def test_choosing_rows_fills_the_panel_with_one_selection_across_the_lists():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_eco_row(pilot, app, "income", 0)
        panel = _eco_panel(app)
        assert "Name: Salt Mine" in panel and "Type: Typical" in panel
        assert "Current Income: 100 (the usual for Typical)" in panel
        assert "A rich seam." in panel and "**" not in panel  # emphasis rendered

        await _select_eco_row(pilot, app, "expenditure", 3)
        view = _cov_view(app)
        assert view.selected_economics("income") is None  # unchosen
        panel = _eco_panel(app)
        assert "Name: Provisions" in panel
        assert "Rule: 5 pounds per 10 pts Inhabitants" in panel
        assert "Cost: 9" in panel and "Savings: 3" in panel
        assert "17 pts of inhabitants x 5 / 10" in panel

        await _select_eco_row(pilot, app, "savings", 0)
        assert view.selected_economics("expenditure") is None
        panel = _eco_panel(app)
        assert "Name: Laborers" in panel and "Quantity: 3" in panel


async def test_e_and_d_act_on_the_selected_income_source_and_delete_confirms():
    saga = _saga_for_economics()
    saga.covenants[0].economics.income_sources.append(
        IncomeSource(id="b", name="[Toll] bridge", type="Lesser")
    )
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        # The brackets are escaped so they aren't read as markup.
        assert _eco_labels(app, "income")[1].startswith("\\[Toll] bridge")
        await _select_eco_row(pilot, app, "income", 1)

        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)  # no "which one?" picker
        assert app.screen.query_one("#fld-name", Input).value == "[Toll] bridge"
        assert app.screen.query_one("#fld-income", Input).value == ""
        _fill(app, type="Greater", income=260)
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: "260" in _eco_labels(app, "income")[1])
        assert "Current Income: 260 (typed; Greater is usually 250)" in _eco_panel(app)

        await _select_eco_row(pilot, app, "income", 1)
        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Delete [Toll] bridge?"
        await pilot.press("n")
        await pilot.pause()
        assert len(_eco_labels(app, "income")) == 2

        await pilot.press("d")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_eco_labels(app, "income")) == 1)
        assert re.search(r"Total Income:\s+100\b", _eco_wealth(app))

        # The list keeps focus, so the row left is chosen: d and e are
        # about that one, without asking which.
        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("e")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

    assert [s.name for s in _saved_economics().income_sources] == ["Salt Mine"]


async def test_improve_updates_multiplier_and_projected_income_live_then_confirms():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_eco_row(pilot, app, "income", 0)  # Salt Mine, income 100

        await menu(pilot, app, "m", "Improve Income")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        assert app.screen.query_one("#fld-effect", Select).value == "Status Quo"
        live = lambda: str(app.screen.query_one("#fields-live", Static).render())
        assert live() == "Income Multiplier x1. Projected Income 100"

        app.screen.query_one("#fld-effect", Select).value = "Boom"
        await pilot.pause()
        assert live() == "Income Multiplier x1.5. Projected Income 150"

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message == "Update Salt Mine's income from 100 to 150?"

        await pilot.press("n")  # decline: still on the Improve dialog, unchanged
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)

        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

        await wait_until(
            pilot, lambda: "experienced Boom" in _eco_labels(app, "income")[0]
        )
        label = _eco_labels(app, "income")[0]
        assert label == (
            "Salt Mine Typical 150 1220 - Salt Mine experienced Boom "
            "changing Income from 100 to 150."
        )
        await _select_eco_row(pilot, app, "income", 0)
        panel = _eco_panel(app)
        assert panel.index("Note:") < panel.index("Description:")
        assert "A rich seam." in panel  # the description, still there afterward

    source = _saved_economics().income_sources[0]
    assert source.income == 150
    assert source.note == (
        "1220 - Salt Mine experienced Boom changing Income from 100 to 150."
    )


async def test_improve_with_status_quo_records_the_no_change_note():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_eco_row(pilot, app, "income", 0)
        await menu(pilot, app, "m", "Improve Income")
        await pilot.pause()
        app.screen.query_one("#btn-save", Button).press()
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        assert "from 100 to 100" in str(
            app.screen.query_one("#confirm-message", Static).render()
        )
        await pilot.press("y")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

    source = _saved_economics().income_sources[0]
    assert source.income == 100
    assert source.note == (
        "1220 - Salt Mine experienced no growth or setbacks. Status Quo maintained."
    )


async def test_improve_cancel_and_acting_on_the_focused_row():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        # Nothing chosen: 'i' falls back to asking which one, same as e/A.
        await _open_eco_section(pilot, app, "income")
        await menu(pilot, app, "m", "Improve Income")
        await pilot.pause()
        assert isinstance(app.screen, FieldsDialog)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)

    assert _saved_economics().income_sources[0].income is None  # untouched


async def test_expenditure_rows_take_notes_and_the_typed_ones_take_amounts():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)

        # A calculated row: only its Notes can be typed.
        await _select_eco_row(pilot, app, "expenditure", 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        assert not app.screen.query("#fld-tithes")
        _fill(app, notes="Roof of the north tower")
        await _save_dialog(pilot, app)
        await wait_until(
            pilot,
            lambda: "Roof of the north tower" in _eco_labels(app, "expenditure")[0],
        )
        await wait_until(pilot, lambda: "Roof of the north tower" in _eco_panel(app))
        assert "Roof of the north tower" in _eco_panel(app)  # panel refreshed too

        # A typed row: an amount, which feeds the totals.
        await _select_eco_row(pilot, app, "expenditure", 7)
        await pilot.press("e")
        await pilot.pause()
        assert app.screen.query_one("#fld-tithes", Input).value == "0"
        _fill(app, tithes=4, notes="Church")
        await _save_dialog(pilot, app)
        await wait_until(
            pilot, lambda: _eco_labels(app, "expenditure")[7].startswith("Tithes 4")
        )
        assert re.search(r"Before Cost Savings\):\s+25\b", _eco_wealth(app))  # 21 + 4

        # An empty note is removed, not stored blank.
        await _select_eco_row(pilot, app, "expenditure", 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, notes="")
        await _save_dialog(pilot, app)
        await wait_until(
            pilot, lambda: "Roof" not in _eco_labels(app, "expenditure")[0]
        )

    economics = _saved_economics()
    assert economics.tithes == 4
    assert economics.notes == {"tithes": "Church"}


async def test_e_edits_the_expenditure_row_the_cursor_is_on():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_eco_section(pilot, app, "expenditure")
        await pilot.press("down")  # Consumables (the section starts on row 0)
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        assert isinstance(app.screen, FieldsDialog)
        assert "Consumables" in str(app.screen.query_one("#fields-title").render())


async def test_cost_savings_rows_are_calculated_except_magic_and_emergency_savings():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_eco_row(pilot, app, "savings", 0)  # Laborers
        await pilot.press("e")
        await pilot.pause()
        assert not app.screen.query("#fld-magic_savings")
        await pilot.press("escape")
        await pilot.pause()

        await _select_eco_row(pilot, app, "savings", 2)  # Magic
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, magic_savings=6, notes="A self-sweeping broom")
        await _save_dialog(pilot, app)
        await wait_until(
            pilot, lambda: _eco_labels(app, "savings")[2].startswith("Magic 0 6")
        )

        await _select_eco_row(pilot, app, "savings", 3)  # Emergency Savings
        await pilot.press("e")
        await _wait_for_screen(pilot, app, FieldsDialog)
        _fill(app, emergency_savings=4)
        await _save_dialog(pilot, app)
        await wait_until(
            pilot,
            lambda: _eco_labels(app, "savings")[3].startswith("Emergency Savings 0 4"),
        )
        # 3 (laborers) + 6 + 4
        assert re.search(r"Cost Savings:\s+13\b", _eco_wealth(app))
        assert re.search(r"Total Expenditure:\s+8\b", _eco_wealth(app))  # 21 - 13

    economics = _saved_economics()
    assert (economics.magic_savings, economics.emergency_savings) == (6, 4)
    assert economics.notes == {"magic": "A self-sweeping broom"}


async def test_economics_follows_changes_made_on_other_tabs_and_keeps_the_chosen_row():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _select_eco_row(pilot, app, "expenditure", 3)  # Provisions
        assert "Cost: 9" in _eco_panel(app)

        # Four more turb on the Inhabitants tab: 17 -> 21 points.
        await _open_inh_section(pilot, app, "section-inh-turb")
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")  # (New person)
        await pilot.pause()
        _fill(app, name="More Guards", quantity=4)
        await _save_dialog(pilot, app)
        await wait_until(pilot, lambda: len(_inh_labels(app, "turb")) == 2)

        await _show_economics_tab(pilot, app)
        assert re.search(r"Points of Inhabitants:\s+21\b", _eco_wealth(app))
        view = _cov_view(app)
        assert view.selected_economics("expenditure") == 3  # still chosen
        await wait_until(pilot, lambda: "Cost: 11" in _eco_panel(app))
        assert "Name: Provisions" in _eco_panel(app)

        # The salary in Loyalty drives the Wages multiplier.
        view.covenant.loyalty.money = "Generous salary"
        view.refresh_section("section-inh-loyalty")
        assert "Wages (x1.5)" in _eco_labels(app, "expenditure")[4]


async def test_the_economics_forms_fit_a_120_by_45_terminal():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _select_covenant(pilot, app)
        await _open_eco_section(pilot, app, "income")
        await pilot.press("a")
        await pilot.pause()
        region = app.screen.query_one("#fields-dialog").region
        assert region.right <= 120 and region.bottom <= 45
        # The usual income of each type is shown as a hint.
        hints = " ".join(str(h.render()) for h in app.screen.query(".fd-hint"))
        assert "Lesser 40" in hints and "Legendary 1000" in hints
        await pilot.press("escape")
        await pilot.pause()

        await _open_eco_section(pilot, app, "expenditure")
        await pilot.press("e")
        await pilot.pause()
        await pilot.press("enter")  # the first row of the picker
        await pilot.pause()
        region = app.screen.query_one("#fields-dialog").region
        assert region.right <= 120 and region.bottom <= 45


async def test_the_economics_forms_do_not_stretch_on_a_tall_terminal():
    storage.save_saga(_saga_for_economics())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_covenant(pilot, app)
        await _open_eco_section(pilot, app, "income")
        await pilot.press("a")
        await pilot.pause()
        # well short of the 70 rows (its title is ruled)
        assert app.screen.query_one("#fields-dialog").region.height < 34


def _save_sagas(*names: str) -> None:
    for name in names:
        storage.save_saga(
            Saga(id=storage.generate_saga_id(name), name=name, storyguide="Alex")
        )


def _picker_labels(app) -> list[str]:
    return [
        str(item.query_one(Label).render())
        for item in app.screen.query_one("#saga-list", ListView).children
    ]


async def test_d_deletes_the_highlighted_saga_only_after_confirmation():
    _save_sagas("Alpha", "[Beta] Saga", "Gamma")

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        list_view = app.screen.query_one("#saga-list", ListView)
        list_view.index = 1
        await pilot.pause()
        assert len(_picker_labels(app)) == 3
        assert _picker_labels(app)[1].startswith("[Beta] Saga")  # not read as markup

        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "Delete the saga [Beta] Saga?" in message  # brackets survive
        assert "cannot be undone" in message

        # No (and Escape) keep it; so does Enter on the default No.
        await pilot.press("n")
        await pilot.pause()
        assert storage.list_sagas() == ["alpha", "beta_saga", "gamma"]
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("escape")
        await pilot.pause()
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, SagaPickerScreen)
        assert storage.list_sagas() == ["alpha", "beta_saga", "gamma"]

        await pilot.press("d")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: len(_picker_labels(app)) == 2)
        assert storage.list_sagas() == ["alpha", "gamma"]  # exactly that one
        assert [l.split("  ")[0] for l in _picker_labels(app)] == ["Alpha", "Gamma"]
        assert app.screen.query_one("#saga-list", ListView).index == 1  # stays put

        # Opening still works on what is left.
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, WorkspaceScreen)
        assert app.screen.saga.id == "gamma"


async def test_an_unreadable_saga_is_listed_and_can_be_deleted():
    # One damaged file used to crash the picker on startup.
    _save_sagas("Alpha", "Gamma")
    (storage.SAGAS_DIR / "broken.json").write_text("{not json", encoding="utf-8")

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        labels = _picker_labels(app)
        assert labels[0].startswith("Alpha") and labels[2].startswith("Gamma")
        assert labels[1] == "broken  —  ✘ can't be read"

        # Opening it says why instead of crashing; the picker stays.
        list_view = app.screen.query_one("#saga-list", ListView)
        list_view.index = 1
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, SagaPickerScreen)

        await pilot.press("d")
        await pilot.pause()
        assert "Delete the saga broken?" in str(
            app.screen.query_one("#confirm-message", Static).render()
        )
        await pilot.press("y")
        await wait_until(pilot, lambda: storage.list_sagas() == ["alpha", "gamma"])


async def test_the_delete_key_works_and_deleting_the_last_saga_shows_the_placeholder():
    _save_sagas("Only")

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("delete")
        await pilot.pause()
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await wait_until(pilot, lambda: storage.list_sagas() == [])
        await wait_until(
            pilot, lambda: any("No sagas yet" in l for l in _picker_labels(app))
        )
        assert len(_picker_labels(app)) == 1

        # Nothing left to delete: no dialog, just a notice.
        await pilot.press("d")
        await pilot.pause()
        assert isinstance(app.screen, SagaPickerScreen)


async def test_a_saga_can_still_be_created_after_deleting_all_of_them():
    _save_sagas("Old")

    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.press("d")
        await pilot.pause()
        await pilot.press("y")
        await wait_until(pilot, lambda: storage.list_sagas() == [])

        await pilot.press("n")
        await pilot.pause()
        assert _is_form(app.screen, "Create a New Saga")
        app.screen.query_one("#fld-name", Input).value = "Old"  # the same name
        app.screen.query_one("#fld-storyguide", Input).value = "Alex"
        app.screen.query_one("#fld-year", Input).value = "1220"
        await pilot.click("#btn-save")
        await pilot.pause()
        assert isinstance(app.screen, SagaPickerScreen)

    assert storage.list_sagas() == ["old"]


def _saga_with_a_deficit(deficit: int, wealth: int) -> Saga:
    saga = _saga_for_economics()
    cov = saga.covenants[0]
    cov.economics.tithes = 0
    cov.economics.tithes = eco.summarize(saga, cov).surplus_deficit + deficit
    cov.economics.wealth = wealth
    return saga


async def _edit_emergency_savings(pilot, app) -> None:
    view = app.screen._covenant_sheet_view
    await build_all_tabs(pilot, view)
    rows = view.query_one("#eco-savings-list", SelectableList)
    await _select_eco_row(pilot, app, "savings", len(rows._rows) - 1)
    await pilot.press("e")
    await pilot.pause()


async def test_editing_emergency_savings_offers_to_draw_from_wealth():
    storage.save_saga(_saga_with_a_deficit(36, wealth=100))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_covenant(pilot, app)
        await _edit_emergency_savings(pilot, app)
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message.startswith(
            "Do you wish to draw from Wealth to cover the deficit?"
        )
        assert "Deficit: 36    Wealth: 100" in message
        # No opens the ordinary form instead.
        await pilot.press("n")
        await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert app.screen.query_one("#fld-emergency_savings", Input).value == "0"
        await pilot.press("escape")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert (_saved_economics().emergency_savings, _saved_economics().wealth) == (
            0,
            100,
        )

        await _edit_emergency_savings(pilot, app)
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("y")
        await wait_until(pilot, lambda: _saved_economics().emergency_savings == 36)
        assert _saved_economics().wealth == 64
        rows = app.screen._covenant_sheet_view.query_one(
            "#eco-savings-list", SelectableList
        )
        assert "deficit" not in rows._rows[-1][1]  # covered: the warning goes


async def test_a_short_draw_empties_wealth_and_the_covenant_is_broke():
    storage.save_saga(_saga_with_a_deficit(36, wealth=10))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_covenant(pilot, app)
        await _edit_emergency_savings(pilot, app)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert "Wealth only covers 10 of it" in message
        assert "26 stays uncovered" in message
        await pilot.press("y")
        await wait_until(pilot, lambda: _saved_economics().wealth == 0)
        assert _saved_economics().emergency_savings == 10
        rows = app.screen._covenant_sheet_view.query_one(
            "#eco-savings-list", SelectableList
        )
        assert "Covenant is broke" in rows._rows[-1][1]
        # With no Wealth left there's nothing to offer: straight to the form.
        await _edit_emergency_savings(pilot, app)
        assert isinstance(app.screen, FieldsDialog)


async def test_the_new_year_adds_each_covenants_surplus_to_its_wealth():
    saga = _saga_for_economics()
    saga.current_season = "Winter"
    cov = saga.covenants[0]
    cov.economics.wealth = 5
    cov.economics.emergency_savings = 3
    surplus = eco.summarize(saga, cov).surplus_deficit
    assert surplus > 0
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await pilot.press("t")
        await pilot.pause()
        assert isinstance(app.screen, AdvanceSeasonScreen)
        note = str(app.screen.query_one("#advance-year-note", Static).render())
        assert "surplus is added to its Wealth" in note
        # The dialog hugs its content (now including who has nothing
        # planned) rather than filling the screen.
        assert app.screen.query_one("#advance-dialog").region.height < 25
        app.screen.query_one("#btn-advance", Button).press()
        await wait_until(pilot, lambda: _saved_economics().wealth == 5 + surplus)

    loaded = storage.load_saga("test_saga")
    assert (loaded.current_season, loaded.current_year) == ("Spring", 1221)
    assert loaded.covenants[0].economics.emergency_savings == 0


async def test_other_seasons_leave_wealth_alone():
    saga = _saga_for_economics()
    saga.current_season = "Autumn"
    saga.covenants[0].economics.wealth = 5
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await pilot.press("t")
        await pilot.pause()
        assert not app.screen.query("#advance-year-note")
        app.screen.query_one("#btn-advance", Button).press()
        await wait_until(
            pilot, lambda: storage.load_saga("test_saga").current_season == "Winter"
        )
    assert _saved_economics().wealth == 5


async def _advance_from_winter(pilot, app) -> None:
    """Press t and confirm the Advance Time dialog; when that asks about a
    deficit, wait until the question has its focus (a bare
    pause left `focused` None under parallel load)."""
    await pilot.press("t")
    assert await wait_until(pilot, lambda: isinstance(app.screen, AdvanceSeasonScreen))
    dialog = app.screen
    dialog.query_one("#btn-advance", Button).press()
    assert await wait_until(pilot, lambda: app.screen is not dialog)
    await wait_until(
        pilot,
        lambda: (
            not isinstance(app.screen, ConfirmScreen) or app.screen.focused is not None
        ),
    )


def _winter_saga_with_a_deficit() -> Saga:
    saga = _saga_with_a_deficit(36, wealth=100)
    saga.current_season = "Winter"
    return saga


async def test_rolling_the_year_over_in_deficit_asks_first():
    storage.save_saga(_winter_saga_with_a_deficit())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await _advance_from_winter(pilot, app)
        assert isinstance(app.screen, ConfirmScreen)
        message = str(app.screen.query_one("#confirm-message", Static).render())
        assert message.startswith("The year ends with a covenant in deficit:")
        assert "Test Covenant: -36" in message
        assert "Balance its books first" in message
        # Escape (or No) keeps the year, so the books can be balanced.
        await pilot.press("escape")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert storage.load_saga("test_saga").current_season == "Winter"
        await _advance_from_winter(pilot, app)
        assert isinstance(app.screen, ConfirmScreen)
        await pilot.press("n")
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

    saga = storage.load_saga("test_saga")
    assert (saga.current_season, saga.current_year) == ("Winter", 1220)
    assert saga.covenants[0].economics.wealth == 100


async def test_advance_anyway_advances_the_year_regardless():
    storage.save_saga(_winter_saga_with_a_deficit())

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await _advance_from_winter(pilot, app)
        await pilot.press("y")
        await wait_until(
            pilot, lambda: storage.load_saga("test_saga").current_season == "Spring"
        )

    saga = storage.load_saga("test_saga")
    assert saga.current_year == 1221
    # The deficit isn't taken from Wealth by itself.
    assert saga.covenants[0].economics.wealth == 100


async def test_no_deficit_prompt_without_a_deficit_or_outside_winter():
    saga = _saga_for_economics()  # a surplus
    saga.current_season = "Winter"
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await _advance_from_winter(pilot, app)
        await wait_until(
            pilot, lambda: storage.load_saga("test_saga").current_season == "Spring"
        )
        assert not isinstance(app.screen, ConfirmScreen)

    saga = _saga_with_a_deficit(36, wealth=100)
    saga.current_season = "Autumn"  # a deficit, but not the year's end
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_workspace(pilot)
        await _advance_from_winter(pilot, app)
        await wait_until(
            pilot, lambda: storage.load_saga("test_saga").current_season == "Winter"
        )
