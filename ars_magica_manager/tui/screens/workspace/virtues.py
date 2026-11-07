"""WorkspaceScreen's Virtues and Flaws lists, shared by the character,
familiar and laboratory sheets: a / e / d are the core table's
(section_verbs), the same steps the desktop runs."""

from __future__ import annotations

from ....section_verbs import VIRTUE_FLAW_SIDES
from .base import _SectionOps
from .creation import CreationActions


class VirtueFlawActions(CreationActions):
    def _virtue_flaw_section_ops(self) -> dict[str, _SectionOps]:
        """a / e / d on the Virtues and Flaws lists (character, laboratory,
        familiar), like any other list (see WorkspaceScreen._section_ops)."""
        return {
            section: self._core_ops_of(section)
            for sections in VIRTUE_FLAW_SIDES.values()
            for section in sections
        }
