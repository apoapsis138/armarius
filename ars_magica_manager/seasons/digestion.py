"""Applying a season of a Philosophic Alchemy digestion (The Mysteries
Revised Edition pp. 40-41; the rules are rules.tmre_alchemy's): each
season the magus tends it, its Lab Total less his days away; more than
twenty days out of the laboratory, or experimenting, spoil it; finished,
its vis goes to the pool it was settled for, or its spaces open the
device it was settled in."""

from __future__ import annotations

from collections.abc import Sequence

from ..models import (
    DIGEST_SPACES,
    SEASONS,
    Character,
    DiaryEntry,
    Digestion,
    Saga,
    SeasonPlan,
    SeasonRecordLine,
)
from ..rules import activities as rules
from ..rules import book_seasons as bs
from ..rules import lab_seasons
from ..rules import tmre_alchemy as alchemy

#: Work done in the laboratory besides lab work: reading, studying vis
#: (TMRE p. 41), and teaching, training or writing there (`in_lab`).
_STUDY = (rules.READ, rules.VIS_STUDY)
_IN_LAB = (rules.TEACH, rules.TAUGHT, rules.TRAINED, *bs.SHEET_ACTIVITIES)
#: A month lost to distractions counts as this many days away.
_MONTH = 30


def days_out(plan: SeasonPlan | None) -> int | None:
    """Days the magus spends away from his laboratory in the season (None:
    the season takes him out of it altogether). A season with nothing
    planned is spent there."""
    if plan is None:
        return 0
    if plan.lab_id:
        return max(0, plan.days_away)
    if plan.activity in _STUDY or (plan.activity in _IN_LAB and plan.in_lab):
        return _MONTH * max(0, plan.months_lost)
    return None


def _line(magus: Character, what: str, result: str) -> SeasonRecordLine:
    return SeasonRecordLine(
        magus.id, magus.name, magus.covenant_id, "Philosophic Alchemy", what, result
    )


def _what(digestion: Digestion) -> str:
    if digestion.product == DIGEST_SPACES:
        return "Digestion (open spaces)"
    return f"Digestion ({digestion.form or 'Vim'} vis)"


def _diary(saga: Saga, magus: Character, digestion: Digestion, text: str) -> None:
    entry = DiaryEntry(saga.current_year, saga.current_season, _what(digestion), text)
    magus.diary.append(entry)
    lab_ = saga.laboratory(digestion.lab_id) if digestion.lab_id else None
    if lab_ is not None:
        lab_.diary.append(
            DiaryEntry(
                saga.current_year,
                saga.current_season,
                _what(digestion),
                f"{magus.name}: {text}",
                activity="Extract Vis",
            )
        )


def _finish(saga: Saga, magus: Character, digestion: Digestion) -> str:
    """The yield of a finished digestion, delivered; what it gave."""
    pawns = alchemy.digestion_yield(digestion, magus)
    lowest = min(digestion.totals)
    if digestion.product == DIGEST_SPACES:
        device = next(
            (d for d in saga.enchanted_devices if d.id == digestion.device_id), None
        )
        if device is None:
            return f"Lab Total {lowest}: {pawns} open space(s), but the device is gone."
        alchemy.open_spaces(device, pawns, digestion.extra_room)
        return (
            f"Lab Total {lowest}: {pawns} space(s) of {device.name} opened, as "
            f"{alchemy.spaces_text(digestion.extra_room)}."
        )
    plan = SeasonPlan(
        magus.id,
        saga.current_year,
        saga.current_season,
        lab_seasons.EXTRACT,
        lab_id=digestion.lab_id,
        vis_from=digestion.vis_from,
    )
    pool = lab_seasons.vis_pool(saga, magus, plan)
    art = digestion.form or "Vim"
    if pawns:
        pool[art.lower()] = pool.get(art.lower(), 0) + pawns
    return (
        f"Lab Total {lowest}: {pawns} pawn(s) of {art} vis to "
        f"{lab_seasons.whose_vis(magus, plan)} raw vis."
    )


def _tend(
    saga: Saga, magus: Character, digestion: Digestion, plan: SeasonPlan | None
) -> SeasonRecordLine:
    """The season's work on one digestion."""
    season, year = saga.current_season, saga.current_year
    days = days_out(plan)
    why = ""
    if days is None:
        why = "the season took him out of the laboratory"
    elif alchemy.spoils(days):
        why = f"{days} days away (more than {alchemy.MOST_DAYS_AWAY})"
    elif plan is not None and plan.experimenting:
        why = "he experimented while it digested"
    found: list[str] = []
    work = None
    if not why:
        found, work = lab_seasons.digestion_season(
            saga, magus, digestion, season, year, days or 0
        )
        if work is None:
            why = found[0] if found else "it could not be worked out"
    if why or work is None:
        alchemy.abandon(magus)
        text = f"Spoiled and abandoned: {why} ({alchemy.PHILOSOPHIC_SOURCE})."
        _diary(saga, magus, digestion, text)
        return _line(magus, _what(digestion), text)
    total = max(0, int(work.lab_total.total))
    digestion.totals.append(total)
    if alchemy.finished(digestion):
        text = _finish(saga, magus, digestion)
        alchemy.abandon(magus)
    else:
        text = (
            f"Season {len(digestion.totals)} of {digestion.seasons}: Lab Total "
            f"{total} (the lowest of the {digestion.seasons} gives the yield)."
        )
    _diary(saga, magus, digestion, text)
    return _line(magus, _what(digestion), text)


def apply_digestions(
    saga: Saga, worked: Sequence[rules.Outcome]
) -> list[SeasonRecordLine]:
    """The current season of every digestion running, as its plans were
    worked out (`worked`): a line of the season's record for each."""
    plans = {o.character_id: o.plan for o in worked}
    lines: list[SeasonRecordLine] = []
    now = (saga.current_year, SEASONS.index(saga.current_season))
    for magus in saga.characters:
        digestion = alchemy.digestion_in(magus, saga.current_season, saga.current_year)
        if digestion is not None:
            lines.append(_tend(saga, magus, digestion, plans.get(magus.id)))
            continue
        stale = magus.alchemy.digestion if magus.alchemy is not None else None
        # Its seasons went by unapplied (the date was set past them).
        if (
            stale is not None
            and stale.season in SEASONS
            and (stale.year, SEASONS.index(stale.season)) < now
        ):
            alchemy.abandon(magus)
            text = "Abandoned: its seasons went by untended."
            _diary(saga, magus, stale, text)
            lines.append(_line(magus, _what(stale), text))
    return lines
