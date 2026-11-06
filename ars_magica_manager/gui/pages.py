"""The pages at the top, in the Codex's style: the shelf of sagas and a
saga's covenants, and the cards and headings the pages below them share
(the covenant's is covenant.py), such as a familiar's card.

Each is cards and headings over the core's figures (saga_overview);
choosing a card calls back to the window, which opens the next page.
"""

from __future__ import annotations

import html
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, TypedDict, Unpack

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import (
    artwork,
    battles,
    conflicts,
    creatures,
    fights,
    neighbour_filter,
    neighbours,
    open_stories,
    sieges,
    story_chapters,
    troupe,
    world,
)
from .. import saga_overview as ov
from ..commands import Command
from ..forms import diary as diary_forms
from ..forms import menu as menu_forms
from ..models import Character, Creature, Neighbour, Saga, Tribunal
from ..references import Fact, Ref
from ..sections import CONFLICT_BATTLES_SECTION, FIGHTS_SECTION, SIEGES_SECTION
from ..sheets import character as cs
from ..sheets import creature as crs
from ..sheets import familiar as fs
from ..sheets import region as region_sheet
from ..sheets import saga_content as scs
from ..sheets import tribunal as tribunal_sheet
from . import pictures
from .atlas import AtlasChapter
from .figures import fact_grid
from .menus import Placer
from .saga_settings import SettingsChapter
from .style.ornaments import FleuronButton, ShortRule
from .themes import Palette
from .widgets import (
    CARDS_ACROSS,
    Card,
    ClickableCard,
    Codex,
    card_grid,
    chapter_title,
    chip_row,
    display_name,
    edit_button,
    filter_choice,
    scrolling_page,
    serif,
    text,
)

Open = Callable[[str], None]


def _ignore(_id: str) -> None:
    """The opener a page uses when its window gave none."""


class SagaHooks(TypedDict, total=False):
    """What the window gives a saga page to open the things its cards name,
    run a command and place the More menu's buttons; any left out does
    nothing."""

    open_content: Callable[[], None]
    open_seasons: Callable[[], None]
    placer: Placer | None
    open_character: Open
    open_laboratory: Open
    open_tribunal: Open
    open_neighbour: Open
    open_creature: Open
    open_familiar: Open
    run: Callable[[Command], None]
    #: Runs a command and calls back with what it ended with, instead of
    #: drawing the page again (the Atlas keeps its place on the map).
    run_ended: Callable[[Command, Callable[[object], None]], None]
    open_fight: Open
    open_siege: Open


def divider(words: str, p: Palette) -> QWidget:
    """A quiet break inside a chapter's cards: a gilt rule with a few
    words in italics under it."""
    box = QWidget()
    column = QVBoxLayout(box)
    column.setContentsMargins(0, 4, 0, 0)
    column.setSpacing(0)
    column.addWidget(ShortRule(p))
    label = text(words, p["label"], serif(12, italic=True))
    label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    column.addWidget(label)
    return box


def page_header(
    title: str,
    subtitle: str,
    p: Palette,
    concept: str | None = None,
    emblem: QWidget | None = None,
) -> QWidget:
    """A page's title: an icon (or `emblem` in its place), the name with a
    rubricated initial and the line under it, as the Character sheet
    opens."""
    box = QWidget()
    row = QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(14)
    if emblem is not None:
        row.addWidget(emblem, 0, Qt.AlignmentFlag.AlignTop)
    elif concept is not None:
        symbol = QLabel()
        symbol.setPixmap(pictures.pixmap(artwork.icon(concept), p["heading"], 48, 2.0))
        row.addWidget(symbol, 0, Qt.AlignmentFlag.AlignTop)
    names = QVBoxLayout()
    names.setSpacing(0)
    names.addWidget(display_name(title, p))
    if subtitle:
        names.addWidget(text(subtitle, p["label"], serif(12.5, italic=True)))
    row.addLayout(names)
    row.addStretch(1)
    return box


def card_title(
    card: Card, title: str, subtitle: str, p: Palette, symbol: QLabel | None
) -> None:
    top = QHBoxLayout()
    top.setSpacing(10)
    if symbol is not None:
        top.addWidget(symbol, 0, Qt.AlignmentFlag.AlignTop)
    names = QVBoxLayout()
    names.setSpacing(0)
    names.addWidget(text(title, p["foreground"], serif(16, bold=True), wrap=True))
    if subtitle:
        names.addWidget(text(subtitle, p["label"], serif(11.5, italic=True), wrap=True))
    top.addLayout(names, 1)
    card.column.addLayout(top)


def symbol_label(path: Path, p: Palette, size: int = 36) -> QLabel:
    label = QLabel()
    label.setPixmap(pictures.pixmap(path, p["heading"], size, 2.0))
    return label


def familiar_card(
    figures: fs.FamiliarCard, p: Palette, open_familiar: Open
) -> ClickableCard:
    """A familiar as a card that opens its page."""
    card = ClickableCard(p, pad=12)
    card_title(
        card,
        figures.name,
        figures.subtitle,
        p,
        symbol_label(artwork.icon("familiar"), p, 32),
    )
    card.column.addWidget(text(figures.detail, p["label"]))
    card.clicked = lambda: open_familiar(figures.id)
    return card


