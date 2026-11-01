"""The desktop Character sheet in the Codex layout: a header
with the name and the character's state at a glance, the
Characteristics as cards, a rail of chapters on the left and an
inspector on the right that shows whatever was last chosen.

What it says comes from the shared core (sheets/character.py and the
modules it reads), the same text and figures the terminal sheet shows;
only how it is drawn is here. The tables are Qt Model/View: a
QStandardItemModel of the core's rows, shown by a view (a proxy model
sorts and filters the spells). Every choice is a signal the inspector
listens to.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from typing import Any

from PySide6.QtCore import QModelIndex, QRectF, QSize, QSortFilterProxyModel, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QIcon,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QPixmap,
    QShowEvent,
    QStandardItem,
    QStandardItemModel,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableView,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from .. import (
    artwork,
    casting_text,
    catalog,
    connections,
    creation,
    deeds,
    giving,
    marriages,
    portraits,
    seasons,
    sourcebooks,
    tradition_text,
    traditions,
    vis,
)
from .. import books as bk
from .. import enchanted_devices as ed
from .. import lab_texts as lt
from .. import laboratories as labs
from .. import lineage as lineages
from .. import saga_overview as ov
from .. import sheet_text as st
from .. import spells as spl
from ..actions import NodeKind
from ..arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from ..commands import Command, Form, SectionOps
from ..forms import ability as ability_forms
from ..forms import agents as agent_forms
from ..forms import character as cf
from ..forms import church as church_forms
from ..forms import constant_effect as constant_forms
from ..forms import covers as cover_forms
from ..forms import criamon as criamon_forms
from ..forms import device as device_forms
from ..forms import diary as diary_forms
from ..forms import menu as menu_forms
from ..forms import power as power_forms
from ..forms import religion as religion_forms
from ..forms import season as season_forms
from ..forms import spell as spell_forms
from ..forms import tradition as tradition_forms
from ..forms import trait as trait_forms
from ..forms import virtue as virtue_forms
from ..forms import vis as vis_forms
from ..forms import whereabouts as whereabouts_forms
from ..forms.secrets import NONE_YET, secrets_form
from ..markup import escape
from ..models import (
    CHARGED,
    LINE,
    Agent,
    Character,
    Characteristics,
    Saga,
    ScoredTrait,
    TraditionDef,
)
from ..references import Fact
from ..rules import activities as season_rules
from ..rules import agents as agent_rules
from ..rules import criamon as criamon_rules
from ..rules import enchantment, faiths, hybrid_magic, library, sigils
from ..sections import (
    CANON_SECTION,
    COVERS_SECTION,
    ORDINATIONS_SECTION,
    PETITIONS_SECTION,
    STIGMATA_SECTION,
)
from ..sheets import character as cs
from ..sheets import familiar as fs
from ..sheets import laboratory as labs_sheet
from . import marks, motion, pictures
from .bookmark import with_bookmark
from .church import ledger as church_ledger
from .editing import (
    Chooser,
    RowVerb,
    Section,
    choose_cards,
    choose_rows,
    follower,
    give_verb,
    verb_buttons,
)
from .figures import (
    Dial,
    fact_grid,
    fatigue_ladder,
    prose,
    trait_list,
    wound_track,
)
from .manage import RecordControls
from .markup_html import plain, to_html
from .medallions import Medallion
from .menus import Placer
from .pages import action_rows, card_grid, familiar_card
from .research import research_chapter
from .style.ornaments import FleuronRule
from .themes import Palette
from .timeline import Calendar, legend, season_text
from .widgets import (
    ROW_HEIGHT,
    XP_BAR,
    XP_FROM,
    Card,
    ClickableCard,
    Codex,
    Pips,
    Symbol,
    TallRows,
    XpBarDelegate,
    arts_heat_grid,
    badge,
    chapter_title,
    chip,
    display_name,
    edit_button,
    scrolling_page,
    serif,
    table_view,
    text,
)
from .widgets import (
    table_style as _table_style,
)

#: The House symbol beside the name, and an Art's in a table, in pixels.
HOUSE_SYMBOL = 56
ART_SYMBOL = 20
#: Row heights of the tables.
ROW = ROW_HEIGHT
#: An Ability's mark in its row, the taller row it needs, and the mark
#: drawn large, with its engraved lines, in the panel beside the chapter.
ABILITY_MARK = 24
ABILITY_ROW = 34
ABILITY_MARK_LARGE = 64

#: The chapters, in order, with each one's icon (artwork.ICON_NAMES).
CHAPTERS = (
    ("Statblock", "character"),
    ("Description", "character"),
    ("Abilities", "library"),
    ("Virtues & Flaws", "magic"),
    # His faith and what it lets him do, and a cleric's career; its icon
    # is his faith's (forms.religion.icon).
    ("Religion", "church"),
    ("Hermetic Magic", "enchanted_item"),
    # A Criamon magus's path, its stations and his stigmata.
    ("The Enigma", "twilight"),
    ("Research", "lab_text"),
    ("Inventory", "combat"),
    ("Agents", "faction"),
    # What he does in play from the supplements, under his interests.
    ("Deeds", "deeds"),
    ("Planning", "season"),
    ("Diary", "year"),
    ("Secrets", "secrets"),
)

#: A status tone's colour (character_sheet.condition).
TONES = {cs.GOOD: "text-success", cs.WARNING: "text-warning", cs.BAD: "text-error"}


def _fixed_font() -> QFont:
    font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
    font.setFamilies(["Cascadia Mono", "Consolas", font.family()])
    return font


class TextBlock(QLabel):
    """Core text (app markup) as a selectable, wrapping label."""

    def __init__(
        self, words: str, palette: Palette, *, pre: bool = False, mono: bool = False
    ) -> None:
        """`pre` keeps runs of spaces; `mono` also sets a fixed-pitch font,
        for the core's tables padded into columns."""
        super().__init__(to_html(words, palette, pre=pre or mono))
        if mono:
            self.setFont(_fixed_font())
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)


_ALIGNED = re.compile(r"^\[\$label\](.*?):\s*\[/\] (.*)$")


def is_aligned(line: str) -> bool:
    """Whether `line` is one of the core's `label: value` lines
    (markup.aligned)."""
    return _ALIGNED.match(line) is not None


