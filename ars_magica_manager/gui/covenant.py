"""The desktop covenant page, read-only, in the Codex layout: a header
with the name, its Tribunal and season, the Aegis and living conditions,
and the aura and Loyalty as seals; then chapters for its charter (the
description, Boons and Hooks, Reputations), its people, covenfolk,
laboratories, possessions, treasury, library, seasons, Diary and Build
Points, with the inspector beside them.

The characters who belong to no covenant get the same page with only
their people, laboratories and seasons.

What it says comes from the shared core (covenant_sheet.py and
saga_overview.py), as the terminal's covenant sheet does.
"""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QTableView, QVBoxLayout, QWidget

from .. import artwork, boon_hook_text, catalog
from .. import books as bk
from .. import covenant_build as cov_build
from .. import covenant_diary as cov_diary
from .. import covenant_sheet as cvs
from .. import familiar_sheet as fs
from .. import inhabitants as inh
from .. import saga_overview as ov
from ..character_sheet import Fact
from ..covenants import boon_hook_problems
from ..models import Covenant, Saga
from .character_sheet import columns_text, label_values, side_by_side
from .figures import Seal, aura_seal, fact_grid, prose, shelf, trait_list
from .pages import Open, card_grid, card_title, familiar_card, symbol_label
from .themes import Palette
from .timeline import SeasonTimeline, legend, season_text
from .widgets import (
    Card,
    ClickableCard,
    Codex,
    badge,
    cells_table,
    chapter_title,
    display_name,
    scrolling_page,
    serif,
    text,
)