class SagaShelf(QWidget):
    """Every saga as a card; choosing one opens it. Above them, New Saga
    and Change Save Folder with the folder the saves are in; each card has
    a Delete."""

    def __init__(
        self,
        sagas: Sequence[Saga],
        p: Palette,
        open_saga: Open,
        new_saga: Callable[[], None] = lambda: None,
        delete_saga: Open = lambda _saga_id: None,
        change_folder: Callable[[], None] = lambda: None,
        folder: str = "",
    ) -> None:
        super().__init__()
        cards = []
        for saga in sagas:
            figures = ov.saga_card(saga)
            card = ClickableCard(p, pad=16)
            card_title(
                card,
                figures.name,
                figures.subtitle,
                p,
                symbol_label(artwork.icon("saga"), p),
            )
            card.column.addWidget(
                fact_grid(
                    [
                        cs.Fact("Covenants", str(figures.covenants)),
                        cs.Fact("Characters", str(figures.characters)),
                    ],
                    p,
                    2,
                )
            )
            delete = edit_button(
                "Delete",
                p,
                lambda _checked=False, saga_id=figures.id: delete_saga(saga_id),
                "delete",
            )
            card.column.addWidget(delete, 0, Qt.AlignmentFlag.AlignRight)
            card.clicked = lambda saga_id=figures.id: open_saga(saga_id)
            cards.append(card)
        self.new_saga = edit_button("New Saga", p, new_saga, "add")
        self.change_folder = edit_button("Change Save Folder", p, change_folder, "edit")
        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 0, 0, 0)
        buttons.addWidget(self.new_saga)
        buttons.addWidget(self.change_folder)
        buttons.addStretch(1)
        actions = QWidget()
        actions.setLayout(buttons)
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.addWidget(
            scrolling_page(
                p,
                page_header(
                    "Sagas",
                    "Choose a saga to open"
                    + (f" · the saves are in {folder}" if folder else ""),
                    p,
                    "saga",
                ),
                actions,
                card_grid(cards)
                if cards
                else text(
                    "No sagas yet: New Saga starts one.",
                    p["dim"],
                    serif(13, italic=True),
                ),
            )
        )


def person_card(saga: Saga, character: Character, p: Palette, open_: Open) -> QWidget:
    """A person as a card, with their House's or tradition's symbol, that
    opens their sheet."""
    figures = ov.person_card(saga, character)
    house = artwork.person_symbol(character)
    card = ClickableCard(p, pad=12)
    card_title(
        card,
        figures.name,
        figures.subtitle,
        p,
        symbol_label(house, p, 40)
        if house
        else symbol_label(artwork.icon("character"), p, 32),
    )
    if figures.detail:
        card.column.addWidget(text(figures.detail, p["label"]))
    card.clicked = lambda: open_(figures.id)
    return card


def lab_card(figures: ov.LabCard, p: Palette, open_: Open) -> QWidget:
    """A laboratory as a card with its main figures, that opens it."""
    card = ClickableCard(p, pad=14)
    card_title(
        card,
        figures.name,
        figures.subtitle,
        p,
        symbol_label(artwork.icon("laboratory"), p),
    )
    card.column.addWidget(fact_grid(list(figures.facts), p, 4))
    card.clicked = lambda: open_(figures.id)
    return card


def with_new(cards: list[QWidget], new: QWidget | None) -> list[QWidget]:
    """`cards`, then the New card that adds to them, if there is one."""
    return [*cards, new] if new is not None else cards


def action_rows(rows: Sequence[tuple[QWidget, str]], p: Palette) -> QWidget:
    """Each button beside a line on what it does."""
    box = QWidget()
    grid = QGridLayout(box)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(16)
    grid.setVerticalSpacing(14)
    grid.setColumnStretch(1, 1)
    for row, (button, detail) in enumerate(rows):
        grid.addWidget(button, row, 0, Qt.AlignmentFlag.AlignTop)
        grid.addWidget(
            text(detail, p["label"], serif(12.5, italic=True), wrap=True), row, 1
        )
    return box


def neighbour_card(
    saga: Saga, neighbour: Neighbour, p: Palette, open_neighbour: Open
) -> ClickableCard:
    """A neighbour as a card that opens its page."""
    card = ClickableCard(p, pad=16)
    card_title(
        card,
        neighbour.name,
        region_sheet.card_subtitle(neighbour),
        p,
        symbol_label(artwork.icon(neighbours.icon_concept(neighbour)), p),
    )
    facts = region_sheet.card_facts(saga, neighbour)
    if facts:
        card.column.addWidget(fact_grid(facts, p, 1))
    card.clicked = lambda: open_neighbour(neighbour.id)
    return card


def more_card(
    group_key: str,
    held_back: int,
    p: Palette,
    every: set[str],
    redraw: Callable[[], None],
) -> ClickableCard:
    """The card that draws the rest of a group's neighbours: it adds the
    group to `every` and redraws the cards."""
    card = ClickableCard(p, pad=16)
    title, line = region_sheet.more_cards(group_key, held_back)
    card_title(card, title, line, p, symbol_label(artwork.icon("region"), p))

    def show_all() -> None:
        every.add(group_key)
        # Once the click that asked is over: the redraw removes this card.
        QTimer.singleShot(0, redraw)

    card.clicked = show_all
    return card


