"""Widgets shared by the screens: the bottom bar, the selectable list, sheet
sections and layout rows, and small display helpers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical
from textual.events import Click
from textual.message import Message
from textual.widget import Widget
from textual.widgets import (
    Collapsible,
    Footer,
    OptionList,
    Static,
)
from textual.widgets.option_list import Option

from ..models import (
    CovenantBoonHookDef,
)


def _balance_colored(boon_points: float, hook_points: float, text: str) -> str:
    """Wraps `text` (a Boons/Hooks point total -- both share one colour) in
    the theme's colour for how the two compare: plain while Boons cost less
    than Hooks provide, $text-error once they cost more, $text-success when
    they exactly balance."""
    if boon_points < hook_points:
        return text
    colour = "$text-error" if boon_points > hook_points else "$text-success"
    return f"[{colour}]{text}[/]"


def _tier_text(entry: CovenantBoonHookDef) -> str:
    """ "Minor Boon (1 pt)", "Major Hook (3 pts)" or "Free Boon"."""
    points = abs(entry.cost)
    if not points:
        return f"{entry.tier} {entry.type}"
    return f"{entry.tier} {entry.type} ({points:g} {'pt' if points == 1 else 'pts'})"


def _boon_hook_names(ids: list[str], by_id: dict[str, CovenantBoonHookDef]) -> str:
    """Names of catalog entries, each listed once (Road/Urban exist at both
    tiers), for prerequisite/exclusion notes."""
    return ", ".join(dict.fromkeys(by_id[i].name for i in ids if i in by_id))


def _sign_colored(value: float, text: str) -> str:
    """Wraps `text` in Textual markup coloured by the sign of `value`, in
    the active theme's text colours: positive $text-success, negative
    $text-error, zero left plain."""
    if value == 0:
        return text
    colour = "$text-success" if value > 0 else "$text-error"
    return f"[{colour}]{text}[/]"


class ThemeBar(Static):
    """A one-line bar above the footer showing the app's active theme name."""

    DEFAULT_CSS = """
    ThemeBar {
        height: 1;
        content-align: left middle;
        padding: 0 1;
        color: $text-muted;
    }
    """

    def on_mount(self) -> None:
        self.watch(self.app, "theme", self._show_theme, init=True)

    def _show_theme(self, theme_name: str) -> None:
        self.update(f"Theme: {theme_name.replace('-', ' ').title()}")