def label_values(words: str, palette: Palette) -> QWidget:
    """The core's `label: value` lines (markup.aligned) as a two-column
    grid, since a proportional font can't line them up with spaces; any
    other text as a TextBlock."""
    lines = [_ALIGNED.match(line) for line in words.splitlines()]
    if not lines or not all(lines):
        return TextBlock(words, palette)
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(12)
    grid.setVerticalSpacing(1)
    for row, match in enumerate(lines):
        assert match is not None
        grid.addWidget(
            text(f"{match.group(1)}:", palette["label"]),
            row,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        grid.addWidget(TextBlock(match.group(2), palette), row, 1)
    grid.setColumnStretch(1, 1)
    grid.setRowStretch(len(lines), 1)
    return box


_GAP = re.compile(r"\s{2,}")
_BOLD_LINE = re.compile(r"^\[b\](.*)\[/\]$")


def columns_text(words: str, p: Palette) -> QWidget:
    """The core's text padded into columns with spaces, as a grid, since
    the page's proportional type can't line them up: a line in bold stays
    bold in every cell, and the first column doesn't wrap."""
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(14)
    grid.setVerticalSpacing(1)
    rows = []
    for line in words.splitlines():
        bold = _BOLD_LINE.match(line.strip())
        inner = bold.group(1) if bold else line
        cells = _GAP.split(inner.strip()) if inner.strip() else [""]
        if bold:
            cells = [f"[b]{cell}[/]" if cell else "" for cell in cells]
        if inner.startswith("  ") and len(cells) > 1:
            cells.insert(0, "")
        rows.append(cells)
    width = max((len(cells) for cells in rows), default=1)
    for row, cells in enumerate(rows):
        if len(cells) == 1:
            grid.addWidget(TextBlock(cells[0] or " ", p), row, 0, 1, width)
            continue
        for column, cell in enumerate(cells):
            block = TextBlock(cell, p)
            if column == 0:
                block.setWordWrap(False)
            span = width - column if column == len(cells) - 1 else 1
            grid.addWidget(block, row, column, 1, span)
    grid.setColumnStretch(width - 1, 1)
    return box


def side_by_side(*widgets: QWidget, spacing: int = 24) -> QWidget:
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(spacing)
    for widget in widgets:
        row.addWidget(widget, 1, Qt.AlignmentFlag.AlignTop)
    return box


#: How many buttons sit beside a section's title, and how wide they and
#: each row under it may be: a chapter at its narrowest, beside the
#: inspector in a 1280-wide window, is about 720 pixels.
SIDE_BUTTONS = 6
SIDE_WIDTH = 440
ROW_WIDTH = 680


def _button_rows(controls: list[QWidget], shown: set[int]) -> list[list[QWidget]]:
    """`controls` in rows: the first beside the title (at most SIDE_BUTTONS
    of those shown, SIDE_WIDTH wide), the rest under it, each ROW_WIDTH
    wide, so a chapter never scrolls sideways. A hidden control keeps its
    place and takes no room."""
    rows: list[list[QWidget]] = [[]]
    count = width = 0
    for control in controls:
        if id(control) in shown:
            size = control.sizeHint().width()
            limit = SIDE_WIDTH if len(rows) == 1 else ROW_WIDTH
            full = len(rows) == 1 and count == SIDE_BUTTONS
            if count and (full or width + size > limit):
                rows.append([])
                count = width = 0
            count += 1
            width += size
        rows[-1].append(control)
    return rows


def section(
    title: str,
    p: Palette,
    *widgets: QWidget,
    edits: dict[str, Callable[[], None]] | None = None,
    buttons: Sequence[QWidget] = (),
    emblem: QWidget | None = None,
) -> Section:
    """A titled part of a chapter; `edits` (label -> what clicking it
    does) and `buttons` sit beside the title, and their steps open as
    windows over the page. Past SIDE_BUTTONS of them, the
    rest go on a row of their own under the title, so a narrow window
    never scrolls sideways. `emblem` (a season's medallion) goes before
    the title, and the buttons then stay level with the title's words."""
    box = Section()
    column = box.column
    controls = [
        edit_button(words, p, on_click) for words, on_click in (edits or {}).items()
    ] + list(buttons)
    if controls:
        # The buttons sit on the title's own line, above its rule, so they
        # read as the section's and not the one above.
        # Count only the buttons on offer (verb_buttons hides those with
        # nothing to act on).
        shown = [
            c
            for c in controls
            if not (
                c.testAttribute(Qt.WidgetAttribute.WA_WState_ExplicitShowHide)
                and c.isHidden()
            )
        ]
        rows = _button_rows(controls, set(map(id, shown)))
        beside, under = rows[0], rows[1:]
        head = QVBoxLayout()
        head.setSpacing(1)
        row = QHBoxLayout()
        row.setSpacing(2)
        row.addWidget(chapter_title(title, p, rule=False, emblem=emblem), 1)
        level = (
            Qt.AlignmentFlag.AlignBottom
            if emblem is None
            else Qt.AlignmentFlag.AlignVCenter
        )
        for control in beside:
            row.addWidget(control, 0, level)
        head.addLayout(row)
        for line in under:
            more = QHBoxLayout()
            more.setSpacing(2)
            more.addStretch(1)
            for control in line:
                more.addWidget(control)
            head.addLayout(more)
        head.addWidget(FleuronRule(p))
        column.addLayout(head)
    else:
        column.addWidget(chapter_title(title, p, emblem=emblem))
    for widget in widgets:
        column.addWidget(widget)
    return box


def secrets_chapter(record: Any, p: Palette, run: Callable[[Command], None]) -> QWidget:
    """A record's Secrets chapter (forms/secrets.py): what only the
    storyguide should read, edited through the core's form."""
    hidden = record.secrets.strip()
    return scrolling_page(
        p,
        section(
            "Secrets",
            p,
            prose(hidden, p)
            if hidden
            else text(NONE_YET, p["dim"], serif(12.5, italic=True), wrap=True),
            edits={"Edit Secrets": lambda: run(secrets_form(record))},
        ),
    )


def connections_section(
    saga: Saga, record: Any, p: Palette, run: Callable[[Command], None]
) -> QWidget:
    """A character's, covenant's or laboratory's Connections: the records
    that point at it or that it sits in (connections.py), each name a
    link that opens it."""
    found = connections.facts(saga, record)
    return section(
        "Connections",
        p,
        fact_grid(found, p, 2, follow=follower(run))
        if found
        else text("No connections.", p["dim"], serif(12.5, italic=True)),
    )


def trait_section(
    title: str,
    traits: list[ScoredTrait],
    section_id: str,
    p: Palette,
    run: Callable[[Command], None],
    more: Sequence[QWidget] = (),
) -> QWidget:
    """A Personality Traits or Reputations section, with Add, Edit and
    Delete for the row clicked (trait_forms.trait_ops), and `more`: the
    page's own buttons placed there (Reward or Punish on a grog)."""
    chooser = Chooser()
    ops = trait_forms.trait_ops(traits, section_id)
    # A Reputation marked bad (an Academic one) keeps a positive score.
    rows = [(f"{t.name} (bad)" if t.bad else t.name, t.score) for t in traits]
    return section(
        f"{title} ({len(rows)})",
        p,
        trait_list(rows, p, chooser.choose),
        buttons=[*verb_buttons(ops, chooser, run, p), *more],
    )


def device_section(
    saga: Saga,
    kind: str,
    holder_id: str,
    p: Palette,
    run: Callable[[Command], None],
    inspect: Callable[[str, str, str], None],
) -> QWidget:
    """The Enchanted Devices a character, laboratory or covenant holds:
    each device and its effects, with Add, Edit and Delete for the row
    clicked, and Instill an Effect, Use a Charge and Use (an effect) where
    they can act
    (device_forms)."""
    chooser = Chooser()
    ops = device_forms.device_ops(saga, kind, holder_id)
    targets = ed.device_targets(saga, kind, holder_id)

    def show(index: int) -> None:
        chooser.choose(index)
        device, effect = targets[index]
        name = enchantment.effect_name(effect) if effect is not None else device.name
        inspect(name, "Enchanted Device", ed.target_info_text(saga, targets[index]))

    more = [
        (
            "Instill",
            "magic",
            lambda row: device_forms.instill(saga, kind, holder_id, row),
            lambda row: device_forms.can_take_effect(targets[row][0]),
        ),
        (
            "Use Charge",
            "enchanted_item",
            lambda row: device_forms.use_charge(saga, kind, holder_id, row),
            lambda row: targets[row][1] is None and targets[row][0].type == CHARGED,
        ),
        (
            "Use",
            "magic",
            lambda row: device_forms.use_effect(saga, kind, holder_id, row),
            lambda row: ed.can_use(*targets[row]),
        ),
    ]
    holder = vis.find_holder(saga, kind, holder_id)
    if holder is not None:
        more.append(
            give_verb(saga, giving.DEVICE, holder, lambda: [t[0] for t in targets])
        )
    devices = len(enchantment.held_by(saga, kind, holder_id))
    return section(
        f"Enchanted Devices ({devices})",
        p,
        table_view(ed.device_table(saga, kind, holder_id), p, show)
        if targets
        else TextBlock("[dim]None recorded.[/]", p),
        buttons=verb_buttons(ops, chooser, run, p, more=more),
    )


def _fit_height(view: QAbstractItemView, rows: int, row: int = ROW) -> None:
    """Show every row, so the chapter scrolls rather than the table."""
    header = view.horizontalHeader() if isinstance(view, QTableView) else None
    if isinstance(view, QTreeView):
        header = view.header()
    top = header.sizeHint().height() if header is not None else 0
    view.setFixedHeight(rows * row + top + 2 * view.frameWidth() + 2)
    view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


def _item(words: str = "", *, font: QFont | None = None) -> QStandardItem:
    item = QStandardItem(words)
    item.setEditable(False)
    if font is not None:
        item.setFont(font)
    return item


#: How far each experience bar reached when last drawn, by its table's
#: memory and its row's name: what a bar that moved grows from.
_XP_DRAWN: dict[tuple[str, str], float] = {}


class XpTable(QTreeView):
    """Arts or Abilities as a table grouped under headings, the last column
    an experience bar to the next score. A row's `key` (an Art's name or
    an Ability's index) goes to `on_choose` when the row is chosen. Rows
    are `row` pixels tall, with `icon`-pixel symbols. Given a `memory`
    (whose table this is, as "character id:Abilities"), a bar that has
    moved since that table was last drawn grows to its new length when
    the table is first shown: from where it was, or from nothing for a
    score that went up."""

    def __init__(
        self,
        columns: Sequence[str],
        p: Palette,
        on_choose: Callable[[object], None],
        *,
        row: int = ROW,
        icon: int = ART_SYMBOL,
        memory: str = "",
    ) -> None:
        super().__init__()
        self.p, self.on_choose, self.row = p, on_choose, row
        self.memory = memory
        self.bars: list[tuple[str, QStandardItem, float]] = []
        self.grows = False
        self.model_ = QStandardItemModel(0, len(columns))
        self.model_.setHorizontalHeaderLabels(list(columns))
        self.setModel(self.model_)
        self.setItemDelegate(TallRows(row))
        self.xp_bars = XpBarDelegate(p, row)
        self.setItemDelegateForColumn(len(columns) - 1, self.xp_bars)
        self.setRootIsDecorated(False)
        self.setIndentation(10)
        self.setUniformRowHeights(True)
        self.setIconSize(QSize(icon, icon))
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        _table_style(self, p)
        self.rows = 0
        self.selectionModel().currentRowChanged.connect(self._chosen)

    def group(self, title: str) -> QStandardItem:
        head = _item(title, font=serif(13, caps=True, bold=True))
        head.setForeground(QBrush(QColor(self.p["heading"])))
        head.setSelectable(False)
        self.model_.appendRow(head)
        self.setFirstColumnSpanned(self.model_.rowCount() - 1, self.rootIndex(), True)
        self.rows += 1
        return head

    def add(
        self,
        group: QStandardItem | None,
        key: object,
        cells: Sequence[QStandardItem],
        fraction: float,
        bar: str,
    ) -> None:
        cells[0].setData(key, Qt.ItemDataRole.UserRole)
        last = _item()
        last.setData((fraction, bar), XP_BAR)
        (group or self.model_).appendRow([*cells, last])
        self.rows += 1
        self.bars.append((cells[0].text(), last, fraction))

    def finish(self) -> None:
        if self.memory:
            for name, cell, fraction in self.bars:
                drawn = _XP_DRAWN.get((self.memory, name))
                _XP_DRAWN[(self.memory, name)] = fraction
                if drawn is not None and drawn != fraction:
                    cell.setData(drawn if fraction > drawn else 0.0, XP_FROM)
                    self.grows = True
        self.expandAll()
        header = self.header()
        for column in range(self.model_.columnCount() - 1):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(
            self.model_.columnCount() - 1, QHeaderView.ResizeMode.Stretch
        )
        header.setStretchLastSection(True)
        _fit_height(self, self.rows, self.row)

    def sizeHintForRow(self, row: int) -> int:
        return self.row

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if self.grows:
            self.grows = False
            motion.tween(self, self._grow, motion.SLOW, name="grow")

    def _grow(self, value: float) -> None:
        self.xp_bars.at = value
        self.viewport().update()

    def _chosen(self, current: QModelIndex, _previous: QModelIndex) -> None:
        key = current.siblingAtColumn(0).data(Qt.ItemDataRole.UserRole)
        if key is not None:
            self.on_choose(key)


def _score_item(score: str) -> QStandardItem:
    font = QFont(pictures.UI)
    font.setPointSizeF(11)
    font.setBold(True)
    item = _item(score, font=font)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item


def _xp_words(xp: int, next_xp: int) -> str:
    return f"{xp} / {next_xp} xp"


class CharacterSheet(QWidget):
    """One character's sheet in the Codex layout."""

    def __init__(
        self,
        saga: Saga,
        character: Character,
        palette: Palette,
        open_familiar: Callable[[str], None] = lambda _id: None,
        run: Callable[[Command], None] = lambda _command: None,
        controls: RecordControls | None = None,
        placer: Placer | None = None,
        open_sanctum: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self.saga, self.character, self.p = saga, character, palette
        self.open_familiar = open_familiar
        #: Opens the magus's laboratory, or creates it while they have none.
        self.open_sanctum = open_sanctum
        self.run = run
        self.controls = controls
        self.placer = placer
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(
            with_bookmark(
                self._header(), controls.bookmark(self.p) if controls else None
            )
        )
        outer.addWidget(self._characteristics())

        self.codex = Codex(palette)
        self.inspector = self.codex.inspector
        builders = {
            "Statblock": self._statblock,
            "Description": self._description,
            "Abilities": self._abilities,
            "Virtues & Flaws": self._virtues_flaws,
            "Hermetic Magic": self._hermetic,
            "Research": self._research,
            "Inventory": self._inventory,
            "Agents": self._agents,
            "Religion": self._religion,
            "The Enigma": self._criamon,
            "Deeds": self._deeds,
            "Planning": self._planning,
            "Diary": self._diary,
            "Secrets": lambda: secrets_chapter(character, palette, run),
        }
        for name, concept in CHAPTERS:
            if name in _left_out(saga, character):
                continue
            if name == "Religion":
                concept = religion_forms.icon(character)
            self.codex.add(name, concept, builders[name]())
            if name == "Hermetic Magic" or (
                name == "Virtues & Flaws" and character.type != "magus"
            ):
                for tradition in traditions.of(character):
                    self.codex.add(tradition.title, "magic", self._tradition(tradition))
        if controls is not None:
            self.codex.add("Manage", "manage", controls.chapter(palette))
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def open_chapter(self, name: str) -> None:
        self.codex.open_chapter(name)

    def inspect(
        self, title: str, subtitle: str, markup: str, symbol: Symbol = None
    ) -> None:
        self.codex.inspect(title, subtitle, markup, symbol)

    # The header

    def _header(self) -> QWidget:
        """The House symbol, the name with a rubricated initial, the line
        under it, and Confidence, Warping, Decrepitude and condition."""
        p, c = self.p, self.character
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(14)
        self.portrait = Portrait(self.saga, c, p, self.run)
        row.addWidget(self.portrait, 0, Qt.AlignmentFlag.AlignTop)
        names = QVBoxLayout()
        names.setSpacing(0)
        heading = display_name(c.name, p)
        names.addWidget(heading)
        names.addWidget(
            text(cs.subtitle(self.saga, c), p["label"], serif(12.5, italic=True))
        )
        row.addLayout(names)
        row.addStretch(1)

        b = c.background
        confidence = QVBoxLayout()
        confidence.setSpacing(2)
        confidence.addWidget(text("Confidence", p["label"], serif(10, caps=True)))
        pips = QHBoxLayout()
        pips.addWidget(
            text(str(b.confidence_score), p["foreground"], serif(18, bold=True))
        )
        pips.addWidget(
            Pips(b.confidence_points, max(5, b.confidence_points), p["accent"])
        )
        confidence.addLayout(pips)
        confidence.addStretch(1)
        row.addLayout(confidence)
        row.addSpacing(10)
        row.addWidget(Dial(cs.warping_dial(c), "Warping", p["text-warning"], p))
        row.addWidget(Dial(cs.decrepitude_dial(c), "Decrepitude", p["text-error"], p))
        status = QVBoxLayout()
        status.setSpacing(4)
        for words, tone in cs.condition(c):
            status.addWidget(chip(words, p[TONES[tone]]))
        status.addStretch(1)
        row.addLayout(status)
        mode = self.controls.mode(p) if self.controls is not None else None
        if mode is not None:
            row.addWidget(mode, 0, Qt.AlignmentFlag.AlignTop)
        self.sanctum_button = self._sanctum_button()
        if self.sanctum_button is not None:
            row.addWidget(self.sanctum_button, 0, Qt.AlignmentFlag.AlignTop)
        self.info_edit = edit_button(
            "Edit",
            p,
            lambda: self.run(cf.character_info_form(self.saga, c)),
        )
        self.info_edit.setToolTip("Edit Character Info")
        row.addWidget(self.info_edit, 0, Qt.AlignmentFlag.AlignTop)
        return box

    def _sanctum_button(self) -> QPushButton | None:
        """A magus's Sanctum, one click from their sheet: New Sanctum while
        they have none."""
        c, open_sanctum = self.character, self.open_sanctum
        if c.type != "magus" or open_sanctum is None:
            return None
        lab = labs_sheet.sanctum(self.saga, c)
        button = edit_button(
            "Sanctum" if lab is not None else "New Sanctum",
            self.p,
            open_sanctum,
            "laboratory",
        )
        button.setToolTip(
            f"Open {lab.name}" if lab is not None else "Create their laboratory"
        )
        return button

    def _characteristics(self) -> QWidget:
        """The Characteristic cards, with their Edit button at the end of
        the strip."""
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        # An animal grog has Cunning, not Intelligence.
        captions = {"intelligence": "Cunning"} if self.character.animal else None
        row.addWidget(
            characteristic_cards(self.character.characteristics, self.p, captions), 1
        )
        self.characteristics_edit = edit_button(
            "Edit",
            self.p,
            lambda: self.run(cf.characteristics_form(self.saga, self.character)),
        )
        self.characteristics_edit.setToolTip("Edit Characteristics")
        row.addWidget(self.characteristics_edit, 0, Qt.AlignmentFlag.AlignVCenter)
        return box

    # Chapters

    def _statblock(self) -> QWidget:
        """A Line or Sketch character as the books print an NPC; each part
        is edited where it lives, in the header or its own chapter."""
        p = self.p
        parts: list[QWidget] = []
        for heading, words in cs.statblock(self.saga, self.character):
            parts += [_subheading(heading, p), TextBlock(words, p)]
        return scrolling_page(
            p,
            section(
                "Statblock",
                p,
                *parts,
                edits={
                    "Edit": lambda: self.run(
                        cf.character_info_form(self.saga, self.character)
                    )
                },
            ),
        )

    def _edit_buttons(
        self, forms: dict[str, Form], *names: str, label: str = "Edit"
    ) -> dict[str, Callable[[], None]]:
        """The Edit buttons for the forms `names`: one called `label`, or one
        per form named for it."""
        return {
            (label if len(names) == 1 else name): (
                lambda form=forms[name]: self.run(form)
            )
            for name in names
        }

    def _description(self) -> QWidget:
        """Who the character is, in the book's type: facts with small-caps
        labels, prose with a rubricated initial, and traits, wounds and
        Fatigue drawn rather than listed."""
        saga, c, p = self.saga, self.character, self.p
        forms = cf.description_edits(saga, c)
        parts: list[QWidget] = [
            section("At a Glance", p, fact_grid(cs.glance_facts(saga, c), p, 6))
        ]
        if c.type == "magus":
            parts += self._hermetic_sections(forms)
        # One above the other: side by side, with their buttons, they are
        # wider than the chapter beside the inspector.
        parts.append(
            trait_section(
                "Personality Traits",
                c.personality_traits,
                "section-personality-traits",
                p,
                self.run,
                self._placed("Personality Traits"),
            )
        )
        parts.append(
            trait_section(
                "Reputations",
                c.reputations,
                "section-reputations",
                p,
                self.run,
                self._placed("Reputations"),
            )
        )
        parts += self._biography_sections(forms)
        parts += self._health_sections(forms)
        parts.append(self._constant_effects())
        if cover_forms.shown(c):
            parts.append(self._covers())
        return scrolling_page(p, *parts)

    def _hermetic_sections(self, forms: dict[str, Form]) -> list[QWidget]:
        """A magus's Hermetic Background, and his familiar (or the card to
        bind one)."""
        saga, c, p = self.saga, self.character, self.p
        parts: list[QWidget] = []
        sigil = c.hermetic.wizards_sigil
        lineage: list[QWidget] = [fact_grid(cs.hermetic_facts(c), p)]
        if sigil:
            lineage.append(_sigil(sigil, p))
        voting = sigils.sigil_text(saga, c)
        if voting:
            lineage.append(TextBlock(escape(voting), p))
        lineage.append(TextBlock(lt.access_text(saga, c), p))
        parts.append(
            section(
                "Hermetic Background",
                p,
                *lineage,
                edits=self._edit_buttons(forms, "Hermetic Background"),
                buttons=self._texts_read(),
            )
        )
        familiar = saga.familiar_of(c.id)
        if familiar is not None:
            parts.append(
                section(
                    "Familiar",
                    p,
                    familiar_card(
                        fs.familiar_card(saga, familiar), p, self.open_familiar
                    ),
                )
            )
        elif self.placer is not None:
            bind = self.placer.new_card(
                "Familiar", hint="Bind one: the familiar is shown here."
            )
            if bind is not None:
                parts.append(section("Familiar", p, card_grid([bind], 2)))
        return parts

    def _biography_sections(self, forms: dict[str, Form]) -> list[QWidget]:
        """Biographical Detail, connections, lineage and marriages."""
        saga, c, p = self.saga, self.character, self.p
        parts: list[QWidget] = []
        parts.append(
            section(
                "Biographical Detail",
                p,
                fact_grid(cs.biographical_facts(saga, c), p, 4),
                _subheading("Appearance", p),
                prose(c.description.physical_description, p, initial=False),
                _subheading("Biography", p),
                prose(c.description.biography, p),
                edits=self._edit_buttons(forms, "Biographical Detail"),
            )
        )
        parts.append(connections_section(saga, c, p, self.run))
        if lineages.shown(saga, c):
            line = section("Lineage", p, TextBlock(lineages.text(saga, c), p))
            line.setObjectName(lineages.SECTION)
            parts.append(line)
        if marriages.of_character(saga, c):
            wed = section(
                "Marriages", p, TextBlock(marriages.character_text(saga, c), p)
            )
            wed.setObjectName(marriages.CHARACTER_SECTION)
            parts.append(wed)
        return parts

    def _health_sections(self, forms: dict[str, Form]) -> list[QWidget]:
        """Health (wounds and Fatigue) and Aging."""
        saga, c, p = self.saga, self.character, self.p
        parts: list[QWidget] = []
        health: list[QWidget] = [
            wound_track(cs.wound_track(c), p),
            _subheading("Fatigue", p),
            fatigue_ladder(cs.fatigue_track(c), p),
            fact_grid(cs.health_facts(c, saga), p, 4),
        ]
        parts.append(
            section(
                "Health",
                p,
                *health,
                edits=self._edit_buttons(forms, "Wounds", "Fatigue"),
                buttons=self._placed("Health"),
            )
        )
        aging = cs.aging_facts(c)
        effects = c.aging.effects
        if c.aging.twilight_scars.strip():
            effects = (effects + "\n\n" if effects else "") + (
                "Twilight Scars: " + "; ".join(c.aging.twilight_scars.splitlines())
            )
        parts.append(
            section(
                "Aging",
                p,
                *([fact_grid(aging, p, 4)] if aging else []),
                *([prose(effects, p, initial=False)] if effects or not aging else []),
                edits=self._edit_buttons(forms, "Aging"),
                buttons=self._placed("Aging"),
            )
        )
        return parts

    def _placed(self, section_name: str) -> list[QWidget]:
        """The More menu's buttons placed beside `section_name`."""
        return list(self.placer.buttons(section_name)) if self.placer else []

    def _covers(self) -> QWidget:
        """The character's deep covers and personae (HoH:S pp. 87-89)."""
        p, c = self.p, self.character
        chooser = Chooser()
        rows = cover_forms.table(c)
        chooser.listeners.append(
            lambda index: (
                self.inspect(
                    c.covers[index].name or "A cover",
                    c.covers[index].kind,
                    cover_forms.info(c, index),
                )
                if index is not None and index < len(c.covers)
                else None
            )
        )
        line = cover_forms.personae_line(c)
        widget = section(
            cover_forms.title(c),
            p,
            table_view(rows, p, chooser.choose)
            if rows.rows
            else TextBlock(cover_forms.EMPTY, p),
            *([TextBlock(line, p)] if line else []),
            buttons=[
                *verb_buttons(cover_forms.ops(c), chooser, self.run, p),
                *self._placed("Covers"),
            ],
        )
        widget.setObjectName(COVERS_SECTION)
        return widget

    def _constant_effects(self) -> QWidget:
        """The supernatural effects on the character all the time, and the
        Warping each gives a year (DE pp. 390-391)."""
        p, c = self.p, self.character
        chooser = Chooser()
        rows = constant_forms.table(c)
        chooser.listeners.append(
            lambda index: (
                self.inspect(
                    c.constant_effects[index].name or "A constant effect",
                    c.constant_effects[index].realm,
                    constant_forms.info(c, index),
                )
                if index is not None and index < len(c.constant_effects)
                else None
            )
        )
        total = constant_forms.total_line(c)
        return section(
            constant_forms.title(c),
            p,
            table_view(rows, p, chooser.choose)
            if rows.rows
            else TextBlock(constant_forms.EMPTY, p),
            *([TextBlock(total, p)] if total else []),
            buttons=verb_buttons(
                constant_forms.ops(self.saga, c), chooser, self.run, p
            ),
        )

    def _abilities(self) -> QWidget:
        p, c = self.p, self.character
        chooser = Chooser()
        ops = ability_forms.ability_ops(
            c.abilities,
            c.virtues_flaws,
            books=sourcebooks.saga_books(self.saga),
            note=lambda name: creation.worksheet_note(c, [name]),
        )

        def show(index: object) -> None:
            assert isinstance(index, int)
            chooser.choose(index)
            ability = c.abilities[index]
            specialty = f"  ·  {ability.specialty}" if ability.specialty else ""
            self.inspect(
                ability.name,
                f"{ability.category} Ability{specialty}",
                st.ability_info_text(c.abilities, index, c.virtues_flaws),
                ability_mark(ability.name, ability.category, p),
            )

        rows = cs.abilities_chapter_table(c)
        self.ability_table = ability_view(rows, p, show, memory=f"{c.id}:Abilities")
        return scrolling_page(
            p,
            section(
                f"Abilities ({len(rows)})",
                p,
                self.ability_table,
                buttons=[
                    *verb_buttons(ops, chooser, self.run, p),
                    *(self.placer.buttons("Abilities") if self.placer else []),
                ],
            ),
        )

    def _show_ability(self, chooser: Chooser, index: object) -> None:
        assert isinstance(index, int)
        p, c = self.p, self.character
        chooser.choose(index)
        ability = c.abilities[index]
        specialty = f"  ·  {ability.specialty}" if ability.specialty else ""
        self.inspect(
            ability.name,
            f"{ability.category} Ability{specialty}",
            st.ability_info_text(c.abilities, index, c.virtues_flaws),
            ability_mark(ability.name, ability.category, p),
        )

    def _tradition(self, tradition: TraditionDef) -> QWidget:
        """A tradition's chapter: what the tradition is, and the
        character's Arts and Abilities of it, grouped by the part they
        play, with Add limited to the tradition's own."""
        p, c = self.p, self.character
        chooser = Chooser()
        ops = ability_forms.ability_ops(
            c.abilities,
            c.virtues_flaws,
            books=sourcebooks.saga_books(self.saga),
            note=lambda name: creation.worksheet_note(c, [name]),
            only=tradition.abilities,
        )
        rows = cs.tradition_table(c, tradition)
        table = ability_view(
            rows,
            p,
            lambda index: self._show_ability(chooser, index),
            category=lambda row: c.abilities[row.index].category,
            memory=f"{c.id}:{tradition.id}",
        )
        effects = Chooser()
        effect_rows = tradition_text.effect_table(self.saga, c, tradition)
        bonds = Chooser()
        bond_rows = tradition_text.bond_table(c, tradition)
        casting: list[QWidget] = []
        for part in tradition_text.casting_parts(self.saga, c, tradition):
            casting.append(_subheading(part.title, p))
            if part.table:
                casting.append(TextBlock(part.table, p, mono=True))
            casting.append(TextBlock(part.notes, p))
        return scrolling_page(
            p,
            prose(tradition.description, p),
            section(
                f"Arts and Abilities ({len(rows)})",
                p,
                table,
                buttons=verb_buttons(ops, chooser, self.run, p),
            ),
            section(
                f"Effects and Items ({len(effect_rows.rows)})",
                p,
                table_view(effect_rows, p, effects.choose)
                if effect_rows.rows
                else TextBlock("[dim]None recorded.[/]", p),
                buttons=verb_buttons(
                    tradition_forms.effect_ops(c, tradition), effects, self.run, p
                ),
            ),
            section(
                f"Bound Beings ({len(bond_rows.rows)})",
                p,
                table_view(bond_rows, p, bonds.choose)
                if bond_rows.rows
                else TextBlock("[dim]None bound.[/]", p),
                TextBlock(tradition_text.bonds_text(tradition, c), p),
                buttons=verb_buttons(
                    tradition_forms.bond_ops(self.saga, c, tradition),
                    bonds,
                    self.run,
                    p,
                ),
            ),
            section(
                "Casting",
                p,
                *(
                    casting
                    or [
                        TextBlock(
                            tradition_text.casting_text(self.saga, c, tradition), p
                        )
                    ]
                ),
            ),
            section(
                "Magical Defenses",
                p,
                TextBlock(tradition_text.defenses_text(c, tradition), p),
            ),
            section(
                "Seasons",
                p,
                TextBlock(tradition_text.seasons_text(self.saga, c, tradition), p),
            ),
            section(
                "Warping",
                p,
                TextBlock(tradition_text.warping_text(self.saga, c, tradition), p),
            ),
            *(
                [
                    section(
                        "Pools",
                        p,
                        TextBlock(tradition_text.pools_text(c, tradition), p),
                        buttons=verb_buttons(
                            tradition_forms.pool_ops(c, tradition),
                            Chooser(),
                            self.run,
                            p,
                        ),
                    )
                ]
                if tradition.pools
                else []
            ),
        )

    def _virtues_flaws(self) -> QWidget:
        """The Virtues beside the Flaws, as cards, each side with its Add,
        Edit and Delete (Edit changes only what it names: its Ability, Art or
        Characteristic); under both, the page's own buttons (Gain or Lose in
        Play) on a strip across the page, then the powers."""
        p, c = self.p, self.character
        placed = self.placer.buttons("Virtues & Flaws") if self.placer else []
        strip = [section("During the Saga", p, buttons=placed)] if placed else []
        columns = []
        for side, tone in (("Virtue", "text-success"), ("Flaw", "text-error")):
            chooser = Chooser()
            ops = virtue_forms.virtue_flaw_ops(self.saga, c, side)
            points = cs.virtue_flaw_points(c, side)
            cards = [
                self._vf_card(card, p[tone]) for card in cs.virtue_flaw_cards(c, side)
            ]
            choose_cards(cards, chooser)
            column = QWidget()
            stack = QVBoxLayout(column)
            stack.setContentsMargins(0, 0, 0, 0)
            stack.setSpacing(10)
            stack.addWidget(
                section(
                    f"{side}s  ·  {points:g} points",
                    p,
                    *cards,
                    buttons=verb_buttons(ops, chooser, self.run, p),
                )
            )
            stack.addStretch(1)
            columns.append(column)
        return scrolling_page(
            p, side_by_side(*columns, spacing=18), *strip, self._powers()
        )

    def _powers(self) -> QWidget:
        """The powers the character's Virtues grant, with their Initiative,
        Fatigue and Penetration, and what each Virtue has left."""
        p, c = self.p, self.character
        chooser = Chooser()
        rows = power_forms.table(c)
        chooser.listeners.append(
            lambda index: (
                self.inspect(
                    c.powers[index].name or "A power",
                    c.powers[index].virtue,
                    power_forms.info(c, index, self.saga),
                )
                if index is not None and index < len(c.powers)
                else None
            )
        )
        return section(
            power_forms.title(c),
            p,
            table_view(rows, p, chooser.choose)
            if rows.rows
            else TextBlock(
                "[dim]No powers: a Greater, Lesser, Personal, Ritual or Focus Power "
                "Virtue grants them.[/]",
                p,
            ),
            TextBlock("\n".join(power_forms.budget_lines(c, self.saga)), p),
            buttons=verb_buttons(power_forms.ops(c), chooser, self.run, p),
        )

    def _vf_card(self, card: cs.VirtueFlawCard, colour: str) -> ClickableCard:
        c = self.character
        return vf_card(
            card,
            colour,
            self.p,
            lambda: self.inspect(
                card.name,
                f"{card.tier}  ·  {card.category}",
                st.vf_info_text(c.virtues_flaws, card.index),
            ),
        )

    def _texts_read(self) -> list[QPushButton]:
        """Whose Lab Texts they read, beside the lines that say so."""
        if not menu_forms.lives_at(
            "lab_text_access", NodeKind.CHARACTER, "Hermetic Background"
        ):
            return []
        return [
            edit_button(
                "Texts Read",
                self.p,
                lambda: self.run(menu_forms.lab_text_access(self.saga, self.character)),
                "lab_text",
            )
        ]

    def _hermetic(self) -> QWidget:
        p, saga, c = self.p, self.saga, self.character
        spells = Chooser()
        moving = self.placer.buttons("Current Location") if self.placer else []
        others = self.placer.buttons("Magic Outside the Lab") if self.placer else []
        parts: list[QWidget] = [
            *(
                [
                    section(
                        "Current Location",
                        p,
                        TextBlock(whereabouts_forms.where_line(saga, c), p),
                        buttons=moving,
                    )
                ]
                if moving
                else []
            ),
            section(
                "Magical Arts",
                p,
                self._arts(),
                edits={"Edit": lambda: self.run(cf.arts_form(c))},
            ),
            chapter_title("Casting Scores", p),
            self._casting_grid(),
            *(
                [TextBlock("\n".join(virtues), p)]
                if (virtues := casting_text.casting_virtue_lines(c))
                else []
            ),
            *(
                [TextBlock(escape("\n".join(hybrid)), p)]
                if (hybrid := hybrid_magic.summary(c))
                else []
            ),
            *(
                [TextBlock("\n".join(casting_text.certamen_lines(c)), p)]
                if c.type == "magus"
                else []
            ),
            section(
                f"Known Spells ({len(c.spells_known)})",
                p,
                self._spells(spells),
                buttons=[
                    *verb_buttons(
                        spell_forms.known_spell_ops(saga, c),
                        spells,
                        self.run,
                        p,
                    ),
                    *(self.placer.buttons("Known Spells") if self.placer else []),
                ],
            ),
            self._raw_vis(),
            *([section("Magic Outside the Lab", p, buttons=others)] if others else []),
        ]
        return scrolling_page(p, *parts)

    def _research(self) -> QWidget:
        return research_chapter(
            self.saga,
            self.character,
            self.p,
            self.run,
            lambda title, subtitle, markup: self.inspect(title, subtitle, markup),
        )

    def _show_art(self, art: object) -> None:
        assert isinstance(art, str)
        kind = "Technique" if art in TECHNIQUES else "Form"
        self.inspect(
            art,
            f"{kind}  ·  {ART_ABBREVIATIONS[art]}",
            cs.art_info_text(self.character, art),
            artwork.art_symbol(art),
        )

    def _arts(self) -> QWidget:
        """The Arts as tables like the Abilities, the Techniques beside the
        Forms: each Art with its symbol, score and experience."""
        p, c = self.p, self.character
        views = []
        for title, arts in (("Technique", TECHNIQUES), ("Form", FORMS)):
            table = XpTable(
                [title, "Score", "Experience"],
                p,
                self._show_art,
                memory=f"{c.id}:{title}",
            )
            for row in cs.art_rows(c, arts):
                name = _item(row.art, font=serif(12.5, italic=True))
                symbol = artwork.art_symbol(row.art)
                name.setIcon(
                    QIcon(pictures.pixmap(symbol, p["foreground"], ART_SYMBOL, 2.0))
                )
                name.setToolTip(f"{row.art} ({row.abbreviation})")
                table.add(
                    None,
                    row.art,
                    [name, _score_item(row.score)],
                    row.fraction,
                    _xp_words(row.xp, row.next_xp),
                )
            table.finish()
            views.append(table)
        self.technique_view, self.form_view = views
        return side_by_side(*views, spacing=14)

    def _casting_grid(self) -> QWidget:
        """Every Casting Score as a heat map, Forms across and Techniques
        down; choosing a cell shows its terms."""
        scores = cs.casting_grid(self.saga, self.character)

        def show(technique: str, form: str) -> None:
            self.inspect(
                f"{technique} {form}",
                f"{ART_ABBREVIATIONS[technique]}{ART_ABBREVIATIONS[form]}"
                " Casting Score",
                cs.casting_cell_text(
                    scores[technique, form],
                    cs.spontaneous_score(self.saga, self.character, technique, form),
                    self.character,
                ),
                artwork.art_symbol(form),
            )

        self.casting_view = arts_heat_grid(
            {pair: int(score.total) for pair, score in scores.items()}, self.p, show
        )
        return self.casting_view

    def _spells(self, chooser: Chooser | None = None) -> QWidget:
        """Known Spells as a table that sorts by any column and filters by
        name; choosing a row chooses it for `chooser`."""
        p, saga, c = self.p, self.saga, self.character
        rows = cs.spell_table(saga, c)
        model = _spell_model(rows, p)
        proxy = QSortFilterProxyModel()
        proxy.setSourceModel(model)
        proxy.setFilterKeyColumn(0)
        proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        view = QTableView()
        view.setModel(proxy)
        view.setSortingEnabled(True)
        view.sortByColumn(2, Qt.SortOrder.DescendingOrder)
        view.setIconSize(QSize(18, 18))
        view.verticalHeader().hide()
        view.verticalHeader().setDefaultSectionSize(ROW)
        view.setShowGrid(False)
        view.setAlternatingRowColors(True)
        view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header = view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        _table_style(view, p)
        _fit_height(view, max(len(rows), 1))

        def show(current: QModelIndex, _previous: QModelIndex) -> None:
            index = current.siblingAtColumn(0).data(Qt.ItemDataRole.UserRole)
            if index is None:
                return
            known = c.spells_known[index]
            spell = catalog.find_spell(saga, known.spell_id)
            subtitle = (
                f"{spl.shorthand(spell)}  ·  {spell.range}/{spell.duration}/{spell.target}"
                if spell
                else ""
            )
            symbol = artwork.art_symbol(spell.form) if spell else None
            self.inspect(
                spell.name if spell else known.spell_id,
                subtitle,
                cs.known_spell_info_text(saga, c, index),
                symbol,
            )

        view.selectionModel().currentRowChanged.connect(show)
        if chooser is not None:
            choose_rows(view, chooser, lambda row: rows[row].index)

        search = QLineEdit()
        search.setPlaceholderText("Filter spells…")
        search.addAction(
            pictures.icon("search", p["label"], 16),
            QLineEdit.ActionPosition.LeadingPosition,
        )
        search.setStyleSheet(
            f"background:{p['surface']}; border:1px solid {p['rule']};"
            " border-radius:4px; padding:4px;"
        )
        search.textChanged.connect(proxy.setFilterFixedString)
        self.spell_view, self.spell_filter = view, search
        box = QWidget()
        column = QVBoxLayout(box)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(search)
        column.addWidget(view)
        return box

    def _inventory(self) -> QWidget:
        p, saga, c = self.p, self.saga, self.character
        parts: list[QWidget] = []
        if c.type == "magus":
            parts.append(self._raw_vis())
        gear = Chooser()

        def show_item(index: int) -> None:
            gear.choose(index)
            self.inspect(c.inventory[index].name, "", cs.inventory_item_text(c, index))

        tables: list[QWidget] = []
        for title, table in cs.inventory_tables(c):
            tables.append(text(title, p["label"], serif(12.5, italic=True)))
            tables.append(table_view(table, p, show_item))
        parts.append(
            section(
                cs.gear_title(c),
                p,
                *(tables or [TextBlock("[dim]None recorded.[/]", p)]),
                buttons=[
                    *verb_buttons(
                        cf.inventory_ops(c, sourcebooks.saga_books(saga)),
                        gear,
                        self.run,
                        p,
                        more=[give_verb(saga, giving.GEAR, c, lambda: c.inventory)],
                    ),
                    *(self.placer.buttons("Personal Gear") if self.placer else []),
                ],
            )
        )
        parts.append(device_section(saga, "character", c.id, p, self.run, self.inspect))
        books = library.books_owned_by(saga, "character", c.id)
        chosen_book = Chooser()

        def show_book(index: int) -> None:
            chosen_book.choose(index)
            self.inspect(books[index].name, "", bk.detail_text(saga, books[index]))

        parts.append(
            section(
                f"Books ({len(books)})",
                p,
                table_view(bk.book_table(saga, books), p, show_book)
                if books
                else TextBlock("[dim]None recorded.[/]", p),
                buttons=verb_buttons(
                    SectionOps(rows=lambda: [b.name for b in books]),
                    chosen_book,
                    self.run,
                    p,
                    more=[give_verb(saga, giving.BOOK, c, lambda: books)],
                ),
            )
        )
        return scrolling_page(p, *parts)

    def _agents(self) -> QWidget:
        """The people he controls through personal bonds: the limit and
        the Agency experience, the ledger, Add, Edit and Delete, and
        Impress, Spend Agency Experience, Set a Task and Resolve the Task
        on the chosen agent, who shows in full in the inspector."""
        saga, p, c = self.saga, self.p, self.character
        chooser = Chooser()

        def show(index: int) -> None:
            chooser.choose(index)
            name, subtitle = agent_forms.inspector_title(c, index)
            self.inspect(name, subtitle, agent_forms.info(c, index, wide=False))

        def offered(test: Callable[[Agent], bool]) -> Callable[[int], bool]:
            return lambda row: row < len(c.agents) and test(c.agents[row])

        more: list[RowVerb] = [
            (
                "Impress",
                "character",
                lambda row: agent_forms.impress(saga, c, row),
                offered(agent_rules.can_impress),
            ),
            (
                "Spend Agency Experience",
                "season",
                lambda row: agent_forms.spend(c, row),
                offered(lambda found: agent_rules.can_spend(c, found)),
            ),
            (
                "Set a Task",
                "faction",
                lambda row: agent_forms.set_task(saga, c, row),
                offered(agent_rules.may_be_asked),
            ),
            (
                "Resolve the Task",
                "in_play",
                lambda row: agent_forms.resolve(saga, c, row),
                offered(agent_rules.recruited),
            ),
        ]
        return scrolling_page(
            p,
            section(
                agent_forms.title(c),
                p,
                TextBlock(agent_forms.header(c), p),
                table_view(agent_forms.table(c), p, show)
                if c.agents
                else TextBlock(
                    "[dim]None yet: people won over through a personal bond "
                    "(LoM p. 22).[/]",
                    p,
                ),
                TextBlock(f"[dim]{escape(agent_forms.NOT_AGENTS)}[/]", p),
                buttons=verb_buttons(
                    agent_forms.ops(c), chooser, self.run, p, more=more
                ),
            ),
        )

    def _raw_vis(self) -> QWidget:
        """The magus's raw vis, by Art, with Add, Edit and Delete, and Give
        while there is someone to give it to."""
        c, p = self.character, self.p
        chooser = Chooser()
        ops = vis_forms.raw_vis_ops(c.raw_vis)
        return section(
            "Raw Vis",
            p,
            table_view(cs.raw_vis_table(c.raw_vis), p, chooser.choose)
            if c.raw_vis
            else TextBlock("[dim]None recorded.[/]", p),
            buttons=verb_buttons(
                ops,
                chooser,
                self.run,
                p,
                more=[give_verb(self.saga, giving.VIS, c, lambda: vis.held(c))],
            ),
        )

    def _planning(self) -> QWidget:
        """This Season: the plan and what it will give, with Plan, Edit
        and Clear (a grog's Yearly Update instead), then A Season's Work
        and the Seasons Ahead."""
        saga, p, c = self.saga, self.p, self.character
        buttons = verb_buttons(
            season_forms.character_season_ops(saga, c),
            Chooser(),
            self.run,
            p,
            nouns=season_forms.season_nouns(c),
        )
        # Plan Copying and Clear Copying.
        buttons += self.placer.buttons("This Season") if self.placer else []
        this_season = section(
            f"This Season ({saga.current_season} {saga.current_year})",
            p,
            TextBlock(seasons.plan_text(saga, c, "Click Plan to plan the season."), p),
            buttons=buttons,
            emblem=Medallion(
                saga, saga.current_season, saga.current_year, p, radius=20, now=True
            ),
        )
        work = self._season_work()
        if not season_rules.is_planned(c):
            return scrolling_page(p, this_season, *work)
        chooser = Chooser()
        info = TextBlock(seasons.ahead_info(saga, c, None, "Click Edit"), p)

        def show(index: int) -> None:
            chooser.choose(index)
            info.setText(to_html(seasons.ahead_info(saga, c, index, "Click Edit"), p))

        ahead = section(
            seasons.ahead_title(saga),
            p,
            table_view(seasons.ahead_table(saga, c), p, show),
            info,
            buttons=verb_buttons(
                season_forms.ahead_season_ops(saga, c),
                chooser,
                self.run,
                p,
                nouns=season_forms.PLAN_NOUNS,
            ),
        )
        return scrolling_page(p, this_season, *work, ahead)

    def _season_work(self) -> list[QWidget]:
        """A Season's Work: the supplements' season-long actions, each
        button beside a line on what it does (none: no section)."""
        placed = self.placer.placed_buttons(deeds.SEASON_WORK) if self.placer else []
        rows = [(button, deeds.SEASON_NOTES[item.action]) for item, button in placed]
        return (
            [section(deeds.SEASON_WORK, self.p, action_rows(rows, self.p))]
            if rows
            else []
        )

    def _deeds(self) -> QWidget:
        """The actions the supplements bring for play, a section for each
        interest (deeds.INTERESTS), each button beside a line on what it
        does; while he is In Creation, only a line saying they wait."""
        p, c = self.p, self.character
        if c.in_creation:
            return scrolling_page(
                p,
                TextBlock(
                    f"[dim]{c.name}'s deeds open once the character is In Play.[/]",
                    p,
                ),
            )
        sections = []
        for interest in deeds.INTERESTS:
            placed = self.placer.placed_buttons(interest) if self.placer else []
            rows = [(button, deeds.NOTES[item.action]) for item, button in placed]
            if rows:
                sections.append(section(interest, p, action_rows(rows, p)))
        if not sections:
            return scrolling_page(
                p,
                TextBlock(
                    "[dim]Nothing here yet: the deeds the saga's books bring "
                    "show here when they fit him.[/]",
                    p,
                ),
            )
        return scrolling_page(p, *sections)

    def _diary(self) -> QWidget:
        """The character's seasons as a calendar, a row per year, over the
        Diary's entries."""
        saga, c, p, diary = self.saga, self.character, self.p, self.character.diary
        self.calendar = Calendar(
            ov.calendar(saga, c),
            p,
            lambda who, when, season: self.inspect(who, when, season_text(season)),
            who=c.name,
            saga=saga,
        )
        entries = Chooser()

        def show_entry(index: int) -> None:
            entries.choose(index)
            self.inspect("Diary", "", labs.diary_info_text(diary, index))

        return scrolling_page(
            p,
            section("Seasons", p, legend(p), self.calendar),
            section(
                f"Diary ({len(diary)})",
                p,
                table_view(labs.diary_table(diary), p, show_entry)
                if diary
                else TextBlock("[dim]None recorded.[/]", p),
                buttons=verb_buttons(
                    diary_forms.entry_ops(
                        saga, diary, diary_forms.character_activities()
                    ),
                    entries,
                    self.run,
                    p,
                ),
            ),
        )

    def _criamon(self) -> QWidget:
        return _criamon_chapter(
            self.saga, self.character, self.p, self.run, self.inspect
        )

    def _religion(self) -> QWidget:
        """His Faith (Edit Religion, and the actions his faith offers him),
        then, for a Christian with The Church in play, the Church's
        sections: Holy Orders (Edit Holy Orders, Perform an Exorcism) and
        the Ordinations for one who may hold orders, the Petitions and the
        Canon Court for all, as ledger entries, each with Add, Edit and
        Delete; the chosen one shows in the inspector."""
        saga, p, c = self.saga, self.p, self.character
        faith = section(
            "Faith",
            p,
            fact_grid(
                [Fact(k, plain(v)) for k, v in religion_forms.faith_facts(c)], p, 3
            ),
            prose(religion_forms.faith_note(c), p, initial=False),
            edits={
                "Edit Religion": lambda: self.run(religion_forms.religion_form(saga, c))
            },
            buttons=self._placed("Faith"),
        )
        parts: list[QWidget] = [faith]
        if not religion_forms.church_shown(saga, c):
            return scrolling_page(p, *parts)
        ops = church_forms.ops(saga, c)
        career = c.church
        lists = [
            (
                church_forms.petitions_title(career),
                PETITIONS_SECTION,
                church_forms.petition_entries(c),
                "[dim]None yet: Add petitions the Church.[/]",
            ),
            (
                church_forms.canon_title(career),
                CANON_SECTION,
                church_forms.case_entries(c),
                "[dim]None yet: Add records a case.[/]",
            ),
        ]
        if religion_forms.orders_shown(saga, c):
            words = TextBlock(church_forms.orders_desk_text(saga, c), p)
            words.setFont(serif(12.5))
            parts.append(
                section(
                    "Holy Orders",
                    p,
                    fact_grid(
                        [Fact(k, plain(v)) for k, v in church_forms.orders_facts(c)],
                        p,
                        3,
                    ),
                    *([prose(career.notes.strip(), p)] if career.notes.strip() else []),
                    words,
                    edits={
                        "Edit Holy Orders": lambda: self.run(
                            church_forms.holy_orders_form(saga, c)
                        ),
                        # Any clergyman's, not a layman's or a monk's.
                        **(
                            {
                                "Perform an Exorcism": lambda: self.run(
                                    church_forms.exorcism_form(saga, c)
                                )
                            }
                            if faiths.may_exorcise(c)
                            else {}
                        ),
                    },
                )
            )
            lists.insert(
                0,
                (
                    church_forms.ordinations_title(career),
                    ORDINATIONS_SECTION,
                    church_forms.ordination_entries(c),
                    church_forms.ordination_rows(c)[0][1],
                ),
            )
        for title, section_id, entries, empty in lists:
            chooser = Chooser()
            parts.append(
                section(
                    title,
                    p,
                    church_ledger(entries, p, chooser, self.inspect, empty),
                    buttons=verb_buttons(ops[section_id], chooser, self.run, p),
                )
            )
        return scrolling_page(p, *parts)


def _criamon_chapter(
    saga: Saga,
    c: Character,
    p: Palette,
    run: Callable[[Command], None],
    inspect: Callable[[str, str, str], None],
) -> QWidget:
    """The path (Change Path, Follow an Avenue), its five stations as
    ledger entries, and the stigmata with Add, Edit and Delete; the
    chosen one shows in the inspector."""
    ops = criamon_forms.ops(saga, c)
    words = TextBlock(criamon_forms.path_desk_text(saga, c), p)
    words.setFont(serif(12.5))
    notes = c.enigma.notes.strip()
    path = section(
        criamon_forms.path_title(c),
        p,
        fact_grid(
            [Fact(k, plain(v)) for k, v in criamon_forms.path_facts(saga, c)], p, 3
        ),
        *([prose(notes, p)] if notes else []),
        words,
        edits={
            "Change Path": lambda: run(criamon_forms.path_form(saga, c)),
            "Follow an Avenue": lambda: run(criamon_forms.avenue_form(saga, c)),
        },
    )
    stations = section(
        criamon_forms.stations_title(c),
        p,
        church_ledger(
            criamon_forms.station_entries(c),
            p,
            Chooser(),
            inspect,
            criamon_forms.stations_empty(c),
        ),
    )
    chooser = Chooser()
    stigmata = section(
        criamon_forms.stigmata_title(c),
        p,
        church_ledger(
            criamon_forms.stigma_entries(c),
            p,
            chooser,
            inspect,
            criamon_forms.STIGMATA_EMPTY,
        ),
        buttons=verb_buttons(ops[STIGMATA_SECTION], chooser, run, p),
    )
    return scrolling_page(p, path, stations, stigmata)


def _left_out(saga: Saga, character: Character) -> set[str]:
    """The chapters the character's sheet doesn't have: Hermetic Magic but
    for a magus, the Statblock but for a Line or Sketch character, and
    what only play needs (Inventory, Agents, Deeds, Planning, Research) for those. A Line character
    has no scores either."""
    left = set()
    if character.type != "magus":
        left |= {"Hermetic Magic", "Research"}
    if cs.has_statblock(character):
        left |= {"Inventory", "Agents", "Deeds", "Planning", "Research"}
    else:
        left.add("Statblock")
    if character.detail == LINE:
        left |= {"Abilities", "Virtues & Flaws", "Hermetic Magic", "Research"}
    if cs.has_statblock(character) or not religion_forms.shows(saga, character):
        left.add("Religion")
    if cs.has_statblock(character) or not criamon_rules.has_enigma_tab(character):
        left.add("The Enigma")
    return left | deeds.chapters_off(character)


def characteristic_cards(
    ch: Characteristics, p: Palette, captions: dict[str, str] | None = None
) -> QWidget:
    """The eight Characteristics as a row of cards, each coloured by its
    sign; `captions` renames some (a creature's Cunning)."""
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(8)
    for name in (
        "intelligence",
        "perception",
        "strength",
        "stamina",
        "presence",
        "communication",
        "dexterity",
        "quickness",
    ):
        value = getattr(ch, name)
        colour = (
            p["text-success"]
            if value > 0
            else p["text-error"]
            if value < 0
            else p["dim"]
        )
        card = Card(p, pad=6)
        card.setFixedHeight(64)
        card.column.setSpacing(0)
        number = text(f"{value:+d}" if value else "0", colour, serif(20, bold=True))
        number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        words = (captions or {}).get(name, name.title())
        caption = text(words, p["label"], serif(10.5, caps=True))
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.column.addWidget(number)
        card.column.addWidget(caption)
        row.addWidget(card, 1)
    return box


def ability_view(
    rows: Sequence[cs.AbilityRow],
    p: Palette,
    show: Callable[[object], None],
    *,
    category: Callable[[cs.AbilityRow], str] | None = None,
    memory: str = "",
) -> XpTable:
    """Abilities as a table grouped by category, each with its mark,
    specialty, score and experience; choosing one calls `show` with its
    index. `category` gives the Ability category a row's mark falls back
    to, when rows are grouped under other headings (a tradition's Arts)."""
    table = XpTable(
        ["Ability", "Specialty", "Score", "Experience"],
        p,
        show,
        row=ABILITY_ROW,
        icon=ABILITY_MARK,
        memory=memory,
    )
    groups: dict[str, QStandardItem] = {}
    for row in rows:
        if row.category not in groups:
            groups[row.category] = table.group(row.category)
        specialty = _item(row.specialty, font=serif(11.5, italic=True))
        specialty.setForeground(QBrush(QColor(p["label"])))
        name = _item(row.name)
        kind = category(row) if category is not None else row.category
        name.setIcon(ability_icon(row.name, kind, p))
        table.add(
            groups[row.category],
            row.index,
            [name, specialty, _score_item(row.score)],
            row.fraction,
            _xp_words(row.xp, row.next_xp),
        )
    table.finish()
    return table


class Portrait(QWidget):
    """The character's portrait in a gilt frame beside their name: the
    House symbol (or a figure, for one with no House) while they have
    none. Clicking it chooses one."""

    WIDTH, HEIGHT = 64, 80

    def __init__(
        self,
        saga: Saga,
        character: Character,
        p: Palette,
        run: Callable[[Command], None],
    ) -> None:
        super().__init__()
        self.p = p
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked = lambda: run(portraits.portrait(saga, character))
        found = portraits.path(character)
        self.picture = QPixmap(str(found)) if found is not None else QPixmap()
        symbol = artwork.person_symbol(character) or artwork.icon("character")
        self.symbol = pictures.pixmap(symbol, p["heading"], HOUSE_SYMBOL - 12, 2.0)
        self.setToolTip(
            "Change the portrait" if not self.picture.isNull() else "Choose a portrait"
        )

    def has_picture(self) -> bool:
        return not self.picture.isNull()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.clicked()
        super().mousePressEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        outer = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        inner = outer.adjusted(4, 4, -4, -4)
        painter.setPen(QPen(QColor(self.p["accent"]), 2))
        painter.setBrush(QColor(self.p["panel"]))
        painter.drawRoundedRect(outer, 4, 4)
        if self.has_picture():
            # Fill the frame, cropping what overhangs it.
            picture = self.picture
            scale = max(
                inner.width() / picture.width(), inner.height() / picture.height()
            )
            w, h = inner.width() / scale, inner.height() / scale
            source = QRectF((picture.width() - w) / 2, (picture.height() - h) / 2, w, h)
            painter.drawPixmap(inner, picture, source)
        else:
            size = self.symbol.deviceIndependentSize()
            painter.drawPixmap(
                QRectF(
                    inner.center().x() - size.width() / 2,
                    inner.center().y() - size.height() / 2,
                    size.width(),
                    size.height(),
                ).toRect(),
                self.symbol,
            )
        painter.setPen(QPen(QColor(self.p["heading"]), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(inner)
        painter.end()


def ability_icon(name: str, category: str, p: Palette) -> QIcon:
    """An Ability's mark as its row shows it, untinted when chosen."""
    mark = marks.pixmap(name, category, p["foreground"], ABILITY_MARK)
    icon = QIcon(mark)
    icon.addPixmap(mark, QIcon.Mode.Selected)
    return icon


def ability_mark(name: str, category: str, p: Palette) -> QPixmap:
    """An Ability's mark as the panel beside the chapter shows it."""
    return marks.pixmap(name, category, p["heading"], ABILITY_MARK_LARGE)


def vf_card(
    card: cs.VirtueFlawCard, colour: str, p: Palette, on_click: Callable[[], None]
) -> ClickableCard:
    """A Virtue or Flaw as a card edged in `colour`: its name, tier, summary
    and category."""
    frame = ClickableCard(p, edge=colour, pad=10)
    top = QHBoxLayout()
    top.addWidget(text(card.name, p["foreground"], serif(13.5, bold=True)))
    top.addStretch(1)
    top.addWidget(badge(card.tier, p["dim"] if card.tier == "Free" else colour, p))
    frame.column.addLayout(top)
    if card.summary:
        frame.column.addWidget(text(card.summary, p["label"], wrap=True))
    frame.column.addWidget(text(card.category, p["dim"], serif(10, caps=True)))
    frame.clicked = on_click
    return frame


def _subheading(words: str, p: Palette) -> QLabel:
    label = text(words, p["heading"], serif(12, italic=True))
    label.setContentsMargins(0, 6, 0, 0)
    return label


def _sigil(sigil: str, p: Palette) -> QWidget:
    """The Wizard's Sigil, set apart as a quotation."""
    label = text(
        f"Wizard's Sigil: \u201c{sigil}\u201d",
        p["foreground"],
        serif(13, italic=True),
        wrap=True,
    )
    label.setStyleSheet(
        f"color:{p['foreground']}; background:transparent;"
        f" border-left:3px solid {p['accent']}; padding-left:10px"
    )
    return label


def _spell_model(rows: Sequence[cs.SpellRow], p: Palette) -> QStandardItemModel:
    """The known spells as a model a table view shows, one row each."""
    columns = [
        "Spell",
        "Arts",
        "Level",
        "Range",
        "Duration",
        "Target",
        "Mastery",
        "Shared",
    ]
    model = QStandardItemModel(0, len(columns))
    model.setHorizontalHeaderLabels(columns)
    for row in rows:
        name = _item(row.name, font=serif(12))
        name.setData(row.index, Qt.ItemDataRole.UserRole)
        if row.form:
            name.setIcon(
                QIcon(
                    pictures.pixmap(
                        artwork.art_symbol(row.form), p["foreground"], 18, 2.0
                    )
                )
            )
        level = _item()
        level.setData(
            row.level if row.level is not None else -1, Qt.ItemDataRole.DisplayRole
        )
        if row.level is None:
            level.setText("Gen")
        mastery = _item("★" * row.mastery if row.mastery else "")
        mastery.setForeground(QBrush(QColor(p["accent"])))
        mastery.setToolTip(f"Mastery {row.mastery}")
        duration = row.duration + (", Ritual" if row.ritual else "")
        # A spell they invented: a mark once the saga has it.
        shared = _item(
            {"Shared": "✓", "Own": "Not yet"}.get(row.invented, ""),
        )
        if row.invented == "Shared":
            shared.setForeground(QBrush(QColor(p["accent"])))
            shared.setToolTip("Invented and shared with the saga")
        elif row.invented == "Own":
            shared.setForeground(QBrush(QColor(p["dim"])))
            shared.setToolTip("Invented; Edit it to share it with the saga")
        model.appendRow(
            [
                name,
                _item(row.arts),
                level,
                _item(row.range),
                _item(duration),
                _item(row.target),
                mastery,
                shared,
            ]
        )
    return model
