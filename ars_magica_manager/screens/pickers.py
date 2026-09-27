"""Pickers: the searchable catalog pickers, the row picker used by
Remove/Edit/Restore, and the CSV file picker."""

from __future__ import annotations

import asyncio
from collections import Counter
from pathlib import Path
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import (
    Button,
    DirectoryTree,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

from .. import catalog
from .. import spells as spl
from ..markup import escape
from ..models import (
    Ability,
    AbilityDef,
    CovenantBoonHookDef,
    LabVirtueFlawDef,
    Saga,
    Spell,
    VirtueFlawDef,
    VirtueFlawInstance,
    boon_hook_params,
)
from .fields import FieldsDialog, ModalDialog
from .prompts import _ability_fields, _ability_from, _boon_hook_fields, _param_dialog
from .widgets import _boon_hook_names

_VIRTUE_FLAW_ITEM_ID_PREFIX = "vf-"


_LAB_VIRTUE_FLAW_ITEM_ID_PREFIX = "labvf-"


_ABILITY_ITEM_ID_PREFIX = "ability-"


_REMOVAL_ITEM_ID_PREFIX = "remove-"


_COVENANT_BOON_HOOK_ITEM_ID_PREFIX = "covbhpick-"


class SearchablePickerScreen[EntryT, ResultT](ModalDialog[ResultT]):
    """Base for a ListView-backed catalog picker with a live-filtering
    search box above it.

    The Ability and Virtue/Flaw catalogs are large (78 and 624 entries) --
    a flat unsearchable list doesn't scale, so every catalog picker shares this:
    an Input above the ListView that re-filters it on every keystroke.
    Subclasses supply the entry list and how to search/render/activate
    each one; this owns the Input<->ListView wiring, so that trickier bit
    (live rebuild, keeping the search box focused and typable while
    letting Down/Enter reach the list) only has to be gotten right once.

    Subclasses set `PICKER_TITLE`, `EMPTY_MESSAGE` and `SEARCH_PLACEHOLDER`
    (the defaults for the matching constructor arguments), `LIST_VIEW_ID`
    (kept distinct per picker, not shared, so existing tests that query e.g.
    "#vf-picker-list" by id keep working) and the `_load_entries`/
    `_search_text`/`_label_for`/`_item_id`/`_on_entry_selected` hooks below.
    Generic over the catalog entry type and the dialog's result.
    """

    PICKER_TITLE: ClassVar[str] = "Pick"
    EMPTY_MESSAGE: ClassVar[str] = "(nothing available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search..."
    LIST_VIEW_ID: ClassVar[str] = "picker-list"

    DEFAULT_CSS = """
    SearchablePickerScreen {
        align: center middle;
    }

    #picker-dialog {
        width: 76;
        height: auto;
        max-height: 28;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #picker-search {
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        title: str = "",
        *,
        empty_message: str = "",
        search_placeholder: str = "",
    ) -> None:
        super().__init__()
        self.picker_title = title or self.PICKER_TITLE
        self.empty_message = empty_message or self.EMPTY_MESSAGE
        self.search_placeholder = search_placeholder or self.SEARCH_PLACEHOLDER
        self._entries: list[EntryT] = []
        self._by_item_id: dict[str, EntryT] = {}
        #: One refill at a time; a refill a newer query has superseded is
        #: skipped (typing before the first fill finishes used to interleave
        #: the two fills into one mixed list).
        self._render_lock = asyncio.Lock()
        self._render_generation = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog"):
            yield Label(self.picker_title, id="picker-title")
            yield Input(placeholder=self.search_placeholder, id="picker-search")
            yield ListView(id=self.LIST_VIEW_ID)
            yield Button("Cancel", id="btn-cancel")

    async def on_mount(self) -> None:
        self._entries = self._load_entries()
        await self._render_list("")
        self.query_one("#picker-search", Input).focus()

    # -- subclass hooks --

    def _load_entries(self) -> list[EntryT]:
        raise NotImplementedError

    def _search_text(self, entry: EntryT) -> str:
        raise NotImplementedError

    def _label_for(self, entry: EntryT) -> str:
        raise NotImplementedError

    def _item_id(self, entry: EntryT) -> str:
        raise NotImplementedError

    def _on_entry_selected(self, entry: EntryT) -> None:
        raise NotImplementedError

    # -- filtering / list rendering --

    async def _render_list(self, query: str) -> None:
        self._render_generation += 1
        generation = self._render_generation
        async with self._render_lock:
            if generation == self._render_generation:
                await self._fill_list(query)

    async def _fill_list(self, query: str) -> None:
        list_view = self.query_one(f"#{self.LIST_VIEW_ID}", ListView)
        await list_view.clear()
        self._by_item_id = {}

        if not self._entries:
            await list_view.append(ListItem(Label(self.empty_message)))
            return

        needle = query.strip().lower()
        matches = (
            [e for e in self._entries if needle in self._search_text(e).lower()]
            if needle
            else self._entries
        )
        if not matches:
            await list_view.append(ListItem(Label(f"(no matches for {query!r})")))
            return

        items = []
        for entry in matches:
            item_id = self._item_id(entry)
            self._by_item_id[item_id] = entry
            items.append(ListItem(Label(self._label_for(entry)), id=item_id))
        await list_view.extend(items)
        list_view.index = 0

    async def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "picker-search":
            await self._render_list(event.value)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Enter in the search box activates the top (highlighted) match,
        # the same way arrowing down to it and pressing Enter would.
        if event.input.id != "picker-search":
            return
        list_view = self.query_one(f"#{self.LIST_VIEW_ID}", ListView)
        if list_view.index is None:
            return
        await self._activate(list_view.children[list_view.index])

    def on_key(self, event: Key) -> None:
        # Input has no "down" binding of its own, so it would otherwise
        # just bubble and do nothing -- forward it to move focus into the
        # (already-filtered) list, the natural next step after typing.
        if event.key != "down":
            return
        search = self.query_one("#picker-search", Input)
        if self.focused is not search:
            return
        list_view = self.query_one(f"#{self.LIST_VIEW_ID}", ListView)
        if list_view.children:
            list_view.focus()
            event.stop()

    # -- selection / dismissal --

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        await self._activate(event.item)

    async def _activate(self, item: ListItem) -> None:
        if item.id is None:
            return
        entry = self._by_item_id.get(item.id)
        if entry is None:
            return
        self._on_entry_selected(entry)


class VirtueFlawPickerScreen(
    SearchablePickerScreen[VirtueFlawDef, VirtueFlawInstance | None]
):
    """Pick a character Virtue/Flaw from the catalog, prompting for
    parameters if needed. Dismisses with the new instance, or None if
    cancelled.

    Laboratories have their own, separate Virtue/Flaw catalog and picker
    -- see LabVirtueFlawPickerScreen -- since a lab's Virtues & Flaws
    (ArM5 Chapter 8) are a completely different list from a character's
    (Chapter 4), even though both use the same VirtueFlawInstance shape
    and Free/Minor/Major tiers.
    """

    PICKER_TITLE: ClassVar[str] = "Add a Virtue or Flaw"
    EMPTY_MESSAGE: ClassVar[str] = "(no more Virtues/Flaws available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search Virtues & Flaws..."
    LIST_VIEW_ID: ClassVar[str] = "vf-picker-list"

    def __init__(self, exclude_ids: set[str] | None = None) -> None:
        super().__init__()
        self._exclude_ids = exclude_ids or set()

    def _load_entries(self) -> list[VirtueFlawDef]:
        return [
            entry
            for entry in catalog.load_virtue_flaw_catalog()
            if entry.id not in self._exclude_ids
        ]

    def _search_text(self, entry: VirtueFlawDef) -> str:
        return f"{entry.name} {entry.type} {entry.category} {entry.tier}"

    def _label_for(self, entry: VirtueFlawDef) -> str:
        needs = f"  (needs: {', '.join(entry.parameters)})" if entry.parameters else ""
        return f"{entry.name}  [{entry.type}, {entry.tier}, cost {entry.cost}]{needs}"

    def _item_id(self, entry: VirtueFlawDef) -> str:
        return f"{_VIRTUE_FLAW_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: VirtueFlawDef) -> None:
        if not entry.parameters:
            self.dismiss(VirtueFlawInstance(vf_id=entry.id))
            return

        def handle_params(params: dict[str, str] | None) -> None:
            if params is not None:
                self.dismiss(VirtueFlawInstance(vf_id=entry.id, params=params))

        self.app.push_screen(_param_dialog(entry.name, entry.parameters), handle_params)


class LabVirtueFlawPickerScreen(
    SearchablePickerScreen[LabVirtueFlawDef, VirtueFlawInstance | None]
):
    """Pick a Laboratory Virtue/Flaw from the lab catalog (ArM5 Chapter 8
    -- Structure/Outfittings/Supernatural). Dismisses with the new
    instance, or None if cancelled.

    No ParamPromptScreen branch -- unlike character Virtues/Flaws, lab
    entries are never templated. `repeatable` entries (asterisked in the
    book -- Feature*, Person*, etc.) aren't excluded just because one's
    already attached, the same way templated character entries aren't.
    """

    PICKER_TITLE: ClassVar[str] = "Add a Laboratory Virtue or Flaw"
    EMPTY_MESSAGE: ClassVar[str] = "(no more Virtues/Flaws available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search Laboratory Virtues & Flaws..."
    LIST_VIEW_ID: ClassVar[str] = "lab-vf-picker-list"

    def __init__(self, exclude_ids: set[str] | None = None) -> None:
        super().__init__()
        self._exclude_ids = exclude_ids or set()

    def _load_entries(self) -> list[LabVirtueFlawDef]:
        return [
            entry
            for entry in catalog.load_lab_virtue_flaw_catalog()
            if entry.repeatable or entry.id not in self._exclude_ids
        ]

    def _search_text(self, entry: LabVirtueFlawDef) -> str:
        return f"{entry.name} {entry.type} {entry.category} {entry.tier}"

    def _label_for(self, entry: LabVirtueFlawDef) -> str:
        return f"{entry.name}  [{entry.type}, {entry.tier}, cost {entry.cost}]"

    def _item_id(self, entry: LabVirtueFlawDef) -> str:
        return f"{_LAB_VIRTUE_FLAW_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: LabVirtueFlawDef) -> None:
        self.dismiss(VirtueFlawInstance(vf_id=entry.id))


class CovenantBoonHookPickerScreen(
    SearchablePickerScreen[CovenantBoonHookDef, VirtueFlawInstance | None]
):
    """Pick a covenant Boon or Hook (ArM5 Chapter 6) from the catalog, then
    optionally name what it applies to (which Edifice, which contested
    resource...). Dismisses with the new VirtueFlawInstance, or None if
    cancelled.

    One picker for either kind: `kind` is "Boon" or "Hook". Nothing is
    hidden or blocked: entries already attached are marked "(taken)" but
    can be taken again (a covenant may well have two Edifices), and
    prerequisites and exclusions are shown as notes only.
    """

    LIST_VIEW_ID: ClassVar[str] = "covbh-picker-list"

    def __init__(self, kind: str, attached_ids: list[str] | None = None) -> None:
        super().__init__(
            f"Add a {kind}",
            empty_message=f"(no more {kind}s available)",
            search_placeholder=f"Search {kind}s...",
        )
        self.kind = kind
        self._taken = Counter(attached_ids or [])
        self._by_id = catalog.load_covenant_boon_hook_catalog_by_id()

    def _load_entries(self) -> list[CovenantBoonHookDef]:
        return sorted(
            (entry for entry in self._by_id.values() if entry.type == self.kind),
            key=catalog.boon_hook_sort_key,
        )

    def _search_text(self, entry: CovenantBoonHookDef) -> str:
        return f"{entry.name} {entry.category} {entry.tier} {entry.description}"

    def _names(self, ids: list[str]) -> str:
        return _boon_hook_names(ids, self._by_id)

    def _label_for(self, entry: CovenantBoonHookDef) -> str:
        facts = [entry.category] if entry.category else []
        facts.append(entry.tier)
        if entry.cost:
            facts.append(f"{abs(entry.cost):g} pt")
        label = f"{entry.name}  [{', '.join(facts)}]"
        if entry.requires:
            label += f"  (requires: {self._names(entry.requires)})"
        if entry.excludes:
            label += f"  (not with: {self._names(entry.excludes)})"
        if self._taken[entry.id]:
            label += f"  (taken x{self._taken[entry.id]})"
        return label

    def _item_id(self, entry: CovenantBoonHookDef) -> str:
        return f"{_COVENANT_BOON_HOOK_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: CovenantBoonHookDef) -> None:
        def handle_detail(result: dict[str, Any] | None) -> None:
            if result is None:
                return  # cancelled: back to the picker
            params = boon_hook_params(result["detail"], result["description"])
            self.dismiss(VirtueFlawInstance(vf_id=entry.id, params=params))

        self.app.push_screen(
            FieldsDialog(f"{self.kind}: {escape(entry.name)}", _boon_hook_fields()),
            handle_detail,
        )


class AbilityPickerScreen(SearchablePickerScreen[AbilityDef, Ability | None]):
    """Pick an Ability from the catalog, resolve any parameter, set score/specialty.

    Non-templated entries already held are excluded (no point in a second
    "Athletics" row); templated entries ("Craft: {craft}") stay available
    since a character can hold several distinct instances of the same
    family. Dismisses with the new Ability, or None if cancelled.
    """

    PICKER_TITLE: ClassVar[str] = "Add an Ability"
    EMPTY_MESSAGE: ClassVar[str] = "(no more Abilities available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search Abilities..."
    LIST_VIEW_ID: ClassVar[str] = "ability-picker-list"

    def __init__(self, exclude_names: set[str] | None = None) -> None:
        super().__init__()
        self._exclude_names = exclude_names or set()

    def _load_entries(self) -> list[AbilityDef]:
        return [
            entry
            for entry in catalog.load_ability_catalog()
            if entry.parameters or entry.name not in self._exclude_names
        ]

    def _search_text(self, entry: AbilityDef) -> str:
        return f"{entry.name} {entry.category}"

    def _label_for(self, entry: AbilityDef) -> str:
        needs = f"  (needs: {', '.join(entry.parameters)})" if entry.parameters else ""
        return f"{entry.name}  [{entry.category}]{needs}"

    def _item_id(self, entry: AbilityDef) -> str:
        return f"{_ABILITY_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: AbilityDef) -> None:
        if entry.parameters:

            def handle_params(params: dict[str, str] | None) -> None:
                if params is not None:
                    self._prompt_details(
                        catalog.resolve_ability_name(entry, params), entry.category
                    )

            self.app.push_screen(
                _param_dialog(entry.name, entry.parameters), handle_params
            )
        else:
            self._prompt_details(entry.name, entry.category)

    def _prompt_details(self, name: str, category: str) -> None:
        def handle_ability(result: dict[str, Any] | None) -> None:
            if result is not None:
                self.dismiss(_ability_from(name, category, result))

        self.app.push_screen(
            FieldsDialog(escape(name), _ability_fields(None), save_label="Confirm"),
            handle_ability,
        )


class SpellChooserScreen(SearchablePickerScreen[Spell, str | None]):
    """Pick a spell -- for a Lab Text or Casting Tablet, or a spell a magus
    knows: every spell there is (the catalog, the saga's own, any magus's
    invented spells) less any in `exclude`, searchable by name or shorthand.
    Dismisses with the spell id."""

    PICKER_TITLE: ClassVar[str] = "Choose the spell"
    EMPTY_MESSAGE: ClassVar[str] = "(no spells)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search spells by name or Arts (e.g. CrIg)..."
    LIST_VIEW_ID: ClassVar[str] = "spell-chooser-list"

    def __init__(
        self, saga: Saga, *, exclude: set[str] | None = None, title: str = ""
    ) -> None:
        super().__init__(title)
        self.saga = saga
        self.exclude = exclude or set()
        self._origin: dict[str, str] = {}

    def _load_entries(self) -> list[Spell]:
        entries = []
        for spell, origin in spl.pickable_spells(self.saga):
            if spell.id in self.exclude:
                continue
            self._origin[spell.id] = origin
            entries.append(spell)
        return entries

    def _search_text(self, entry: Spell) -> str:
        return f"{entry.name} {spl.shorthand(entry)}"

    def _label_for(self, entry: Spell) -> str:
        return (
            f"{escape(entry.name)}  [dim]{escape(spl.shorthand(entry))}  "
            f"{escape(self._origin.get(entry.id, ''))}[/]"
        )

    def _item_id(self, entry: Spell) -> str:
        return f"spellpick-{entry.id}"

    def _on_entry_selected(self, entry: Spell) -> None:
        self.dismiss(entry.id)


class RemovalPickerScreen(ModalDialog[int | None]):
    """Pick one entry from a list of display labels, by index.

    Despite the name it's the generic "which one?" picker: used to choose
    what to remove, edit, restore or improve. The caller supplies the labels
    and acts on its own list using the returned index. Dismisses with that
    index, or None if cancelled.
    """

    DEFAULT_CSS = """
    RemovalPickerScreen {
        align: center middle;
    }

    #picker-dialog {
        width: 76;
        height: auto;
        max-height: 24;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }
    """

    def __init__(self, title: str, labels: list[str]) -> None:
        super().__init__()
        self.prompt_title = title
        self.labels = labels

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog"):
            yield Label(self.prompt_title, id="picker-title")
            yield ListView(id="removal-picker-list")
            yield Button("Cancel", id="btn-cancel")

    def on_mount(self) -> None:
        list_view = self.query_one("#removal-picker-list", ListView)
        if not self.labels:
            list_view.append(ListItem(Label("(nothing to remove)")))
            return

        for index, label in enumerate(self.labels):
            list_view.append(
                ListItem(Label(label), id=f"{_REMOVAL_ITEM_ID_PREFIX}{index}")
            )
        list_view.index = 0

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id
        if item_id is None or not item_id.startswith(_REMOVAL_ITEM_ID_PREFIX):
            return
        index = int(item_id.removeprefix(_REMOVAL_ITEM_ID_PREFIX))
        self.dismiss(index)


class _CsvDirectoryTree(DirectoryTree):
    """Folders and .csv files only (hidden entries left out)."""

    def filter_paths(self, paths):
        return [
            path
            for path in paths
            if not path.name.startswith(".")
            and (path.is_dir() or path.suffix.lower() == ".csv")
        ]


class CsvFilePickerScreen(ModalDialog[Path | None]):
    """A small file explorer for choosing a .csv file: browse the folders
    below `start` (Enter opens a folder or picks a file), Up goes to the
    parent folder, and the path box takes a typed folder or file. Dismisses
    with the chosen file, or None if cancelled."""

    DEFAULT_CSS = """
    CsvFilePickerScreen {
        align: center middle;
    }

    #picker-dialog {
        width: 90;
        max-width: 100%;
        height: 80%;
        max-height: 100%;
        border: round $accent;
        padding: 1 2;
        background: $surface;
    }

    #picker-path-row {
        width: 100%;
        height: 1;
        margin: 1 0;
    }

    #picker-path {
        width: 1fr;
    }

    #btn-picker-up {
        margin-right: 1;
    }

    #picker-tree {
        height: 1fr;
    }

    #picker-error {
        color: $error;
        height: auto;
    }

    #picker-buttons {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, title: str, start: Path) -> None:
        super().__init__()
        self.title_text = title
        self.start = start

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog"):
            yield Label(self.title_text, id="picker-title")
            with Horizontal(id="picker-path-row"):
                yield Button("Up", id="btn-picker-up", compact=True)
                yield Input(str(self.start), id="picker-path", compact=True)
            yield _CsvDirectoryTree(self.start, id="picker-tree")
            yield Static("", id="picker-error")
            with Horizontal(id="picker-buttons"):
                yield Button("Open", id="btn-picker-open", variant="success")
                yield Button("Cancel", id="btn-picker-cancel")

    def on_mount(self) -> None:
        self.query_one("#picker-tree", DirectoryTree).focus()

    def _show_folder(self, folder: Path) -> None:
        self.query_one("#picker-tree", DirectoryTree).path = folder
        self.query_one("#picker-path", Input).value = str(folder)
        self.query_one("#picker-error", Static).update("")

    def _choose(self, raw: str) -> None:
        """Open a typed folder, or pick a typed .csv file."""
        path = Path(raw.strip().strip('"')).expanduser()
        error = self.query_one("#picker-error", Static)
        if path.is_dir():
            self._show_folder(path)
        elif path.is_file() and path.suffix.lower() == ".csv":
            self.dismiss(path)
        elif path.is_file():
            error.update(f"{escape(path.name)} isn't a .csv file.")
        else:
            error.update(f"No such file or folder: {escape(str(path))}")

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        event.stop()
        self.dismiss(event.path)

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        event.stop()
        self.query_one("#picker-path", Input).value = str(event.path)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self._choose(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "btn-picker-up":
            tree = self.query_one("#picker-tree", DirectoryTree)
            self._show_folder(Path(tree.path).resolve().parent)
        elif event.button.id == "btn-picker-open":
            tree = self.query_one("#picker-tree", DirectoryTree)
            node = tree.cursor_node
            if tree.has_focus and node is not None and node.data is not None:
                self._choose(str(node.data.path))
            else:
                self._choose(self.query_one("#picker-path", Input).value)
        else:
            self.dismiss(None)
