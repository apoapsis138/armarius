"""Undo Last Season (undo_season.py): the saga put back to the backup
taken before the last advance, whole, one advance at a time."""

from __future__ import annotations

from ars_magica_manager import storage, undo_season
from ars_magica_manager.commands import Confirm, Refuse
from ars_magica_manager.models import Character, Saga


def _saga() -> Saga:
    saga = Saga(id="u", name="Undo")
    saga.characters.append(Character(id="mag1", name="Leandro", type="magus"))
    storage.save_saga(saga)
    return saga


def _advance(saga: Saga, season: str, year: int | None = None) -> None:
    """As Advance Season does: backed up, played (here only the date moves
    and Leandro's season leaves a mark), then the after-copy kept."""
    storage.backup_saga(saga)
    saga.current_season = season
    if year is not None:
        saga.current_year = year
    saga.characters[0].name = f"Leandro ({season})"
    storage.remember_after(saga)
    storage.save_saga(saga)


def test_nothing_to_undo_before_any_advance() -> None:
    saga = _saga()
    assert undo_season.offer(saga) is None
    assert isinstance(undo_season.undo_command(saga), Refuse)


def test_an_advance_is_undone_whole_and_the_saga_as_it_was_is_kept() -> None:
    saga = _saga()
    _advance(saga, "Summer")
    saga.characters.append(Character(id="grog", name="Hob", type="grog"))
    found = undo_season.offer(saga)
    assert found is not None
    assert (found.back_to, found.now) == ("Spring 1220", "Summer 1220")
    assert found.lost == ("Hob",)  # changed since the advance, by name
    asked = undo_season.undo_command(saga)
    assert isinstance(asked, Confirm) and "Hob" in asked.question
    done = asked.apply()
    assert isinstance(done, undo_season.Undone)
    assert saga.current_season == "Spring" and saga.characters[0].name == "Leandro"
    assert [c.id for c in saga.characters] == ["mag1"]
    assert storage.undone_path("u").exists()
    assert undo_season.offer(saga) is None  # the one advance is used up


def test_one_advance_at_a_time_as_far_as_the_backups_go() -> None:
    saga = _saga()
    _advance(saga, "Summer")
    _advance(saga, "Autumn")
    first = undo_season.offer(saga)
    assert first is not None and first.back_to == "Summer 1220"
    undo_season.undo(saga, first)
    second = undo_season.offer(saga)
    assert second is not None and second.back_to == "Spring 1220"


def test_a_set_date_since_the_advance_means_nothing_to_undo() -> None:
    saga = _saga()
    _advance(saga, "Summer")
    saga.current_season = "Winter"  # Set Date
    assert undo_season.offer(saga) is None


def test_an_advance_cancelled_part_way_is_passed_over() -> None:
    saga = _saga()
    _advance(saga, "Summer")
    storage.backup_saga(saga)  # a second advance, cancelled before its end
    found = undo_season.offer(saga)
    assert found is not None and found.back_to == "Spring 1220"


def test_a_downtime_run_undoes_as_one() -> None:
    saga = _saga()
    storage.backup_saga(saga)  # the run's one backup
    for season in ("Summer", "Autumn", "Winter"):
        saga.current_season = season
    storage.remember_after(saga)  # at the run's end
    found = undo_season.offer(saga)
    assert found is not None and found.back_to == "Spring 1220"
    undo_season.undo(saga, found)
    assert saga.current_season == "Spring"
