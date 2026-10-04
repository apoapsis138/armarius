"""The Help screen (STORY-115): a topic list beside the chosen page, opened
with ? (or F1) on the help for whatever has focus."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Input, Label, Markdown, OptionList, Static
from textual.widgets.option_list import Option, OptionDoesNotExist

from .. import ROOT, __version__
from .. import help_text as ht
from ..markup import escape
from .fields import ModalDialog

#: The About page: the version and NOTICE.md (licences, credits).
ABOUT = "about"
NOTICE_PATH = ROOT / "NOTICE.md"

#: The pages under REFERENCE, after the generated About.
_REFERENCE = ("keys",)

#: Option ids say which group a topic was listed in, so one topic can be
#: listed twice (THIS SCREEN and ALL PAGES).
_HERE, _REF, _ALL, _FOUND = "here:", "ref:", "all:", "found:"


@dataclass
class HelpContext:
    """What Help opens on: the topic ids for where focus is (most specific
    first), where that is in words, and the keys that work there."""

    ids: list[str] = field(default_factory=list)
    where: str = ""
    keys: list[str] = field(default_factory=list)


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
                return context
    return HelpContext()


class HelpScreen(ModalDialog[None]):
    """Topics on the left (THIS SCREEN, REFERENCE, ALL PAGES; a filter
    replaces them with what matches), the chosen page on the right."""

    BINDINGS: ClassVar[list[BindingType]] = [
        ("escape", "cancel", "Close"),
        Binding("slash", "filter", "Filter", show=False),
    ]

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    #help-dialog {
        width: 100%;
        height: 100%;
        border: round $accent;
        background: $surface;
    }

    #help-title {
        text-style: bold;
        padding: 0 1;
        width: 100%;
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
        self.book = ht.book()
        self._page_shown: str | None = None
        #: The topic on show.
        self.topic_id: str | None = None

    def compose(self) -> ComposeResult:
        where = f"  ›  {self.context.where}" if self.context.where else ""
        with Vertical(id="help-dialog"):
            yield Label(f"Help{where}", id="help-title")
            with Horizontal(id="help-body"):
                with Vertical(id="help-side"):
                    yield Input(placeholder="/ Filter topics", id="help-filter")
                    yield OptionList(id="help-topics")
                with Vertical(id="help-main"):
                    yield Static("", id="help-keys")
                    with VerticalScroll(id="help-scroll"):
                        yield Markdown("", id="help-page", open_links=False)
            yield Static(
                "↑↓ Choose topic   Tab Page   / Filter   esc Close", id="help-hint"
            )

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
        found: list[str] = []
        for topic_id in self.context.ids:
            if topic_id in self.book.topics and topic_id not in found:
                found.append(topic_id)
        return found

    def _list_topics(self, query: str = "") -> None:
        topics = self.query_one("#help-topics", OptionList)
        topics.clear_options()
        options: list[Option] = []
        if query.strip():
            found = self.book.search(query)
            options.append(_heading(f"FOUND ({len(found)})"))
            options += [Option(escape(t.title), id=_FOUND + t.id) for t in found]
        else:
            here = self._here()
            if here:
                options.append(_heading("THIS SCREEN"))
                options += [
                    Option(escape(self.book.topics[t].title), id=_HERE + t)
                    for t in here
                ]
            options.append(_heading("REFERENCE"))
            options.append(Option("About this App", id=_REF + ABOUT))
            options += [
                Option(escape(self.book.topics[t].title), id=_REF + t)
                for t in _REFERENCE
                if t in self.book.topics
            ]
            options.append(_heading("ALL PAGES"))
            for page in self.book.pages.values():
                if page.id in _REFERENCE:
                    continue
                indent = "  " if self.book.topics[page.id].level == 2 else ""
                options.append(Option(indent + escape(page.title), id=_ALL + page.id))
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
        if topic_id == ABOUT:
            try:
                notice = NOTICE_PATH.read_text(encoding="utf-8")
            except OSError:
                notice = "NOTICE.md is missing: see the repository for licences."
            return ABOUT, f"# Ars Magica Manager v{__version__}\n\n{notice}"
        page = self.book.page_for(topic_id)
        if page is None:
            return None
        return page.id, ht.display_text(page.text)

    def show_topic(self, topic_id: str, *, here: bool = False) -> None:
        """Show `topic_id`'s page, scrolled to it; the keys line only for
        where Help was opened from."""
        found = self._page_text(topic_id)
        if found is None:
            return
        page_id, text = found
        self.topic_id = topic_id
        keys = self.query_one("#help-keys", Static)
        if here and self.context.keys:
            keys.update("Keys here:  " + "   ".join(self.context.keys))
            keys.display = True
        else:
            keys.display = False
        if page_id != self._page_shown:
            self._page_shown = page_id
            markdown = self.query_one("#help-page", Markdown)
            self.run_worker(self._load(markdown, text, topic_id), exclusive=True)
        else:
            self._scroll_to(topic_id)

    async def _load(self, markdown: Markdown, text: str, topic_id: str) -> None:
        await markdown.update(text)
        self._scroll_to(topic_id)

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
                heading = markdown.query_one(f"#{block_id}")
                if heading.virtual_region.y == 0 and tries:
                    self.call_after_refresh(self._scroll_to, topic_id, tries - 1)
                    return
                scroll.scroll_to_widget(heading, top=True, animate=False)
                return

    def on_markdown_link_clicked(self, event: Markdown.LinkClicked) -> None:
        href = event.href
        if href.startswith("help:"):
            event.prevent_default()
            topic_id = href.removeprefix("help:")
            option = _ALL + topic_id
            topics = self.query_one("#help-topics", OptionList)
            try:
                topics.highlighted = topics.get_option_index(option)
            except OptionDoesNotExist:  # a topic on a page: show it
                self.show_topic(topic_id)
        elif href.startswith(("http://", "https://")):
            self.app.open_url(href)


def _heading(text: str) -> Option:
    return Option(f"[b]{text}[/]", disabled=True)
