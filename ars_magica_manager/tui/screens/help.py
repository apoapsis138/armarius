"""The Help screen: a topic list beside the chosen page, opened
with ? (or F1) on the help for whatever has focus."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Input, Label, Markdown, OptionList, Static
from textual.widgets.option_list import Option, OptionDoesNotExist

from ... import help_text as ht
from ...markup import escape
from .fields import ModalDialog

ABOUT, WHATS_NEW = ht.ABOUT, ht.WHATS_NEW
whats_new_text = ht.whats_new_text

#: Option ids say which group a topic was listed in, so one topic can be
#: listed twice (THIS SCREEN and ALL PAGES).
_HERE, _GUIDE, _REF, _ALL, _FOUND = "here:", "guide:", "ref:", "all:", "found:"
_PREFIX = {"here": _HERE, "guide": _GUIDE, "ref": _REF, "all": _ALL, "found": _FOUND}


@dataclass
class HelpContext:
    """What Help opens on: the topic ids for where focus is (most specific
    first), where that is in words, and the keys that work there; and, from
    a screen with places to go to, what opens one (Go there): it takes a
    tab's or section's id, opens it once Help has closed, and says whether
    the screen has it."""

    ids: list[str] = field(default_factory=list)
    where: str = ""
    keys: list[str] = field(default_factory=list)
    go_to: Callable[[str], bool] | None = None


def shown_keys(screen: Screen, leave_out: tuple[str, ...] = ()) -> list[str]:
    """The keys `screen`'s footer shows (enabled, not in `leave_out`), as
    "key Label"."""
    keys: list[str] = []
    for active in screen.active_bindings.values():
        binding = active.binding
        if not binding.show or not active.enabled or binding.action in leave_out:
            continue
        shown = f"{screen.app.get_key_display(binding)} {binding.description}"
        if shown not in keys:
            keys.append(shown)
    return keys


def help_context(stack: list[Screen]) -> HelpContext:
    """The help for the top screen that has some (a dialog without a page
    of its own shows the help of the screen it was opened from)."""
    for screen in reversed(stack):
        provider = getattr(screen, "help_context", None)
        if callable(provider):
            context = provider()
            if isinstance(context, HelpContext):
                if screen is not stack[-1]:
                    # Go there opens a place on the screen below Help, not
                    # behind a dialog.
                    context.go_to = None
                return context
    return HelpContext()


class HelpScreen(ModalDialog[None]):
    """Topics on the left (THIS SCREEN, REFERENCE, ALL PAGES; a filter
    replaces them with what matches), the chosen page on the right."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "cancel", "Close"),
        Binding("slash", "filter", "Filter", show=False),
        Binding("g", "go_there", "Go there", show=False),
    ]

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    #help-dialog {
        width: 100%;
        height: 100%;
    }

    #help-title {
        padding: 0 1;
    }

    #help-body {
        height: 1fr;
    }

    #help-side {
        width: 38;
        height: 100%;
        border-right: solid $accent;
    }

    #help-filter {
        margin: 0 1;
    }

    #help-topics {
        height: 1fr;
        border: none;
    }

    #help-main {
        width: 1fr;
        height: 100%;
        padding: 0 1;
    }

    #help-keys {
        height: auto;
        color: $text-muted;
        padding: 0 1;
    }

    #help-scroll {
        height: 1fr;
    }

    #help-hint {
        color: $text-muted;
        padding: 0 1;
    }
    """

    def __init__(self, context: HelpContext | None = None) -> None:
        super().__init__()
        self.context = context or HelpContext()
        self.book = ht.book(ht.TUI)
        self._page_shown: str | None = None
        #: The topic on show.
        self.topic_id: str | None = None
        #: One page loads at a time; a page another has replaced stops.
        self._loading = asyncio.Lock()

    def compose(self) -> ComposeResult:
        where = f"  ›  {self.context.where}" if self.context.where else ""
        with Vertical(id="help-dialog", classes="dialog-box"):
            yield Label(f"Help{where}", id="help-title", classes="dialog-title")
            with Horizontal(id="help-body"):
                with Vertical(id="help-side"):
                    yield Input(placeholder="/ Filter topics", id="help-filter")
                    yield OptionList(id="help-topics")
                with Vertical(id="help-main"):
                    yield Static("", id="help-keys")
                    with VerticalScroll(id="help-scroll"):
                        yield Markdown("", id="help-page", open_links=False)
            yield Static(_hint(), id="help-hint")

    def on_mount(self) -> None:
        topics = self.query_one("#help-topics", OptionList)
        self._list_topics()
        topics.focus()
        here = self._here()
        start = here[0] if here else "keys"
        self._highlight((_HERE if here else _REF) + start)

    # -- the topic list --

    def _here(self) -> list[str]:
        """THIS SCREEN: the context's topics the help has, once each."""
        return [t for t in dict.fromkeys(self.context.ids) if t in self.book.topics]

    def _list_topics(self, query: str = "") -> None:
        topics = self.query_one("#help-topics", OptionList)
        topics.clear_options()
        options: list[Option] = []
        for heading, entries in ht.contents(self.book, self.context.ids, query):
            options.append(_heading(heading))
            options += [
                Option(
                    "  " * entry.indent + escape(entry.title),
                    id=_PREFIX[entry.group] + entry.id,
                )
                for entry in entries
            ]
        topics.add_options(options)

    def _highlight(self, option_id: str) -> None:
        topics = self.query_one("#help-topics", OptionList)
        try:
            topics.highlighted = topics.get_option_index(option_id)
        except OptionDoesNotExist:  # not listed: show it all the same
            self.show_topic(option_id.split(":", 1)[1])

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        option_id = event.option.id
        if option_id:
            self.show_topic(
                option_id.split(":", 1)[1], here=option_id.startswith(_HERE)
            )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.query_one("#help-scroll", VerticalScroll).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self._list_topics(event.value)
        topics = self.query_one("#help-topics", OptionList)
        if topics.option_count > 1:
            topics.highlighted = 1  # the first after the heading

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.query_one("#help-topics", OptionList).focus()

    def action_filter(self) -> None:
        self.query_one("#help-filter", Input).focus()

    # -- the page --

    def _page_text(self, topic_id: str) -> tuple[str, str] | None:
        """The page `topic_id` is on: its id and Markdown."""
        return ht.page_text(self.book, topic_id)

    def show_topic(self, topic_id: str, *, here: bool = False) -> None:
        """Show `topic_id`'s page, scrolled to it; the keys line only for
        where Help was opened from."""
        found = self._page_text(topic_id)
        if found is None:
            return
        page_id, text = found
        self.topic_id = topic_id
        self.query_one("#help-hint", Static).update(_hint(self._can_go(topic_id)))
        keys = self.query_one("#help-keys", Static)
        if here and self.context.keys:
            keys.update("Keys here:  " + "   ".join(self.context.keys))
            keys.display = True
        else:
            keys.display = False
        if page_id != self._page_shown:
            self._page_shown = page_id
            markdown = self.query_one("#help-page", Markdown)
            self.run_worker(self._load(markdown, page_id, text, topic_id))
        else:
            self._scroll_to(topic_id)

    async def _load(
        self, markdown: Markdown, page_id: str, text: str, topic_id: str
    ) -> None:
        """Show `text`. A long page (What's New) shows its start at once and
        the rest a few sections at a time, so Help answers keys while it
        fills in. Not cancelled midway (that can leave the Markdown waiting
        for ever): a page that another has replaced stops between pieces."""
        async with self._loading:
            first, *rest = page_chunks(text)
            for n, chunk in enumerate([first, *rest]):
                if self._page_shown != page_id:
                    return
                if n == 0:
                    await markdown.update(chunk)
                    self._scroll_to(topic_id)
                else:
                    await markdown.append(chunk)

    def _scroll_to(self, topic_id: str, tries: int = 25) -> None:
        """Scroll the page to `topic_id`'s heading (its top for a page).
        A page just loaded isn't laid out yet: until it is, try again after
        the next refresh."""
        scroll = self.query_one("#help-scroll", VerticalScroll)
        topic = self.book.topic(topic_id)
        if topic is None or topic.level < 3:
            scroll.scroll_home(animate=False)
            return
        markdown = self.query_one("#help-page", Markdown)
        for _, title, block_id in markdown.table_of_contents or ():
            if str(title) == topic.title and block_id:
                # The contents can name a heading not mounted yet.
                found = markdown.query(f"#{block_id}")
                waiting = not found or found.first().virtual_region.y == 0
                if waiting and tries:
                    self.call_after_refresh(self._scroll_to, topic_id, tries - 1)
                    return
                if not found:
                    return
                heading = found.first()
                scroll.scroll_to_widget(heading, top=True, animate=False)
                return

    # -- Go there --

    def _can_go(self, topic_id: str) -> bool:
        """Whether Go there is offered for `topic_id`: a tab or section,
        with Help opened from a screen that has places."""
        return self.context.go_to is not None and self.book.is_place(topic_id)

    def action_go_there(self) -> None:
        """g: close Help and open the tab or section the topic on show
        describes."""
        if self.topic_id is not None and self._can_go(self.topic_id):
            self.go_there(self.topic_id)

    def go_there(self, place: str) -> None:
        """Close Help and open `place` on the screen it was opened from, or
        say why it can't be."""
        if self.context.go_to is None:
            self.notify("Go there works from a sheet.", severity="warning")
        elif self.context.go_to(place):
            self.dismiss(None)
        else:
            self.notify(self.book.not_here(place), severity="warning")

    def on_markdown_link_clicked(self, event: Markdown.LinkClicked) -> None:
        href = event.href
        if href.startswith(ht.GO):
            event.prevent_default()
            self.go_there(href.removeprefix(ht.GO))
        elif href.startswith("help:"):
            event.prevent_default()
            topic_id = href.removeprefix("help:")
            option = (_GUIDE if ht.is_guide(topic_id) else _ALL) + topic_id
            topics = self.query_one("#help-topics", OptionList)
            try:
                topics.highlighted = topics.get_option_index(option)
            except OptionDoesNotExist:  # a topic on a page: show it
                self.show_topic(topic_id)
        elif href.startswith(("http://", "https://")):
            self.app.open_url(href)


def page_chunks(text: str, lines: int = 60) -> list[str]:
    """`text` cut before "## " headings into pieces of at least `lines`
    lines (one piece for a short page); joined, they are `text`."""
    chunks: list[str] = []
    current: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith("## ") and len(current) >= lines:
            chunks.append("".join(current))
            current = []
        current.append(line)
    chunks.append("".join(current))
    return chunks


def _hint(go_there: bool = False) -> str:
    """The keys line under Help: g Go there while it is offered."""
    go = "   g Go there" if go_there else ""
    return f"↑↓ Choose topic   Tab Page   / Filter{go}   esc Close"


def _heading(text: str) -> Option:
    return Option(f"[b]{text}[/]", disabled=True)
