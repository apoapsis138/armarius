"""Read in full on a sheet: which sections offer it, and the long catalog
entry their chosen row reads, whichever catalog it is from.

A long Virtue or Flaw (a character's or familiar's), Ability (a
character's, in its Abilities or a tradition's chapter, or a familiar's)
or Boon or Hook (a covenant's) shows its summary on the sheet; Read in
full opens the whole entry on its reading page (entry_reading). Each
section names the function that finds its chosen row's page, so More's
one action, the terminal's link and the desktop's inspector button all
ask the same table.

Pattern: Strategy, reduced to a dict: each section maps to the function
that reads its row; Read in full is one Command for all of them.
"""

from __future__ import annotations

from collections.abc import Callable

from .. import entry_reading
from ..commands import Form, Refuse
from ..handout_layout import Reading
from ..markup import escape
from ..section_verbs import (
    ABILITIES_SECTION,
    BOONS_SECTION,
    FAMILIAR_ABILITIES_SECTION,
    HOOKS_SECTION,
)
from ..traditions import SECTION_PREFIX as TRADITION_PREFIX
from . import ability as ability_forms
from . import covenant as covenant_forms
from . import virtue as virtue_forms

#: What a section's row reads: its record and the row's index (as the
#: sheet's list gives it) to the entry's page and name, or None for a
#: row with nothing long to read.
Reader = Callable[[object, int | None], tuple[Reading, str] | None]


def _virtue_flaw(owner: object, index: int | None) -> tuple[Reading, str] | None:
    entry = virtue_forms.long_entry(owner, index)
    return (virtue_forms.entry_page(entry), entry.name) if entry else None


def _ability(owner: object, index: int | None) -> tuple[Reading, str] | None:
    entry = ability_forms.long_entry(owner, index)
    return (ability_forms.entry_page(entry), entry.name) if entry else None


def _boon_hook(covenant: object, index: int | None) -> tuple[Reading, str] | None:
    entry = covenant_forms.long_boon_hook(covenant, index)
    return (covenant_forms.boon_hook_page(entry), entry.name) if entry else None


#: Each section that offers Read in full, and how it reads its row; a
#: tradition's chapter (its own section per tradition) reads as Abilities.
READERS: dict[str, Reader] = {
    **dict.fromkeys(virtue_forms.READ_SECTIONS, _virtue_flaw),
    ABILITIES_SECTION: _ability,
    FAMILIAR_ABILITIES_SECTION: _ability,
    BOONS_SECTION: _boon_hook,
    HOOKS_SECTION: _boon_hook,
}


def reader(section: str) -> Reader | None:
    """How `section` reads its chosen row, or None where Read in full
    isn't offered."""
    if section.startswith(TRADITION_PREFIX):
        return _ability
    return READERS.get(section)


def _found(
    record: object, section: str, index: int | None
) -> tuple[Reading, str] | None:
    read = reader(section)
    return read(record, index) if read is not None else None


def offered(record: object, section: str, index: int | None) -> bool:
    """Whether Read in full is offered in `section` on its chosen row (at
    `index`): a section that has it, and a long entry there. The one rule
    both front-ends ask."""
    return _found(record, section, index) is not None


def read_in_full(record: object, section: str, index: int | None) -> Form | Refuse:
    """Read in full on the row at `index` of `section` of `record`: its
    catalog entry on a reading page, each front-end drawing it in place of
    fields. Only a long entry is offered it; closing it changes nothing."""
    found = _found(record, section, index)
    if found is None:
        return Refuse(entry_reading.READ_TITLE, entry_reading.READ_REFUSED)
    reading, name = found
    return Form(
        f"{entry_reading.READ_TITLE}: {escape(name)}",
        list,
        lambda _values: None,
        save_label="Close",
        help_id=entry_reading.READ_HELP,
        reading=reading,
    )
