"""The supplement seasons' registry (rules/season_work): every activity is
registered once, by one book's module, with its outcome and check."""

from __future__ import annotations

import pytest

from ars_magica_manager import sourcebooks
from ars_magica_manager.models import Character, Saga, SeasonPlan
from ars_magica_manager.rules import activity_groups as groups
from ars_magica_manager.rules import supplement_seasons, supplement_work
from ars_magica_manager.rules.season_work import (
    ACTIVITIES,
    BY_KEY,
    REGISTRY,
    base,
)

#: The activities whose season does something beyond experience.
WITH_OUTCOMES = {
    # Hermetic Numerology and Architecture (The Mysteries Revised).
    "invent_rotes",
    "bind_mystical_structure",
    # The mystic's Spiritual Path quests (The Church p. 22).
    "path_service",
    "path_devotion",
    "path_preaching",
    "path_mission",
    "working_season",
    "tournament",
    "apothecary",
    "workshop_production",
    "make_excellent_item",
    "make_wondrous_item",
    "improve_station",
    "merchant_venture",
    "improve_workshop",
    "produce_remedies",
    "medical_season",
    "create_art",
    "research_formula",
    "attend_university",
    "pilgrimage",
    "care_of_souls",
    "tame_animal",
    "search_lacuna",
    "undergo_initiation",
    "record_lectures",
    "inspeximus",
    "bind_catalog",
    "library_research",
    # Ancient Magic: Ptolemy's measuring of the fixed stars.
    "measure_fixed_stars",
    # Art & Academe's scholars: editing lectures, seeking a post.
    "edit_lectures",
    "seek_post",
    # The Church's season of personal devotion.
    "personal_devotion",
    # Legends of Hermes: Hermetic Viresculture's Stirpes.
    "vitalize_stirps",
    "invigorate_stirps",
    # The Mysteries Revised Edition: making an armillary sphere.
    "make_armillary_sphere",
    # The Mysteries Revised Edition: reinventing the Lesser Elixir.
    "reinvent_lesser_elixir",
    # Transforming Mythic Europe: copying books by magic.
    "copy_books_by_magic",
    # Transforming Mythic Europe: casting a land project's Rituals.
    "shape_land",
    # The Church: an Ordination's examination.
    "ordination",
    # Hermetic Projects: a master mason's season on a Great Tower.
    "build_great_tower",
}


def test_every_activity_is_registered_once() -> None:
    keys = [a.key for a in ACTIVITIES]
    doubled = sorted({k for k in keys if keys.count(k) > 1})
    assert not doubled, f"registered more than once: {doubled}"
    assert set(keys) == set(REGISTRY) == set(BY_KEY)
    # with the scholars' two, personal devotion, and Viresculture's two
    assert len(keys) == 59


def test_registering_a_key_twice_fails() -> None:
    entry = REGISTRY["travel"]
    with pytest.raises(ValueError, match="travel"):
        base.register(entry.activity, entry.outcome)
    assert REGISTRY["travel"] is entry


def test_each_activity_has_its_outcome_and_check() -> None:
    wrong = [
        key
        for key, entry in REGISTRY.items()
        if not callable(entry.outcome)
        or not callable(entry.check)
        or (entry.outcome is not base.experience_only) != (key in WITH_OUTCOMES)
    ]
    assert not wrong, f"outcome missing or unexpected: {wrong}"


def test_each_activity_names_a_known_book_and_group() -> None:
    bad = [
        a.key
        for a in ACTIVITIES
        if not (a.book == sourcebooks.CORE or a.book in sourcebooks.SOURCEBOOKS)
        or a.group not in groups.GROUPS
    ]
    assert not bad, f"unknown book or group: {bad}"


def test_activities_are_in_picker_order() -> None:
    place = {g: i for i, g in enumerate(groups.GROUPS)}
    order = [(place[a.group], a.label.lower()) for a in ACTIVITIES]
    assert order == sorted(order)


def test_old_modules_still_name_the_registry() -> None:
    assert supplement_seasons.ACTIVITIES is ACTIVITIES
    assert supplement_seasons.BY_KEY is BY_KEY
    assert supplement_work.SupplementWork is base.SupplementWork
    assert supplement_work.work is base.work
    assert supplement_work.problems is base.problems


def test_an_unregistered_activity_does_nothing_more() -> None:
    saga = Saga(
        id="s", name="S", characters=[Character(id="c", name="Wulf", type="companion")]
    )
    plan = SeasonPlan("c", 1220, "Spring", "no_such_activity", [])
    character = saga.characters[0]
    assert base.problems(saga, character, plan) == []
    assert base.work(saga, character, plan, None) == base.SupplementWork()


def test_a_check_and_an_outcome_run_from_the_registry() -> None:
    wulf = Character(id="c", name="Wulf", type="companion")
    saga = Saga(id="s", name="S", characters=[wulf])
    plan = SeasonPlan("c", 1220, "Spring", "working_season", [])
    assert base.problems(saga, wulf, plan) == [
        "Choose the Ability the season works with."
    ]
    plan = SeasonPlan("c", 1220, "Spring", "merchant_venture", [], other_modifier=7)
    assert base.work(saga, wulf, plan, None).labor_points == 7