def group_cards(
    saga: Saga,
    group_key: str,
    members: list[Neighbour],
    every: set[str],
    p: Palette,
    open_neighbour: Open,
    redraw: Callable[[], None],
) -> QWidget:
    """A group's neighbours as cards: the first few, and a card that
    draws the rest, until `every` holds the group."""
    drawn, held_back = region_sheet.cards_shown(members, group_key in every)
    cards: list[QWidget] = [neighbour_card(saga, n, p, open_neighbour) for n in drawn]
    if held_back:
        cards.append(more_card(group_key, held_back, p, every, redraw))
    return card_grid(cards)


class NeighbourFilterBar(QWidget):
    """What the Region's neighbours are narrowed to, as quiet drop-downs
    on one line (neighbour_filter.Filter): a Tribunal's lands (while a
    place names one), a region and a kind."""

    def __init__(self, saga: Saga, p: Palette) -> None:
        super().__init__()
        self.saga = saga
        wanted = neighbour_filter.current(saga)
        self.region = filter_choice(
            "Every region", [(r.name, r.id) for r in neighbour_filter.regions(saga)]
        )
        self.kind = filter_choice(
            "Every kind", [(k.name, k.key) for k in neighbour_filter.kinds(saga)]
        )
        lands = neighbour_filter.tribunals(saga)
        #: Whose lands, only while some place names a Tribunal.
        self.tribunal = (
            filter_choice("Every Tribunal", [(t.name, t.id) for t in lands])
            if lands
            else None
        )
        row = QHBoxLayout(self)
        # Level with the heading's words beside it.
        row.setContentsMargins(0, 8, 0, 0)
        row.setSpacing(10)
        row.addStretch(1)
        row.addWidget(text("Show", p["dim"], serif(12, italic=True)))
        shown = [(self.region, wanted.region), (self.kind, wanted.kind)]
        if self.tribunal is not None:
            shown.insert(0, (self.tribunal, wanted.tribunal))
        for combo, value in shown:
            combo.setObjectName("quiet")
            combo.setCurrentIndex(max(combo.findData(value or None), 0))
            row.addWidget(combo)

    def wanted(self) -> neighbour_filter.Filter:
        return neighbour_filter.Filter(
            region=self.region.currentData() or "",
            kind=self.kind.currentData() or "",
            tribunal=(
                self.tribunal.currentData() or "" if self.tribunal is not None else ""
            ),
        )

    def changed(self, then: Callable[[], None]) -> None:
        """Call `then` whenever a drop-down changes."""
        for combo in (self.region, self.kind, self.tribunal):
            if combo is None:
                continue
            combo.currentIndexChanged.connect(lambda _index: then())


def _region_facts(saga: Saga, p: Palette, open_neighbour: Open) -> QWidget:
    """The Region's facts, Threat due with a leaf that opens the threat."""
    beside: dict[str, QWidget] = {}
    threat = region_sheet.due_threat(saga)
    if threat is not None:
        leaf = FleuronButton(p, f"Open {threat.name}")
        leaf.clicked.connect(lambda: open_neighbour(threat.id))
        beside["Threat due"] = leaf
    return fact_grid(region_sheet.facts(saga, showing=False), p, 3, beside)


def story_card(
    saga: Saga, row: int, p: Palette, run: Callable[[Command], None]
) -> Card:
    """An open story as a card: what it concerns, the season it arose and
    the covenant whose Diary keeps it, its words, and its Edit and Grow
    into a Threat."""
    story = open_stories.stories(saga)[row]
    entry = story.entry
    card = Card(p, pad=16)
    card_title(
        card,
        entry.name or "(unnamed)",
        f"{entry.season} {entry.year}, {story.covenant.name}'s Diary",
        p,
        symbol_label(artwork.icon("threat"), p),
    )
    facts = [Fact("Concerns", open_stories.concerns_text(saga, story.covenant, entry))]
    card.column.addWidget(fact_grid(facts, p, 1))
    if entry.details.strip():
        card.column.addWidget(
            text(entry.details.strip(), p["foreground"], serif(12.5), wrap=True)
        )
    chapters = story_chapters.story_chapters(story.covenant, entry)
    if chapters:
        card.column.addWidget(
            text(
                "\n".join(f"{c.when}: {c.words}" for c in chapters),
                p["label"],
                serif(12, italic=True),
                wrap=True,
            )
        )
    ops = open_stories.ops(
        saga, lambda covenant: diary_forms.covenant_diary_ops(saga, covenant)
    )
    line = QHBoxLayout()
    line.setSpacing(6)
    if ops.edit is not None:
        edit = ops.edit
        line.addWidget(edit_button("Edit", p, lambda: run(edit(row))))
    line.addWidget(
        edit_button(
            story_chapters.TAKE_UP,
            p,
            lambda: run(
                story_chapters.take_up_story(saga, story.covenant, story.entry)
            ),
            "more",
        )
    )
    line.addWidget(
        edit_button(
            open_stories.GROW_TITLE,
            p,
            lambda: run(open_stories.grow_form(saga, row)),
            "threat",
        )
    )
    line.addStretch(1)
    card.column.addLayout(line)
    return card


