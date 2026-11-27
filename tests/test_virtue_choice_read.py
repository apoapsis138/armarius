"""Read in full in the Add Virtue or Flaw list, in the core: a long entry's
preview shows its source, summary and Effect lines, and the entry carries
its reading page (Choice.read); a short entry shows its whole text and
offers nothing to read."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from ars_magica_manager import catalog, commands
from ars_magica_manager.forms import virtue as virtue_forms
from ars_magica_manager.markup import plain

LONG_VF = "vf_verditius_elder_runes"
SHORT_VF = "vf_ablating"


def _entry(vf_id: str) -> Any:
    return catalog.load_virtue_flaw_catalog_by_id()[vf_id]


def test_a_long_entry_offers_its_reading_page() -> None:
    entry = _entry(LONG_VF)

    choice = virtue_forms.virtue_flaw_choice(entry)

    assert choice.read is not None
    reading = choice.read()
    assert reading.laid.title == entry.name
    assert reading.help_id == virtue_forms.READ_HELP


def test_a_short_entry_offers_nothing_to_read() -> None:
    assert virtue_forms.virtue_flaw_choice(_entry(SHORT_VF)).read is None


def test_a_long_entrys_preview_shows_its_source_and_summary_not_its_text() -> None:
    entry = _entry(LONG_VF)

    detail = plain(virtue_forms.virtue_flaw_choice(entry).detail)

    assert detail.startswith(f"Source: {entry.source}\n")
    assert " ".join(entry.summary.split()) in " ".join(detail.split())
    assert entry.description[:200] not in detail


def test_a_short_entrys_preview_shows_its_whole_text() -> None:
    entry = _entry(SHORT_VF)

    detail = plain(virtue_forms.virtue_flaw_choice(entry).detail)

    assert detail.startswith(f"Source: {entry.source}\n")
    assert " ".join(entry.description.split()) in " ".join(detail.split())


def test_a_short_entrys_preview_draws_its_markdown() -> None:
    entry = replace(_entry(SHORT_VF), description="Its **bold** words, [b]as typed[/].")

    detail = plain(virtue_forms.virtue_flaw_choice(entry).detail)

    assert "Its bold words, [b]as typed[/]." in detail


def test_an_entry_not_offered_can_still_be_read() -> None:
    choice = virtue_forms.virtue_flaw_choice(_entry(LONG_VF))

    assert commands.not_offered(choice, "too old").read is choice.read
