"""Widgets shared by the screens: the bottom bar, the selectable list, sheet
sections and layout rows, the details panel, and small display helpers."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from typing import Any, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import (
    Horizontal,
    ScrollableContainer,
    Vertical,
    VerticalScroll,
)
from textual.content import Content
from textual.events import Click, Focus
from textual.message import Message
from textual.screen import Screen
from textual.scroll_view import ScrollView
from textual.widget import Widget
from textual.widgets import (
    Button,
    Collapsible,
    Footer,
    OptionList,
    Static,
)
from textual.widgets._collapsible import CollapsibleTitle
from textual.widgets._footer import FooterKey
from textual.widgets._tabbed_content import ContentTabs
from textual.widgets.option_list import Option

from .. import catalog
from .. import sheet_text as st
from ..covenants import (
    UNKNOWN_HOOK_POINTS,
    boon_hook_is_unknown,
    covenant_boon_points,
    covenant_hook_points,
)
from ..markup import escape, markdown_inline
from ..models import (
    BOON_HOOK_DESCRIPTION,
    Covenant,
    CovenantBoonHookDef,
)


def counted(label: str, count: int) -> str:
    """A list section's title with how many entries it has: "Rooms (3)"."""
    return f"{label} ({count})"


def points_title(label: str, points: float, colour: str | None = None) -> str:
    """A title with the points its list comes to: "Boons (3 pts)", the
    points in the theme `colour` if given (see match_colour)."""
    unit = "pt" if points == 1 else "pts"
    text = f"({points:g} {unit})"
    return f"{label} [{colour}]{text}[/]" if colour else f"{label} {text}"


def match_colour(points: float, other: float) -> str:
    """The colour for the two sides of a balance (Virtues against Flaws):
    $text-success when they match, $text-error when they don't."""
    return "$text-success" if points == other else "$text-error"


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


def boon_hook_title(covenant: Covenant, kind: str) -> str:
    """ "Boons (7 pts)" / "Hooks (7 pts)": Boons show the points they
    cost, Hooks the points they provide. Both totals share one colour:
    plain while the Boons cost less than the Hooks provide (points still
    to spend), $text-success when they match, $text-error when the Boons
    cost more."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    boons = covenant_boon_points(covenant, by_id)
    hooks = covenant_hook_points(covenant, by_id)
    colour = None if boons < hooks else match_colour(boons, hooks)
    if kind == "Boon":
        return points_title("Boons", boons, colour)
    return points_title("Hooks", hooks, colour)


def boon_hook_rows(covenant: Covenant, kind: str) -> list[tuple[int, str]]:
    """The attached Boons or Hooks of `kind` as (index into
    covenant.boons_hooks, display label) pairs, in attach order."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    return [
        (
            index,
            escape(catalog.describe_boon_hook(bh, by_id))
            + (
                f" [dim](Unknown, {UNKNOWN_HOOK_POINTS} pts)[/]"
                if boon_hook_is_unknown(bh, by_id[bh.vf_id])
                else ""
            ),
        )
        for index, bh in enumerate(covenant.boons_hooks)
        if bh.vf_id in by_id and by_id[bh.vf_id].type == kind
    ]