def stories_part(saga: Saga, p: Palette, run: Callable[[Command], None]) -> QWidget:
    """The Region's Open Stories: their heading, and a card for each."""
    part = QWidget()
    column = QVBoxLayout(part)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(12)
    column.addWidget(chapter_title(open_stories.title(saga), p))
    count = len(open_stories.stories(saga))
    if count:
        column.addWidget(card_grid([story_card(saga, i, p, run) for i in range(count)]))
    else:
        column.addWidget(
            text(open_stories.grid(saga).empty, p["dim"], serif(12.5, italic=True))
        )
    return part


def _tribunals_parts(
    saga: Saga, p: Palette, open_tribunal: Open, new: QWidget | None
) -> list[QWidget]:
    """The Tribunals' heading and cards, ending in the New card."""
    courts: list[QWidget] = [
        tribunal_card(saga, t, p, open_tribunal) for t in saga.tribunals
    ]
    listed = with_new(courts, new)
    return [
        chapter_title(f"Tribunals ({len(courts)})", p),
        card_grid(listed, 2)
        if listed
        else text("None.", p["dim"], serif(12.5, italic=True)),
    ]


def _heading_with(
    title: QWidget, buttons: Sequence[QWidget], spacing: int = 6
) -> QWidget:
    """`title`, with `buttons` at its right when there are any."""
    if not buttons:
        return title
    row = QWidget()
    line = QHBoxLayout(row)
    line.setContentsMargins(0, 0, 0, 0)
    line.setSpacing(spacing)
    line.addWidget(title, 1)
    for button in buttons:
        line.addWidget(button, 0, Qt.AlignmentFlag.AlignTop)
    return row


def _clear(holder: QVBoxLayout) -> None:
    """Take every widget out of `holder`, to be drawn again."""
    while holder.count():
        item = holder.takeAt(0)
        old = item.widget() if item is not None else None
        if old is not None:
            old.setParent(None)
            old.deleteLater()


def _view_chips(saga: Saga, p: Palette, then: Callable[[], None]) -> QWidget:
    """By kind or by place: the two ways into the Region."""

    def show(chosen: str) -> Callable[[], None]:
        def flip() -> None:
            region_sheet.choose_view(saga, chosen)
            then()

        return flip

    shown = region_sheet.view(saga)
    return chip_row(
        "Show",
        [
            ("By kind", shown == region_sheet.BY_KIND, show(region_sheet.BY_KIND)),
            ("By place", shown == region_sheet.BY_PLACE, show(region_sheet.BY_PLACE)),
        ],
        p,
    )


def _by_place(saga: Saga, p: Palette, follow: Callable[[Ref], None]) -> QWidget:
    """The Region by place as one block of lines, indented by depth, each
    name a link (one label, so hundreds of records draw at once)."""
    rows = region_sheet.by_place(saga)
    if not rows:
        return text(
            "No places yet: add one under Places.", p["dim"], serif(12.5, italic=True)
        )
    by_href: dict[str, Ref] = {}
    lines = []
    for row in rows:
        indent = "&nbsp;" * (4 * row.depth)
        name = html.escape(row.name)
        if row.ref is None:
            lines.append(f"{indent}<b>{name}</b>")
            continue
        href = str(len(by_href))
        by_href[href] = row.ref
        lines.append(
            f'{indent}<a href="{href}" style="color:{p["primary"]}; '
            f'text-decoration:none">{name}</a>'
            f'&nbsp;&nbsp;<span style="color:{p["label"]}">{html.escape(row.what)}</span>'
        )
    label = text("<br>".join(lines), p["foreground"], serif(13), wrap=True)
    label.setTextFormat(Qt.TextFormat.RichText)
    # A wrapped label asks for the width of its longest line; let it take
    # the column's width instead, wrapping the rest.
    label.setMinimumWidth(240)
    label.linkActivated.connect(
        lambda href: follow(by_href[href]) if href in by_href else None
    )
    return label


