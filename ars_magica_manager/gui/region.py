"""The desktop's page for a neighbour (the saga page's Region chapter
lists them as cards: pages.region_chapter): its facts and summary over
its attitude toward each player covenant, the favours owed and its
links. What it says comes from sheets/region.py; its buttons run
forms/neighbour.py."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from .. import (
    arms,
    battles,
    hermetic_projects,
    lords,
    manors,
    marriages,
    menagerie,
    neighbours,
    place_events,
    staged_projects,
    tombs,
    town_court,
    towns,
)
from ..commands import Act, Command, Refuse, SectionOps
from ..forms import charter_strength as charter_strength_forms
from ..forms import hunting as hunting_forms
from ..forms import neighbour as neighbour_forms
from ..forms import threshold as threshold_forms
from ..models import Covenant, Neighbour, Saga
from ..models.hermetic_projects import BURNING_CITY, INTANGIBLE_ASSASSIN, LIVING_CORPSE
from ..neighbour_lists import KindBlock, KindList, KindTab, LedgerEntry
from ..sections import (
    BATTLES_SECTION,
    BEASTS_SECTION,
    CHARTER_LORDS_SECTION,
    COURT_CASES_SECTION,
    ESTABLISHMENTS_SECTION,
    FAIRS_SECTION,
    GRATITUDE_SECTION,
    HOUSEHOLD_SECTION,
    MANORS_SECTION,
    MARRIAGES_SECTION,
    PROJECTS_SECTION,
    STAGED_SECTION,
    TABLES_SECTION,
    TOMB_TRAPS_SECTION,
    TOWER_SECTION,
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
from .editing import Chooser, RowVerb, Run, follower, open_in_a_window, verb_buttons
from .figures import fact_grid, prose
from .heraldry import arms_section
from .manage import RecordControls
from .ornaments import InspectorFrame
from .pages import page_header
from .ruled_entry import RuledEntry
from .themes import Palette
from .widgets import (
    Codex,
    badge,
    chip_row,
    edit_button,
    scrolling_page,
    serif,
    table_view,
    text,
)
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
    """A neighbour in the Codex layout.
    Its buttons' forms, lists and questions open as windows over it."""

    def __init__(
        self,
        saga: Saga,
        neighbour: Neighbour,
        p: Palette,
        run: Run = lambda _command: None,
        controls: RecordControls | None = None,
    ) -> None:
        super().__init__()
        open_in_a_window(self)
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
        shown = [m for m in kind.more if m.shows(neighbour)]
        for more in (m for m in shown if not m.after_standing):
            self.codex.add(
                more.title, more.icon or kind.key, self._kind_chapter(more, facts=False)
            )
        self.codex.add(
            "Standing" if kind.attitude else "Found Here", "region", self._standing()
        )
        for more in (m for m in shown if m.after_standing):
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
                    edits={
                        "Edit Neighbour": self._edit,
                        **(
                            {
                                threshold_forms.TITLE: lambda: self.run(
                                    threshold_forms.threshold_form(saga, n)
                                )
                            }
                            if threshold_forms.offers(saga, n)
                            else {}
                        ),
                    },
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


def _on_covenant(
    saga: Saga, n: Neighbour, step: Callable[[Covenant], Command]
) -> Command:
    """`step` on the covenant a kind tab shows (its record adapted as a
    neighbour's, manors.manors_of); a refusal on any other record."""
    covenant = saga.covenant(n.id)
    if covenant is None:
        return Refuse("Hermetic Projects", "Only a covenant keeps projects.")
    return step(covenant)


