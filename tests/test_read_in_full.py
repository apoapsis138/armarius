"""Read in full: a long catalog entry shows a short view on the sheet and
opens whole in a reading window (entry_reading; the More action
read_in_full)."""

from __future__ import annotations

from typing import Any

from screen_helpers import _open_section, _saga_with_bare_character, _select_character
from support import wait_until
from textual.app import App
from textual.widgets import Static

from ars_magica_manager import (
    catalog,
    entry_reading,
    handouts,
    storage,
    viewing,
    worksheet,
)
from ars_magica_manager import handout_markup as hm
from ars_magica_manager import sheet_text as st
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import handouts as handout_forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import more
from ars_magica_manager.forms import virtue as virtue_forms
from ars_magica_manager.forms.handouts import HANDOUTS_HELP
from ars_magica_manager.forms.page import Page
from ars_magica_manager.markup import plain
from ars_magica_manager.models import (
    Character,
    Familiar,
    Handout,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.handout_reading import HandoutReading
from ars_magica_manager.tui.screens.prompts import MenuScreen
from ars_magica_manager.tui.screens.steps import run_steps
from ars_magica_manager.tui.screens.workspace.screen import WorkspaceScreen

#: A long entry (an Inner Mystery with its Initiation Script) and a short one.
LONG_VF = "vf_verditius_elder_runes"
SHORT_VF = "vf_ablating"
SHORT_FLAW = "vf_afflicted_tongue"
LONG_FLAW = "vf_abandoned_apprentice"


def _details(vf_id: str, hint: str = entry_reading.READ_HINT) -> str:
    return plain(st.vf_info_text([VirtueFlawInstance(vf_id=vf_id)], 0, hint))


def test_a_long_virtue_shows_its_summary_and_points_to_read_in_full() -> None:
    entry = catalog.load_virtue_flaw_catalog_by_id()[LONG_VF]

    shown = _details(LONG_VF, "Read it all")

    assert entry.summary in shown
    assert "Read it all" in shown
    assert entry.description[:60] not in shown
    assert "Source: HoH:MC" in shown


def test_the_creation_worksheet_shows_a_long_virtues_whole_text() -> None:
    """The worksheet has no Read in full: its details keep the whole text."""
    entry = catalog.load_virtue_flaw_catalog_by_id()[LONG_VF]
    magus = _magus(LONG_VF)
    saga = Saga(id="s", name="Saga", characters=[magus])

    details = [plain(row.details) for row in worksheet._virtue_rows(saga, magus)]

    assert any(entry.description[:60] in d for d in details)
    assert not any("Read in full" in d for d in details)


def test_a_panel_shortens_only_a_long_entry_with_a_summary() -> None:
    assert entry_reading.shortens("x" * 751, "Gist.")
    assert not entry_reading.shortens("x" * 751, "  ")
    assert not entry_reading.shortens("x" * 750, "Gist.")


def _magus(*vf_ids: str) -> Character:
    return Character(
        id="m",
        name="Magus",
        type="magus",
        virtues_flaws=[VirtueFlawInstance(vf_id=v) for v in vf_ids],
    )


def test_read_in_full_opens_the_chosen_long_virtue_on_a_reading_page() -> None:
    entry = catalog.load_virtue_flaw_catalog_by_id()[LONG_VF]
    magus = _magus(SHORT_VF, LONG_VF)

    form = virtue_forms.read_in_full(magus, 1)

    assert isinstance(form, Form) and form.reading is not None
    assert form.reading.laid.title == entry.name
    assert form.save_label == "Close" and form.fields() == []
    assert form.help_id == virtue_forms.READ_HELP


def test_read_in_full_refuses_a_short_entry_or_no_row() -> None:
    magus = _magus(SHORT_VF, LONG_VF)

    assert isinstance(virtue_forms.read_in_full(magus, 0), Refuse)
    assert isinstance(virtue_forms.read_in_full(magus, None), Refuse)
    assert isinstance(virtue_forms.read_in_full(magus, 2), Refuse)


#: Flaws and Virtues taken in mixed order: a sheet's list gives each row as
#: its index into the whole list.
MIXED = (SHORT_FLAW, LONG_VF, LONG_FLAW)


def _page(row: int | None, section: str = "section-vf-virtues") -> Page:
    saga = Saga(id="s", name="Saga")
    magus = _magus(*MIXED)
    saga.characters = [magus]
    return Page(saga, NodeKind.CHARACTER, character=magus, section=section, row=row)


def test_more_offers_read_in_full_only_on_a_chosen_long_entry() -> None:
    assert more.available("read_in_full", _page(1))
    assert more.available("read_in_full", _page(2, "section-vf-flaws"))
    assert not more.available("read_in_full", _page(0, "section-vf-flaws"))
    assert not more.available("read_in_full", _page(None))
    assert not more.available("read_in_full", _page(1, "section-abilities"))


def test_more_read_in_full_opens_the_chosen_row_and_saves_nothing() -> None:
    flaw = menu_forms.command(_page(2, "section-vf-flaws"), "read_in_full")
    virtue = menu_forms.command(_page(1), "read_in_full")

    assert isinstance(flaw, Form) and flaw.reading is not None
    assert isinstance(virtue, Form) and virtue.reading is not None
    assert flaw.reading.laid.title == "Abandoned Apprentice"
    assert virtue.reading.laid.title == "Verditius Elder Runes"
    assert more.REFRESH["read_in_full"].saves is False


def test_a_familiars_long_virtue_reads_in_full_too() -> None:
    saga = Saga(id="s", name="Saga")
    familiar = Familiar(
        id="f",
        name="Raven",
        character_id="m",
        virtues_flaws=[VirtueFlawInstance(vf_id=v) for v in MIXED],
    )
    saga.familiars = [familiar]
    page = Page(
        saga,
        NodeKind.FAMILIAR,
        familiar=familiar,
        section="section-fam-vf-virtues",
        row=1,
    )

    assert more.available("read_in_full", page)
    form = menu_forms.command(page, "read_in_full")
    assert isinstance(form, Form) and form.reading is not None
    assert form.reading.laid.title == "Verditius Elder Runes"


def test_a_player_or_a_seat_may_read_in_full() -> None:
    assert "read_in_full" in viewing.LOOKING_ACTIONS


async def test_the_terminal_reads_the_entry_full_screen_with_its_own_help() -> None:
    form = virtue_forms.read_in_full(_magus(LONG_VF), 0)
    app: App[Any] = App()
    async with app.run_test(size=(120, 45)) as pilot:
        run_steps(app, form, lambda _e: None)
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, HandoutReading)
        read = [_words(s) for s in screen.query(Static)]
        help_id = screen.help_id
        await pilot.press("escape")
        await pilot.pause()
        closed = not isinstance(app.screen, HandoutReading)

    assert read[0] == "— Minor Virtue —"
    assert "Verditius Elder Runes" in read
    assert help_id == virtue_forms.READ_HELP
    assert closed