def region_chapter(
    saga: Saga,
    p: Palette,
    open_neighbour: Open,
    new: QWidget | None,
    open_tribunal: Open,
    new_tribunal: QWidget | None,
    run: Callable[[Command], None] = lambda _command: None,
    buttons: Sequence[QWidget] = (),
    follow: Callable[[Ref], None] | None = None,
) -> QWidget:
    """The Region: its Tribunals as cards, ending in the New card that
    adds one; its facts (Threat due with a leaf that opens the threat),
    under the Neighbours heading with `buttons` (More's actions on the
    Region) at its right,
    then each group's neighbours the filter lets through as cards, the
    filter's quiet drop-downs at the right of the first group's heading,
    and the New card that adds one; then the troupe's open stories. A
    line of chips under the heading turns the groups into the Region by
    place, each name a link `follow` opens."""
    facts = _region_facts(saga, p, open_neighbour)
    opened = follow or (
        lambda found: open_neighbour(found.id) if found.kind == "neighbours" else None
    )

    parts: list[QWidget] = [
        *_tribunals_parts(saga, p, open_tribunal, new_tribunal),
        _heading_with(chapter_title(region_sheet.neighbours_title(saga), p), buttons),
    ]
    groups = QWidget()
    holder = QVBoxLayout(groups)
    holder.setContentsMargins(0, 0, 0, 0)
    holder.setSpacing(12)
    bar = NeighbourFilterBar(saga, p) if saga.neighbours else None

    def heading(words: str, first: bool) -> QWidget:
        """A group's heading; the first shown carries the filter."""
        title = chapter_title(words, p)
        return title if bar is None or not first else _heading_with(title, [bar], 16)

    def fill() -> None:
        if bar is not None:
            bar.setParent(None)
        _clear(holder)
        holder.addWidget(_view_chips(saga, p, fill))
        if region_sheet.view(saga) == region_sheet.BY_PLACE:
            holder.addWidget(_by_place(saga, p, opened))
            return
        first = True
        for group in neighbours.groups_shown(saga):
            members = neighbour_filter.shown(saga, group.key)
            if not members:
                continue
            holder.addWidget(heading(region_sheet.group_title(saga, group.key), first))
            first = False
            holder.addWidget(
                group_cards(saga, group.key, members, every, p, open_neighbour, fill)
            )
        if saga.neighbours and first:
            if bar is not None:
                holder.addWidget(bar)
            holder.addWidget(
                text("None match the filter.", p["dim"], serif(12.5, italic=True))
            )

    #: The groups whose every card was asked for.
    every: set[str] = set()

    def refilter() -> None:
        assert bar is not None
        neighbour_filter.choose(saga, bar.wanted())
        fill()

    parts.append(facts)
    if bar is not None:
        bar.changed(refilter)
    fill()
    parts.append(groups)
    if new is not None:
        parts.append(card_grid(with_new([], new)))
    elif not saga.neighbours:
        parts.append(text("None yet.", p["dim"], serif(12.5, italic=True)))
    return scrolling_page(p, *parts, stories_part(saga, p, run))


def creature_card(
    saga: Saga, creature: Creature, p: Palette, open_creature: Open
) -> ClickableCard:
    """A creature as a card that opens its page: its Might, Size and
    where it is found."""
    card = ClickableCard(p, pad=16)
    card_title(
        card,
        creature.name,
        crs.subtitle(creature),
        p,
        symbol_label(artwork.icon(creatures.icon_concept(creature)), p),
    )
    facts = [f for f in crs.facts(saga, creature) if f.label in ("Size", "Found at")]
    card.column.addWidget(fact_grid(facts, p, 2))
    card.clicked = lambda: open_creature(creature.id)
    return card


def bestiary_chapter(
    saga: Saga, p: Palette, open_creature: Open, new: QWidget | None
) -> QWidget:
    """The Bestiary: its facts, then every creature as a card, by name,
    and the New card that adds one."""
    cards: list[QWidget] = [
        creature_card(saga, c, p, open_creature) for c in creatures.listed(saga)
    ]
    listed = with_new(cards, new)
    return scrolling_page(
        p,
        chapter_title(crs.bestiary_title(saga), p),
        fact_grid(crs.bestiary_facts(saga), p, 3),
        card_grid(listed)
        if listed
        else text("None yet.", p["dim"], serif(12.5, italic=True)),
    )


def battle_card(
    saga: Saga, index: int, p: Palette, run: Callable[[Command], None]
) -> QWidget:
    """A battle as a card: its armies, their groups and how its events
    went, with Battle Event, Edit and Delete (a battle has no page of its
    own: Battle Event plays it)."""
    entry = saga.battles[index]
    row = battles.grid(saga).rows[index]
    card = Card(p, pad=16)
    top = QHBoxLayout()
    top.setSpacing(10)
    top.addWidget(symbol_label(artwork.icon("lord"), p), 0, Qt.AlignmentFlag.AlignTop)
    names = QVBoxLayout()
    names.setSpacing(0)
    names.addWidget(text(entry.name, p["foreground"], serif(16, bold=True), wrap=True))
    when = (
        f"{entry.season} {entry.year}"
        + (f", {entry.place}" if entry.place else "")
        + (", at sea" if entry.at_sea else "")
    )
    names.addWidget(text(when, p["label"], serif(11.5, italic=True), wrap=True))
    top.addLayout(names, 1)
    card.column.addLayout(top)
    facts = [
        Fact("Armies", row[1]),
        Fact("Combat groups", row[2]),
        Fact("Ground and numbers", f"{row[3]}, {row[4]}"),
        Fact("Events", row[5]),
    ]
    if entry.at_sea:
        # A fleet battle: its ships, whose count sets the Weight of Numbers.
        facts.insert(2, Fact("Ships", battles.ships_text(saga, entry)))
    card.column.addWidget(fact_grid(facts, p, 1))
    ops = conflicts.ops(saga)[CONFLICT_BATTLES_SECTION]
    line = QHBoxLayout()
    line.setSpacing(6)
    line.addWidget(
        edit_button(
            "Battle Event",
            p,
            lambda: run(conflicts.command(saga, "conflict_battle_event", index)),
            "combat",
        )
    )
    line.addWidget(
        edit_button(
            "Muster and Aftermath",
            p,
            lambda: run(conflicts.command(saga, "battle_muster", index)),
            "players",
        )
    )
    if ops.edit is not None:
        edit = ops.edit
        line.addWidget(edit_button("Edit", p, lambda: run(edit(index))))
    if ops.remove is not None:
        remove = ops.remove
        line.addWidget(edit_button("Delete", p, lambda: run(remove(index)), "delete"))
    line.addStretch(1)
    card.column.addLayout(line)
    return card