def _none(words: str, p: Palette) -> QLabel:
    return text(words, p["dim"], serif(12.5, italic=True))


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
    ) -> None:
        super().__init__()
        self.saga, self.p = saga, p
        self.open_character, self.open_laboratory = open_character, open_laboratory
        self.open_familiar = open_familiar
        self.covenant_id = covenant_id
        #: Each inhabitant, possession and treasury table, by its kind.
        self.tables: dict[str, QTableView] = {}
        covenant = saga.covenant(covenant_id)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 12, 12, 8)
        outer.setSpacing(10)
        outer.addWidget(self._header(covenant))
        self.codex = Codex(p)
        self.inspector = self.codex.inspector
        labs = ov.lab_cards(saga, covenant_id)
        chapters = []
        if covenant is not None:
            chapters.append(("Charter", "lab_text", lambda: self._charter(covenant)))
        chapters.append(("People", "character", self._people))
        if covenant is not None:
            chapters.append(("Covenfolk", "players", lambda: self._covenfolk(covenant)))
        if covenant is not None or labs:
            chapters.append(("Laboratories", "laboratory", lambda: self._labs(labs)))
        if covenant is not None:
            chapters += [
                ("Possessions", "vis", lambda: self._possessions(covenant)),
                ("Treasury", "income", lambda: self._treasury(covenant)),
                ("Library", "library", lambda: self._library(covenant)),
            ]
        chapters.append(("Seasons", "season", self._seasons))
        if covenant is not None:
            chapters += [
                ("Diary", "year", lambda: self._diary(covenant)),
                ("Build", "covenant", lambda: self._build(covenant)),
            ]
        for name, concept, build in chapters:
            self.codex.add(name, concept, build())
        outer.addWidget(self.codex, 1)

    def chapters(self) -> list[str]:
        return self.codex.chapters()

    def inspect(self, title: str, subtitle: str, markup: str, symbol=None) -> None:
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
        return box

    # Chapters

    def _charter(self, covenant: Covenant) -> QWidget:
        """The description, Reputations, and the Boons beside the Hooks."""
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
            heading = chapter_title(f"{kind}s", p)
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
            for card in cards:
                stack.addWidget(self._boon_hook_card(covenant, card, p[tone]))
            if not cards:
                stack.addWidget(_none(f"No {kind}s.", p))
            stack.addStretch(1)
            columns.append(column)
        parts: list[QWidget] = [
            chapter_title("The Covenant", p),
            prose(covenant.notes.strip(), p),
        ]
        reputations = cvs.reputations(covenant)
        parts += [
            chapter_title(f"Reputations ({len(reputations)})", p),
            trait_list(
                [
                    (r.name + ("" if r.known else " (not known here)"), r.score)
                    for r in reputations
                ],
                p,
            ),
        ]
        problems = boon_hook_problems(
            covenant, catalog.load_covenant_boon_hook_catalog_by_id()
        )
        for problem in problems:
            parts.append(text(problem, p["text-error"], wrap=True))
        parts.append(side_by_side(*columns, spacing=18))
        return scrolling_page(*parts)

    def _boon_hook_card(
        self, covenant: Covenant, card: cvs.BoonHookCard, colour: str
    ) -> QWidget:
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
        p, saga = self.p, self.saga
        parts: list[QWidget] = []
        for title, people in ov.people_groups(saga, self.covenant_id):
            cards = []
            for character in people:
                figures = ov.person_card(saga, character)
                house = artwork.house_symbol(figures.house)
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
                card.clicked = lambda character_id=figures.id: self.open_character(
                    character_id
                )
                cards.append(card)
            parts += [chapter_title(f"{title} ({len(people)})", p), card_grid(cards)]
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
        return scrolling_page(*parts)

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
        household.column.addWidget(
            text("The Household", p["heading"], serif(13, bold=True))
        )
        household.column.addWidget(label_values(inh.population_text(saga, covenant), p))
        left, right = inh.misc_text(covenant)
        household.column.addWidget(
            side_by_side(label_values(left, p), label_values(right, p), spacing=18)
        )
        parts: list[QWidget] = [
            chapter_title("Loyalty", p),
            side_by_side(standing, modifiers, spacing=14),
            household,
        ]
        parts += self._groups(cvs.inhabitant_groups(saga, covenant), "Inhabitant")
        return scrolling_page(*parts)

    def _groups(self, groups: Sequence[cvs.Group], noun: str) -> list[QWidget]:
        """Each group's title over its table; choosing a row shows its
        details in the inspector."""
        p = self.p
        parts: list[QWidget] = []
        for group in groups:

            def show(row: int, group: cvs.Group = group) -> None:
                if 0 <= row < len(group.details):
                    self.inspect(
                        group.table.rows[row][0],
                        group.title.split(" (")[0],
                        group.details[row],
                    )

            view = cells_table(group.table.columns, group.table.rows, p, show)
            self.tables[group.kind] = view
            parts += [chapter_title(group.title, p), view]
        if not parts:
            parts.append(_none(f"No {noun.lower()}s recorded.", p))
        return parts

    def _labs(self, labs: Sequence[ov.LabCard]) -> QWidget:
        p = self.p
        cards = []
        for figures in labs:
            card = ClickableCard(p, pad=14)
            card_title(
                card,
                figures.name,
                figures.subtitle,
                p,
                symbol_label(artwork.icon("laboratory"), p),
            )
            card.column.addWidget(fact_grid(list(figures.facts), p, 4))
            card.clicked = lambda lab_id=figures.id: self.open_laboratory(lab_id)
            cards.append(card)
        return scrolling_page(
            chapter_title(f"Laboratories ({len(labs)})", p),
            card_grid(cards, 2) if cards else _none("No laboratories yet.", p),
        )

    def _possessions(self, covenant: Covenant) -> QWidget:
        return scrolling_page(
            *self._groups(cvs.possession_groups(self.saga, covenant), "Possession")
        )

    def _treasury(self, covenant: Covenant) -> QWidget:
        """The year's account as a ledger: what comes in against what goes
        out and the balance, the covenant's wealth, then the tables."""
        p = self.p
        figures = cvs.treasury(self.saga, covenant)
        account = []
        for caption, value, colour in (
            ("Income a year", f"{figures.income} £", p["text-success"]),
            ("Expenditure a year", f"{figures.expenditure} £", p["text-error"]),
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
        parts += [
            chapter_title("Wealth", p),
            fact_grid(figures.wealth, p, 6),
        ]
        parts += self._groups(figures.groups, "Row")
        return scrolling_page(*parts)

    def _library(self, covenant: Covenant) -> QWidget:
        """The books on their shelves, a summa as tall as its level."""
        p, saga = self.p, self.saga

        def show(spine: cvs.Spine) -> None:
            book = spine.book
            symbol = artwork.art_symbol(spine.art) if spine.art else None
            self.inspect(
                book.name,
                book.type + (f"  ·  {spine.subject}" if spine.subject else ""),
                bk.detail_text(saga, book),
                symbol,
            )

        parts: list[QWidget] = []
        shelves = cvs.shelves(saga, covenant)
        for title, spines in shelves:
            parts += [
                chapter_title(f"{title} ({len(spines)})", p),
                shelf(spines, p, show),
            ]
        if not shelves:
            parts += [chapter_title("Library", p), _none("No books yet.", p)]
        return scrolling_page(*parts)

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
        return scrolling_page(
            chapter_title(
                f"Seasons  ·  now {saga.current_season} {saga.current_year}", p
            ),
            legend(p),
            self.timeline,
        )

    def _diary(self, covenant: Covenant) -> QWidget:
        p = self.p
        cards = []
        for entry in cvs.diary_cards(covenant.diary):
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
        return scrolling_page(
            chapter_title(f"Diary ({len(cards)})", p),
            card_grid(cards, 2) if cards else _none("Nothing written yet.", p),
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
            chapter_title(cov_build.title(saga, covenant), p),
            side_by_side(table, counted, spacing=14),
        )
