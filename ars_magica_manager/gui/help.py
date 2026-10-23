"""The desktop Help page: the same help pages the terminal's Help shows
(help_text.py), opened with ? or F1 or the top bar's Help on the help for the
page on show.

The topics are listed on the left under THIS PAGE, HOW-TO GUIDES,
REFERENCE and ALL PAGES (help_text.contents), with a box that filters
them; the chosen topic's page is on the right, drawn from its Markdown
and scrolled to the topic. A `help:` link shows that topic; a web link
opens in the browser.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from .. import help_text as ht
from . import pictures
from .pages import page_header
from .themes import Palette

#: The list's group headings, as the terminal's Help names them.
_HERE_HEADING = "THIS SCREEN"
#: An entry's topic id, on its list item.
_TOPIC = Qt.ItemDataRole.UserRole


class HelpPage(QWidget):
    """Help, opened on `here` (the topic ids for the page it was opened
    from, most specific first; `where` names that page)."""

    def __init__(self, p: Palette, here: list[str], where: str = "") -> None:
        super().__init__()
        self.p = p
        self.book = ht.book(ht.GUI)
        self.here = here
        self._page_shown: str | None = None
        #: The topic on show.
        self.topic_id: str | None = None
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(
            page_header("Help", f"Opened on {where}" if where else "", p, "help")
        )
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filter topics")
        self.filter.setClearButtonEnabled(True)
        self.filter.textChanged.connect(self._list)
        self.topics = QListWidget()
        self.topics.currentItemChanged.connect(self._chosen)
        side = QWidget()
        column = QVBoxLayout(side)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(self.filter)
        column.addWidget(self.topics, 1)
        self.page = QTextBrowser()
        self.page.setOpenLinks(False)
        self.page.anchorClicked.connect(self._link)
        self.page.setStyleSheet(
            f"QTextBrowser {{ background:{p['surface']}; border:none;"
            " padding:8px 14px; }"
        )
        split = QSplitter()
        split.addWidget(side)
        split.addWidget(self.page)
        split.setStretchFactor(1, 1)
        split.setSizes([300, 900])
        row = QHBoxLayout()
        row.addWidget(split)
        outer.addLayout(row, 1)
        self._list()
        start = self._here()
        self.show_topic(start[0] if start else "keys")

    def _here(self) -> list[str]:
        return [t for t in dict.fromkeys(self.here) if t in self.book.topics]

    # The topic list

    def _list(self, query: str = "") -> None:
        self.topics.blockSignals(True)
        self.topics.clear()
        for heading, entries in ht.contents(self.book, self.here, query):
            item = QListWidgetItem(heading, self.topics)
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            font = item.font()
            font.setBold(True)
            item.setFont(font)
            for entry in entries:
                listed = QListWidgetItem(
                    "    " * (entry.indent + 1) + entry.title, self.topics
                )
                listed.setData(_TOPIC, entry.id)
        self.topics.blockSignals(False)
        if query.strip():
            first = self._item(lambda _item: True)
            if first is not None:
                self.topics.setCurrentItem(first)

    def entries(self) -> list[str]:
        """The topic list as shown: headings and titles."""
        return [self.topics.item(i).text().strip() for i in range(self.topics.count())]

    def _item(
        self, matches: Callable[[QListWidgetItem], bool]
    ) -> QListWidgetItem | None:
        for i in range(self.topics.count()):
            item = self.topics.item(i)
            if item.data(_TOPIC) is not None and matches(item):
                return item
        return None

    def _chosen(self, item: QListWidgetItem | None) -> None:
        topic_id = item.data(_TOPIC) if item is not None else None
        if topic_id:
            self._show(topic_id)

    # The page

    def show_topic(self, topic_id: str) -> None:
        """Choose `topic_id` in the list (its first listing) and show it;
        a topic on a page, not listed, is shown all the same."""
        item = self._item(lambda listed: listed.data(_TOPIC) == topic_id)
        if item is not None:
            self.topics.setCurrentItem(item)
        else:
            self._show(topic_id)

    def _show(self, topic_id: str) -> None:
        found = ht.page_text(self.book, topic_id)
        if found is None:
            return
        page_id, markdown = found
        self.topic_id = topic_id
        if page_id != self._page_shown:
            self._page_shown = page_id
            self.page.setMarkdown(markdown)
            self._rubricate()
        self._scroll_to(topic_id)

    def _rubricate(self) -> None:
        """Set the page's headings in the serif, in the heading colour,
        as the rest of the app's are."""
        heading = QTextCharFormat()
        heading.setForeground(QColor(self.p["heading"]))
        heading.setFontFamilies([pictures.SERIF])
        link = QTextCharFormat()
        link.setForeground(QColor(self.p["primary"]))
        block = self.page.document().begin()
        while block.isValid():
            if block.blockFormat().headingLevel():
                cursor = QTextCursor(block)
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                cursor.mergeCharFormat(heading)
            fragments = block.begin()
            while not fragments.atEnd():
                fragment = fragments.fragment()
                if fragment.isValid() and fragment.charFormat().isAnchor():
                    cursor = QTextCursor(self.page.document())
                    cursor.setPosition(fragment.position())
                    cursor.setPosition(
                        fragment.position() + fragment.length(),
                        QTextCursor.MoveMode.KeepAnchor,
                    )
                    cursor.mergeCharFormat(link)
                fragments += 1
            block = block.next()

    def _scroll_to(self, topic_id: str) -> None:
        """Scroll the page to `topic_id`'s heading (its top for a page)."""
        bar = self.page.verticalScrollBar()
        topic = self.book.topic(topic_id)
        if topic is None or topic.level < 3:
            bar.setValue(0)
            return
        found = self.page.document().find(
            topic.title, 0, QTextDocument.FindFlag.FindCaseSensitively
        )
        while not found.isNull() and found.block().blockFormat().headingLevel() == 0:
            found = self.page.document().find(
                topic.title, found, QTextDocument.FindFlag.FindCaseSensitively
            )
        if found.isNull():
            return
        found.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        bar.setValue(
            int(
                self.page.document()
                .documentLayout()
                .blockBoundingRect(found.block())
                .top()
            )
        )

    def _link(self, url: QUrl) -> None:
        href = url.toString()
        if href.startswith("help:"):
            self.show_topic(href.removeprefix("help:"))
        elif href.startswith(("http://", "https://")):
            QDesktopServices.openUrl(url)

    def shown_text(self) -> str:
        """The page on show, as plain text."""
        return self.page.toPlainText()