def fight_card(saga: Saga, index: int, p: Palette, open_fight: Open) -> ClickableCard:
    """A fight as a card that opens its page: when and where, its sides,
    who still stands and how it goes."""
    fight = saga.fights[index]
    row = fights.grid(saga).rows[index]
    card = ClickableCard(p, pad=16)
    card_title(card, fight.name, row[4], p, symbol_label(artwork.icon("combat"), p))
    facts = [Fact("When", row[1]), Fact("Sides", row[2]), Fact("Standing", row[3])]
    card.column.addWidget(fact_grid(facts, p, 1))
    card.clicked = lambda: open_fight(fight.id)
    return card


def siege_card(saga: Saga, index: int, p: Palette, open_siege: Open) -> ClickableCard:
    """A siege as a card that opens its page: the castle, the besieger,
    the castle's figures and how long it has run."""
    siege = saga.sieges[index]
    row = sieges.grid(saga).rows[index]
    card = ClickableCard(p, pad=16)
    card_title(card, siege.name, row[6], p, symbol_label(artwork.icon("covenant"), p))
    facts = [
        Fact("Castle", row[1]),
        Fact("Besieger", row[2]),
        Fact("Garrison", row[3]),
        Fact("Defenses", row[4]),
        Fact("Supplies", row[5]),
    ]
    card.column.addWidget(fact_grid(facts, p, 2))
    card.clicked = lambda: open_siege(siege.id)
    return card


def conflicts_chapter(
    saga: Saga,
    p: Palette,
    run: Callable[[Command], None],
    open_fight: Open,
    open_siege: Open,
) -> QWidget:
    """Conflicts: its facts, then the battles, the fights and the sieges
    as cards, each list with its Add."""
    ops = conflicts.ops(saga)
    parts: list[QWidget] = [
        chapter_title("Conflicts", p),
        fact_grid(conflicts.header_facts(saga), p, 5),
    ]
    for title, section, cards in (
        (
            battles.title(saga),
            CONFLICT_BATTLES_SECTION,
            [battle_card(saga, i, p, run) for i in range(len(saga.battles))],
        ),
        (
            fights.title(saga),
            FIGHTS_SECTION,
            [fight_card(saga, i, p, open_fight) for i in range(len(saga.fights))],
        ),
        (
            sieges.title(saga),
            SIEGES_SECTION,
            [siege_card(saga, i, p, open_siege) for i in range(len(saga.sieges))],
        ),
    ):
        add = ops[section].add
        head = QWidget()
        line = QHBoxLayout(head)
        line.setContentsMargins(0, 8, 0, 0)
        line.addWidget(text(title, p["heading"], serif(16, bold=True)))
        line.addStretch(1)
        if add is not None:
            line.addWidget(
                edit_button("Add", p, lambda add=add: run(add()), "add"),
            )
        parts.append(head)
        parts.append(
            card_grid(cards)
            if cards
            else text("None yet.", p["dim"], serif(12.5, italic=True))
        )
    return scrolling_page(p, *parts)


def covenant_card(
    figures: ov.CovenantCard, p: Palette, open_covenant: Callable[[str | None], None]
) -> ClickableCard:
    """A covenant as a card that opens its page; a troupe covenant's with
    its mark and a flourish."""
    card = ClickableCard(p, pad=16, flourished=figures.played)
    card_title(
        card,
        f"{world.TROUPE_GLYPH} {figures.name}" if figures.played else figures.name,
        figures.subtitle,
        p,
        symbol_label(artwork.icon("covenant"), p),
    )
    card.column.addWidget(fact_grid(list(figures.facts), p, 5))
    card.clicked = lambda: open_covenant(figures.id)
    return card


def tribunal_card(
    saga: Saga, tribunal: Tribunal, p: Palette, open_tribunal: Open
) -> ClickableCard:
    """A Tribunal as a card with its next meeting, that opens its page."""
    card = ClickableCard(p, pad=16)
    card_title(
        card,
        tribunal.name,
        f"Next meeting: {tribunal_sheet.next_meeting(tribunal)}",
        p,
        symbol_label(artwork.icon("tribunal"), p),
    )
    card.column.addWidget(fact_grid(tribunal_sheet.facts(saga, tribunal)[5:], p, 3))
    card.clicked = lambda: open_tribunal(tribunal.id)
    return card


