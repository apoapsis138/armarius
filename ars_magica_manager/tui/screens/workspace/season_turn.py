"""WorkspaceScreen's season actions: advancing the saga a season, and setting
its date."""

from __future__ import annotations

from typing import Any

from .... import storage
from ....actions import (
    NodeKind,
)
from ....forms import advance as advance_forms
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
            self.app.push_screen(SeasonSummaryScreen(saga, played.advanced.record))
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