def _staged_edits(saga: Saga, n: Neighbour, run: Run) -> dict[str, Callable[[], None]]:
    """The staged project shown's commands, by its kind: a Burning City's
    Warning Bell, an Intangible Assassin's Gather a Connection and Lower
    an Aegis, a Living Corpse's Death Roll."""
    project = staged_projects.shown(saga, n)
    kind = project.kind if project is not None else ""
    found: dict[str, Callable[[Covenant], Command]] = {
        BURNING_CITY: {
            staged_projects.WARNING_BELL: lambda c: staged_projects.bell_form(saga, c)
        },
        INTANGIBLE_ASSASSIN: {
            staged_projects.GATHER: lambda c: staged_projects.gather_form(saga, c),
            staged_projects.LOWER_AEGIS: lambda c: staged_projects.aegis_form(saga, c),
        },
        LIVING_CORPSE: {
            staged_projects.DEATH_ROLL: lambda c: staged_projects.death_form(saga, c)
        },
    }.get(kind, {})
    return {
        label: (lambda step=step: run(_on_covenant(saga, n, step)))
        for label, step in found.items()
    }


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
                ("Assart", "more", lambda row: manors.assart_form(saga, n, row)),
                # The hunt and Area Lore on the chosen manor.
                (
                    hunting_forms.HUNT_TITLE,
                    "more",
                    lambda row: hunting_forms.hunt_on_manor(saga, n, row),
                ),
                (
                    hunting_forms.AREA_LORE_TITLE,
                    "more",
                    lambda row: hunting_forms.area_lore_on_manor(saga, n, row),
                ),
            ],
            ESTABLISHMENTS_SECTION: [
                (
                    "Winter Roll",
                    "season",
                    lambda row: manors.winter_roll(saga, n, row),
                )
            ],
            # A tomb's trap springs (Lands of the Nile).
            TOMB_TRAPS_SECTION: [
                (
                    "Overcome It",
                    "threat",
                    lambda row: tombs.overcome_trap(saga, n, row),
                )
            ],
            # A covenant's Hermetic Projects: the project the tab shows.
            PROJECTS_SECTION: [
                (
                    hermetic_projects.SHOW_PROJECT,
                    "more",
                    lambda row: _on_covenant(
                        saga,
                        n,
                        lambda c: hermetic_projects.show_project(saga, c, row),
                    ),
                )
            ],
            # A lord's marriages: the chosen one ends.
            MARRIAGES_SECTION: [
                (
                    marriages.END,
                    "more",
                    lambda row: marriages.end_form(saga, n, row),
                )
            ],
            # A covenant's Menagerie: taming the chosen beast.
            BEASTS_SECTION: [
                (
                    menagerie.TAME_BEAST,
                    "more",
                    lambda row: _on_covenant(
                        saga, n, lambda c: menagerie.tame_form(saga, c, row)
                    ),
                ),
                (
                    menagerie.REPUTATION_AWARD,
                    "more",
                    lambda row: _on_covenant(
                        saga, n, lambda c: menagerie.award_form(saga, c, row)
                    ),
                ),
            ],
        }
        # Charter Strength (TME p. 36): the charter lords' own buttons.
        if charter_strength_forms.offered(saga):
            verbs[CHARTER_LORDS_SECTION] = [
                (
                    charter_strength_forms.DRAFT_TITLE,
                    "more",
                    lambda row: charter_strength_forms.draft_form(saga, n, row),
                ),
                (
                    charter_strength_forms.LOOPHOLE_TITLE,
                    "more",
                    lambda row: charter_strength_forms.loophole_form(saga, n, row),
                ),
            ]
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
        # A covenant's Hermetic Projects: the tower's Stress Check and
        # Conjure Levels.
        if entry.section_id == TOWER_SECTION:
            return {
                hermetic_projects.STRESS_CHECK: lambda: run(
                    _on_covenant(
                        saga, n, lambda c: hermetic_projects.stress_form(saga, c)
                    )
                ),
                hermetic_projects.CONJURE_LEVELS: lambda: run(
                    _on_covenant(
                        saga, n, lambda c: hermetic_projects.conjure_form(saga, c)
                    )
                ),
            }
        # A staged project: its kind's own commands.
        if entry.section_id == STAGED_SECTION:
            return _staged_edits(saga, n, run)
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

        if entry.ledger is not None and grid.rows:
            body = self._ledger(entry, grid.keys, chooser)
        else:
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
        toggles = entry.toggles(saga, n) if entry.toggles is not None else []
        if toggles:
            run = self.run
            widgets.insert(
                0,
                chip_row(
                    "Show",
                    [
                        (t.label, t.on, lambda flip=t.flip: run(Act(flip)))
                        for t in toggles
                    ],
                    p,
                ),
            )
        return section(title, p, *widgets, buttons=buttons)

    def _ledger(
        self, entry: KindList, keys: Sequence[int | None], chooser: Chooser
    ) -> QWidget:
        """The list `entry` as entries ruled off on the page; choosing one
        shows it in full in the inspector."""
        saga, n, p = self.saga, self.n, self.p
        ledger = entry.ledger
        found = ledger(saga, n) if ledger is not None else []
        rows = [LedgerRow(e, p) for e in found]
        for row, shown, key in zip(rows, found, keys, strict=False):
            if key is None:
                continue

            def clicked(shown: LedgerEntry = shown, key: int = key) -> None:
                info = entry.info(saga, n, key) if entry.info is not None else ""
                self.codex.inspect(shown.title, shown.subtitle, info)

            def chosen(
                row_clicked: Callable[[], None] = clicked, key: int = key
            ) -> None:
                chooser.choose(key)
                row_clicked()

            row.clicked = chosen

        def mark(picked: int | None) -> None:
            for row, key in zip(rows, keys, strict=False):
                row.set_chosen(key == picked)

        chooser.listeners.append(mark)
        body = QWidget()
        stack = QVBoxLayout(body)
        stack.setContentsMargins(0, 0, 0, 0)
        stack.setSpacing(2)
        for row in rows:
            stack.addWidget(row)
        return body

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
            return _gloss(block.titled(saga, n), words, p, edits)
        shown: list[QWidget] = []
        if block.facts is not None:
            shown.append(fact_grid(block.facts(saga, n), p, 3))
        words = block.prose(saga, n) if block.prose is not None else ""
        if words:
            shown.append(prose(words, p))
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
        return section(block.titled(saga, n), p, *shown, edits=edits or None)


class LedgerRow(RuledEntry):
    """A row of a kind's list ruled off on the page, as in a muster roll:
    a mark in the margin, its heading in small capitals with an italic
    line and a badge beside it, then its words and a note."""

    def __init__(self, entry: LedgerEntry, p: Palette) -> None:
        super().__init__(p)
        row = self.ruled_row()
        mark = text(entry.rubric, p["heading"], serif(18, bold=True))
        mark.setFixedWidth(40)
        mark.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        row.addWidget(mark, 0, Qt.AlignmentFlag.AlignTop)
        column = QVBoxLayout()
        column.setSpacing(3)
        top = QHBoxLayout()
        top.setSpacing(8)
        top.addWidget(
            text(entry.title, p["heading"], serif(12.5, bold=True, caps=True))
        )
        if entry.meta:
            top.addWidget(text(entry.meta, p["label"], serif(11, italic=True)))
        top.addStretch(1)
        if entry.badge:
            top.addWidget(badge(entry.badge, p[entry.tone], p))
        column.addLayout(top)
        if entry.body:
            words = TextBlock(entry.body, p)
            words.setFont(serif(13))
            column.addWidget(words)
        if entry.note:
            note = TextBlock(entry.note, p)
            note.setFont(serif(11.5))
            column.addWidget(note)
        row.addLayout(column, 1)