def boon_hook_info_text(covenant: Covenant, index: int | None) -> str:
    """The details panel for the attached Boon/Hook at `index` into
    covenant.boons_hooks: its name, type, notes, the user's own
    description (if any), then the official rules text and the book it
    comes from."""
    if index is None:
        return "[dim]Select a Boon or Hook to see its details.[/]"
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    instance = covenant.boons_hooks[index]
    definition = by_id.get(instance.vf_id)
    if definition is None:
        return escape(f"{instance.vf_id} (not in catalog)")

    lines = [f"[b]Name:[/] {escape(catalog.describe_boon_hook(instance, by_id))}"]
    if definition.category:
        lines.append(f"[b]Type:[/] {definition.category}")
    lines.append(f"[b]Tier:[/] {_tier_text(definition)}")
    if boon_hook_is_unknown(instance, definition):
        lines.append(
            f"[b]Unknown:[/] Yes (counts {UNKNOWN_HOOK_POINTS} points, as a Major Hook)"
        )
    elif definition.unknown:
        lines.append("[dim]May be Unknown (mark it in its Edit form).[/]")
    if definition.requires:
        lines.append(f"[b]Requires:[/] {_boon_hook_names(definition.requires, by_id)}")
    if definition.requires_any:
        lines.append(
            "[b]Requires one of:[/] " + _boon_hook_names(definition.requires_any, by_id)
        )
    if definition.excludes:
        lines.append(f"[b]Not with:[/] {_boon_hook_names(definition.excludes, by_id)}")
    lines += st.effect_lines(definition.modifiers)
    if definition.max_count:
        lines.append(
            f"[dim]May be taken up to {definition.max_count} times; "
            "the effects stack.[/]"
        )
    elif definition.repeatable:
        lines.append("[dim]May be taken more than once; the effects stack.[/]")
    # The user's own description leads; the official rules text follows.
    description = instance.params.get(BOON_HOOK_DESCRIPTION, "").strip()
    if description:
        lines += ["", "[b]Description:[/]", markdown_inline(description)]
    lines += ["", "[b]Rules:[/]", escape(definition.description)]
    if definition.source:
        lines += ["", f"[dim]Source: {escape(definition.source)}[/]"]
    return "\n".join(lines)


def _sign_colored(value: float, text: str) -> str:
    """Wraps `text` in Textual markup coloured by the sign of `value`, in
    the active theme's text colours: positive $text-success, negative
    $text-error, zero left plain."""
    if value == 0:
        return text
    colour = "$text-success" if value > 0 else "$text-error"
    return f"[{colour}]{text}[/]"


class ThemeBar(Static):
    """The app's active theme name, at the right end of the row above the
    footer (see BottomBar)."""

    DEFAULT_CSS = """
    ThemeBar {
        width: auto;
        height: 1;
        padding: 0 1;
        color: $text-muted;
    }
    """

    def on_mount(self) -> None:
        self.watch(self.app, "theme", self._show_theme, init=True)

    def _show_theme(self, theme_name: str) -> None:
        self.update(f"Theme: {theme_name.replace('-', ' ').title()}")


class BottomBar(Vertical):
    """Docks a status row directly above the Footer: where focus is (set
    by the screen with set_where(); STORY-1008) and, at its right end, the
    ThemeBar.

    Both dock to the same screen edge independently otherwise (Textual's
    dock arrangement doesn't stack same-edge docked siblings -- they'd
    overlap on the same row), so this wraps them in one bottom-docked
    container where Footer's own `dock: bottom` pins it to the container's
    last row and the status row, undocked, takes the row above it in
    normal flow.
    """

    DEFAULT_CSS = """
    BottomBar {
        dock: bottom;
        height: 2;
    }

    BottomBar #status-row {
        width: 1fr;
        height: 1;
    }

    BottomBar #where-bar {
        width: 1fr;
        height: 1;
        padding: 0 1;
    }
    """

    def __init__(self, right_actions: Iterable[str] = ()) -> None:
        super().__init__()
        self._right_actions = frozenset(right_actions)
        self._where = ""

    def compose(self) -> ComposeResult:
        with Horizontal(id="status-row"):
            yield Static(id="where-bar")
            yield ThemeBar(id="theme-bar")
        yield SplitFooter(self._right_actions)

    @property
    def where(self) -> str:
        """Where focus is, as last set (markup)."""
        return self._where

    def set_where(self, where: str) -> None:
        """Show `where` (markup) as the place focus is."""
        if where != self._where:
            self._where = where
            self.query_one("#where-bar", Static).update(where)


