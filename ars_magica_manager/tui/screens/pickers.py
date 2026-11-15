"""Pickers: the searchable catalog pickers, the row picker used by
Remove/Edit/Restore, and the CSV file picker."""

from __future__ import annotations

import asyncio
from collections import Counter
from collections.abc import Callable, Collection, Iterable, Sequence
from pathlib import Path
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Key
from textual.widgets import (
    Button,
    Checkbox,
    DirectoryTree,
    Input,
    Label,
    ListItem,
    ListView,
    OptionList,
    Select,
    SelectionList,
    Static,
)
from textual.widgets.option_list import Option

from ... import catalog, sourcebooks
from ... import laboratories as labs
from ... import saga_content as sc
from ... import sheet_text as st
from ... import spells as spl
from ...boon_hook_text import boon_hook_entry_text, boon_hook_names
from ...forms import covenant as covenant_forms
from ...forms import virtue as virtue_forms
from ...hosting import ConfinedFolder
from ...markup import escape
from ...models import (
    VIRTUE_FLAW_TIER_COST,
    Ability,
    AbilityDef,
    CovenantBoonHookDef,
    Laboratory,
    LabVirtueFlawDef,
    Saga,
    SagaSource,
    ShapeMaterialBonus,
    ShapeMaterialDef,
    Spell,
    VirtueFlawDef,
    VirtueFlawInstance,
)
from ...rules import creation_access as access
from ...rules.vf_eligibility import VirtueFlawChooser
from .fields import FieldsDialog, ModalDialog
from .prompts import (
    _ability_dialog,
    _ability_from,
    _lab_choice_dialog,
    _param_dialog,
    param_choices,
)

_VIRTUE_FLAW_ITEM_ID_PREFIX = "vf-"


_LAB_VIRTUE_FLAW_ITEM_ID_PREFIX = "labvf-"


_ABILITY_ITEM_ID_PREFIX = "ability-"


_REMOVAL_ITEM_ID_PREFIX = "remove-"


_COVENANT_BOON_HOOK_ITEM_ID_PREFIX = "covbhpick-"


