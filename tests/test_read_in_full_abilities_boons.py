"""Read in full for long Abilities and Boons and Hooks, in the core: their
details panels and picker previews show the summary, their Add lists carry
the reading page (Choice.read), and More's Read in full opens the chosen
row's entry on a character's or familiar's Abilities and a covenant's Boons
and Hooks (forms/read_in_full)."""

from __future__ import annotations

from ars_magica_manager import boon_hook_text, catalog, entry_reading, familiars
from ars_magica_manager import sheet_text as st
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import ability as ability_forms
from ars_magica_manager.forms import covenant as covenant_forms
from ars_magica_manager.forms import familiar as familiar_forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import more
from ars_magica_manager.forms import read_in_full as read_forms
from ars_magica_manager.forms.page import Page
from ars_magica_manager.markup import plain
from ars_magica_manager.models import (
    Ability,
    Character,
    Covenant,
    Familiar,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.section_verbs import (
    ABILITIES_SECTION,
    BOONS_SECTION,
    FAMILIAR_ABILITIES_SECTION,
    HOOKS_SECTION,
)
from ars_magica_manager.traditions import tradition_section

LONG_ABILITY = "ab_hex"
SHORT_ABILITY = "ab_athletics"
LONG_BOON = "covbh_boon_minor_chase"
SHORT_BOON = "covbh_boon_minor_wealth"
LONG_HOOK = "covbh_hook_minor_infants"


def _ability(ability_id: str) -> Ability:
    entry = catalog.load_ability_catalog_by_id()[ability_id]
    return Ability(name=entry.name, category=entry.category, xp=5)


def _hedge_witch() -> Character:
    return Character(
        id="m",
        name="Agnes",
        type="companion",
        abilities=[_ability(SHORT_ABILITY), _ability(LONG_ABILITY)],
    )


def _covenant() -> Covenant:
    covenant = Covenant(id="c", saga_id="s", name="Keep")
    # A Hook between the Boons: a Boons row is its index into the whole list.
    covenant.boons_hooks = [
        VirtueFlawInstance(vf_id=SHORT_BOON),
        VirtueFlawInstance(vf_id=LONG_HOOK),
        VirtueFlawInstance(vf_id=LONG_BOON),
    ]
    return covenant


# -- the catalogs --


def test_the_long_entries_carry_their_summaries() -> None:
    hex_ = catalog.load_ability_catalog_by_id()[LONG_ABILITY]
    chase = catalog.load_covenant_boon_hook_catalog_by_id()[LONG_BOON]

    assert hex_.summary.startswith("Brings misfortune")
    assert chase.summary.startswith("A tamed royal or noble forest")


# -- details panels and picker previews --


def test_a_long_abilitys_panel_shows_its_summary_and_the_hint() -> None:
    entry = catalog.load_ability_catalog_by_id()[LONG_ABILITY]

    shown = plain(st.ability_info_text(_hedge_witch().abilities, 1, read_hint="Read!"))

    assert " ".join(entry.summary.split()) in " ".join(shown.split())
    assert "Read!" in shown
    assert entry.description[:80] not in shown


def test_a_short_abilitys_panel_shows_its_whole_text_and_no_hint() -> None:
    entry = catalog.load_ability_catalog_by_id()[SHORT_ABILITY]

    shown = plain(st.ability_info_text(_hedge_witch().abilities, 0, read_hint="Read!"))

    assert entry.description in shown
    assert "Read!" not in shown


def test_a_long_abilitys_panel_keeps_its_whole_text_with_no_hint() -> None:
    """Where nothing offers Read in full (a creature's sheet)."""
    entry = catalog.load_ability_catalog_by_id()[LONG_ABILITY]

    shown = plain(st.ability_info_text(_hedge_witch().abilities, 1, read_hint=None))

    assert " ".join(entry.description.split()) in " ".join(shown.split())


def test_a_long_abilitys_picker_preview_shows_its_summary() -> None:
    entry = catalog.load_ability_catalog_by_id()[LONG_ABILITY]

    shown = plain(st.ability_entry_text(entry))

    assert entry.summary in " ".join(shown.split())
    assert entry.description[:80] not in shown
    assert "Source:" in shown


def test_a_long_boons_panel_shows_its_summary_and_the_hint() -> None:
    entry = catalog.load_covenant_boon_hook_catalog_by_id()[LONG_BOON]

    shown = plain(boon_hook_text.boon_hook_info_text(_covenant(), 2, "Read!"))

    assert entry.summary in " ".join(shown.split())
    assert "Read!" in shown
    assert entry.description[:80] not in shown
    assert "Source: Covenants" in shown


def test_a_short_boons_panel_shows_its_whole_text() -> None:
    entry = catalog.load_covenant_boon_hook_catalog_by_id()[SHORT_BOON]

    shown = plain(boon_hook_text.boon_hook_info_text(_covenant(), 0, "Read!"))

    assert " ".join(entry.description.split()) in " ".join(shown.split())
    assert "Read!" not in shown


def test_a_long_boons_picker_preview_shows_its_summary() -> None:
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    entry = by_id[LONG_BOON]

    shown = plain(boon_hook_text.boon_hook_entry_text(entry, by_id))

    assert entry.summary in " ".join(shown.split())
    assert entry.description[:80] not in shown


# -- the Add lists --


def test_the_add_ability_list_offers_a_long_entrys_reading_page() -> None:
    by_id = catalog.load_ability_catalog_by_id()

    long_choice = ability_forms.ability_choice(by_id[LONG_ABILITY])
    short_choice = ability_forms.ability_choice(by_id[SHORT_ABILITY])

    assert long_choice.read is not None
    reading = long_choice.read()
    assert reading.laid.title == "Hex"
    assert reading.laid.stationery.label == "Supernatural Ability"
    assert reading.help_id == entry_reading.READ_HELP
    assert short_choice.read is None


def test_a_familiars_add_ability_list_offers_it_too() -> None:
    saga = Saga(id="s", name="Saga")

    choices = familiar_forms.ability_choices(saga, [])
    hex_ = next(c for c in choices if c.value.id == LONG_ABILITY)
    athletics = next(c for c in choices if c.value.id == SHORT_ABILITY)

    assert hex_.read is not None and athletics.read is None


def test_the_add_boon_list_offers_a_long_entrys_reading_page() -> None:
    saga = Saga(id="s", name="Saga")

    choices = covenant_forms.boon_hook_choices(saga, _covenant(), "Boon")
    chase = next(c for c in choices if c.value.id == LONG_BOON)
    wealth = next(c for c in choices if c.value.id == SHORT_BOON)

    assert chase.read is not None
    reading = chase.read()
    assert reading.laid.title == "Chase"
    assert reading.laid.stationery.label == "Minor Boon"
    assert wealth.read is None


# -- More's Read in full on the sheets --


def _character_page(row: int | None, section: str = ABILITIES_SECTION) -> Page:
    witch = _hedge_witch()
    saga = Saga(id="s", name="Saga", characters=[witch])
    return Page(saga, NodeKind.CHARACTER, character=witch, section=section, row=row)


def _covenant_page(row: int | None, section: str) -> Page:
    covenant = _covenant()
    saga = Saga(id="s", name="Saga", covenants=[covenant])
    return Page(saga, NodeKind.COVENANT, covenant=covenant, section=section, row=row)


def test_more_offers_read_in_full_on_a_chosen_long_ability() -> None:
    assert more.available("read_in_full", _character_page(1))
    assert not more.available("read_in_full", _character_page(0))
    assert not more.available("read_in_full", _character_page(None))
    assert not more.available("read_in_full", _character_page(9))


def test_more_reads_a_long_ability_in_full() -> None:
    form = menu_forms.command(_character_page(1), "read_in_full")

    assert isinstance(form, Form) and form.reading is not None
    assert form.reading.laid.title == "Hex"
    assert form.save_label == "Close" and form.fields() == []
    assert form.help_id == entry_reading.READ_HELP


def test_a_traditions_chapter_reads_its_long_ability_in_full() -> None:
    page = _character_page(1, tradition_section("trad_folk_witches"))

    assert more.available("read_in_full", page)


def test_a_familiars_long_ability_reads_in_full() -> None:
    familiar = Familiar(
        id="f",
        name="Cat",
        character_id="m",
        abilities=[_ability(SHORT_ABILITY), _ability(LONG_ABILITY)],
    )
    saga = Saga(id="s", name="Saga", familiars=[familiar])
    page = Page(
        saga,
        NodeKind.FAMILIAR,
        familiar=familiar,
        section=FAMILIAR_ABILITIES_SECTION,
        row=1,
    )

    assert more.available("read_in_full", page)
    form = menu_forms.command(page, "read_in_full")
    assert isinstance(form, Form) and form.reading is not None
    assert "Read in full" in plain(
        familiars.ability_info_text(familiar, 1, "Read in full")
    )


def test_more_offers_read_in_full_on_a_chosen_long_boon_or_hook() -> None:
    assert more.available("read_in_full", _covenant_page(2, BOONS_SECTION))
    assert more.available("read_in_full", _covenant_page(1, HOOKS_SECTION))
    assert not more.available("read_in_full", _covenant_page(0, BOONS_SECTION))
    assert not more.available("read_in_full", _covenant_page(None, HOOKS_SECTION))


def test_more_reads_the_chosen_boon_in_full() -> None:
    boon = menu_forms.command(_covenant_page(2, BOONS_SECTION), "read_in_full")
    hook = menu_forms.command(_covenant_page(1, HOOKS_SECTION), "read_in_full")

    assert isinstance(boon, Form) and boon.reading is not None
    assert isinstance(hook, Form) and hook.reading is not None
    assert boon.reading.laid.title == "Chase"
    assert hook.reading.laid.title == "Infants"


def test_read_in_full_refuses_a_short_entry_another_section_or_no_row() -> None:
    witch = _hedge_witch()

    assert isinstance(read_forms.read_in_full(witch, ABILITIES_SECTION, 0), Refuse)
    assert isinstance(read_forms.read_in_full(witch, ABILITIES_SECTION, None), Refuse)
    assert isinstance(read_forms.read_in_full(witch, "section-inventory", 1), Refuse)
    assert isinstance(
        read_forms.read_in_full(_covenant(), ABILITIES_SECTION, 2), Refuse
    )
