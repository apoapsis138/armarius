"""Study totals (STORY-803)."""

import pytest

from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Book,
    Character,
    Characteristics,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import study
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _student(*virtues: VirtueFlawInstance, **kw) -> Character:
    return Character(
        id="s",
        name="Student",
        type="magus",
        arts={"perdo": ArtScore(xp=art_xp(3))},
        abilities=[Ability("Latin", xp=ability_xp(4))],
        virtues_flaws=list(virtues),
        **kw,
    )


def test_affinity_multiplies_after_the_bonuses_and_rounds_up():
    # The book's example: Affinity with Perdo turns 37 xp into 56.
    student = _student(
        VirtueFlawInstance(vf_id="vf_affinity_with_art", params={"art": "perdo"})
    )
    result = study.season_of_study(
        student, "Perdo", 37, activity="reading", is_art=True
    )
    assert (result.advancement_total, result.xp) == (37, 56)


def test_book_learner_and_poor_student():
    learner = _student(VirtueFlawInstance(vf_id="vf_book_learner"))
    assert (
        study.season_of_study(learner, "Latin", 10, activity="reading", is_art=False).xp
        == 13
    )
    assert (
        study.season_of_study(
            learner, "Latin", 10, activity="teaching", is_art=False
        ).xp
        == 10
    )
    poor = _student(VirtueFlawInstance(vf_id="vf_poor_student"))
    assert (
        study.season_of_study(poor, "Latin", 2, activity="reading", is_art=False).xp
        == 1
    )


def test_a_summa_stops_at_its_level():
    student = _student()  # Perdo 3 (6 xp)
    summa = Book(id="b", name="B", type="Art Summa", art="perdo", level=5, quality=15)
    result = study.reading(student, summa)
    assert result is not None
    assert result.xp == 15 - 6  # to score 5 (15 xp) only
    assert "Capped at score 5" in result.notes[0]


def test_only_magi_study_the_arts():
    companion = _student()
    companion.type = "companion"
    summa = Book(id="b", name="B", type="Art Summa", art="perdo", level=5, quality=15)
    assert study.reading(companion, summa) is None
    tractatus = Book(
        id="t",
        name="T",
        type="Tractatus",
        subject_kind="Ability",
        ability="Latin",
        quality=8,
    )
    result = study.reading(companion, tractatus)
    assert result is not None and result.xp == 8


def test_teaching_and_training_quality():
    teacher = Character(
        id="t",
        name="T",
        type="magus",
        characteristics=Characteristics(communication=2),
        abilities=[
            Ability("Teaching", xp=ability_xp(3)),
            Ability("Latin", xp=ability_xp(5)),
        ],
    )
    assert study.teaching_quality(teacher) == 2 + 3 + 3 + 6
    assert study.teaching_quality(teacher, students=2) == 2 + 3 + 3 + 3
    teacher.virtues_flaws = [VirtueFlawInstance(vf_id="vf_good_teacher")]
    assert study.teaching_quality(teacher, students=3) == 2 + 3 + 3 + 5
    assert study.max_students(teacher) == 15
    assert study.training_quality(teacher, "Latin") == 8


@pytest.mark.parametrize(
    ("total", "months", "left"), [(15, 0, 15), (15, 1, 10), (16, 1, 11), (15, 3, 0)]
)
def test_distractions(total, months, left):
    assert study.after_distraction(total, months) == left


def test_vis_study_pawns():
    assert study.vis_pawns(0) == 1
    assert study.vis_pawns(11) == 3