def troupe_chapter(
    saga: Saga, p: Palette, opens: dict[str, Callable[[Any], None]]
) -> QWidget:
    """The Troupe: the player characters by covenant, the covenants the
    troupe plays, then whatever else the reader has bookmarked, by kind.
    `opens` opens a record of each kind (troupe.KIND_TITLES)."""
    covenants = {f.id: f for f in ov.covenant_cards(saga)}
    # How each kind of record is drawn as a card.
    cards: dict[str, Callable[[Any], QWidget]] = {
        "character": lambda r: person_card(saga, r, p, opens["character"]),
        "covenant": lambda r: covenant_card(covenants[r.id], p, opens["covenant"]),
        "laboratory": lambda r: lab_card(
            next(f for f in ov.lab_cards(saga, r.covenant_id) if f.id == r.id),
            p,
            opens["laboratory"],
        ),
        "familiar": lambda r: familiar_card(
            fs.familiar_card(saga, r),
            p,
            opens["familiar"],
        ),
        "tribunal": lambda r: tribunal_card(saga, r, p, opens["tribunal"]),
        "neighbour": lambda r: neighbour_card(saga, r, p, opens["neighbour"]),
        "creature": lambda r: creature_card(saga, r, p, opens["creature"]),
    }

    def quiet(words: str) -> QWidget:
        return text(words, p["dim"], serif(12.5, italic=True), wrap=True)

    groups = troupe.player_characters(saga)
    played = sum(len(members) for _, members in groups)
    parts: list[QWidget] = [chapter_title(f"Player Characters ({played})", p)]
    for covenant, members in groups:
        if len(groups) > 1:
            parts.append(
                divider(
                    world.marked_name(covenant) if covenant else "Of no covenant", p
                )
            )
        parts.append(card_grid([cards["character"](c) for c in members]))
    if not groups:
        parts.append(
            quiet(
                "No one yet. A character whose Biographical Detail names their "
                "Player is a player character, and is gathered here."
            )
        )
    homes = troupe.troupe_covenants(saga)
    parts.append(chapter_title(f"Troupe Covenants ({len(homes)})", p))
    parts.append(
        card_grid([cards["covenant"](c) for c in homes], 2)
        if homes
        else quiet("None. A covenant's Edit says whether the troupe plays it.")
    )
    marked = troupe.other_bookmarks(saga)
    count = sum(len(records) for _, records in marked)
    parts.append(chapter_title(f"Bookmarked ({count})", p))
    for kind, records in marked:
        parts.append(divider(troupe.KIND_TITLES[kind], p))
        parts.append(
            card_grid(
                [cards[kind](r) for r in records],
                2 if kind in ("covenant", "laboratory", "tribunal") else CARDS_ACROSS,
            )
        )
    if not marked:
        parts.append(
            quiet(
                "Nothing yet. Bookmark a page you keep going back to, with the "
                "ribbon at the right of its header, and it is kept here."
            )
        )
    return scrolling_page(p, *parts)


