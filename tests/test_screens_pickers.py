"""The pickers: Virtue/Flaw, ability and spell pickers, their search and filters."""

import asyncio

import pytest
from screen_helpers import (
    _open_familiar_section,
    _open_section,
    _saga_with_bare_character,
    _saga_with_familiar,
    _select_character,
    _select_familiar,
    _select_vf_picker_entry,
    _wait_for_picker_ready,
    _wait_for_screen,
)
from support import picker_labels, wait_until
from textual.widgets import Button, Input, Label, Select, Static

from ars_magica_manager import catalog, storage
from ars_magica_manager.models import Character, Saga, VirtueFlawInstance
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    AbilityPickerScreen,
    CovenantBoonHookPickerScreen,
    FieldsDialog,
    LabVirtueFlawPickerScreen,
    SpellChooserScreen,
    VirtueFlawPickerScreen,
    WorkspaceScreen,
)


async def test_overlapping_picker_refills_leave_only_the_newest():
    # Two refills in flight at once (the first fill, and a search typed
    # before it finished) interleaved their rows into one mixed list.
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        picker = VirtueFlawPickerScreen()
        app.push_screen(picker)
        await _wait_for_picker_ready(pilot, app)
        await asyncio.gather(picker._render_list(""), picker._render_list("affinity"))
        await pilot.pause()
        expected = [
            picker._item_id(vf)
            for vf in catalog.load_virtue_flaw_catalog()
            if "affinity" in picker._search_text(vf).lower()
        ]
        assert await wait_until(pilot, lambda: picker.shown_ids() == expected), (
            picker.shown_ids()[:10]
        )


async def test_spell_picker_details_follow_the_highlight():
    # Every spell picker shows the highlighted spell's details, so the choice
    # is an informed one.
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        picker = SpellChooserScreen(Saga(id="s", name="S"))
        app.push_screen(picker)
        await _wait_for_picker_ready(pilot, app)
        details = picker.query_one("#picker-details-text", Static)
        first, second = (picker._by_item_id[i] for i in picker.shown_ids()[:2])
        assert first.name in str(details.render())
        await pilot.press("down", "down")  # into the list, then the next row
        assert await wait_until(pilot, lambda: second.name in str(details.render()))


@pytest.mark.parametrize(
    "make_picker, describe",
    [
        (
            lambda: CovenantBoonHookPickerScreen("Boon"),
            lambda e: e.description,
        ),
        (LabVirtueFlawPickerScreen, lambda e: e.description),
        (AbilityPickerScreen, lambda e: e.description),
    ],
    ids=["boons-hooks", "lab-virtues-flaws", "abilities"],
)
async def test_catalog_picker_details_follow_the_highlight(make_picker, describe):
    # The Boon/Hook, lab Virtue/Flaw and Ability pickers show the
    # highlighted entry's rules text and book under the list, as the spell
    # picker does; a search with no match empties the panel.
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        picker = make_picker()
        app.push_screen(picker)
        await _wait_for_picker_ready(pilot, app)
        details = picker.query_one("#picker-details-text", Static)

        def shown() -> str:
            return " ".join(str(details.render()).split())

        first, second = (picker._by_item_id[i] for i in picker.shown_ids()[:2])
        assert " ".join(describe(first).split())[:40] in shown()
        assert "Source: " in shown()
        await pilot.press("down", "down")
        assert await wait_until(
            pilot, lambda: " ".join(describe(second).split())[:40] in shown()
        )
        picker.query_one("#picker-search", Input).value = "zzzz no such entry"
        assert await wait_until(pilot, lambda: shown() == "")