class SearchablePickerScreen[EntryT, ResultT](ModalDialog[ResultT]):
    """Base for a catalog picker: a list with a live-filtering search box
    above it.

    The catalogs are large (1,100 Virtues/Flaws, 1,300 spells) -- a flat
    unsearchable list doesn't scale, so every catalog picker shares this:
    an Input above the list that re-filters it on every keystroke. The list
    is an OptionList, which draws only the rows on screen: a ListView
    mounts a widget per row, and took seconds to list every spell.
    Subclasses supply the entry list and how to search/render/activate
    each one; this owns the Input<->list wiring, so that trickier bit
    (live rebuild, keeping the search box focused and typable while
    letting Down/Enter reach the list) only has to be gotten right once.

    Subclasses set `PICKER_TITLE`, `EMPTY_MESSAGE` and `SEARCH_PLACEHOLDER`
    (the defaults for the matching constructor arguments), `LIST_VIEW_ID`
    (kept distinct per picker, not shared, so existing tests that query e.g.
    "#vf-picker-list" by id keep working) and the `_load_entries`/
    `_search_text`/`_label_for`/`_item_id`/`_on_entry_selected` hooks below
    (an entry's item id is its option's id). A picker that shows the
    highlighted entry's details under the list sets `DETAILS_HEIGHT` (its
    rows) and `_details`. A picker with filters beside the search box also
    overrides `_compose_filters`/`_compose_below_list`/`_candidates`/
    `_match`/`_filled`.
    Generic over the catalog entry type and the dialog's result.

    Given the saga's `books` in play (sourcebooks.saga_books; None: every
    book), entries whose books are all out of play are hidden, with F3 to
    list them too, marked; a subclass says where an entry is
    from with `_source`. So are the entries the saga hides (catalog.hidden).
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("f3", "toggle_other_books", "Show other books"),
    ]

    PICKER_TITLE: ClassVar[str] = "Pick"
    EMPTY_MESSAGE: ClassVar[str] = "(nothing available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search..."
    LIST_VIEW_ID: ClassVar[str] = "picker-list"
    #: The details panel's height in rows; 0: no panel.
    DETAILS_HEIGHT: ClassVar[int] = 0

    DEFAULT_CSS = """
    SearchablePickerScreen {
        align: center middle;
    }

    #picker-dialog {
        width: 76;
        height: auto;
        max-height: 28;
        padding: 1 2;
    }

    #picker-search {
        margin-bottom: 1;
    }

    SearchablePickerScreen #picker-dialog > OptionList {
        height: 1fr;
    }

    #picker-books {
        color: $text-muted;
    }

    SearchablePickerScreen.-with-details #picker-dialog {
        width: 100;
        max-height: 40;
    }

    #picker-details {
        margin-top: 1;
    }
    """

    def __init__(
        self,
        title: str = "",
        *,
        empty_message: str = "",
        search_placeholder: str = "",
        books: frozenset[str] | None = None,
    ) -> None:
        super().__init__()
        if self.DETAILS_HEIGHT:
            self.add_class("-with-details")
        self.picker_title = title or self.PICKER_TITLE
        #: The books in play (None: every book), whether entries from other
        #: books are listed too (F3), and how many the last refill hid.
        self._books = books
        #: Whether anything can be left out: books narrowed, or entries the
        #: saga hides.
        self._narrowed = books is not None or catalog.hides_any()
        self._show_other_books = False
        self._other_books = 0
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
        with Vertical(id="picker-dialog", classes="dialog-box"):
            yield Label(self.picker_title, id="picker-title", classes="dialog-title")
            yield Input(placeholder=self.search_placeholder, id="picker-search")
            yield from self._compose_filters()
            yield OptionList(id=self.LIST_VIEW_ID, compact=True)
            yield from self._compose_below_list()
            if self.DETAILS_HEIGHT:
                with VerticalScroll(id="picker-details") as details:
                    details.styles.height = self.DETAILS_HEIGHT
                    yield Static(id="picker-details-text")
            if self._narrowed:
                yield Static(id="picker-books")
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

    def _details(self, entry: EntryT) -> str:
        """The highlighted entry's details, under the list (with
        DETAILS_HEIGHT set)."""
        return ""

    def _source(self, entry: EntryT) -> str:
        """The book(s) `entry` is from ("": none, always in play)."""
        return ""

    # -- optional hooks, for a picker with filters --

    def _compose_filters(self) -> ComposeResult:
        """Widgets between the search box and the list."""
        yield from ()

    def _compose_below_list(self) -> ComposeResult:
        """Widgets between the list and the Cancel button."""
        yield from ()

    def _candidates(self) -> list[EntryT]:
        """The entries the filters let through, before the search text:
        those from books in play, unless F3 lists the others too."""
        in_play = [e for e in self._entries if self._in_play(e)]
        self._other_books = len(self._entries) - len(in_play)
        return self._entries if self._show_other_books else in_play

    def _in_play(self, entry: EntryT) -> bool:
        return sourcebooks.in_play(
            self._source(entry), self._books
        ) and not catalog.hidden(entry)

    def _out_of_play_note(self, entry: EntryT) -> str:
        """Why an entry listed with F3 is out of play."""
        if catalog.hidden(entry):
            return "hidden in this saga"
        return "book not in play"

    def action_toggle_other_books(self) -> None:
        if not self._narrowed:
            return
        self._show_other_books = not self._show_other_books
        self.run_worker(
            self._render_list(self.query_one("#picker-search", Input).value),
            exclusive=True,
            group="picker-books",
        )

    def _update_books_note(self) -> None:
        if not self._narrowed:
            return
        what = (
            "from books not in play or hidden in this saga"
            if catalog.hides_any()
            else "from books not in play"
        )
        if self._show_other_books:
            note = f"{self._other_books} {what} marked (F3 hides them)"
        else:
            note = f"{self._other_books} {what} hidden (F3 shows them)"
        self.query_one("#picker-books", Static).update(note)

    def _match(self, entries: list[EntryT], needle: str) -> list[EntryT]:
        """The `entries` the (lower-cased) search text matches, in order."""
        return [e for e in entries if needle in self._search_text(e).lower()]

    def _filled(self, shown: list[EntryT]) -> None:
        """Called with the entries listed after each refill."""

    def _heading(self, entry: EntryT) -> str:
        """The heading `entry` is listed under ("": none); a heading is
        shown above the first entry of each run that shares it."""
        return ""

    def _show_details(self, entry: EntryT | None) -> None:
        """Show `entry`'s details under the list (None: a message row, or
        nothing listed)."""
        if self.DETAILS_HEIGHT:
            text = self._details(entry) if entry is not None else ""
            self.query_one("#picker-details-text", Static).update(text)

    # -- filtering / list rendering --

    async def _render_list(self, query: str) -> None:
        self._render_generation += 1
        generation = self._render_generation
        async with self._render_lock:
            if generation == self._render_generation:
                await self._fill_list(query)

    def _option_list(self) -> OptionList:
        return self.query_one(f"#{self.LIST_VIEW_ID}", OptionList)

    def shown_ids(self) -> list[str]:
        """The listed entries' item ids, in order (message rows left out)."""
        option_list = self._option_list()
        return [
            option.id
            for option in (
                option_list.get_option_at_index(index)
                for index in range(option_list.option_count)
            )
            if option.id is not None
        ]

    def highlight(self, item_id: str) -> None:
        """Move the highlight to the entry with this item id."""
        option_list = self._option_list()
        option_list.highlighted = option_list.get_option_index(item_id)

    async def _fill_list(self, query: str) -> None:
        option_list = self._option_list()
        option_list.clear_options()
        self._by_item_id = {}

        if not self._entries:
            self._filled([])
            self._show_details(None)
            option_list.add_option(Option(self.empty_message, disabled=True))
            return

        needle = query.strip().lower()
        candidates = self._candidates()
        self._update_books_note()
        matches = self._match(candidates, needle) if needle else candidates
        self._filled(matches)
        self._show_details(matches[0] if matches else None)
        if not matches:
            message = (
                f"(no matches for {escape(repr(query))})"
                if needle
                else "(nothing matches the filters)"
            )
            option_list.add_option(Option(message, disabled=True))
            return

        options = []
        heading = ""
        for entry in matches:
            if (under := self._heading(entry)) and under != heading:
                options.append(Option(f"[b]{escape(under)}[/]", disabled=True))
            heading = under
            item_id = self._item_id(entry)
            self._by_item_id[item_id] = entry
            label = self._label_for(entry)
            if not self._in_play(entry):
                label += f"  [dim]({self._out_of_play_note(entry)})[/]"
            options.append(Option(label, id=item_id))
        option_list.add_options(options)
        option_list.highlighted = next(
            index for index, option in enumerate(options) if not option.disabled
        )

    async def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "picker-search":
            await self._render_list(event.value)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        # Enter in the search box activates the top (highlighted) match,
        # the same way arrowing down to it and pressing Enter would.
        if event.input.id != "picker-search":
            return
        option = self._option_list().highlighted_option
        if option is not None:
            await self._activate(option.id)

    def on_key(self, event: Key) -> None:
        # Input has no "down" binding of its own, so it would otherwise
        # just bubble and do nothing -- forward it to move focus into the
        # (already-filtered) list, the natural next step after typing.
        if event.key != "down":
            return
        search = self.query_one("#picker-search", Input)
        if self.focused is not search:
            return
        option_list = self._option_list()
        if option_list.option_count:
            option_list.focus()
            event.stop()

    # -- selection / dismissal --

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()

    # A filter's Select has an OptionList of its own: only the picker's
    # list counts.

    async def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        if event.option_list.id == self.LIST_VIEW_ID:
            await self._activate(event.option_id)

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        if event.option_list.id == self.LIST_VIEW_ID:
            option_id = event.option_id
            self._show_details(self._by_item_id.get(option_id) if option_id else None)

    async def _activate(self, item_id: str | None) -> None:
        if item_id is None:
            return
        entry = self._by_item_id.get(item_id)
        if entry is None:
            return
        self._on_entry_selected(entry)


