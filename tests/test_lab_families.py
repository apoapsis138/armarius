"""Lab work by family (STORY-2367): lab_seasons.FAMILIES says how each
family's season is worked out, lab_apply.FAMILY_APPLIERS how it changes the
saga, and every lab season goes through them by its activity."""

import pytest

from ars_magica_manager.models import Character, Laboratory, Saga, SeasonPlan
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import lab, lab_seasons
from ars_magica_manager.rules.lab_work import LabWork
from ars_magica_manager.seasons import lab_apply


def test_each_lab_activity_is_in_one_family_at_most() -> None:
    seen: dict[str, str] = {}
    for family in lab_seasons.FAMILIES:
        for activity in family.activities:
            assert activity not in seen, (activity, seen.get(activity), family.name)
            seen[activity] = family.name
    assert set(seen) <= set(lab_seasons.LAB_ACTIVITIES)


def test_every_family_has_an_applier() -> None:
    assert {f.name for f in lab_seasons.FAMILIES} == set(lab_apply.FAMILY_APPLIERS)


def test_activities_outside_the_families_belong_to_none() -> None:
    for activity in (
        lab_seasons.INVENT,
        lab_seasons.LAB_TEXT,
        lab_seasons.EXTRACT,
        lab_seasons.LONGEVITY,
    ):
        assert lab_seasons.family_of(activity) is None


def _one_of_each() -> list[tuple[str, str]]:
    return [(family.name, min(family.activities)) for family in lab_seasons.FAMILIES]


@pytest.mark.parametrize(("family", "activity"), _one_of_each())
def test_a_season_is_worked_out_by_its_family(
    monkeypatch: pytest.MonkeyPatch, family: str, activity: str
) -> None:
    """lab_seasons._work hands the season to its family's work, once the
    checks every lab season shares are passed."""
    magus = Character(id="m", name="Aldo", type="magus", covenant_id="c")
    laboratory = Laboratory(id="l", covenant_id="c", name="Tower", owner_id="m")
    saga = Saga(id="s", name="S", characters=[magus], laboratories=[laboratory])
    plan = SeasonPlan(
        character_id="m", year=1220, season="Spring", activity=activity, lab_id="l"
    )
    called: list[str] = []
    found = lab_seasons.family_of(activity)
    assert found is not None and found.name == family
    patched = lab_seasons.LabFamily(
        found.name,
        found.activities,
        lambda *_args: (called.append(found.name), (["stop"], None))[1],
    )
    monkeypatch.setitem(lab_seasons._FAMILY_OF, activity, patched)
    assert lab_seasons.work(saga, magus, plan)[0] == ["stop"]
    assert called == [family]


@pytest.mark.parametrize(("family", "activity"), _one_of_each())
def test_a_season_is_applied_by_its_family(
    monkeypatch: pytest.MonkeyPatch, family: str, activity: str
) -> None:
    """lab_apply hands the season to its family's applier, between what
    every lab season does: the lab's Diary gets its line either way."""
    magus = Character(id="m", name="Aldo", type="magus", covenant_id="c")
    laboratory = Laboratory(id="l", covenant_id="c", name="Tower", owner_id="m")
    saga = Saga(id="s", name="S", characters=[magus], laboratories=[laboratory])
    plan = SeasonPlan(
        character_id="m", year=1220, season="Spring", activity=activity, lab_id="l"
    )
    work = LabWork(spell=None, lab_total=lab.LabTotal(total=0, lines=[]), level=0)
    called: list[str] = []
    monkeypatch.setitem(
        lab_apply.FAMILY_APPLIERS, family, lambda *_args: called.append(family)
    )
    outcome = rules.Outcome(character_id="m", plan=plan, activity=None)
    outcome.lab_work = work
    lab_apply.apply_lab_work(saga, magus, outcome)
    assert called == [family]
    assert len(laboratory.diary) == 1