class SagaPage(QWidget):
    """A saga as a Codex: The Troupe (its player characters, the troupe's
    covenants and what the reader has bookmarked), The Covenants (its
    covenants, and the characters and laboratories that belong to none,
    each list ending in a New card), The Region (its Tribunals and
    neighbours), The Atlas (its maps and the records pinned on them), The Bestiary (its creatures), its Conflicts (fights and sieges), its Seasons, its Rules and Content, its Saga Settings, and Saga Management."""

    def __init__(
        self,
        saga: Saga,
        p: Palette,
        open_covenant: Callable[[str | None], None],
        **hooks: Unpack[SagaHooks],
    ) -> None:
        super().__init__()
        open_content = hooks.get("open_content", lambda: None)
        open_seasons = hooks.get("open_seasons", lambda: None)
        open_character = hooks.get("open_character", _ignore)
        open_laboratory = hooks.get("open_laboratory", _ignore)
        open_tribunal = hooks.get("open_tribunal", _ignore)
        open_neighbour = hooks.get("open_neighbour", _ignore)
        open_creature = hooks.get("open_creature", _ignore)
        open_familiar = hooks.get("open_familiar", _ignore)
        run = hooks.get("run", lambda _command: None)
        open_fight = hooks.get("open_fight", _ignore)
        open_siege = hooks.get("open_siege", _ignore)
        self.saga, self.p = saga, p
        self.open_tribunal = open_tribunal
        self.open_neighbour = open_neighbour
        self.placer = hooks.get("placer")
        self.open_covenant = open_covenant
        self.open_character, self.open_laboratory = open_character, open_laboratory
        column = QVBoxLayout(self)
        column.setContentsMargins(18, 12, 12, 8)
        column.setSpacing(10)
        column.addWidget(page_header(saga.name, ov.saga_card(saga).subtitle, p, "saga"))
        if saga.description:
            column.addWidget(
                text(saga.description, p["foreground"], serif(13), wrap=True)
            )
        self.codex = Codex(p)
        opens: dict[str, Callable[[Any], None]] = {
            "character": open_character,
            "covenant": open_covenant,
            "laboratory": open_laboratory,
            "familiar": open_familiar,
            "tribunal": open_tribunal,
            "neighbour": open_neighbour,
            "creature": open_creature,
        }
        self.codex.add("The Troupe", "troupe", troupe_chapter(saga, p, opens))
        self.codex.add("The Covenants", "covenant", self._covenants())
        # The Region and The Bestiary are built when first opened: a
        # pack's Tribunal brings hundreds of neighbours and dozens of
        # creatures, too many cards to draw each time the saga opens.
        self.codex.add(
            "The Region",
            "region",
            lambda: region_chapter(
                saga,
                p,
                self.open_neighbour,
                self._new("Neighbours"),
                self.open_tribunal,
                self._new("Tribunals"),
                run,
                self._buttons("The Region"),
                lambda found: self._follow(opens, found),
            ),
        )
        # The Atlas is built when first opened: its maps are large pictures.
        run_ended = hooks.get("run_ended", lambda command, _ended: run(command))
        self.codex.add(
            "The Atlas",
            "atlas",
            lambda: AtlasChapter(saga, p, run, run_ended, self.codex.inspect),
        )
        self.codex.add(
            "The Bestiary",
            "familiar",
            lambda: bestiary_chapter(saga, p, open_creature, self._new("Creatures")),
        )
        self.codex.add(
            "Conflicts",
            "combat",
            lambda: conflicts_chapter(saga, p, run, open_fight, open_siege),
        )
        self.codex.add("Seasons", "season", self._seasons(open_seasons))
        self.codex.add(
            "Rules and Content", "library", self._rules_and_content(open_content)
        )
        self.settings = SettingsChapter(
            saga, p, self.codex, run, self._buttons("Saga Settings")
        )
        self.codex.add("Saga Settings", "edit", self.settings.page)
        self.codex.add("Saga Management", "manage", self._management())
        column.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    @staticmethod
    def _follow(opens: dict[str, Callable[[Any], None]], found: Ref) -> None:
        """Open the record a link of the Region by place names."""
        kind = found.kind.removesuffix("s")
        if kind in opens:
            opens[kind](found.id)

    def _new(self, spot: str, hint: str = "") -> QWidget | None:
        return self.placer.new_card(spot, hint=hint) if self.placer else None

    def _buttons(self, spot: str) -> list[QPushButton]:
        return self.placer.buttons(spot) if self.placer else []

    def _covenants(self) -> QWidget:
        p, saga = self.p, self.saga
        figures = ov.covenant_cards(saga)
        troupe = sum(f.played for f in figures)
        covenants: list[QWidget] = [
            covenant_card(f, p, self.open_covenant) for f in figures
        ]
        people = [
            person_card(saga, c, p, self.open_character) for c in ov.members(saga, None)
        ]
        labs = [lab_card(f, p, self.open_laboratory) for f in ov.lab_cards(saga, None)]
        parts: list[QWidget] = []
        for title, cards, across in (
            ("Covenants", covenants, 2),
            ("Unassigned Characters", people, CARDS_ACROSS),
            ("Unassigned Laboratories", labs, 2),
        ):
            listed = with_new(cards, self._new(title))
            parts.append(chapter_title(f"{title} ({len(cards)})", p))
            if title == "Covenants" and 0 < troupe < len(cards):
                # The troupe's covenants, then a divider, then the rest.
                parts.append(card_grid(cards[:troupe], across))
                parts.append(divider("Other covenants", p))
                listed = listed[troupe:]
            parts.append(
                card_grid(listed, across)
                if listed
                else text("None.", p["dim"], serif(12.5, italic=True))
            )
        return scrolling_page(p, *parts)

    def _seasons(self, open_seasons: Callable[[], None]) -> QWidget:
        p, saga = self.p, self.saga
        kept = len(saga.season_records)
        past = ClickableCard(p, pad=16)
        card_title(
            past,
            "The Seasons Played",
            "What everyone did each season, and what it gave them",
            p,
            symbol_label(artwork.icon("season"), p),
        )
        past.column.addWidget(fact_grid([cs.Fact("Recorded", str(kept))], p, 4))
        past.clicked = open_seasons
        self.seasons = past
        heading = QWidget()
        row = QHBoxLayout(heading)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.addWidget(chapter_title("The Date", p), 1)
        for button in self._buttons("Seasons"):
            row.addWidget(button, 0, Qt.AlignmentFlag.AlignTop)
        return scrolling_page(
            p,
            heading,
            text(
                f"It is {saga.current_season} {saga.current_year}. Advance Season, "
                "at the top of the window, plays the season out.",
                p["foreground"],
                serif(13),
                wrap=True,
            ),
            chapter_title("Records", p),
            card_grid([past], 2),
        )

    def _rules_and_content(self, open_content: Callable[[], None]) -> QWidget:
        p, saga = self.p, self.saga
        content = ClickableCard(p, pad=16)
        card_title(
            content,
            "Saga Content",
            "The books in play, catalogs, House Rules and spells",
            p,
            symbol_label(artwork.icon("library"), p),
        )
        content.column.addWidget(fact_grid(scs.header_facts(saga), p, 4))
        content.clicked = open_content
        self.content = content
        return scrolling_page(
            p, chapter_title("Rules and Content", p), card_grid([content], 2)
        )

    def _management(self) -> QWidget:
        p = self.p
        placed = self.placer.placed_buttons("Saga Management") if self.placer else []
        rows = [
            (button, menu_forms.management_note(item.action)) for item, button in placed
        ]
        return scrolling_page(
            p,
            chapter_title("Saga Management", p),
            action_rows(rows, p)
            if rows
            else text("Nothing to manage.", p["dim"], serif(12.5, italic=True)),
        )
