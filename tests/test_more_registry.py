"""The More registry (forms/more, ADR 0030): one entry per More and New
action, gathered in ORDER."""

from ars_magica_manager.forms import more
from ars_magica_manager.forms.more import (
    character,
    conflicts,
    covenant,
    familiar,
    laboratory,
    new,
    records,
    region,
    saga,
)
from ars_magica_manager.forms.more.registry import ORDER

AREAS = (
    records,
    saga,
    character,
    covenant,
    laboratory,
    familiar,
    region,
    conflicts,
    new,
)


def test_every_entry_is_in_order_once_and_order_names_only_entries():
    keys = [entry.key for area in AREAS for entry in area.ENTRIES]
    assert len(keys) == len(set(keys)), "an action has two entries"
    assert sorted(ORDER) == sorted(keys)
    assert len(ORDER) == len(set(ORDER))
    assert list(more.REGISTRY) == list(ORDER)


def test_each_entry_has_a_letter_a_label_and_a_menu():
    for key, entry in more.REGISTRY.items():
        assert len(entry.letter) == 1 and entry.letter.isalpha(), key
        assert entry.label.strip(), key
        assert entry.menu in ("more", "new"), key


def test_what_an_action_changes_is_said_by_those_the_core_runs():
    """A step runs in the core, so the front-end needs its Refresh; Give
    Silver's step is finished by the page placement (it gives from the
    purse of the section that offers it), and Restore is still the
    terminal's own (STILL_THE_TERMINALS)."""
    stepped = {k for k, e in more.REGISTRY.items() if e.step is not None}
    refreshed = {k for k, e in more.REGISTRY.items() if e.refresh is not None}
    assert refreshed - stepped == {"give_silver"}
    assert stepped - refreshed == {"restore"}


def test_new_actions_open_what_they_make():
    for key, entry in more.REGISTRY.items():
        if entry.menu == "new":
            assert entry.refresh is not None and entry.refresh.made, key


def test_an_entry_offered_in_one_section_is_offered_only_there():
    """With no rule of its own, an entry naming its one section is offered
    there and nowhere else."""
    entry = next(
        e
        for e in more.REGISTRY.values()
        if e.section and e.on_record is None and e.in_section is None
    )

    class Facts:
        def __init__(self, section: str) -> None:
            self._section = section

        def active_section(self) -> str:
            return self._section

    assert entry.offered(Facts(entry.section))  # type: ignore[arg-type]
    assert not entry.offered(Facts("section-elsewhere"))  # type: ignore[arg-type]
