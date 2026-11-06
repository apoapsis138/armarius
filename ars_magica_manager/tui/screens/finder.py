"""Find (Ctrl+F): a field over the saga's records, to open one.

The list is the core's index (saga_index.py), searched again on each
keystroke: the field's Changed message redraws it (Observer), and this
screen only draws what the index finds. Enter or a click on a match
dismisses with its entry, whose Ref the workspace opens as it opens a
link, at the entry's Spot for a book, device or spell."""

from __future__ import annotations

from typing import ClassVar

from ... import saga_index
from ...markup import escape
from ...models import Saga
from .pickers import SearchablePickerScreen


class FinderScreen(SearchablePickerScreen[saga_index.Entry, saga_index.Entry | None]):
    """Every record Find can open, narrowed as a name is typed; dismisses
    with the chosen one."""

    PICKER_TITLE: ClassVar[str] = "Find"
    EMPTY_MESSAGE: ClassVar[str] = "(the saga has no records yet)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "A name, a place or a Tribunal..."
    LIST_VIEW_ID: ClassVar[str] = "finder-list"

    help_id = "find"

    # Wider than a catalog picker's: a match's kind and place follow its name.
    DEFAULT_CSS = """
    FinderScreen #picker-dialog {
        width: 100;
    }
    """

    def __init__(self, saga: Saga) -> None:
        super().__init__()
        # The saga's records are never out of play, nor hidden.
        self._narrowed = False
        self.saga = saga
        #: Each entry's place in the index, for its option's id (two
        #: entries may open the same page: a covenant and its books).
        self._index: dict[int, int] = {}
        #: Why the last search found each entry, when not by its name.
        self._why: dict[int, str] = {}

    def _load_entries(self) -> list[saga_index.Entry]:
        found = saga_index.entries(self.saga)
        self._index = {id(entry): n for n, entry in enumerate(found)}
        return found

    def _match(
        self, entries: list[saga_index.Entry], needle: str
    ) -> list[saga_index.Entry]:
        matches = saga_index.search(entries, needle)
        self._why = {id(m.entry): m.note for m in matches if m.note}
        return [m.entry for m in matches]

    def _candidates(self) -> list[saga_index.Entry]:
        self._why = {}
        return self._entries

    def _in_play(self, entry: saga_index.Entry) -> bool:
        return True

    def _search_text(self, entry: saga_index.Entry) -> str:
        return entry.name

    def _label_for(self, entry: saga_index.Entry) -> str:
        why = self._why.get(id(entry), "")
        after = saga_index.SEPARATOR.join(
            part for part in (entry.kind, entry.place) if part
        )
        label = f"{escape(entry.name)}  [dim]{escape(after)}[/]"
        return f"{label}  [dim]({escape(why)})[/]" if why else label

    def _item_id(self, entry: saga_index.Entry) -> str:
        return f"find-{self._index[id(entry)]}"

    def _on_entry_selected(self, entry: saga_index.Entry) -> None:
        self.dismiss(entry)
