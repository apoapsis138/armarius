"""The desktop covenant page, read-only, in the Codex layout: a header
with the name, its Tribunal and season, the Aegis and living conditions,
and the aura and Loyalty as seals; then chapters for its attributes (the
description, Boons and Hooks, Reputations), its Charter of Covenant and
clauses, its people, covenfolk,
laboratories, possessions, treasury, library, seasons, Diary and Build
Points, with the inspector beside them.

The characters who belong to no covenant get the same page with only
their people, laboratories and seasons.

What it says comes from the shared core (sheets/covenant.py and
saga_overview.py), as the terminal's covenant sheet does.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from .. import (
    artwork,
    boon_hook_text,
    catalog,
    giving,
    hermetic_projects,
    manors,
    seasons,
    town_charter,
    vis,
    world,
)
from .. import books as bk
from .. import covenant_build as cov_build
from .. import covenant_diary as cov_diary
from .. import inhabitants as inh
from .. import possessions as pos
from .. import saga_overview as ov
from ..actions import NodeKind
from ..commands import Form, SectionOps
from ..covenants import boon_hook_problems
from ..forms import covenant as covenant_forms
from ..forms import creation as creation_forms
from ..forms import diary as diary_forms
from ..forms import inhabitant as inhabitant_forms
from ..forms import library as library_forms
from ..forms import menu as menu_forms
from ..forms import possession as possession_forms
from ..forms import season as season_forms
from ..forms import world as world_forms
from ..models import FULL, INHABITANT_KINDS, LINE, POSSESSION_KINDS, Covenant, Saga
from ..references import Fact
from ..rules import library
from ..sections import COV_CHARTER_LORDS_SECTION, COV_CHARTER_TERMS_SECTION
from ..sheets import character as cs
from ..sheets import covenant as cvs
from ..sheets import familiar as fs
from .ahead import ahead_section
from .bookmark import with_bookmark
from .character_sheet import (
    TextBlock,
    columns_text,
    connections_section,
    device_section,
    label_values,
    secrets_chapter,
    section,
    side_by_side,
    trait_section,
)
from .charter import charter_section, clauses_section
from .editing import Chooser, RowVerb, Run, choose_cards, give_verb, verb_buttons
from .figures import Seal, attitude_seal, aura_seal, fact_grid, prose, shelf
from .heraldry import arms_section, neighbours_arms
from .manage import RecordControls
from .medallions import Medallion
from .menus import Placer
from .pages import (
    Open,
    card_grid,
    familiar_card,
    lab_card,
    person_card,
    symbol_label,
    with_new,
)
from .region import KindChapters
from .ships import ships_section
from .themes import Palette
from .timeline import SeasonTimeline, legend, season_text
from .widgets import (
    Card,
    ClickableCard,
    Codex,
    Symbol,
    badge,
    cells_table,
    chapter_title,
    display_name,
    edit_button,
    scrolling_page,
    serif,
    table_view,
    text,
)
from .world import relations, table_section


def _none(words: str, p: Palette) -> QLabel:
    return text(words, p["dim"], serif(12.5, italic=True))


def _choose_cards_by(
    cards: Sequence[ClickableCard], indexes: Sequence[int], chooser: Chooser
) -> None:
    """As editing.choose_cards, for cards shown in another order than
    their rows: clicking card i chooses row `indexes[i]`."""
    for card, index in zip(cards, indexes, strict=True):
        before = card.clicked

        def clicked(index: int = index, before: Callable[[], None] = before) -> None:
            chooser.choose(index)
            before()

        card.clicked = clicked

    def outline(chosen: int | None) -> None:
        for card, index in zip(cards, indexes, strict=True):
            card.set_chosen(index == chosen)

    chooser.listeners.append(outline)


class CovenantPage(QWidget):
    """A covenant in the Codex layout. Choosing a person or a laboratory
    opens their page; choosing anything else shows it in the inspector."""

    def __init__(
        self,
        saga: Saga,
        covenant_id: str | None,
        p: Palette,
        open_character: Open,
        open_laboratory: Open,
        open_familiar: Open = lambda _id: None,
        run: Run = lambda _command: None,
        controls: RecordControls | None = None,
        placer: Placer | None = None,
    ) -> None:
        super().__init__()
        self.saga, self.p = saga, p
        self.run = run
        self.controls = controls
        self.placer = placer
        self.open_character, self.open_laboratory = open_character, open_laboratory
        self.open_familiar = open_familiar
        self.covenant_id = covenant_id
        #: Each inhabitant, possession and treasury table, by its kind.
        self.tables: dict[str, QTableView] = {}
        covenant = saga.covenant(covenant_id)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(
            with_bookmark(
                self._header(covenant), controls.bookmark(p) if controls else None
            )
        )
        self.codex = Codex(p)
        self.inspector = self.codex.inspector
        labs = ov.lab_cards(saga, covenant_id)
        chapters = []
        if covenant is not None and covenant.detail != FULL:
            # A Line or Sketch covenant: one chapter of what it is to the
            # saga, and its Diary.
            chapters += [
                ("Sketch", "covenant", lambda: self._sketch(covenant)),
                ("Charter", "charter", lambda: self._charter(covenant)),
                ("Diary", "year", lambda: self._diary(covenant)),
            ]
        elif covenant is not None:
            chapters += [
                ("Attributes", "key", lambda: self._attributes(covenant)),
                ("Charter", "charter", lambda: self._charter(covenant)),
            ]
        if covenant is None or covenant.detail == FULL:
            chapters.append(("People", "character", self._people))
        if covenant is not None and covenant.detail == FULL:
            chapters.append(("Covenfolk", "players", lambda: self._covenfolk(covenant)))
        full = covenant is None or covenant.detail == FULL
        if full and (covenant is not None or labs):
            chapters.append(("Laboratories", "laboratory", lambda: self._labs(labs)))
        if covenant is not None and full:
            chapters += [
                ("Possessions", "vis", lambda: self._possessions(covenant)),
                ("Treasury", "income", lambda: self._treasury(covenant)),
                ("Manors", "place", lambda: self._manors(covenant)),
                ("Library", "library", lambda: self._library(covenant)),
            ]
            # A covenant's Hermetic Projects, once one is begun: after Manors.
            if hermetic_projects.has_projects(covenant):
                chapters.insert(
                    [name for name, _, _ in chapters].index("Manors") + 1,
                    ("Projects", "covenant", lambda: self._projects(covenant)),
                )
        if full:
            chapters.append(("Seasons", "season", self._seasons))
        if covenant is not None and full:
            chapters += [
                ("Diary", "year", lambda: self._diary(covenant)),
                ("Build", "covenant", lambda: self._build(covenant)),
            ]
        if covenant is not None:
            chapters.append(
                ("Secrets", "secrets", lambda: secrets_chapter(covenant, p, self.run))
            )
        for name, concept, build in chapters:
            self.codex.add(name, concept, build())
        if covenant is not None and controls is not None:
            self.codex.add("Manage", "manage", controls.chapter(p))
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def inspect(
        self, title: str, subtitle: str, markup: str, symbol: Symbol | None = None
    ) -> None:
        self.codex.inspect(title, subtitle, markup, symbol)

    # Above the chapters

    def _header(self, covenant: Covenant | None) -> QWidget:
        p, saga = self.p, self.saga
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(14)
        row.addWidget(
            symbol_label(artwork.icon("covenant"), p, 56), 0, Qt.AlignmentFlag.AlignTop
        )
        names = QVBoxLayout()
        names.setSpacing(0)
        names.addWidget(display_name(covenant.name if covenant else "Unassigned", p))
        names.addWidget(
            text(
                cvs.subtitle(saga, covenant)
                if covenant
                else "Characters who belong to no covenant",
                p["label"],
                serif(12.5, italic=True),
            )
        )
        row.addLayout(names)
        row.addStretch(1)
        if covenant is None:
            return box
        if covenant.detail != FULL:
            row.addWidget(fact_grid(cvs.sketch_facts(saga, covenant), p, 3))
            row.addSpacing(10)
            if covenant.detail != LINE:
                row.addWidget(aura_seal(cvs.aura(covenant), p))
            for target in world_forms.attitude_targets(saga, covenant):
                seal = attitude_seal(world.attitude_toward(covenant, target.id), p)
                seal.setToolTip(f"Toward {target.name}: {seal.toolTip()}")
                row.addWidget(seal)
            row.addWidget(
                self._edit_button(
                    lambda: world_forms.sketch_covenant_form(saga, covenant)
                ),
                0,
                Qt.AlignmentFlag.AlignTop,
            )
            return box
        row.addWidget(fact_grid(cvs.charter_facts(saga, covenant), p, 2))
        row.addSpacing(10)
        row.addWidget(aura_seal(cvs.aura(covenant), p))
        loyalty = cvs.loyalty(saga, covenant)
        tone = (
            "text-success"
            if loyalty.score > 0
            else "text-error"
            if loyalty.score < 0
            else "label"
        )
        row.addWidget(
            Seal(
                f"{loyalty.score:+d}" if loyalty.score else "0",
                "Loyalty",
                p[tone],
                f"Prevailing Loyalty {loyalty.score:+d}"
                f" ({loyalty.points} Loyalty Points)",
                p,
            )
        )
        row.addWidget(self._season_badge(covenant))
        mode = self.controls.mode(p) if self.controls is not None else None
        if mode is not None:
            row.addWidget(mode, 0, Qt.AlignmentFlag.AlignTop)
        row.addWidget(
            self._edit_button(lambda: covenant_forms.covenant_form(saga, covenant)),
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        return box

    def _season_badge(self, covenant: Covenant) -> Medallion:
        """The covenant's own season (its Covenant Season, not the saga's
        present one) as a medallion, with no words: the subtitle says it."""
        badge = Medallion(
            self.saga, covenant.covenant_season, self.saga.current_year, self.p
        )
        badge.setToolTip(f"{covenant.covenant_season} covenant")
        return badge

    def _edit_button(self, form: Callable[[], Form]) -> QPushButton:
        """The header's Edit, opening Edit Covenant."""
        button = edit_button("Edit", self.p, lambda: self.run(form()))
        button.setToolTip("Edit Covenant")
        return button

    # Chapters

    def _attributes(self, covenant: Covenant) -> QWidget:
        """Its arms, the description, Reputations, and the Boons beside
        the Hooks."""
        p = self.p
        boons, hooks = cvs.boon_hook_points(covenant)
        balance = (
            p["foreground"]
            if boons < hooks
            else p["text-success"]
            if boons == hooks
            else p["text-error"]
        )
        columns = []
        for kind, points, tone in (
            ("Boon", boons, "text-success"),
            ("Hook", hooks, "text-error"),
        ):
            column = QWidget()
            stack = QVBoxLayout(column)
            stack.setContentsMargins(0, 0, 0, 0)
            stack.setSpacing(10)
            chooser = Chooser()
            ops = covenant_forms.boon_hook_ops(self.saga, covenant, kind)
            heading = section(
                f"{kind}s", p, buttons=verb_buttons(ops, chooser, self.run, p)
            )
            stack.addWidget(heading)
            stack.addWidget(
                text(
                    f"{points:g} {'point' if points == 1 else 'points'}"
                    + (" spent" if kind == "Boon" else " provided"),
                    balance,
                    serif(12, italic=True),
                )
            )
            cards = cvs.boon_hook_cards(covenant, kind)
            frames = [self._boon_hook_card(covenant, card, p[tone]) for card in cards]
            choose_cards(frames, chooser)
            for frame in frames:
                stack.addWidget(frame)
            if not cards:
                stack.addWidget(_none(f"No {kind}s.", p))
            stack.addStretch(1)
            columns.append(column)
        others = neighbours_arms(self.saga, covenant, p)
        parts: list[QWidget] = [
            arms_section(covenant, p, self.run),
            *([others] if others is not None else []),
            section(
                "The Covenant",
                p,
                prose(covenant.notes.strip(), p),
                edits={
                    "Edit Description": lambda: self.run(
                        covenant_forms.description_form(covenant)
                    ),
                    # A covenant's Hermetic Projects: the first shows their
                    # chapter.
                    hermetic_projects.BEGIN_PROJECT: lambda: self.run(
                        hermetic_projects.begin_form(self.saga, covenant)
                    ),
                },
            ),
            trait_section(
                "Reputations",
                covenant.reputations,
                "section-cov-reputations",
                p,
                self.run,
            ),
            connections_section(self.saga, covenant, p, self.run),
        ]
        if not covenant.played:
            parts += relations(self.saga, covenant, p, self.run)
        problems = boon_hook_problems(
            covenant, catalog.load_covenant_boon_hook_catalog_by_id()
        )
        for problem in problems:
            parts.append(text(problem, p["text-error"], wrap=True))
        parts.append(side_by_side(*columns, spacing=18))
        return scrolling_page(p, *parts)

    def _charter(self, covenant: Covenant) -> QWidget:
        """Its Charter of Covenant and clauses; then, for a full covenant,
        the town charter of its Chartered Town Boon and the towns it
        charters as a Charter Lord."""
        p, saga = self.p, self.saga
        parts: list[QWidget] = [
            charter_section(saga, covenant, p, self.run),
            clauses_section(
                saga,
                covenant,
                p,
                self.run,
                lambda title, subtitle, markup: self.inspect(title, subtitle, markup),
            ),
        ]
        if covenant.detail == FULL:
            parts += self._own_charter(covenant)
        return scrolling_page(p, *parts)

    def _own_charter(self, covenant: Covenant) -> list[QWidget]:
        """The covenant's own charter, for the Chartered Town Boon: its
        lords and terms, as a town's Charter chapter shows them; and the
        towns it charters, for the Charter Lord Hook."""
        p, saga = self.p, self.saga
        found: list[QWidget] = []
        if town_charter.has_boon_hook(covenant, town_charter.CHARTERED_TOWN):
            charter = town_charter.charter_of(covenant)
            ops = town_charter.covenant_charter_ops(saga, covenant)
            grid = town_charter.lords_grid(saga, charter)
            chooser = Chooser()

            def choose(row: int) -> None:
                chooser.choose(row)
                if row in grid.keys:
                    self.inspect(
                        grid.rows[grid.keys.index(row)][0],
                        "Charter lord",
                        town_charter.lord_info(saga, charter, row),
                    )

            found.append(
                section(
                    "Charter " + town_charter.lords_title(saga, charter),
                    p,
                    table_view(grid.table(), p, choose)
                    if grid.rows
                    else _none(grid.empty, p),
                    buttons=verb_buttons(
                        ops[COV_CHARTER_LORDS_SECTION], chooser, self.run, p
                    ),
                )
            )
            ticks = []
            for column in town_charter.terms_columns(saga, charter):
                block = TextBlock(column, p)
                block.setFont(serif(12.5))
                ticks.append(block)
            terms = ops[COV_CHARTER_TERMS_SECTION].edit
            found.append(
                section(
                    "Charter Terms",
                    p,
                    fact_grid(town_charter.terms_facts(saga, charter), p, 3),
                    side_by_side(*ticks),
                    edits=(
                        {"Edit Terms": lambda: self.run(terms(0))}
                        if terms is not None
                        else None
                    ),
                )
            )
        if town_charter.has_boon_hook(covenant, town_charter.CHARTER_LORD):
            found.append(
                section(
                    "Towns It Charters",
                    p,
                    TextBlock(town_charter.chartered_towns_text(saga, covenant), p),
                )
            )
        return found

    def _sketch(self, covenant: Covenant) -> QWidget:
        """A Line or Sketch covenant: who it is, its magi and their votes,
        What Matters, and its attitude to each player covenant, the favours
        owed, its links and its connections. A Line covenant has no magi or What Matters."""
        p, saga = self.p, self.saga
        ops = world_forms.covenant_ops(saga, covenant)
        summary = covenant.summary.strip()
        parts: list[QWidget] = [
            arms_section(covenant, p, self.run),
            section(
                "In the Saga",
                p,
                prose(summary, p)
                if summary
                else _none("Not written yet: edit the covenant to say.", p),
            ),
        ]
        if covenant.detail != LINE:

            def show(index: int) -> None:
                magus = world.covenant_magi(saga, covenant)[index]
                self.inspect(
                    magus.name,
                    f"{magus.detail} · {covenant.name}",
                    cs.statblock_text(saga, magus),
                )

            parts.append(
                table_section(
                    world_forms.magi_title(saga, covenant),
                    world_forms.magi_table(saga, covenant),
                    ops[world_forms.MAGI_SECTION],
                    p,
                    self.run,
                    empty="No magi written down.",
                    on_choose=show,
                )
            )
            parts.append(
                section(
                    "What Matters",
                    p,
                    TextBlock(world_forms.what_matters_text(covenant), p),
                    edits={
                        "Edit": lambda: self.run(
                            world_forms.what_matters_form(covenant)
                        )
                    },
                )
            )
        parts += relations(saga, covenant, p, self.run)
        parts.append(connections_section(saga, covenant, p, self.run))
        parts.append(
            text(
                "A sketch covenant counts toward its Tribunal's roster and votes. "
                "It plays no seasons, and the yearly step leaves it alone, until "
                "it is promoted.",
                p["dim"],
                serif(12, italic=True),
                wrap=True,
            )
        )
        return scrolling_page(p, *parts)

    def _boon_hook_card(
        self, covenant: Covenant, card: cvs.BoonHookCard, colour: str
    ) -> ClickableCard:
        p = self.p
        frame = ClickableCard(p, edge=colour, pad=10)
        top = QHBoxLayout()
        top.addWidget(
            text(card.name, p["foreground"], serif(13.5, bold=True), wrap=True), 1
        )
        top.addWidget(badge(card.tier, p["dim"] if card.tier == "Free" else colour, p))
        frame.column.addLayout(top)
        words = card.category or "—"
        if card.note:
            words += f"  ·  {card.note}"
        frame.column.addWidget(text(words, p["label"], serif(10.5, caps=True)))
        frame.clicked = lambda: self.inspect(
            card.name,
            f"{card.tier}  ·  {card.category}" if card.category else card.tier,
            boon_hook_text.boon_hook_info_text(covenant, card.index),
        )
        return frame

    def _people(self) -> QWidget:
        """Each group of people (every group, so each can be added to),
        ending in a New card for one more of its kind."""
        p, saga = self.p, self.saga
        parts: list[QWidget] = []
        for title, people in ov.people_groups(saga, self.covenant_id, every=True):
            cards = [
                person_card(saga, character, p, self.open_character)
                for character in people
            ]
            kind, words = ov.NEW_PERSON[title]
            new = (
                self.placer.new_card(
                    "People",
                    words,
                    creation_forms.new_character_form(saga, self.covenant_id, kind),
                )
                if self.placer
                else None
            )
            listed = with_new(cards, new)
            if listed:
                parts += [
                    chapter_title(f"{title} ({len(people)})", p),
                    card_grid(listed),
                ]
        familiars = fs.familiars_in(saga, self.covenant_id)
        if familiars:
            cards = [
                familiar_card(fs.familiar_card(saga, f), p, self.open_familiar)
                for f in familiars
            ]
            parts += [
                chapter_title(f"Familiars ({len(familiars)})", p),
                card_grid(cards),
            ]
        if not parts:
            parts.append(_none("No one yet.", p))
        return scrolling_page(p, *parts)

    def _covenfolk(self, covenant: Covenant) -> QWidget:
        """Loyalty and how it is reached, the household's numbers, and a
        table for each kind of inhabitant."""
        p, saga = self.p, self.saga
        loyalty = cvs.loyalty(saga, covenant)
        standing = Card(p)
        standing.column.addWidget(text("Loyalty", p["heading"], serif(13, bold=True)))
        standing.column.addWidget(
            fact_grid(
                [
                    Fact("Governance", loyalty.governance),
                    Fact("Base Points", str(loyalty.base)),
                    Fact("Modifiers", f"{loyalty.modifiers:+d}"),
                    Fact("Loyalty Points", str(loyalty.points)),
                    Fact("Prevailing Score", f"{loyalty.score:+d}"),
                ],
                p,
                3,
            )
        )
        modifiers = Card(p)
        _title, situation = inh.loyalty_right_text(saga, covenant).split("\n", 1)
        modifiers.column.addWidget(
            text("Situational Modifiers", p["heading"], serif(13, bold=True))
        )
        modifiers.column.addWidget(label_values(situation, p))
        household = Card(p)
        household.column.addWidget(label_values(inh.population_text(saga, covenant), p))
        left, right = inh.misc_text(covenant)
        household.column.addWidget(
            side_by_side(label_values(left, p), label_values(right, p), spacing=18)
        )
        run = self.run
        parts: list[QWidget] = [
            section(
                "Loyalty",
                p,
                side_by_side(standing, modifiers, spacing=14),
                edits={
                    "Edit": lambda: run(inhabitant_forms.loyalty_form(saga, covenant))
                },
            ),
            section(
                "The Household",
                p,
                household,
                edits={
                    "Edit Inhabitants": lambda: run(
                        inhabitant_forms.population_form(saga, covenant)
                    ),
                    "Edit Miscellaneous": lambda: run(
                        inhabitant_forms.misc_form(covenant)
                    ),
                },
            ),
        ]
        parts += self._every_kind(
            cvs.inhabitant_groups(saga, covenant),
            {kind: inh.KIND_TITLES[kind] for kind in INHABITANT_KINDS},
            lambda kind: inhabitant_forms.inhabitant_ops(saga, covenant, kind),
        )
        return scrolling_page(p, *parts)

    def _groups(
        self,
        groups: Sequence[cvs.Group],
        ops: Callable[[str], SectionOps | None] = lambda _kind: None,
        more: Callable[[str], Sequence[RowVerb]] = lambda _kind: (),
    ) -> list[QWidget]:
        """Each group's table under its title, with the buttons of its
        `ops` and `more` (by its kind) beside the title; choosing a row
        shows its details in the inspector, and is the row they act on."""
        return [
            self._group(group, ops(group.kind), more(group.kind)) for group in groups
        ]

    def _group(
        self, group: cvs.Group, ops: SectionOps | None, more: Sequence[RowVerb] = ()
    ) -> QWidget:
        p = self.p
        chooser = Chooser()

        def show(row: int) -> None:
            chooser.choose(row)
            if 0 <= row < len(group.details):
                self.inspect(
                    group.table.rows[row][0],
                    group.title.split(" (")[0],
                    group.details[row],
                )

        buttons = (
            verb_buttons(ops, chooser, self.run, p, more=more)
            if ops is not None
            else []
        )
        if not group.table.rows:
            return section(group.title, p, _none("None recorded.", p), buttons=buttons)
        view = cells_table(group.table.columns, group.table.rows, p, show)
        self.tables[group.kind] = view
        return section(group.title, p, view, buttons=buttons)

    def _every_kind(
        self,
        groups: Sequence[cvs.Group],
        titles: dict[str, str],
        ops: Callable[[str], SectionOps],
        more: Callable[[str], Sequence[RowVerb]] = lambda _kind: (),
    ) -> list[QWidget]:
        """A section for every kind in `titles`, those with no rows too, so
        each can be added to."""
        by_kind = {group.kind: group for group in groups}
        return self._groups(
            [
                by_kind.get(kind)
                or cvs.Group(kind, f"{title} (0)", cvs.Table([], []), [])
                for kind, title in titles.items()
            ],
            ops,
            more,
        )

    def _labs(self, labs: Sequence[ov.LabCard]) -> QWidget:
        """The laboratories as cards, ending in a New Laboratory card."""
        p = self.p
        cards = [lab_card(figures, p, self.open_laboratory) for figures in labs]
        listed = with_new(
            cards, self.placer.new_card("Laboratories") if self.placer else None
        )
        return scrolling_page(
            p,
            chapter_title(f"Laboratories ({len(labs)})", p),
            card_grid(listed, 2) if listed else _none("No laboratories yet.", p),
        )

    def _possessions(self, covenant: Covenant) -> QWidget:
        saga = self.saga

        def more(kind: str) -> list[RowVerb]:
            if kind == "vis_store":
                return [
                    give_verb(saga, giving.VIS, covenant, lambda: vis.held(covenant))
                ]
            if kind not in giving.GEAR_KINDS:
                return []
            return [
                give_verb(
                    saga,
                    giving.GEAR,
                    covenant,
                    lambda: [
                        e.record for e in pos.entries_for_kind(saga, covenant, kind)
                    ],
                )
            ]

        return scrolling_page(
            self.p,
            # The ships are ledger entries of their own (gui.ships).
            ships_section(saga, covenant, self.p, self.run, self.inspect),
            *self._every_kind(
                cvs.possession_groups(saga, covenant),
                {
                    kind: pos.KIND_TITLES[kind]
                    for kind in POSSESSION_KINDS
                    if kind != "ship"
                },
                lambda kind: possession_forms.possession_ops(saga, covenant, kind),
                more,
            ),
            device_section(
                saga, "covenant", covenant.id, self.p, self.run, self.inspect
            ),
        )

    def _treasury(self, covenant: Covenant) -> QWidget:
        """The year's account as a ledger: what comes in against what goes
        out and the balance, the covenant's wealth, then the tables."""
        p = self.p
        figures = cvs.treasury(self.saga, covenant)
        account = []
        for caption, value, colour in (
            ("Annual Income", f"{figures.income} £", p["text-success"]),
            ("Annual Expense", f"{figures.expenditure} £", p["text-error"]),
            (
                "Surplus" if figures.balance >= 0 else "Deficit",
                f"{figures.balance:+d} £",
                p["text-success"] if figures.balance >= 0 else p["text-error"],
            ),
        ):
            card = Card(p, pad=12)
            number = text(value, colour, serif(24, bold=True))
            number.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label = text(caption, p["label"], serif(10.5, caps=True))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.column.addWidget(number)
            card.column.addWidget(label)
            account.append(card)
        parts: list[QWidget] = [
            chapter_title(f"The Year's Account  ·  {self.saga.current_year}", p),
            card_grid(account, 3),
        ]
        if figures.status:
            parts.append(text(figures.status, p["text-error"], serif(13), wrap=True))
        saga = self.saga
        parts.append(
            section(
                "Wealth",
                p,
                fact_grid(figures.wealth, p, 6),
                edits={"Edit": lambda: self.run(covenant_forms.wealth_form(covenant))},
                buttons=self.placer.buttons("Wealth") if self.placer else [],
            )
        )

        def ops(kind: str) -> SectionOps:
            if kind == "income":
                return covenant_forms.income_ops(covenant)
            return covenant_forms.economics_row_ops(saga, covenant, kind)

        def more(kind: str) -> list[RowVerb]:
            if kind != "income" or not menu_forms.lives_at(
                "improve", NodeKind.COVENANT, "Income"
            ):
                return []
            sources = covenant.economics.income_sources
            return [
                (
                    "Improve",
                    "income",
                    lambda row: menu_forms.improve_form(saga, sources[row], covenant),
                    lambda _row: True,
                )
            ]

        parts += self._groups(figures.groups, ops, more)
        return scrolling_page(p, *parts)

    def _manors(self, covenant: Covenant) -> QWidget:
        """The covenant's manors, kennels, mews and stables, under their
        check beside its income, as a lord's Manors chapter shows them."""
        saga = self.saga
        return KindChapters(
            saga,
            manors.manors_of(covenant),
            self.p,
            self.run,
            manors.covenant_ops(saga, covenant),
            self.codex,
        ).chapter(manors.COVENANT_TAB)

    def _projects(self, covenant: Covenant) -> QWidget:
        """The covenant's Hermetic Projects, and the shown one's tower,
        works and craft devices (hermetic_projects.py)."""
        saga = self.saga
        return KindChapters(
            saga,
            manors.manors_of(covenant),
            self.p,
            self.run,
            hermetic_projects.covenant_ops(saga, covenant),
            self.codex,
        ).chapter(hermetic_projects.projects_tab(saga, covenant))

    def _library(self, covenant: Covenant) -> QWidget:
        """The books on their shelves, a summa as tall as its level."""
        p, saga = self.p, self.saga
        books = library.books_in_covenant(saga, covenant)
        chooser = Chooser()
        ops = library_forms.book_ops(
            saga,
            lambda: library.books_in_covenant(saga, covenant),
            bk.owner_value("covenant", covenant.id),
        )

        def show(spine: cvs.Spine) -> None:
            book = spine.book
            chooser.choose(next(i for i, b in enumerate(books) if b is book))
            symbol = artwork.art_symbol(spine.art) if spine.art else None
            self.inspect(
                book.name,
                book.type + (f"  ·  {spine.subject}" if spine.subject else ""),
                bk.detail_text(saga, book),
                symbol,
            )

        parts: list[QWidget] = [
            section(
                f"Library ({len(books)})",
                p,
                *([] if books else [_none("No books yet.", p)]),
                buttons=[
                    *verb_buttons(
                        ops,
                        chooser,
                        self.run,
                        p,
                        more=[
                            give_verb(
                                saga,
                                giving.BOOK,
                                covenant,
                                lambda: library.books_in_covenant(saga, covenant),
                            )
                        ],
                    ),
                    *(
                        [
                            edit_button(
                                "Change Owner",
                                p,
                                lambda: self.run(
                                    library_forms.change_owner(
                                        saga, library.books_in_covenant(saga, covenant)
                                    )
                                ),
                                "library",
                            )
                        ]
                        if len(books) > 1
                        else []
                    ),
                    *(self.placer.buttons("Library") if self.placer else []),
                ],
            )
        ]
        for title, spines in cvs.shelves(saga, covenant):
            parts += [
                chapter_title(f"{title} ({len(spines)})", p),
                shelf(spines, p, show),
            ]
        return scrolling_page(p, *parts)

    def _seasons(self) -> QWidget:
        p, saga = self.p, self.saga
        people = [
            c
            for _title, group in ov.people_groups(saga, self.covenant_id)
            for c in group
        ]
        self.timeline = SeasonTimeline(
            ov.timeline(saga, people),
            p,
            lambda name, when, season: self.codex.inspect(
                name, when, season_text(season)
            ),
        )
        covenant = saga.covenant(self.covenant_id)
        plans = (
            [
                self._season_list(covenant, kind, title)
                for kind, title in seasons.SEASON_KINDS
            ]
            if covenant is not None
            else []
        )
        ahead = (
            [ahead_section(saga, p, self.run, self.inspect, covenant)]
            if covenant is not None
            else []
        )
        return scrolling_page(
            p,
            *ahead,
            chapter_title(
                f"Seasons  ·  now {saga.current_season} {saga.current_year}",
                p,
                emblem=Medallion(
                    saga, saga.current_season, saga.current_year, p, radius=20, now=True
                ),
            ),
            *plans,
            legend(p),
            self.timeline,
        )

    def _season_list(self, covenant: Covenant, kind: str, title: str) -> QWidget:
        """The covenant's people of `kind` and what each has planned this
        season, with Plan and Clear for the one chosen."""
        p, saga = self.p, self.saga
        people = seasons.covenant_people(saga, covenant, kind)
        chooser = Chooser()

        def show(index: int) -> None:
            chooser.choose(index)
            self.inspect(
                people[index].name,
                f"{saga.current_season} {saga.current_year}",
                seasons.season_info_text(saga, people[index]),
            )

        table = seasons.season_table(saga, covenant, kind)
        return section(
            seasons.season_title(saga, covenant, kind, title),
            p,
            table_view(table, p, show) if table.rows else _none("Nobody here.", p),
            buttons=verb_buttons(
                season_forms.covenant_season_ops(saga, covenant, kind),
                chooser,
                self.run,
                p,
                nouns=season_forms.COVENANT_NOUNS,
            ),
        )

    def _diary(self, covenant: Covenant) -> QWidget:
        p = self.p
        chooser = Chooser()
        ops = diary_forms.covenant_diary_ops(self.saga, covenant)
        cards: list[ClickableCard] = []
        entries = cvs.diary_cards(covenant.diary)
        for entry in entries:
            card = ClickableCard(p, pad=10)
            top = QHBoxLayout()
            top.addWidget(text(entry.when, p["label"], serif(11.5, italic=True)), 1)
            if entry.status:
                top.addWidget(
                    badge(
                        entry.status,
                        p["text-warning"] if entry.status == "Open" else p["dim"],
                        p,
                    )
                )
            card.column.addLayout(top)
            card.column.addWidget(
                text(
                    entry.name or "—",
                    p["foreground"],
                    serif(13.5, bold=True),
                    wrap=True,
                )
            )
            details = "  ·  ".join(
                part for part in (entry.category, entry.amounts) if part
            )
            if details:
                card.column.addWidget(text(details, p["label"], wrap=True))
            card.clicked = lambda index=entry.index, name=entry.name: self.inspect(
                name, "Diary", cov_diary.info_text(covenant, index)
            )
            cards.append(card)
        _choose_cards_by(cards, [entry.index for entry in entries], chooser)
        return scrolling_page(
            p,
            section(
                f"Diary ({len(cards)})",
                p,
                card_grid(cards, 2) if cards else _none("Nothing written yet.", p),
                buttons=verb_buttons(ops, chooser, self.run, p),
            ),
        )

    def _build(self, covenant: Covenant) -> QWidget:
        p, saga = self.p, self.saga
        table, counted = Card(p), Card(p)
        table.column.addWidget(columns_text(cov_build.table_text(saga, covenant), p))
        counted.column.addWidget(
            text("What's Counted", p["heading"], serif(13, bold=True))
        )
        counted.column.addWidget(columns_text(cov_build.items_text(saga, covenant), p))
        return scrolling_page(
            p,
            chapter_title(cov_build.title(saga, covenant), p),
            side_by_side(table, counted, spacing=14),
        )