async def test_vf_picker_offers_repeatable_entries_and_refuses_a_same_choice_repeat():
    # A taken Virtue is hidden unless repeatable; a repeat with
    # the same parameters is refused (with a notice) and the picker stays.
    creo = VirtueFlawInstance("vf_affinity_with_art", {"art": "creo"})
    taken = [creo, VirtueFlawInstance("vf_humble")]
    app = ArsMagicaManagerApp()
    results: list[VirtueFlawInstance | None] = []
    async with app.run_test(size=(140, 50)) as pilot:
        picker = VirtueFlawPickerScreen(taken)
        app.push_screen(picker, results.append)
        await _wait_for_picker_ready(pilot, app)
        offered = {e.id for e in picker._entries}
        assert "vf_affinity_with_art" in offered
        assert "vf_humble" not in offered
        art = catalog.load_virtue_flaw_catalog_by_id()["vf_affinity_with_art"]
        picker._add(art, {"art": "creo"})
        await pilot.pause()
        assert app.screen is picker and not results
        picker._add(art, {"art": "rego"})
        assert await wait_until(pilot, lambda: bool(results))
        assert results == [VirtueFlawInstance("vf_affinity_with_art", {"art": "rego"})]
    # Two copies of a max-2 Virtue: no longer offered at all.
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 50)) as pilot:
        rego = VirtueFlawInstance("vf_affinity_with_art", {"art": "rego"})
        picker = VirtueFlawPickerScreen([creo, rego])
        app.push_screen(picker)
        await _wait_for_picker_ready(pilot, app)
        assert "vf_affinity_with_art" not in {e.id for e in picker._entries}


def _vf_listed(picker: VirtueFlawPickerScreen) -> list:
    """The catalog entries a Virtue/Flaw picker lists, in order."""
    return [picker._by_item_id[item_id] for item_id in picker.shown_ids()]


def _vf_item_label(picker: VirtueFlawPickerScreen, vf_id: str) -> str:
    return picker_labels(picker)[f"vf-{vf_id}"]


async def test_vf_picker_opens_on_the_side_of_its_section():
    # The Flaws section's picker lists Flaws, the Virtues one Virtues.
    storage.save_saga(_saga_with_bare_character())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_character(pilot, app)
        for section, side, title in (
            ("section-vf-flaws", "Flaw", "Add a Flaw"),
            ("section-vf-virtues", "Virtue", "Add a Virtue"),
        ):
            await _open_section(pilot, app, section)
            await pilot.press("a")
            await _wait_for_screen(pilot, app, VirtueFlawPickerScreen)
            await _wait_for_picker_ready(pilot, app)
            picker = app.screen
            assert str(picker.query_one("#picker-title", Label).render()) == title
            assert {entry.side for entry in _vf_listed(picker)} == {side}
            await pilot.press("escape")
            await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))


async def test_vf_picker_f2_cycles_virtues_flaws_and_both():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        picker = VirtueFlawPickerScreen(side="Virtue")
        app.push_screen(picker)
        await _wait_for_picker_ready(pilot, app)
        title = picker.query_one("#picker-title", Label)

        def sides() -> set[str]:
            return {entry.side for entry in _vf_listed(picker)}

        assert sides() == {"Virtue"}
        for expected, text in (
            ({"Flaw"}, "Add a Flaw"),
            ({"Virtue", "Flaw"}, "Add a Virtue or Flaw"),
            ({"Virtue"}, "Add a Virtue"),
        ):
            await pilot.press("f2")
            assert await wait_until(
                pilot, lambda expected=expected: sides() == expected, timeout=10
            )
            assert str(title.render()) == text


async def test_vf_picker_type_and_tier_filters_combine_with_the_search():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        picker = VirtueFlawPickerScreen()  # both sides
        app.push_screen(picker)
        await _wait_for_picker_ready(pilot, app)

        def hermetic_major(entry) -> bool:
            types = (entry.category, *entry.extra_categories)
            return "Hermetic" in types and entry.tier == "Major"

        picker.query_one("#vf-picker-type", Select).value = "Hermetic"
        picker.query_one("#vf-picker-tier", Select).value = "Major"
        # Wait for the list to be exactly what the filters let through: a
        # refill still in progress can list a partial or stale set.
        assert await wait_until(
            pilot,
            lambda: (
                (picker._type, picker._tier) == ("Hermetic", "Major")
                and _vf_listed(picker) == picker._candidates()
            ),
            timeout=10,
        )
        both = _vf_listed(picker)
        assert both and all(map(hermetic_major, both))
        assert {entry.side for entry in both} == {"Virtue", "Flaw"}
        # "Hermetic, Tainted" counts as Hermetic.
        assert any(entry.id == "vf_hermetic_sorcery" for entry in both)

        picker.query_one("#picker-search", Input).value = "spell"
        assert await wait_until(
            pilot,
            lambda: _vf_listed(picker) == picker._match(picker._candidates(), "spell"),
            timeout=10,
        )
        assert 0 < len(_vf_listed(picker)) < len(both)
        for entry in _vf_listed(picker):
            assert hermetic_major(entry)
            assert "spell" in picker._search_text(entry).lower()


