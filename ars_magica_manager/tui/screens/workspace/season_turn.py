"""WorkspaceScreen's season actions: advancing the saga a season, and setting
its date."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .... import places, storage
from ....actions import (
    NodeKind,
)
from ....commands import Command
from ....forms import advance as advance_forms
from ....forms import downtime as downtime_forms
from ....forms import hunting as hunting_forms
from ....forms import travel as travel_forms
from ....sections import AHEAD_SECTION, COV_AHEAD_SECTION
from ..fields import (
    FieldsDialog,
)
from ..prompts import (
    AdvanceSeasonScreen,
    _date_fields,
)
from ..season_records import SeasonSummaryScreen
from ..steps import run_steps
from .base import (
    _SEASON_SECTIONS,
    WorkspaceBase,
)


class SeasonActions(WorkspaceBase):
    # -- Saga time --

    async def _apply_saga_date(self, season: str, year: int) -> None:
        """Single path for every change to the saga's calendar: store it, then
        refresh everything that inherits it (Header, covenant panel, saga
        summary)."""
        saga = self.saga
        saga.current_season, saga.current_year = season, year
        places.sync(saga)
        storage.save_saga(saga)
        self._update_saga_clock()
        self._refresh_covenant_section("section-cov-info")
        if self.selected_kind == NodeKind.SAGA:
            await self._show_saga_detail()

    def action_advance_season(self) -> None:
        """Advance the saga by one season: the core's steps
        (advance_forms), the first drawn as the Advance Time dialog."""
        saga = self.saga

        def done(end: object) -> None:
            if isinstance(end, advance_forms.Played):
                storage.save_saga(saga)
                self.run_worker(self._season_played(end))

        def handle_result(confirmed: bool | None) -> None:
            if confirmed:
                run_steps(
                    self.app,
                    advance_forms.play_season(saga, storage.backup_saga),
                    done,
                )

        self.app.push_screen(
            AdvanceSeasonScreen(advance_forms.advance_text(saga)), handle_result
        )

    async def _season_played(self, played: advance_forms.Played) -> None:
        """Save the season played out and redraw what it changed: xp
        (scores, casting and lab totals), the Diary, This Season and
        Wealth; then show its results."""
        saga = self.saga
        await self._apply_saga_date(saga.current_season, saga.current_year)
        for section in _SEASON_SECTIONS:
            self._refresh_character_section(section)
        self._refresh_laboratory_section("tab-lab-planning")
        self._refresh_covenant_section("tab-cov-seasons")
        self._refresh_covenant_section("section-cov-ahead")
        if self._seasons_view is not None:
            self._seasons_view.refresh_all()
        if played.advanced.added:
            self._refresh_covenant_section("section-eco-wealth")
        if saga.keep_season_records and played.results:
            self._rebuild_tree()
        if played.results:
            self.app.push_screen(
                SeasonSummaryScreen(saga, played.advanced.record, played.changed)
            )
        self.notify(played.message)

    def action_plan_journey(self) -> None:
        """More's Travel on Ahead: the calculator, from the covenant on
        show. Close records nothing; Set Out writes the travellers' Diaries
        and Fatigue and the arrival on Ahead."""
        on_covenant = self._active_section() == COV_AHEAD_SECTION
        covenant = self.selected_covenant if on_covenant else None

        def done(end: object) -> None:
            self._commit(AHEAD_SECTION, COV_AHEAD_SECTION)
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, travel_forms.travel(self.saga, covenant), done)

    def action_downtime_run(self) -> None:
        """Run Downtime: several seasons at once (forms/downtime.py), each
        kept as it is played; the end tells what the run did."""
        saga = self.saga

        def done(end: object) -> None:
            storage.save_saga(saga)
            self.run_worker(self._downtime_kept(end))

        run_steps(
            self.app, downtime_forms.downtime_form(saga, storage.backup_saga), done
        )

    async def _downtime_kept(self, end: object) -> None:
        """Redraw what a season of the run changed; at the run's end, tell
        what it did."""
        saga = self.saga
        await self._apply_saga_date(saga.current_season, saga.current_year)
        for section in _SEASON_SECTIONS:
            self._refresh_character_section(section)
        self._refresh_laboratory_section("tab-lab-planning")
        self._refresh_covenant_section("tab-cov-seasons")
        if self._seasons_view is not None:
            self._seasons_view.refresh_all()
        self._rebuild_tree()
        if isinstance(end, list) and end:
            self.notify("\n".join(str(line) for line in end), timeout=30)

    def action_set_date(self) -> None:
        saga = self.saga

        async def handle_result(result: dict[str, Any] | None) -> None:
            if result is None:
                return
            season, year = result["season"], result["year"]
            if (season, year) == (saga.current_season, saga.current_year):
                return
            await self._apply_saga_date(season, year)
            self.notify(f"Date set to {season} {year}.")

        self.app.push_screen(
            FieldsDialog(
                "Set the Saga's Date",
                _date_fields(saga.current_season, saga.current_year),
                save_label="Set",
            ),
            handle_result,
        )

    # -- the hunt and Area Lore on the road (Lords of Men, City & Guild) --

    def _on_the_road(self, build: Callable[..., Command]) -> None:
        """Run `build(saga, covenant)` from Ahead, the covenant on show if
        it is a covenant's Ahead."""
        on_covenant = self._active_section() == COV_AHEAD_SECTION
        covenant = self.selected_covenant if on_covenant else None

        def done(end: object) -> None:
            self._commit(AHEAD_SECTION, COV_AHEAD_SECTION)
            if isinstance(end, list) and end:
                self.notify("\n".join(str(line) for line in end))

        run_steps(self.app, build(self.saga, covenant), done)

    def action_hunt_on_journey(self) -> None:
        """More's The Hunt on Ahead: a hunt on the road."""
        self._on_the_road(hunting_forms.hunt_on_journey)

    def action_area_lore_on_journey(self) -> None:
        """More's Area Lore on Ahead: finding the way, an inn, a hunting
        spot."""
        self._on_the_road(hunting_forms.area_lore_on_journey)
