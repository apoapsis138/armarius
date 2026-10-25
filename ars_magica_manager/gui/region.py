"""The desktop's page for a neighbour (the saga page's Region chapter
lists them as cards: pages.region_chapter): its facts and summary over
its attitude toward each player covenant, the favours owed and its
links. What it says comes from sheets/region.py; its buttons run
forms/neighbour.py."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from .. import (
    arms,
    battles,
    lords,
    manors,
    neighbours,
    place_events,
    town_court,
    towns,
)
from ..commands import Command, SectionOps
from ..forms import neighbour as neighbour_forms
from ..models import Neighbour, Saga
from ..neighbour_lists import KindBlock, KindList, KindTab
from ..sections import (
    BATTLES_SECTION,
    COURT_CASES_SECTION,
    ESTABLISHMENTS_SECTION,
    FAIRS_SECTION,
    GRATITUDE_SECTION,
    HOUSEHOLD_SECTION,
    MANORS_SECTION,
    TABLES_SECTION,
)
from ..sheets import region as region_sheet
from .bookmark import with_bookmark
from .character_sheet import (
    TextBlock,
    is_aligned,
    label_values,
    secrets_chapter,
    section,
    side_by_side,
)
from .editing import Chooser, RowVerb, Run, follower, verb_buttons
from .figures import fact_grid, prose
from .heraldry import arms_section
from .manage import RecordControls
from .ornaments import InspectorFrame
from .pages import page_header
from .themes import Palette
from .widgets import Codex, edit_button, scrolling_page, serif, table_view, text
from .world import relations


def _column(words: str, p: Palette) -> QWidget:
    """A column of a block: label: value lines as a grid, under a bold
    first line as its heading; other lines (a list of ticks) in the book
    face."""
    first, _, rest = words.partition("\n")
    if not rest or not first.startswith("[b]"):
        if all(is_aligned(line) for line in words.splitlines()):
            return label_values(words, p)
        block = TextBlock(words, p)
        block.setFont(serif(12.5))
        return block
    box = QWidget()
    column = QVBoxLayout(box)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(4)
    column.addWidget(TextBlock(first, p))
    column.addWidget(label_values(rest, p))
    column.addStretch(1)
    return box


class NeighbourPage(QWidget):
    """A neighbour in the Codex layout."""

    def __init__(
        self,
        saga: Saga,
        neighbour: Neighbour,
        p: Palette,
        run: Run = lambda _command: None,
        controls: RecordControls | None = None,
    ) -> None:
        super().__init__()
        self.saga, self.neighbour, self.p, self.run = saga, neighbour, p, run
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(
            with_bookmark(
                page_header(
                    neighbour.name,
                    region_sheet.card_subtitle(neighbour),
                    p,
                    neighbours.icon_concept(neighbour),
                ),
                controls.bookmark(p) if controls else None,
            )
        )
        outer.addWidget(
            fact_grid(
                region_sheet.neighbour_facts(saga, neighbour),
                p,
                3,
                follow=follower(run),
            )
        )
        self.codex = Codex(p)
        self.ops = neighbour_forms.neighbour_ops(saga, neighbour)
        self.kinds = KindChapters(saga, neighbour, p, run, self.ops, self.codex)
        kind = neighbours.kind_of(neighbour)
        if kind.tab is not None:
            self.codex.add(
                kind.tab.title, kind.tab.icon or kind.key, self._kind_chapter(kind.tab)
            )
        for more in (m for m in kind.more if not m.after_standing):
            self.codex.add(
                more.title, more.icon or kind.key, self._kind_chapter(more, facts=False)
            )
        self.codex.add(
            "Standing" if kind.attitude else "Found Here", "region", self._standing()
        )
        for more in (m for m in kind.more if m.after_standing):
            self.codex.add(
                more.title, more.icon or kind.key, self._kind_chapter(more, facts=False)
            )
        self.codex.add("Secrets", "secrets", secrets_chapter(neighbour, p, run))
        if controls is not None:
            self.codex.add("Manage", "manage", controls.chapter(p))
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def _edit(self) -> None:
        self.run(neighbour_forms.edit_neighbour_form(self.saga, self.neighbour))

    def _kind_chapter(self, tab: KindTab, facts: bool = True) -> QWidget:
        """What the neighbour's kind works out (on its first chapter),
        then its lists."""
        saga, n, p = self.saga, self.neighbour, self.p
        worked_out = neighbours.kind_of(n).facts
        head: list[QWidget] = []
        if facts:
            head.append(
                section(
                    tab.title,
                    p,
                    fact_grid(
                        worked_out(saga, n) if worked_out is not None else [],
                        p,
                        2,
                        follow=follower(self.run),
                    ),
                    edits={"Edit Neighbour": self._edit},
                )
            )
        return self.kinds.chapter(tab, head)

    def _standing(self) -> QWidget:
        p = self.p
        summary = self.neighbour.summary.strip()
        return scrolling_page(
            p,
            section(
                "Summary",
                p,
                prose(summary, p)
                if summary
                else text(
                    "Not written yet: edit the neighbour to say.",
                    p["dim"],
                    serif(12.5, italic=True),
                    wrap=True,
                ),
                edits={"Edit Neighbour": self._edit},
            ),
            *(
                [arms_section(self.neighbour, p, self.run)]
                if arms.bears_arms(self.neighbour)
                else []
            ),
            *relations(
                self.saga,
                self.neighbour,
                p,
                self.run,
                attitude=neighbours.kind_of(self.neighbour).attitude,
            ),
        )


def _gloss(
    heading: str, words: str, p: Palette, edits: dict[str, Callable[[], None]]
) -> QWidget:
    """A check boxed as a gloss, with its Edit at its foot."""
    panel = InspectorFrame(heading, p)
    box = QVBoxLayout(panel)
    box.setContentsMargins(InspectorFrame.MARGIN, 44, 20, 16)
    block = TextBlock(words, p)
    block.setFont(serif(13))
    box.addWidget(block)
    if edits:
        row = QHBoxLayout()
        row.addStretch(1)
        for label, on_click in edits.items():
            row.addWidget(edit_button(label, p, on_click))
        box.addLayout(row)
    return panel


class KindChapters:
    """A kind's tabs as desktop chapters: their lists as ledger tables whose
    chosen row shows in the inspector, with their section's buttons, and
    their blocks of worked-out text. Drawn for a neighbour, and for a
    covenant's Manors (manors.manors_of adapts it to a neighbour)."""

    def __init__(
        self,
        saga: Saga,
        n: Neighbour,
        p: Palette,
        run: Run,
        ops: dict[str, SectionOps],
        codex: Codex,
    ) -> None:
        self.saga, self.n, self.p, self.run = saga, n, p, run
        self.ops, self.codex = ops, codex

    def chapter(self, tab: KindTab, head: Sequence[QWidget] = ()) -> QWidget:
        """`head`, then the tab's lists and blocks in order."""
        shown: list[QWidget] = list(head)
        for entry in tab.parts():
            if isinstance(entry, KindBlock):
                shown.append(self._block(entry))
                continue
            shown.append(
                self._grid(entry, self._more(entry.section_id), self._edits(entry))
            )
        return scrolling_page(self.p, *shown)

    def _more(self, section_id: str) -> list[RowVerb]:
        """The More commands drawn as the section's own buttons, acting on
        its chosen row."""
        saga, n = self.saga, self.n
        verbs: dict[str, list[tuple[str, str, Callable[[int], Command]]]] = {
            TABLES_SECTION: [
                ("Roll", "more", lambda row: place_events.roll_table(saga, n, row))
            ],
            FAIRS_SECTION: [
                ("Roll Income", "income", lambda row: towns.roll_fair(saga, n, row))
            ],
            GRATITUDE_SECTION: [
                (
                    "Redeem Gratitude",
                    "more",
                    lambda row: lords.redeem_form(saga, n, row),
                )
            ],
            COURT_CASES_SECTION: [
                (
                    "Court Roll",
                    "more",
                    lambda row: town_court.court_roll(saga, n, row),
                )
            ],
            BATTLES_SECTION: [
                ("Battle Event", "more", lambda row: battles.event_for(saga, n, row))
            ],
            MANORS_SECTION: [
                ("Assart", "more", lambda row: manors.assart_form(saga, n, row))
            ],
            ESTABLISHMENTS_SECTION: [
                (
                    "Winter Roll",
                    "season",
                    lambda row: manors.winter_roll(saga, n, row),
                )
            ],
        }
        return [
            (words, concept, step, lambda _row: True)
            for words, concept, step in verbs.get(section_id, [])
        ]

    def _edits(self, entry: KindList | KindBlock) -> dict[str, Callable[[], None]]:
        """The section's commands that need no chosen row."""
        saga, n, run = self.saga, self.n, self.run
        if entry.section_id == MANORS_SECTION:
            return {manors.BUY: lambda: run(manors.buy_form(saga, n))}
        if entry.section_id == HOUSEHOLD_SECTION:
            return {manors.SETTLE: lambda: run(manors.settle_form(saga, n))}
        return {}

    def _grid(
        self,
        entry: KindList,
        more: Sequence[RowVerb],
        edits: dict[str, Callable[[], None]],
    ) -> QWidget:
        """The list `entry` as a table under its title, with its section's
        Add, Edit and Delete (and `more`) acting on the row chosen;
        choosing a row also shows it in full in the inspector."""
        saga, n, p = self.saga, self.n, self.p
        title, grid = entry.title(saga, n), entry.grid(saga, n)
        chooser = Chooser()

        def choose(row: int) -> None:
            chooser.choose(row)
            shown = (
                entry.info(saga, n, row)
                if entry.info is not None
                else grid.row_text(row)
            )
            if shown and row in grid.keys:
                name = grid.rows[grid.keys.index(row)][0]
                self.codex.inspect(name, title.split(" (")[0], shown)

        body = (
            table_view(grid.table(), p, choose)
            if grid.rows
            else text(grid.empty, p["dim"], serif(12.5, italic=True), wrap=True)
        )
        buttons = verb_buttons(
            self.ops[entry.section_id], chooser, self.run, p, more=more
        )
        # The commands that need no row go after Add, Edit and Delete.
        ops = self.ops[entry.section_id]
        verbs = sum(step is not None for step in (ops.add, ops.edit, ops.remove))
        buttons[verbs:verbs] = [
            edit_button(words, p, on_click) for words, on_click in edits.items()
        ]
        header = entry.header(saga, n) if entry.header is not None else ""
        widgets = [TextBlock(header, p), body] if header else [body]
        return section(title, p, *widgets, buttons=buttons)

    def _block(self, block: KindBlock) -> QWidget:
        """A block of worked-out text under its title: its facts as a
        grid, each paragraph of its text (label: value lines as a grid),
        then its columns side by side, with its Edit beside the title; a
        gloss block boxed as a gloss."""
        saga, n, p = self.saga, self.n, self.p
        edit = block.edit
        edits = (
            {block.edit_label: lambda: self.run(edit(saga, n))}
            if edit is not None
            else {}
        )
        edits.update(self._edits(block))
        if block.gloss:
            words = block.text(saga, n) if block.text is not None else ""
            return _gloss(block.title, words, p, edits)
        shown: list[QWidget] = []
        if block.facts is not None:
            shown.append(fact_grid(block.facts(saga, n), p, 3))
        if block.text is not None:
            shown += [
                label_values(paragraph, p)
                for paragraph in block.text(saga, n).split("\n\n")
                if paragraph.strip()
            ]
        if block.columns is not None:
            shown.append(
                side_by_side(*(_column(column, p) for column in block.columns(saga, n)))
            )
        return section(block.title, p, *shown, edits=edits or None)