async def test_vf_picker_search_matches_summaries_after_names():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        picker = VirtueFlawPickerScreen()
        app.push_screen(picker)
        await _wait_for_picker_ready(pilot, app)
        picker.query_one("#picker-search", Input).value = "demon"
        assert await wait_until(
            pilot, lambda: 0 < len(_vf_listed(picker)) < 100, timeout=10
        )
        listed = _vf_listed(picker)
        in_name = ["demon" in entry.name.lower() for entry in listed]
        assert in_name == sorted(in_name, reverse=True)  # names first
        assert any(in_name) and not all(in_name)
        # The chosen row's book text shows under the list.
        details = str(picker.query_one("#picker-details-text", Static).render())
        assert listed[0].description[:30] in details.replace("\n", " ")


async def test_vf_picker_hides_ineligible_entries_and_f3_marks_them():
    companion = Character(id="c", name="Alys", type="companion")
    chooser = catalog.VirtueFlawChooser.for_character(companion)
    app = ArsMagicaManagerApp()
    results: list[VirtueFlawInstance | None] = []
    async with app.run_test(size=(140, 60)) as pilot:
        picker = VirtueFlawPickerScreen(side="Virtue", chooser=chooser)
        app.push_screen(picker, results.append)
        await _wait_for_picker_ready(pilot, app)
        status = picker.query_one("#vf-picker-status", Static)
        hermetic = "vf_adept_laboratory_student"
        assert hermetic not in {entry.id for entry in _vf_listed(picker)}
        assert "ineligible hidden (F3 shows them)" in str(status.render())

        await pilot.press("f3")
        assert await wait_until(
            pilot,
            lambda: hermetic in {entry.id for entry in _vf_listed(picker)},
            timeout=10,
        )
        assert "(needs The Gift)" in _vf_item_label(picker, hermetic)
        assert "(only for faeries)" in _vf_item_label(picker, "vf_faerie_beast")
        assert "(" not in _vf_item_label(picker, "vf_common_sense")
        assert "ineligible marked" in str(status.render())
        # Shown, an ineligible entry can still be taken: the troupe decides.
        await _select_vf_picker_entry(pilot, app, hermetic)
        assert await wait_until(pilot, lambda: bool(results))
        assert results == [VirtueFlawInstance(hermetic)]


async def test_familiar_vf_picker_offers_animal_and_magic_being_entries():
    storage.save_saga(_saga_with_familiar())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _select_familiar(pilot, app)
        await _open_familiar_section(pilot, app, "section-fam-vf-virtues")
        await pilot.press("a")
        await _wait_for_screen(pilot, app, VirtueFlawPickerScreen)
        await _wait_for_picker_ready(pilot, app)
        listed = {entry.id for entry in _vf_listed(app.screen)}
        assert {"vf_aggressive", "vf_gift_of_speech", "vf_common_sense"} <= listed
        assert not {"vf_faerie_beast", "vf_nephilim", "vf_adept_laboratory_student"} & (
            listed
        )


async def test_a_companion_can_become_a_mythic_companion():
    saga = _saga_with_bare_character()
    saga.characters[0].type = "companion"
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_character(pilot, app)
        app.screen._edit_character_info()
        await _wait_for_screen(pilot, app, FieldsDialog)
        field = app.screen.query_one("#fld-type", Select)
        assert field.value == "companion"
        field.value = "mythic companion"
        await pilot.pause()
        app.screen.query_one("#btn-save", Button).press()
        await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    assert storage.load_saga("test_saga").characters[0].type == "mythic companion"