#: The picker's "Show" choices: one side of the ledger, or both.
_VF_SIDES: list[tuple[str, str]] = [
    ("Virtues", "Virtue"),
    ("Flaws", "Flaw"),
    ("Virtues & Flaws", "both"),
]
_VF_SIDE_TITLES: dict[str, str] = {
    "Virtue": "Add a Virtue",
    "Flaw": "Add a Flaw",
    "both": "Add a Virtue or Flaw",
}
#: The core book's Virtue/Flaw types, listed first in the Type filter.
_VF_CORE_TYPES: tuple[str, ...] = (
    "General",
    "Hermetic",
    "Supernatural",
    "Social Status",
    "Personality",
    "Story",
    "Tainted",
)


def _vf_types(entries: Sequence[VirtueFlawDef]) -> list[str]:
    """Every printed type among `entries`: the core book's in its order,
    then the supplements' alphabetically."""
    printed = {t for e in entries for t in (e.category, *e.extra_categories)}
    core = [t for t in _VF_CORE_TYPES if t in printed]
    return core + sorted(printed - set(core))


def _hidden_note(entry: Any) -> str:
    """Why nobody in particular can take `entry`: the saga hides it."""
    return "hidden in this saga" if catalog.hidden(entry) else ""


class VirtueFlawPickerScreen(
    SearchablePickerScreen[VirtueFlawDef, VirtueFlawInstance | None]
):
    """Pick a character Virtue/Flaw from the catalog, prompting for
    parameters if needed. Dismisses with the new instance, or None if
    cancelled.

    Opened on one side (Virtues or Flaws, from the section it was launched
    from), with a filter bar: that side or both (F2 cycles), a printed type,
    a tier, and whether to list the entries `chooser` can't take (F3), each
    marked with why (VirtueFlawChooser). The search also matches
    each entry's summary, which shows under the list for the chosen row.

    Laboratories have their own, separate Virtue/Flaw catalog and picker
    -- see LabVirtueFlawPickerScreen -- since a lab's Virtues & Flaws
    (ArM5 Covenants, Chapter 9) are a completely different list from a character's
    (Chapter 4), even though both use the same VirtueFlawInstance shape
    and Free/Minor/Major tiers.
    """

    EMPTY_MESSAGE: ClassVar[str] = "(no more Virtues/Flaws available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search names, types and summaries..."
    LIST_VIEW_ID: ClassVar[str] = "vf-picker-list"
    DETAILS_HEIGHT: ClassVar[int] = 12

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("f2", "cycle_side", "Virtues/Flaws/Both"),
        Binding("f3", "toggle_ineligible", "Show ineligible"),
    ]

    DEFAULT_CSS = """
    VirtueFlawPickerScreen #picker-search {
        margin-bottom: 0;
    }

    VirtueFlawPickerScreen #vf-picker-filters {
        width: 1fr;
        height: 1;
        margin: 1 0 0 0;
    }

    VirtueFlawPickerScreen #vf-picker-filters Select {
        margin-right: 2;
    }

    VirtueFlawPickerScreen #vf-picker-side {
        width: 19;
    }

    VirtueFlawPickerScreen #vf-picker-type {
        width: 28;
    }

    VirtueFlawPickerScreen #vf-picker-tier {
        width: 14;
    }

    VirtueFlawPickerScreen #vf-picker-status {
        color: $text-muted;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        taken: Sequence[VirtueFlawInstance] = (),
        *,
        side: str = "both",
        chooser: VirtueFlawChooser | None = None,
        own_abilities: Sequence[str] = (),
        refusal: Callable[[VirtueFlawInstance], str] | None = None,
    ) -> None:
        super().__init__(_VF_SIDE_TITLES[side])
        #: The character's own Abilities, offered with the catalog's when a
        #: Virtue or Flaw names an {ability}.
        self._own_abilities = list(own_abilities)
        #: The character's Virtues & Flaws: an entry already taken is only
        #: offered again if it is repeatable (catalog.virtue_flaw_offerable),
        #: and a repeat is refused past its limits once its parameters are
        #: known (catalog.virtue_flaw_repeat_refusal).
        self._taken = list(taken)
        #: Who is choosing; None: nobody in particular, everything is offered.
        self._chooser = chooser
        #: Why the chooser can't take an entry with given parameters, from
        #: their own scores ("Great Intelligence needs Intelligence at
        #: +3"); "" if they can. Choices it refuses are not offered.
        self._instance_refusal = refusal
        self._catalog = catalog.virtue_flaws_by_name(catalog.load_virtue_flaw_catalog())
        #: Why the chooser can't take an entry, by id ("" if it can).
        self._refusals: dict[str, str] = {}
        # The filters: "Virtue", "Flaw" or "both"; a printed type and a
        # tier (None: any); and whether ineligible entries are listed.
        self._side = side
        self._type: str | None = None
        self._tier: str | None = None
        self._show_ineligible = False
        self._hidden = 0

    # -- the filter bar --

    def _compose_filters(self) -> ComposeResult:
        with Horizontal(id="vf-picker-filters"):
            yield Select(
                _VF_SIDES,
                value=self._side,
                allow_blank=False,
                id="vf-picker-side",
                compact=True,
            )
            yield Select(
                [(t, t) for t in _vf_types(self._catalog)],
                prompt="Type: any",
                id="vf-picker-type",
                compact=True,
            )
            yield Select(
                [(tier, tier) for tier in VIRTUE_FLAW_TIER_COST],
                prompt="Tier: any",
                id="vf-picker-tier",
                compact=True,
            )
            yield Checkbox("Show ineligible", id="vf-picker-ineligible", compact=True)
        yield Static(id="vf-picker-status")

    def action_cycle_side(self) -> None:
        sides = [value for _, value in _VF_SIDES]
        following = sides[(sides.index(self._side) + 1) % len(sides)]
        self.query_one("#vf-picker-side", Select).value = following

    def action_toggle_ineligible(self) -> None:
        self.query_one("#vf-picker-ineligible", Checkbox).toggle()

    async def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()
        value = event.value if isinstance(event.value, str) else None
        before = (self._side, self._type, self._tier)
        if event.select.id == "vf-picker-side" and value is not None:
            self._side = value
            self.query_one("#picker-title", Label).update(_VF_SIDE_TITLES[value])
        elif event.select.id == "vf-picker-type":
            self._type = value
        elif event.select.id == "vf-picker-tier":
            self._tier = value
        if (self._side, self._type, self._tier) != before:
            await self._refilter()

    async def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        event.stop()
        self._show_ineligible = event.value
        await self._refilter()

    async def _refilter(self) -> None:
        if self.is_mounted:
            await self._render_list(self.query_one("#picker-search", Input).value)

    # -- the searchable list --

    def _load_entries(self) -> list[VirtueFlawDef]:
        entries = [
            entry
            for entry in self._catalog
            if catalog.virtue_flaw_offerable(entry, self._taken)
        ]
        chooser = self._chooser
        self._refusals = {
            entry.id: (chooser.refusal(entry) if chooser else _hidden_note(entry))
            or self._no_choice_left(entry)
            for entry in entries
        }
        return entries

    def _choices(self, entry: VirtueFlawDef) -> dict[str, list[tuple[str, str]]]:
        """The parameter choices offered for `entry`: a lone parameter's
        values the chooser's own refusal turns down are left out."""
        found = param_choices(entry, self._taken, self._own_abilities)
        refusal = self._instance_refusal
        if refusal is not None and len(entry.parameters) == 1:
            param = entry.parameters[0]
            if param in found:
                found[param] = [
                    (label, value)
                    for label, value in found[param]
                    if not refusal(VirtueFlawInstance(entry.id, {param: value}))
                ]
        return found

    def _no_choice_left(self, entry: VirtueFlawDef) -> str:
        """Why `entry` is ineligible when the chooser's own refusal turns
        down every value of its lone parameter ("" otherwise)."""
        if self._instance_refusal is None or len(entry.parameters) != 1:
            return ""
        param = entry.parameters[0]
        if param != "characteristic":
            return ""
        if self._choices(entry).get(param):
            return ""
        return "no Characteristic qualifies"

    def _candidates(self) -> list[VirtueFlawDef]:
        listed = [
            entry
            for entry in self._entries
            if self._side in ("both", entry.side)
            and (
                self._type is None
                or self._type in (entry.category, *entry.extra_categories)
            )
            and self._tier in (None, entry.tier)
        ]
        eligible = [entry for entry in listed if not self._refusals[entry.id]]
        self._hidden = len(listed) - len(eligible)
        return listed if self._show_ineligible else eligible

    def _match(self, entries: list[VirtueFlawDef], needle: str) -> list[VirtueFlawDef]:
        """Entries whose name matches come first, then the rest (their type
        or summary matches)."""
        matches = super()._match(entries, needle)
        return sorted(matches, key=lambda entry: needle not in entry.name.lower())

    def _filled(self, shown: list[VirtueFlawDef]) -> None:
        if self._show_ineligible:
            hidden = f"{self._hidden} ineligible marked (F3 hides them)"
        else:
            hidden = f"{self._hidden} ineligible hidden (F3 shows them)"
        self.query_one("#vf-picker-status", Static).update(
            f"{len(shown)} listed, {hidden}.  F2: Virtues / Flaws / Both"
        )

    def _details(self, entry: VirtueFlawDef) -> str:
        """The entry's book text (its summary if it has none), source and
        (if any) why it's ineligible."""
        facts = [f"Source: {entry.source}"]
        if refusal := self._refusals.get(entry.id):
            facts.append(f"Ineligible: {refusal}")
        text = entry.description or entry.summary
        return f"[dim]{escape('   '.join(facts))}[/]\n{escape(text)}"

    def _search_text(self, entry: VirtueFlawDef) -> str:
        return (
            f"{entry.name} {entry.type} {entry.category_label} {entry.tier} "
            f"{entry.summary}"
        )

    def _label_for(self, entry: VirtueFlawDef) -> str:
        needs = catalog.needs_note(entry.name, entry.parameters)
        facts = f"{entry.tier} {entry.type}, {entry.category_label}"
        label = escape(f"{catalog.blank_name(entry.name)}  [{facts}]{needs}")
        if refusal := self._refusals.get(entry.id):
            label += f"  [dim]({escape(refusal)})[/]"
        return label

    def _item_id(self, entry: VirtueFlawDef) -> str:
        return f"{_VIRTUE_FLAW_ITEM_ID_PREFIX}{entry.id}"

    def _on_entry_selected(self, entry: VirtueFlawDef) -> None:
        if not entry.parameters:
            self._add(entry, {})
            return

        def handle_params(params: dict[str, str] | None) -> None:
            if params is not None:
                self._add(entry, params)

        self.app.push_screen(
            _param_dialog(
                catalog.blank_name(entry.name), entry.parameters, self._choices(entry)
            ),
            handle_params,
        )

    def _add(self, entry: VirtueFlawDef, params: dict[str, str]) -> None:
        """Dismiss with the new instance, unless it's a repeat the book
        doesn't allow: then say why and stay open to pick again."""
        instance = VirtueFlawInstance(vf_id=entry.id, params=params)
        refusal = catalog.virtue_flaw_repeat_refusal(entry, self._taken, params)
        if not refusal and self._instance_refusal is not None:
            refusal = self._instance_refusal(instance)
        if refusal:
            self.app.notify(refusal, severity="warning")
            return
        self.dismiss(instance)