class BottomBar(Vertical):
    """Docks the ThemeBar directly above the Footer.

    Both dock to the same screen edge independently otherwise (Textual's
    dock arrangement doesn't stack same-edge docked siblings -- they'd
    overlap on the same row), so this wraps them in one bottom-docked
    container where Footer's own `dock: bottom` pins it to the container's
    last row and ThemeBar, undocked, takes the row above it in normal flow.
    """

    DEFAULT_CSS = """
    BottomBar {
        dock: bottom;
        height: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield ThemeBar(id="theme-bar")
        yield Footer()


class SelectableList(OptionList):
    """The standard "selectable list" (see DESIGN.md, UI Conventions): rows
    that each carry a selector -- a dim `○`, or a blue bold `●` on the chosen
    row -- with at most one row chosen at a time.

    Rows are `(data index, label)` pairs: the data index is the entry's
    position in whatever list the sheet keeps its data in (it becomes the
    Option id, so a filtered list still maps back to the true entry), and
    the label is markup -- escape user text with `escape()` first. An empty
    list shows one disabled "(none recorded)" row.

    A row with a `None` data index is a **header**: a disabled, unselectable
    separator (bold text, no marker) for sections whose data doesn't split
    cleanly into two side-by-side lists (e.g. Abilities' several categories,
    unlike Virtues/Flaws' two). Headers are skipped by keyboard navigation
    the same way the empty-list placeholder already is.

    Choosing a row (arrow keys or click) moves the marker and posts
    `SelectableList.Chosen(data_index)`; the owning view reacts (fills a
    details panel...). Nothing is chosen until the user picks a row, and
    `set_rows()` clears the choice. Lists given the same `group` (e.g.
    Virtues and Flaws, which share one details panel) have one choice
    between them: choosing a row in one unchooses the others.

    With `multi=True`, rows can also be *checked* for acting on several at
    once: Space (or Ctrl+click) toggles a green check in front of a row,
    independently of the chosen one, and posts `SelectableList.Checked`.
    `set_rows()` clears the checks too.
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("space", "toggle_check", "Mark"),
    ]

    DEFAULT_CSS = """
    SelectableList,
    SelectableList:focus {
        height: auto;
        max-height: 14;
        border: none;
        padding: 0;
        background: transparent;
    }

    /* The marker is the selection indicator: a solid highlight bar would
       swallow it, so the bar is neutralised (normal and focused) and the
       chosen row is just bold. */
    SelectableList > .option-list--option-highlighted,
    SelectableList:focus > .option-list--option-highlighted {
        background: transparent;
        color: $foreground;
        text-style: bold;
    }
    """

    class Chosen(Message):
        """A row was chosen; `data_index` is its entry's data index."""

        def __init__(self, selectable_list: SelectableList, data_index: int) -> None:
            super().__init__()
            self.selectable_list = selectable_list
            self.data_index = data_index

        @property
        def control(self) -> SelectableList:
            return self.selectable_list

    class Checked(Message):
        """The set of checked rows changed (multi lists only)."""

        def __init__(self, selectable_list: SelectableList) -> None:
            super().__init__()
            self.selectable_list = selectable_list

        @property
        def control(self) -> SelectableList:
            return self.selectable_list

    def __init__(
        self,
        rows: Sequence[tuple[int | None, str]] | None = None,
        *,
        id: str | None = None,
        multi: bool = False,
        group: str | None = None,
    ) -> None:
        super().__init__(id=id, compact=True)
        self.multi = multi
        self.group = group
        self._rows: list[tuple[int | None, str]] = []
        self._marked: int | None = None
        self._checked: set[int] = set()  # list positions
        self._add_rows(rows or [])

    def _prompt(self, position: int) -> str:
        index, label = self._rows[position]
        if index is None:  # header row
            return f"[b]{label}[/]"
        marker = "[dodgerblue]●[/]" if position == self._marked else "[dim]○[/]"
        if not self.multi:
            return f"{marker} {label}"
        check = "[$text-success]✔[/]" if position in self._checked else " "
        return f"{check} {marker} {label}"

    def _render_row(self, position: int | None) -> None:
        if position is not None and position < len(self._rows):
            self.replace_option_prompt_at_index(position, self._prompt(position))

    def _add_rows(self, rows: Sequence[tuple[int | None, str]]) -> None:
        # Added after construction on purpose: OptionList(*options)
        # highlights its first row, and nothing should be chosen until the
        # user picks one.
        self._rows = list(rows)
        if not self._rows:
            self.add_option(Option("[dim](none recorded)[/]", disabled=True))
            return
        self.add_options(
            Option(
                self._prompt(position),
                id=(str(index) if index is not None else None),
                disabled=index is None,
            )
            for position, (index, _) in enumerate(self._rows)
        )

    def set_rows(self, rows: Sequence[tuple[int | None, str]]) -> None:
        """Replace all rows (synchronous; nothing is chosen or checked
        afterwards)."""
        self.clear_options()
        self._marked = None
        self._checked = set()
        self._add_rows(rows)

    def relabel(self, labels: list[str]) -> None:
        """New labels for the same rows, in order (e.g. re-laid-out columns);
        the chosen row and any checks stay as they are."""
        if len(labels) != len(self._rows):
            return
        self._rows = [(index, label) for (index, _), label in zip(self._rows, labels)]
        for position in range(len(self._rows)):
            self._render_row(position)

    @property
    def selected_data_index(self) -> int | None:
        """Data index of the chosen row, or None if none is chosen."""
        option = self.highlighted_option
        return int(option.id) if option is not None and option.id else None

    @property
    def checked_data_indexes(self) -> list[int]:
        """Data indexes of the checked rows, in list order."""
        return [self._rows[p][0] for p in sorted(self._checked)]

    def clear_selection(self) -> None:
        """Unchoose everything. Posts no message."""
        self._mark(None)
        self.highlighted = None

    def select_data_index(self, index: int) -> bool:
        """Choose the row whose data index is `index`, as if the user had
        (posts Chosen); False, choosing nothing, if no row has it."""
        for position, (data_index, _) in enumerate(self._rows):
            if data_index == index:
                self.highlighted = position
                return True
        return False

    def _clear_group(self) -> None:
        """Unchoose the other lists in this list's group."""
        if self.group is None:
            return
        for other in self.screen.query(SelectableList):
            if other is not self and other.group == self.group:
                other.clear_selection()

    def _mark(self, row: int | None) -> None:
        """Move the selector marker to list position `row` (None: no marker)."""
        previous = self._marked
        if previous == row:
            return
        self._marked = row
        self._render_row(previous)
        self._render_row(row)

    def toggle_check(self, position: int) -> None:
        """Check or uncheck the row at list position `position`."""
        if not self.multi or not 0 <= position < len(self._rows):
            return
        self._checked ^= {position}
        self._render_row(position)
        self.post_message(self.Checked(self))

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "toggle_check":
            return self.multi and bool(self._rows)
        return True

    def action_toggle_check(self) -> None:
        if self.highlighted is not None:
            self.toggle_check(self.highlighted)

    async def _on_click(self, event: Click) -> None:
        if self.multi and event.ctrl:
            clicked = event.style.meta.get("option")
            if clicked is not None:
                event.stop()
                self.toggle_check(clicked)
                return
        await super()._on_click(event)

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        event.stop()
        if event.option.id is None:  # the disabled "(none recorded)" row
            return
        self._mark(event.option_index)
        self._clear_group()
        self.post_message(self.Chosen(self, int(event.option.id)))