class SplitFooter(Footer):
    """A Footer whose keys for `right_actions` sit at its right end, just
    left of the command palette's ^p, instead of in the row of keys on the
    left (e.g. the saga picker's "? About this App")."""

    DEFAULT_CSS = """
    SplitFooter .footer-spacer {
        width: 1fr;
        height: 1;
    }
    SplitFooter FooterKey.-first-right {
        border-left: vkey $foreground 20%;
    }
    """

    def __init__(self, right_actions: frozenset[str] = frozenset()) -> None:
        super().__init__()
        self._right_actions = right_actions
        #: The keys last composed (see _shown_keys), and whether a rebuild
        #: is already waiting for the next refresh.
        self._shown: tuple[Any, ...] | None = None
        self._rebuild_pending = False
        #: How many times the keys were rebuilt (the performance guard tests
        #: count these).
        self.rebuilds = 0

    def bindings_changed(self, screen: Screen) -> None:
        """Rebuild the keys when they changed -- once per refresh, however
        many times the screen asked (Footer rebuilds on every request, and
        every focus move, tab switch and list row asks)."""
        self._bindings_ready = True
        if not screen.app.app_focus:
            return
        if self.is_attached and screen is self.screen and not self._rebuild_pending:
            self._rebuild_pending = True
            self.call_after_refresh(self._rebuild_if_changed)

    async def _rebuild_if_changed(self) -> None:
        self._rebuild_pending = False
        if not self.is_attached:
            return
        shown = self._shown_keys()
        if shown == self._shown:
            return
        self._shown = shown
        self.rebuilds += 1
        await self.recompose()

    def _shown_keys(self) -> tuple[Any, ...]:
        """What compose() would show: each shown binding with its state."""
        return tuple(
            (
                key,
                binding.action,
                binding.description,
                binding.group,
                enabled,
                tooltip,
            )
            for key, (_, binding, enabled, tooltip) in (
                self.screen.active_bindings.items()
            )
            if binding.show
        )

    def compose(self) -> ComposeResult:
        right: list[FooterKey] = []
        for widget in super().compose():
            if (
                isinstance(widget, FooterKey)
                and widget.action in self._right_actions
                and not widget.has_class("-grouped")
            ):
                right.append(widget.add_class("-right"))
            else:
                yield widget
        if right:
            # Takes up the free width, pushing the keys after it right; one
            # divider sets the group apart.
            right[0].add_class("-first-right")
            yield Static(classes="footer-spacer")
            yield from right


