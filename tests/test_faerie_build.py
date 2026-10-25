"""A faerie built by Realms of Power: Faerie (pp. 45-64): its Might from its
Virtues and the choices every faerie makes."""

from ars_magica_manager.models import Creature, VirtueFlawInstance
from ars_magica_manager.rules import faerie_build


def _faerie(*vf_ids: str, might: int = 5) -> Creature:
    return Creature(
        id="f",
        name="Sprite",
        realm="Faerie",
        might=might,
        virtues_flaws=[VirtueFlawInstance(v) for v in vf_ids],
    )


def test_faerie_might_comes_from_its_virtues():
    assert faerie_build.might_from_virtues(_faerie()).might == 5
    built = faerie_build.might_from_virtues(
        _faerie("vf_increased_faerie_might", "vf_increased_faerie_might_major")
    )
    assert built.might == 25
    assert faerie_build.might_from_virtues(_faerie("vf_decreased_might")).might == 1


def test_a_faerie_built_by_the_book_makes_every_choice():
    whole = _faerie(
        "vf_humanoid_faerie",
        "vf_narrowly_cognizant",
        "vf_passes_for_human",
        "vf_traditional_ward",
        "vf_increased_faerie_might",
        might=10,
    )
    assert faerie_build.problems(whole) == []
    lacking = _faerie("vf_humanoid_faerie", might=10)
    found = faerie_build.problems(lacking)
    assert any("a level of cognizance" in p and "a taboo" in p for p in found)
    assert any("Faerie Might of 5" in p for p in found)


def test_what_a_faerie_cant_have():
    found = faerie_build.problems(_faerie("vf_humanoid_faerie", "vf_the_gift"))
    assert any("The Gift" in p for p in found)


def test_faeries_written_another_way_arent_checked():
    assert faerie_build.problems(_faerie("vf_traditional_ward", might=30)) == []
    assert faerie_build.problems(Creature(id="m", name="M", realm="Magic")) == []


def test_pretense_points():
    plain = _faerie()
    assert faerie_build.pretense_points(plain, 21) == 360
    assert faerie_build.pretense_points(_faerie("vf_pretentious"), 21) == 440
    assert (
        faerie_build.pretense_points(_faerie("vf_aloof", "vf_freshly_sprung"), 21)
        == 230
    )