async def test_on_the_terminal_sheet_more_reads_the_long_virtue_in_full() -> None:
    saga = _saga_with_bare_character()
    saga.characters[0].virtues_flaws = [
        VirtueFlawInstance(vf_id=SHORT_FLAW),
        VirtueFlawInstance(vf_id=LONG_VF),
    ]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")
        workspace = app.screen
        assert isinstance(workspace, WorkspaceScreen)
        details = _words(workspace.query_one("#vf-info", Static))
        await pilot.press("m")
        if await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen)):
            await pilot.press("f")
        opened = await wait_until(pilot, lambda: isinstance(app.screen, HandoutReading))
        await pilot.pause()
        await pilot.press("escape")
        await wait_until(pilot, lambda: not isinstance(app.screen, HandoutReading))
        # The panel's Read in full link runs the same action.
        workspace.action_read_entry_in_full()
        linked = await wait_until(pilot, lambda: isinstance(app.screen, HandoutReading))
        await pilot.pause()

    assert "Read in full" in details and "m, More" in details
    assert opened and linked


async def test_a_handouts_reading_keeps_the_handouts_help() -> None:
    saga = Saga(id="quiet", name="Quiet")
    saga.handouts = [Handout("letter", "A Letter", text="Greetings.")]
    handouts.choose_story(saga, "")
    app: App[Any] = App()
    async with app.run_test() as pilot:
        run_steps(app, handout_forms.preview_handout(saga, 0), lambda _e: None)
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, HandoutReading)
        help_id = screen.help_id

    assert help_id == HANDOUTS_HELP


def _words(widget: Static) -> str:
    drawn = widget.render()
    return getattr(drawn, "plain", str(drawn))


def test_a_short_virtue_shows_its_whole_text_as_before() -> None:
    entry = catalog.load_virtue_flaw_catalog_by_id()[SHORT_VF]

    shown = _details(SHORT_VF, "Read it all")

    assert entry.description in shown
    assert "Read it all" not in shown


def test_an_entry_is_long_past_750_characters() -> None:
    assert not entry_reading.is_long("x" * 750)
    assert entry_reading.is_long("x" * 751)


def test_the_reading_page_heads_the_text_with_its_kind_category_and_summary() -> None:
    reading = entry_reading.reading(
        "Elder Runes",
        "Minor Virtue",
        "Mystery",
        "Runes that double an Art.",
        "The rune magic of old.\n\n**Initiation**\n\n- A season's journey\n- A sacrifice",
        "HoH:MC",
    )

    laid = reading.laid
    assert laid.title == "Elder Runes"
    assert laid.stationery.label == "Minor Virtue"
    words = [(block.kind, plain(block.text)) for block in laid.blocks]
    assert words == [
        (hm.CENTRED, "Mystery"),
        (hm.TEXT, "Runes that double an Art."),
        (hm.TEXT, "The rune magic of old."),
        (hm.TEXT, "Initiation"),
        (hm.TEXT, "• A season's journey\n• A sacrifice"),
        (hm.RIGHT, "Source: HoH:MC"),
    ]


def test_the_reading_page_never_reads_the_entry_as_markup() -> None:
    reading = entry_reading.reading(
        "[b]Odd[/]", "Flaw", "General", "", "A [red]bracket[/] here.", ""
    )

    texts = [block.text for block in reading.laid.blocks]
    assert all("[red]" not in text or "\\[red]" in text for text in texts)
    assert [plain(t) for t in texts] == ["General", "A [red]bracket[/] here."]