class SelectableList(OptionList):
    """The standard "selectable list" (see DESIGN.md, UI Conventions): rows
    that each carry a selector -- a dim `○`, or a bold `●` in the theme's
    primary colour on the chosen row -- with at most one row chosen at a
    time.

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

    class Moved(Message):
        """The chosen row changed. Unlike Chosen, which the owning view
        handles and stops, this one is for the screen (its where-am-I
        row)."""

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
        marker = "[$text-primary]●[/]" if position == self._marked else "[dim]○[/]"
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
        """Replace all rows (synchronous; nothing is checked afterwards).
        Nothing is chosen either, unless the list has focus: a focused list
        always has a row to act on, so the row at the old position (or the
        nearest one) is chosen again."""
        position = self.highlighted if self.has_focus else None
        self.clear_options()
        self._marked = None
        self._checked = set()
        self._add_rows(rows)
        if position is not None:
            self._choose_near(position)
        if self.is_mounted:
            self.screen.refresh_bindings()

    def _choose_near(self, position: int) -> None:
        """Choose the row at list position `position`, else the nearest one
        below or above it that can be chosen (headers can't)."""
        count = len(self._rows)
        for candidate in (*range(position, count), *range(count - 1, -1, -1)):
            if 0 <= candidate < count and self._rows[candidate][0] is not None:
                self.highlighted = candidate
                return

    def on_focus(self, event: Focus) -> None:
        # A focused list always has a row to act on (STORY-1005): the one
        # chosen before, else the first.
        if self.highlighted is None:
            self._choose_near(0)

    def relabel(self, labels: list[str]) -> None:
        """New labels for the same rows, in order (e.g. re-laid-out columns);
        the chosen row and any checks stay as they are."""
        if len(labels) != len(self._rows):
            return
        self._rows = [(index, label) for (index, _), label in zip(self._rows, labels)]
        for position in range(len(self._rows)):
            self._render_row(position)

    @property
    def row_count(self) -> int:
        """Number of rows, header rows included."""
        return len(self._rows)

    @property
    def selected_data_index(self) -> int | None:
        """Data index of the chosen row, or None if none is chosen."""
        option = self.highlighted_option
        return int(option.id) if option is not None and option.id else None

    @property
    def chosen_text(self) -> str:
        """The chosen row's first column as plain text ("" with none)."""
        position = self.highlighted
        if position is None or position >= len(self._rows):
            return ""
        plain = Content.from_markup(self._rows[position][1]).plain.strip()
        return re.split(r"\s{2,}", plain, maxsplit=1)[0]

    @property
    def checked_data_indexes(self) -> list[int]:
        """Data indexes of the checked rows, in list order."""
        # Only rows with a data index can be checked (the others are disabled).
        return [
            index
            for p in sorted(self._checked)
            if (index := self._rows[p][0]) is not None
        ]

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
        self.post_message(self.Moved())
        # A key can depend on the chosen row (e.g. More on a Charged Item).
        self.screen.refresh_bindings()


class ToggleList(SelectableList):
    """A SelectableList whose chosen row Space turns on or off (e.g. the lab's
    Specializations): it posts `ToggleList.Toggled` and the owner decides
    what that means and how the row then looks. Replaces the multi-select
    "Mark" binding, so a ToggleList is never `multi`."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("space", "toggle_row", "On/Off"),
    ]

    class Toggled(Message):
        """Space on the chosen row; `data_index` is its entry's data index."""

        def __init__(self, toggle_list: ToggleList, data_index: int) -> None:
            super().__init__()
            self.toggle_list = toggle_list
            self.data_index = data_index

        @property
        def control(self) -> ToggleList:
            return self.toggle_list

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "toggle_row":
            return self.selected_data_index is not None
        return super().check_action(action, parameters)

    def action_toggle_row(self) -> None:
        index = self.selected_data_index
        if index is not None:
            self.post_message(self.Toggled(self, index))


class SectionTitle(CollapsibleTitle, inherit_bindings=False):
    """A sheet section's title: a CollapsibleTitle without its Enter key.
    Collapsing is the workspace's `c` (or a second click), never a side
    effect of where focus happens to be (STORY-1005)."""


def section_of(widget: Widget | None) -> Collapsible | None:
    """The sheet section `widget` is in (or is), if any."""
    if widget is None:
        return None
    for ancestor in widget.ancestors_with_self:
        if isinstance(ancestor, Collapsible):
            return ancestor
    return None


def is_stop(widget: Widget) -> bool:
    """Whether Tab can stop on `widget` inside a sheet: a list or a field,
    not a button (the mouse's; its action has a key), a section title (see
    section_stop) or a container that is only focusable to scroll."""
    if not widget.focusable or isinstance(
        widget, (Button, CollapsibleTitle, ContentTabs)
    ):
        return False
    # Lists and trees scroll too (ScrollView is a ScrollableContainer).
    return isinstance(widget, ScrollView) or not isinstance(widget, ScrollableContainer)


def section_stop(section: Collapsible) -> Widget:
    """Where focus goes when `section` takes it: its first list or field
    while it's open and has one, else its title."""
    if not section.collapsed:
        for widget in section.query("*"):
            if is_stop(widget) and section_of(widget) is section:
                return widget
    return section.query_one(CollapsibleTitle)


def first_stop(container: Widget) -> Widget | None:
    """The first place Tab would stop inside `container`: its first
    section's stop, or a list or field outside any section (a flat tab)."""
    for widget in container.query("*"):
        if isinstance(widget, Collapsible):
            return section_stop(widget)
        if is_stop(widget):
            return widget
    return None


def sheet_focus_chain(chain: Sequence[Widget]) -> list[Widget]:
    """`chain` (a screen's focus chain) with one stop per sheet section
    (STORY-1005): a section's lists and fields, or its title when it has
    none; never a button, the tab strip or a scrolling container."""
    stops: list[Widget] = []
    for widget in chain:
        if isinstance(widget, CollapsibleTitle):
            section = section_of(widget)
            if section is None or section_stop(section) is widget:
                stops.append(widget)
        elif is_stop(widget):
            stops.append(widget)
    return stops


class FocusableSection(Collapsible):
    """What every sheet section shares: a click anywhere in it makes it the
    focused section, so the keys and the Footer follow the mouse."""

    # The focused section stands out by its rule and title, wherever in it
    # focus is (a list's chosen row is only bold).
    DEFAULT_CSS = """
    FocusableSection:focus-within {
        border-top: hkey $primary;
    }

    FocusableSection:focus-within > CollapsibleTitle {
        color: $text-primary;
        text-style: bold;
    }

    FocusableSection > CollapsibleTitle:focus {
        color: $block-cursor-foreground;
    }
    """

    def focus_section(self) -> None:
        """Give the section focus, at its stop (see section_stop)."""
        section_stop(self).focus()

    def on_click(self, event: Click) -> None:
        # Unless the click already focused something inside (a list row),
        # which is focus enough and should keep the arrow keys.
        focused = self.screen.focused
        if focused is None or self not in focused.ancestors_with_self:
            self.focus_section()


class SheetSection(FocusableSection):
    """A sheet section (on every sheet): a Collapsible that starts
    expanded. Textual's own default is collapsed, so every sheet section
    goes through this (project convention: sections are open by default,
    the user can still collapse them).

    A click on the title of a section that isn't the focused one only
    focuses it; a click on the focused section's title collapses or expands
    it (STORY-1005). From the keyboard that is the workspace's `c`."""

    def __init__(self, *children: Widget, title: str, **kwargs: Any) -> None:
        kwargs.setdefault("collapsed", False)
        super().__init__(*children, title=title, **kwargs)
        self._title = SectionTitle(
            label=title,
            collapsed_symbol="▶",
            expanded_symbol="▼",
            collapsed=self.collapsed,
        )

    def toggle(self) -> None:
        """Collapse or expand, keeping focus in the section. A collapsed
        section has no chosen row: e and d never act on one out of sight."""
        self.collapsed = not self.collapsed
        if self.collapsed:
            for rows in self.query(SelectableList):
                rows.clear_selection()
        self.focus_section()

    def _on_collapsible_title_toggle(self, event: Message) -> None:
        # A click on the title. prevent_default() keeps Collapsible's own
        # handler from flipping `collapsed` (see PinnedCollapsible).
        event.stop()
        event.prevent_default()
        if getattr(self.screen, "section_before_focus", None) is self:
            self.toggle()
        else:
            self.focus_section()


#: The gap, in columns, between side-by-side lists (sections).
LIST_COLUMN_GAP = 2
#: The gap between side-by-side blocks of text (info panels, totals).
TEXT_COLUMN_GAP = 4


class TwoColumns(Horizontal):
    """A full-width row whose children share it equally, each as tall as its
    content: the side-by-side panels and sections of the sheets. Columns
    are LIST_COLUMN_GAP apart, or TEXT_COLUMN_GAP with `text=True` (blocks
    of text rather than lists) -- set here only, so every sheet matches."""

    DEFAULT_CSS = f"""
    TwoColumns {{
        width: 1fr;
        height: auto;
    }}

    TwoColumns > * {{
        width: 1fr;
        height: auto;
        margin-right: {LIST_COLUMN_GAP};
    }}

    TwoColumns.-text > * {{
        margin-right: {TEXT_COLUMN_GAP};
    }}

    TwoColumns > *:last-child {{
        margin-right: 0;
    }}
    """

    def __init__(self, *children: Widget, text: bool = False, **kwargs: Any) -> None:
        super().__init__(*children, **kwargs)
        self.set_class(text, "-text")


class StackingColumns(Horizontal):
    """A row of columns side by side that stacks them one above the other
    (the `-stacked` class) whenever the row is too narrow for all of them at
    once. Each column is as wide as its content or, with `equal=True`, gets
    an equal share of the row (like TwoColumns) -- then it stacks as soon as
    any column's content is wider than its share. Call restack() after
    changing a column's content; a resize re-checks by itself. Its columns
    are blocks of text, TEXT_COLUMN_GAP apart (the gap is each column's
    right margin, so it counts when measuring)."""

    DEFAULT_CSS = f"""
    StackingColumns {{
        width: 1fr;
        height: auto;
    }}

    StackingColumns > * {{
        width: auto;
        height: auto;
        margin-right: {TEXT_COLUMN_GAP};
    }}

    StackingColumns > *:last-child {{
        margin-right: 0;
    }}

    StackingColumns.-equal > * {{
        width: 1fr;
    }}

    StackingColumns.-stacked {{
        layout: vertical;
    }}

    StackingColumns.-equal.-stacked > * {{
        width: auto;
    }}
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


class PinnedCollapsible(FocusableSection):
    """A Collapsible that is permanently expanded and ignores toggling.

    Used for each sheet's always-visible top panel. It
    stays a real Collapsible (with a focusable CollapsibleTitle) so the
    focus-ancestry dispatch in WorkspaceScreen treats it like every other
    section, but it can never be collapsed.
    """

    def __init__(self, *children: Widget, title: str, id: str | None = None) -> None:
        super().__init__(
            *children, title=title, collapsed=False, expanded_symbol="", id=id
        )
        self._title = SectionTitle(
            label=title, collapsed_symbol="▶", expanded_symbol="", collapsed=False
        )

    def _on_collapsible_title_toggle(self, event: Message) -> None:
        # Textual dispatches a message to every class in the MRO's handler
        # of the same name, so stop() alone isn't enough -- prevent_default()
        # is what keeps Collapsible's own handler from flipping `collapsed`.
        event.stop()
        event.prevent_default()


#: A details panel's height in rows, padding included: it fits its text,
#: from one line (nothing chosen) up to the old fixed 12 (STORY-114,
#: STORY-1010), beyond which the text scrolls.
DETAILS_PANEL_MIN_HEIGHT = 3
DETAILS_PANEL_MAX_HEIGHT = 12


class PanelText(Static):
    """The text of a DetailsPanel. Updating it scrolls the panel back to the
    top, so a newly chosen row never opens part-way down."""

    def update(self, content: Any = "", *, layout: bool = True) -> None:
        super().update(content, layout=layout)
        if isinstance(self.parent, DetailsPanel):
            self.parent.scroll_home(animate=False)


class DetailsPanel(VerticalScroll):
    """A selectable list's details panel: one per tab, docked below the
    tab's scrolling part on a shaded background, as tall as its text
    between DETAILS_PANEL_MIN_HEIGHT and DETAILS_PANEL_MAX_HEIGHT rows;
    longer text scrolls inside it (mouse wheel). It holds one
    PanelText, which carries the id (or class) the sheet updates it by --
    query it as a Static. Not focusable, so it adds no stop to the focus chain."""

    can_focus = False

    DEFAULT_CSS = f"""
    DetailsPanel.details-panel {{
        width: 1fr;
        height: auto;
        min-height: {DETAILS_PANEL_MIN_HEIGHT};
        max-height: {DETAILS_PANEL_MAX_HEIGHT};
        margin-top: 1;
        padding: 1 2;
        background: $panel;
        /* an accent edge ties it to the list it explains (STORY-1012) */
        border-left: outer $accent;
    }}

    DetailsPanel > PanelText {{
        width: 1fr;
        height: auto;
    }}
    """

    def __init__(
        self, text: str, *, id: str | None = None, text_classes: str = ""
    ) -> None:
        """`id` and `text_classes` go on the text (the panel is its parent)."""
        super().__init__(
            PanelText(text, id=id, classes=text_classes), classes="details-panel"
        )


class TableHeader(Static):
    """The column headings above a table-like list (books, spells, Arts,
    inhabitants...), in muted text."""

    DEFAULT_CSS = """
    TableHeader {
        width: 1fr;
        height: auto;
        color: $text-muted;
    }
    """