class LabVirtueFlawPickerScreen(
    SearchablePickerScreen[LabVirtueFlawDef, VirtueFlawInstance | None]
):
    """Pick a Laboratory Virtue/Flaw from the lab catalog (ArM5 Covenants, Chapter 9
    -- Structure/Outfittings/Supernatural). Dismisses with the new
    instance, or None if cancelled.

    An entry that asks for something (a Specialization, a Servant's grog
    or Intelligence) opens _lab_choice_dialog. `repeatable` entries (asterisked in the
    book -- Feature*, Person*, etc.) aren't excluded just because one's
    already attached, the same way templated character entries aren't.
    """

    PICKER_TITLE: ClassVar[str] = "Add a Laboratory Virtue or Flaw"
    EMPTY_MESSAGE: ClassVar[str] = "(no more Virtues/Flaws available)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search Laboratory Virtues & Flaws..."
    LIST_VIEW_ID: ClassVar[str] = "lab-vf-picker-list"
    DETAILS_HEIGHT: ClassVar[int] = 10

    def __init__(
        self,
        exclude_ids: set[str] | None = None,
        *,
        books: frozenset[str] | None = None,
        saga: Saga | None = None,
        lab: Laboratory | None = None,
    ) -> None:
        super().__init__(books=books)
        self._exclude_ids = exclude_ids or set()
        self._saga, self._lab = saga, lab

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

    def _source(self, entry: LabVirtueFlawDef) -> str:
        return entry.source

    def _details(self, entry: LabVirtueFlawDef) -> str:
        return labs.vf_entry_text(entry)

    def _on_entry_selected(self, entry: LabVirtueFlawDef) -> None:
        if not virtue_forms.lab_needs_input(entry):
            self.dismiss(VirtueFlawInstance(vf_id=entry.id))
            return

        def handle_choice(params: dict[str, str] | None) -> None:
            if params is not None:
                self.dismiss(VirtueFlawInstance(vf_id=entry.id, params=params))

        self.app.push_screen(
            _lab_choice_dialog(entry, self._saga, self._lab), handle_choice
        )


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
    DETAILS_HEIGHT: ClassVar[int] = 10

    def __init__(
        self,
        kind: str,
        attached_ids: list[str] | None = None,
        *,
        books: frozenset[str] | None = None,
    ) -> None:
        super().__init__(
            f"Add a {kind}",
            empty_message=f"(no more {kind}s available)",
            search_placeholder=f"Search {kind}s...",
            books=books,
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
        return boon_hook_names(ids, self._by_id)

    def _label_for(self, entry: CovenantBoonHookDef) -> str:
        facts = [entry.category] if entry.category else []
        facts.append(entry.tier)
        if entry.cost:
            facts.append(f"{abs(entry.cost):g} pt")
        label = f"{entry.name}  [{', '.join(facts)}]"
        if entry.requires:
            label += f"  (requires: {self._names(entry.requires)})"
        if entry.requires_any:
            label += f"  (requires one of: {self._names(entry.requires_any)})"
        if entry.excludes:
            label += f"  (not with: {self._names(entry.excludes)})"
        if entry.unknown:
            label += "  (may be Unknown)"
        if self._taken[entry.id]:
            label += f"  (taken x{self._taken[entry.id]})"
        return label

    def _item_id(self, entry: CovenantBoonHookDef) -> str:
        return f"{_COVENANT_BOON_HOOK_ITEM_ID_PREFIX}{entry.id}"

    def _source(self, entry: CovenantBoonHookDef) -> str:
        return entry.source

    def _details(self, entry: CovenantBoonHookDef) -> str:
        return boon_hook_entry_text(entry, self._by_id)

    def _on_entry_selected(self, entry: CovenantBoonHookDef) -> None:
        def handle_detail(result: dict[str, Any] | None) -> None:
            if result is None:
                return  # cancelled: back to the picker
            params = covenant_forms.boon_hook_entry_params(entry, result)
            self.dismiss(VirtueFlawInstance(vf_id=entry.id, params=params))

        self.app.push_screen(
            FieldsDialog(
                f"{self.kind}: {escape(entry.name)}",
                covenant_forms.boon_hook_entry_fields(entry),
            ),
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
    DETAILS_HEIGHT: ClassVar[int] = 10

    def __init__(
        self,
        exclude_names: set[str] | None = None,
        *,
        books: frozenset[str] | None = None,
        virtues_flaws: Sequence[VirtueFlawInstance] = (),
        ask_details: bool = True,
        only: Collection[str] | None = None,
    ) -> None:
        """`ask_details`: False dismisses with the chosen Ability at once,
        with no xp or Specialty asked (a form that only needs which one).
        `only`: offer just the Abilities of these catalog names (a
        tradition's own)."""
        super().__init__(books=books)
        self._exclude_names = exclude_names or set()
        self._only = None if only is None else set(only)
        # the owner's, for Puissant and Affinity in the xp's live score
        self._virtues_flaws = virtues_flaws
        self._ask_details = ask_details

    def _load_entries(self) -> list[AbilityDef]:
        entries = catalog.abilities_to_offer(self._exclude_names)
        if self._only is None:
            return entries
        return [e for e in entries if e.name in self._only]

    def _search_text(self, entry: AbilityDef) -> str:
        return f"{entry.name} {entry.category}"

    def _label_for(self, entry: AbilityDef) -> str:
        needs = catalog.needs_note(entry.name, entry.parameters)
        return f"{entry.name}  [{entry.category}]{needs}"

    def _item_id(self, entry: AbilityDef) -> str:
        return f"{_ABILITY_ITEM_ID_PREFIX}{entry.id}"

    def _source(self, entry: AbilityDef) -> str:
        return entry.source

    def _details(self, entry: AbilityDef) -> str:
        return st.ability_entry_text(entry)

    def _on_entry_selected(self, entry: AbilityDef) -> None:
        if entry.parameters:

            def handle_params(params: dict[str, str] | None) -> None:
                if params is not None:
                    self._prompt_details(
                        catalog.resolve_ability_name(entry, params), entry.category
                    )

            self.app.push_screen(
                _param_dialog(catalog.blank_name(entry.name), entry.parameters),
                handle_params,
            )
        else:
            self._prompt_details(entry.name, entry.category)

    def _prompt_details(self, name: str, category: str) -> None:
        if not self._ask_details:
            self.dismiss(
                Ability(
                    name=name,
                    category=category,
                    xp_table=access.ability_xp_table(name),
                )
            )
            return

        def handle_ability(result: dict[str, Any] | None) -> None:
            if result is not None:
                self.dismiss(_ability_from(name, category, result))

        self.app.push_screen(
            _ability_dialog(name, None, self._virtues_flaws, save_label="Confirm"),
            handle_ability,
        )


class CatalogEntryPickerScreen(SearchablePickerScreen[Any, str | None]):
    """Pick a shared entry of one catalog (saga_content.CATALOGS) for the
    saga to hide: every entry not hidden yet, whatever its book, searchable
    by name or book. Dismisses with the entry's id."""

    PICKER_TITLE: ClassVar[str] = "Hide an Entry"
    EMPTY_MESSAGE: ClassVar[str] = "(every entry is hidden already)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search by name or book..."
    LIST_VIEW_ID: ClassVar[str] = "catalog-entry-picker-list"

    def __init__(self, saga: Saga, key: str) -> None:
        info = sc.CATALOGS[key]
        super().__init__(f"Hide an Entry: {info.label}")
        # Lists every entry: what's hidden or out of play is the point here.
        self._narrowed = False
        self._saga = saga
        self._key = key

    def _load_entries(self) -> list[Any]:
        hidden = set(self._saga.hidden_entries.get(self._key, ()))
        entries = sc.CATALOGS[self._key].shared()
        return sorted((e for e in entries if e.id not in hidden), key=lambda e: e.name)

    def _in_play(self, entry: Any) -> bool:
        return True

    def _search_text(self, entry: Any) -> str:
        return f"{entry.name} {getattr(entry, 'source', '')}"

    def _label_for(self, entry: Any) -> str:
        source = getattr(entry, "source", "")
        return escape(f"{entry.name}  [{source}]" if source else entry.name)

    def _item_id(self, entry: Any) -> str:
        return f"hide-{entry.id}"

    def _on_entry_selected(self, entry: Any) -> None:
        self.dismiss(entry.id)


class SpellChooserScreen(SearchablePickerScreen[Spell, str | None]):
    """Pick a spell -- for a Lab Text or Casting Tablet, or a spell a magus
    knows: every spell there is (the catalog, the saga's own, any magus's
    invented spells) less any in `exclude`, searchable by name or shorthand.
    Dismisses with the spell id.

    The highlighted spell's details show under the list, so the choice is
    an informed one."""

    PICKER_TITLE: ClassVar[str] = "Choose the spell"
    EMPTY_MESSAGE: ClassVar[str] = "(no spells)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search spells by name or Arts (e.g. CrIg)..."
    LIST_VIEW_ID: ClassVar[str] = "spell-chooser-list"
    DETAILS_HEIGHT: ClassVar[int] = 12

    def __init__(
        self,
        saga: Saga,
        *,
        exclude: set[str] | None = None,
        title: str = "",
        details: Callable[[Spell], str] | None = None,
    ) -> None:
        """`details`: an extra line (e.g. a creation Lab Total) after the
        highlighted spell's details."""
        super().__init__(title, books=sourcebooks.saga_books(saga))
        self.saga = saga
        self.exclude = exclude or set()
        self._origin: dict[str, str] = {}
        self._extra_details = details

    def _details(self, entry: Spell) -> str:
        text = spl.detail_text(self.saga, entry)
        if self._extra_details is not None:
            text += "\n" + self._extra_details(entry)
        return text

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

    def _source(self, entry: Spell) -> str:
        """A catalog spell's book; the saga's own and invented spells are
        always in play."""
        return entry.source if self._origin.get(entry.id) == entry.source else ""

    def _on_entry_selected(self, entry: Spell) -> None:
        self.dismiss(entry.id)


class ShapeMaterialPickerScreen(
    SearchablePickerScreen[
        tuple[ShapeMaterialDef, int | None], ShapeMaterialBonus | None
    ]
):
    """Pick one bonus from DE's Shape and Material Bonuses Table:
    a row per (shape or material, bonus), searchable by either. Dismisses
    with the bonus as a ShapeMaterialBonus (a row with no bonus, e.g. Living
    Tree, gives its note and +0)."""

    PICKER_TITLE: ClassVar[str] = "Choose a Shape & Material bonus"
    EMPTY_MESSAGE: ClassVar[str] = "(no bonuses)"
    SEARCH_PLACEHOLDER: ClassVar[str] = "Search shapes, materials or effects..."
    LIST_VIEW_ID: ClassVar[str] = "shape-material-list"

    def _load_entries(self) -> list[tuple[ShapeMaterialDef, int | None]]:
        entries: list[tuple[ShapeMaterialDef, int | None]] = []
        for row in catalog.load_shape_material_catalog():
            if not row.bonuses:
                entries.append((row, None))
            entries += [(row, index) for index in range(len(row.bonuses))]
        return entries

    @staticmethod
    def _bonus(entry: tuple[ShapeMaterialDef, int | None]) -> ShapeMaterialBonus:
        row, index = entry
        if index is None:
            return ShapeMaterialBonus(0, row.note, row.name)
        bonus, effect = row.bonuses[index]
        return ShapeMaterialBonus(bonus, effect, row.name)

    def _search_text(self, entry: tuple[ShapeMaterialDef, int | None]) -> str:
        bonus = self._bonus(entry)
        return f"{bonus.shape} {bonus.applies_to}"

    def _label_for(self, entry: tuple[ShapeMaterialDef, int | None]) -> str:
        bonus = self._bonus(entry)
        figure = f"{bonus.bonus:+d} " if entry[1] is not None else ""
        return f"{escape(bonus.shape)}  [dim]{figure}{escape(bonus.applies_to)}[/]"

    def _item_id(self, entry: tuple[ShapeMaterialDef, int | None]) -> str:
        row, index = entry
        return f"smpick-{row.id}-{'note' if index is None else index}"

    def _source(self, entry: tuple[ShapeMaterialDef, int | None]) -> str:
        return entry[0].source

    def _on_entry_selected(self, entry: tuple[ShapeMaterialDef, int | None]) -> None:
        self.dismiss(self._bonus(entry))


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
        padding: 1 2;
    }
    """

    def __init__(self, title: str, labels: list[str]) -> None:
        super().__init__()
        self.prompt_title = title
        self.labels = labels

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog", classes="dialog-box"):
            yield Label(self.prompt_title, id="picker-title", classes="dialog-title")
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


class SourcebookPickerScreen(ModalDialog[list[str] | None]):
    """Tick the supplements and saga sources a saga has in play; the core
    book is always in play. Dismisses with the ticked abbreviations (every
    one of them: every book), or None if cancelled."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("f2", "tick_all", "All"),
        Binding("f3", "tick_none", "None"),
    ]

    DEFAULT_CSS = """
    SourcebookPickerScreen {
        align: center middle;
    }

    #books-dialog {
        width: 76;
        height: auto;
        max-height: 40;
        padding: 1 2;
    }

    #books-list {
        height: auto;
        max-height: 26;
    }

    #books-hint {
        color: $text-muted;
        margin: 1 0;
    }

    #books-buttons {
        width: auto;
        height: auto;
    }
    """

    def __init__(
        self, books_in_play: list[str] | None, sources: Sequence[SagaSource] = ()
    ) -> None:
        super().__init__()
        #: Every book that can be ticked: abbreviation -> its line.
        self._books = {
            **{
                book: f"{sourcebooks.SOURCEBOOKS[book]} ({book})"
                for book in sourcebooks.SUPPLEMENTS
            },
            **{
                s.abbreviation: f"{s.title or s.abbreviation} ({s.abbreviation}, "
                "the saga's own)"
                for s in sources
            },
        }
        self._ticked = set(self._books if books_in_play is None else books_in_play)

    def compose(self) -> ComposeResult:
        with Vertical(id="books-dialog", classes="dialog-box"):
            yield Label("Books in play", id="books-title", classes="dialog-title")
            yield SelectionList[str](
                *(
                    (escape(line), book, book in self._ticked)
                    for book, line in self._books.items()
                ),
                id="books-list",
            )
            yield Static(
                f"{sourcebooks.SOURCEBOOKS[sourcebooks.CORE]} is always in play. "
                "Space ticks a book; F2 ticks all, F3 none.",
                id="books-hint",
            )
            with Horizontal(id="books-buttons"):
                yield Button("Save", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel")

    #: Focused once composed (Textual's own auto focus), never looked up
    #: after the screen may have closed.
    AUTO_FOCUS = "#books-list"

    def action_tick_all(self) -> None:
        self.query_one("#books-list", SelectionList).select_all()

    def action_tick_none(self) -> None:
        self.query_one("#books-list", SelectionList).deselect_all()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.action_cancel()
        elif event.button.id == "btn-save":
            ticked = set(self.query_one("#books-list", SelectionList).selected)
            self.dismiss([b for b in self._books if b in ticked])


class _CsvDirectoryTree(DirectoryTree):
    """Folders and files of one kind only (.csv unless `suffix` says
    otherwise; hidden entries left out)."""

    def __init__(
        self, path: Path, *, suffix: tuple[str, ...] = (".csv",), id: str | None = None
    ):
        super().__init__(path, id=id)
        self.suffix = suffix

    def filter_paths(self, paths: Iterable[Path]):
        return [
            path
            for path in paths
            if not path.name.startswith(".")
            and (path.is_dir() or path.name.lower().endswith(self.suffix))
        ]


#: What a hosted copy's chooser says of a path outside its folder.
OUTSIDE_EXPORTS = "Only files in the exports folder can be chosen here."


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
        padding: 1 2;
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

    def __init__(
        self,
        title: str,
        start: Path,
        *,
        suffix: str | tuple[str, ...] = ".csv",
        confined: ConfinedFolder | None = None,
    ) -> None:
        super().__init__()
        self.title_text = title
        #: The folder it may not leave (a hosted copy's exports folder), or
        #: None to browse the whole computer.
        self.confined = confined
        self.start = confined.start(start) if confined is not None else start
        #: The kinds of file to choose (".json" and ".zip" for an export).
        found = (suffix,) if isinstance(suffix, str) else suffix
        self.suffix = tuple(s.lower() for s in found)

    def _shown(self, path: Path) -> str:
        return self.confined.show(path) if self.confined is not None else str(path)

    def _typed(self, raw: str) -> Path | None:
        """The path typed in the box; None if it is outside the folder the
        chooser keeps to."""
        if self.confined is not None:
            return self.confined.find(raw)
        return Path(raw.strip().strip('"')).expanduser()

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog", classes="dialog-box"):
            yield Label(self.title_text, id="picker-title", classes="dialog-title")
            with Horizontal(id="picker-path-row"):
                yield Button("Up", id="btn-picker-up", compact=True)
                yield Input(self._shown(self.start), id="picker-path", compact=True)
            yield _CsvDirectoryTree(self.start, suffix=self.suffix, id="picker-tree")
            yield Static("", id="picker-error")
            with Horizontal(id="picker-buttons"):
                yield Button("Open", id="btn-picker-open", variant="success")
                yield Button("Cancel", id="btn-picker-cancel")

    #: Focused once composed (see the books chooser's AUTO_FOCUS).
    AUTO_FOCUS = "#picker-tree"

    def _show_folder(self, folder: Path) -> None:
        self.query_one("#picker-tree", DirectoryTree).path = folder
        self.query_one("#picker-path", Input).value = self._shown(folder)
        self.query_one("#picker-error", Static).update("")

    def _choose(self, raw: str) -> None:
        """Open a typed folder, or pick a typed file of the right kind."""
        path = self._typed(raw)
        error = self.query_one("#picker-error", Static)
        if path is None:
            error.update(OUTSIDE_EXPORTS)
        elif path.is_dir():
            self._show_folder(path)
        elif path.is_file() and path.name.lower().endswith(self.suffix):
            self.dismiss(path)
        elif path.is_file():
            error.update(
                f"{escape(path.name)} isn't a {' or '.join(self.suffix)} file."
            )
        else:
            error.update(f"No such file or folder: {escape(self._shown_typed(raw))}")

    def _shown_typed(self, raw: str) -> str:
        return raw.strip() if self.confined is not None else str(self._typed(raw))

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        event.stop()
        if self.confined is not None and not self.confined.holds(event.path):
            self.query_one("#picker-error", Static).update(OUTSIDE_EXPORTS)
            return
        self.dismiss(event.path)

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        event.stop()
        if self.confined is None or self.confined.holds(event.path):
            self.query_one("#picker-path", Input).value = self._shown(event.path)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self._choose(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "btn-picker-up":
            tree = self.query_one("#picker-tree", DirectoryTree)
            folder = Path(tree.path)
            self._show_folder(
                self.confined.up(folder)
                if self.confined is not None
                else folder.resolve().parent
            )
        elif event.button.id == "btn-picker-open":
            tree = self.query_one("#picker-tree", DirectoryTree)
            node = tree.cursor_node
            if tree.has_focus and node is not None and node.data is not None:
                self._choose(str(node.data.path))
            else:
                self._choose(self.query_one("#picker-path", Input).value)
        else:
            self.dismiss(None)


class _FolderTree(DirectoryTree):
    """Folders only (hidden ones left out)."""

    def filter_paths(self, paths: Iterable[Path]):
        return [p for p in paths if p.is_dir() and not p.name.startswith(".")]


class FolderPickerScreen(CsvFilePickerScreen):
    """The file explorer for choosing a folder: Enter opens a folder, Up
    goes to the parent, the path box takes a typed folder (one that doesn't
    exist yet is made when it's used), and Choose takes the highlighted
    folder or the typed one. Dismisses with the folder, or None."""

    def compose(self) -> ComposeResult:
        with Vertical(id="picker-dialog", classes="dialog-box"):
            yield Label(self.title_text, id="picker-title", classes="dialog-title")
            with Horizontal(id="picker-path-row"):
                yield Button("Up", id="btn-picker-up", compact=True)
                yield Input(str(self.start), id="picker-path", compact=True)
            yield _FolderTree(self.start, id="picker-tree")
            yield Static("", id="picker-error")
            with Horizontal(id="picker-buttons"):
                yield Button("Choose", id="btn-picker-open", variant="success")
                yield Button("Cancel", id="btn-picker-cancel")

    def _choose(self, raw: str) -> None:
        path = Path(raw.strip().strip('"')).expanduser()
        if path.is_file():
            self.query_one("#picker-error", Static).update(
                f"{escape(path.name)} is a file, not a folder."
            )
        elif raw.strip():
            self.dismiss(path)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Enter in the path box shows a typed folder that exists; Choose
        # takes it.
        event.stop()
        path = Path(event.value.strip().strip('"')).expanduser()
        if path.is_dir():
            self._show_folder(path)
        else:
            self._choose(event.value)