class SheetSection(Collapsible):
    """A sheet section (on every sheet): a Collapsible that starts
    expanded. Textual's own default is collapsed, so every sheet section
    goes through this (project convention: sections are open by default,
    the user can still collapse them)."""

    def __init__(self, *children: Widget, title: str, **kwargs: Any) -> None:
        kwargs.setdefault("collapsed", False)
        super().__init__(*children, title=title, **kwargs)


def _tab_placeholder(tab_name: str) -> str:
    """Text for a not-yet-built flat placeholder tab (e.g. Diary, both on
    the covenant and character sheets)."""
    return f"The {tab_name} tab isn't built yet -- coming in a future update."


class TwoColumns(Horizontal):
    """A full-width row whose children share it equally, each as tall as its
    content: the side-by-side panels and sections of the sheets. (Gaps
    between the columns are the left column's own right margin.)"""

    DEFAULT_CSS = """
    TwoColumns {
        width: 1fr;
        height: auto;
    }

    TwoColumns > * {
        width: 1fr;
        height: auto;
    }
    """


class StackingColumns(Horizontal):
    """A row of columns side by side that stacks them one above the other
    (the `-stacked` class) whenever the row is too narrow for all of them at
    once. Each column is as wide as its content or, with `equal=True`, gets
    an equal share of the row (like TwoColumns) -- then it stacks as soon as
    any column's content is wider than its share. Call restack() after
    changing a column's content; a resize re-checks by itself. (Gaps between
    the columns are the left column's own right margin.)"""

    DEFAULT_CSS = """
    StackingColumns {
        width: 1fr;
        height: auto;
    }

    StackingColumns > * {
        width: auto;
        height: auto;
    }

    StackingColumns.-equal > * {
        width: 1fr;
    }

    StackingColumns.-stacked {
        layout: vertical;
    }

    StackingColumns.-equal.-stacked > * {
        width: auto;
    }
    """

    def __init__(self, *children: Widget, equal: bool = False, **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.equal = equal
        self.set_class(equal, "-equal")

    def on_resize(self) -> None:
        self.restack()

    def restack(self) -> None:
        if not self.size.width:
            return  # not laid out yet; on_resize will come
        columns = [child for child in self.children if child.display]
        if not columns:
            return
        widths = [
            child.get_content_width(self.size, self.app.size)
            + child.styles.gutter.width
            for child in columns
        ]
        margins = sum(child.styles.margin.width for child in columns)
        if self.equal:
            needed = max(widths) * len(columns) + margins
        else:
            needed = sum(widths) + margins
        self.set_class(needed > self.size.width, "-stacked")


class PinnedCollapsible(Collapsible):
    """A Collapsible that is permanently expanded and ignores toggling.

    Used for each sheet's always-visible top panel (and the Arts panel). It
    stays a real Collapsible (with a focusable CollapsibleTitle) so the
    focus-ancestry dispatch in WorkspaceScreen treats it like every other
    section, but it can never be collapsed.
    """

    def __init__(self, *children: Widget, title: str, id: str | None = None) -> None:
        super().__init__(
            *children, title=title, collapsed=False, expanded_symbol="", id=id
        )

    def _on_collapsible_title_toggle(self, event: Message) -> None:
        # Textual dispatches a message to every class in the MRO's handler
        # of the same name, so stop() alone isn't enough -- prevent_default()
        # is what keeps Collapsible's own handler from flipping `collapsed`.
        event.stop()
        event.prevent_default()

    def on_click(self, event: Click) -> None:
        # Clicking anywhere in the section (not just its title) makes it the
        # active section, so 'e' and the Footer hint work after a click --
        # unless the click already focused something inside it (the Arts
        # lists), which is active enough and should keep the arrow keys.
        focused = self.screen.focused
        if focused is None or self not in focused.ancestors_with_self:
            self.query_one("CollapsibleTitle").focus()
