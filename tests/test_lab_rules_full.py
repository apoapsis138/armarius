"""The laboratory's rules in full: the Teaching and Texts
Specializations, Refinement's Spotless roll and familiarity, the lab
Virtues' and Flaws' missing modifiers, Illusions, Hidden Defects, unpaid
Upkeep and an unfixed Arcane Connection's last season (DE pp. 250,
287-296; Covenants pp. 118-119)."""

import random

from ars_magica_manager import catalog, economics
from ars_magica_manager.models import (
    Ability,
    ArcaneConnection,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    LabCharacteristics,
    Laboratory,
    LabSpecialtyEntry,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import activities, book_seasons, lab_seasons, lab_stats
from ars_magica_manager.rules import laboratory_seasons as ls
from ars_magica_manager.rules.xp import ability_xp, art_xp


class _Dice(random.Random):
    """A random source throwing `faces` (d10 faces, 0-9) in order."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):
        return self.faces.pop(0) if self.faces else 5


def _saga(*vfs: VirtueFlawInstance) -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2, communication=1)
    magus.abilities = [
        Ability("Magic Theory", xp=ability_xp(5)),
        Ability("Teaching", xp=ability_xp(2)),
        Ability("Dead Language: Latin", xp=ability_xp(5)),
        Ability("Profession: Scribe", xp=ability_xp(2)),
    ]
    magus.arts = {"creo": ArtScore(xp=art_xp(5))}
    magus.assigned_lab_id = "lab"
    lab = Laboratory(
        id="lab",
        covenant_id="cov",
        name="Tower",
        owner_id="m",
        characteristics=LabCharacteristics(size=1, refinement=1),
        virtues_flaws=list(vfs),
    )
    return Saga(
        id="s", name="S", covenants=[covenant], characters=[magus], laboratories=[lab]
    )


def _total(saga: Saga, characteristic: str) -> int:
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    return lab_stats.lab_characteristic_total(
        saga.laboratories[0], by_id, characteristic, saga
    )[3]


def _spec(saga: Saga, name: str) -> int:
    return lab_stats.specialty_points(saga, saga.laboratories[0], name)


# -- Specializations (DE p. 291) --


def test_the_teaching_specialization_adds_at_most_3_to_teaching():
    saga = _saga()
    lab = saga.laboratories[0]
    lab.specialties = [LabSpecialtyEntry("Teaching", 5, "notes")]
    assert lab_stats.teaching_bonus(saga, lab) == 3
    lines = activities._lab_teaching(saga, saga.character("m"))
    assert [(line.label, line.amount) for line in lines] == [
        ("Teaching Specialization (in the laboratory)", 3)
    ]
    lab.specialties = []
    assert activities._lab_teaching(saga, saga.character("m")) == []


def test_the_texts_specialization_adds_a_point_per_full_three():
    saga = _saga()
    saga.laboratories[0].specialties = [LabSpecialtyEntry("Texts", 7, "notes")]
    plan = _plan(book_seasons.COPY_BOOK)
    assert book_seasons.texts_bonus(saga, saga.character("m"), plan) == 2
    # Copied away from the laboratory: no Texts Specialization.
    plan.in_lab = False
    assert book_seasons.texts_bonus(saga, saga.character("m"), plan) == 0
    plan.in_lab = True
    saga.character("m").assigned_lab_id = None
    assert book_seasons.texts_bonus(saga, saga.character("m"), plan) == 0


# -- Refinement (DE pp. 287-288) --


def _plan(activity: str, **kw) -> SeasonPlan:
    return SeasonPlan("m", 1220, "Spring", activity, lab_id="lab", **kw)


def test_refining_reminds_of_the_familiarity_it_needs():
    saga = _saga()
    _, work = ls.work(saga, saga.character("m"), _plan(ls.REFINE), saga.laboratories[0])
    assert "1 year worked in this laboratory" in work.notes[-1]


def test_a_tidy_magus_may_make_the_laboratory_spotless():
    saga = _saga()
    magus = saga.character("m")
    magus.personality_traits = [ScoredTrait("Tidy", 3)]
    plan = _plan(ls.REFINE)
    _, work = ls.work(saga, magus, plan, saga.laboratories[0])
    # The organization roll (die 4), then Tidy 3 + die 7 against 9.
    notes = ls.roll(work, magus, plan, _Dice(4, 7), saga)
    assert ls.SPOTLESS in work.gains_vf
    assert notes[-1] == "Tidy 3 + die 7 = 10: the laboratory is Spotless."
    _, work = ls.work(saga, magus, plan, saga.laboratories[0])
    ls.roll(work, magus, plan, _Dice(4, 2), saga)
    assert ls.SPOTLESS not in work.gains_vf


def test_an_untidy_magus_makes_no_tidy_roll():
    saga = _saga()
    magus = saga.character("m")
    plan = _plan(ls.REFINE)
    _, work = ls.work(saga, magus, plan, saga.laboratories[0])
    notes = ls.roll(work, magus, plan, _Dice(4), saga)
    assert len(notes) == 1 and ls.SPOTLESS not in work.gains_vf


def test_hidden_defects_can_pile_up_and_are_found_one_at_a_time():
    lab = _saga().laboratories[0]
    ls.add_vf(lab, ls.HIDDEN_DEFECT)
    ls.add_vf(lab, ls.HIDDEN_DEFECT)
    ls.add_vf(lab, ls.HIGHLY_ORGANIZED)
    ls.add_vf(lab, ls.HIGHLY_ORGANIZED)
    ids = [vf.vf_id for vf in lab.virtues_flaws]
    assert ids.count(ls.HIDDEN_DEFECT) == 2 and ids.count(ls.HIGHLY_ORGANIZED) == 1
    ls.remove_vf(lab, ls.HIDDEN_DEFECT)
    assert [vf.vf_id for vf in lab.virtues_flaws].count(ls.HIDDEN_DEFECT) == 1


def test_a_take_over_that_lowers_refinement_warns_of_virtues_lost():
    saga = _saga(
        VirtueFlawInstance("labvf_spotless"),
        VirtueFlawInstance("labvf_greater_feature", {"specialization": "Spells"}),
    )
    lab = saga.laboratories[0]
    lab.owner_id = None
    lab.characteristics.refinement = 3
    magus = saga.character("m")
    magus.abilities[0] = Ability("Magic Theory", xp=ability_xp(4))  # Refinement 1
    _, work = ls.work(saga, magus, _plan(ls.TAKE_OVER), lab)
    assert work.refinement == 1
    assert any("Virtues are lost until it fits" in note for note in work.notes)


# -- The lab Virtues and Flaws (DE pp. 293-296; Covenants pp. 118-119) --


def test_cramped_puts_a_point_in_the_activity_it_spares():
    saga = _saga(VirtueFlawInstance("labvf_cramped", {"specialization": "Spells"}))
    assert _spec(saga, "Spells") == 1


def test_empty_costs_upkeep_or_health_as_chosen():
    upkeep = _saga(VirtueFlawInstance("labvf_empty", {"cost": "Upkeep"}))
    assert (_total(upkeep, "upkeep"), _total(upkeep, "health")) == (1, 0)
    health = _saga(VirtueFlawInstance("labvf_empty", {"cost": "Health"}))
    assert (_total(health, "upkeep"), _total(health, "health")) == (0, -1)


def test_the_virtues_that_grant_specialization_points():
    for vf_id, choice, points in (
        ("labvf_natural_environment", "Herbam", 3),
        ("labvf_greater_guardian", "Vim", 3),
        ("labvf_greater_horde", "Rego", 2),
        ("labvf_sacrifices", "Animal", 2),
    ):
        saga = _saga(VirtueFlawInstance(vf_id, {"specialization": choice}))
        assert _spec(saga, choice) == points, vf_id


def test_faerie_ingredients_lower_the_upkeep():
    saga = _saga(
        VirtueFlawInstance("labvf_faerie_ingredients", {"specialization": "Herbam"})
    )
    assert _total(saga, "upkeep") == -1


def test_lightless_holds_aesthetics_to_minus_1():
    saga = _saga(
        VirtueFlawInstance("labvf_lightless", {"specialization": "Perdo"}),
        VirtueFlawInstance("labvf_spotless"),
    )
    saga.laboratories[0].characteristics.aesthetics = 3
    assert _total(saga, "aesthetics") == -1


def test_shrouded_halves_aesthetics_after_the_rest():
    saga = _saga(
        VirtueFlawInstance("labvf_shrouded"), VirtueFlawInstance("labvf_spotless")
    )
    saga.laboratories[0].characteristics.aesthetics = 4
    manual, virtues, flaws, total = lab_stats.lab_characteristic_total(
        saga.laboratories[0],
        catalog.load_lab_virtue_flaw_catalog_by_id(),
        "aesthetics",
        saga,
    )
    assert total == 2 and manual + virtues + flaws == total


def test_an_illusions_balancing_virtue_has_no_effect():
    saga = _saga(
        VirtueFlawInstance("labvf_spotless"),
        VirtueFlawInstance("labvf_lesser_illusion", {"illusory": "Spotless"}),
    )
    assert _total(saga, "health") == 0
    saga.laboratories[0].virtues_flaws[1].params = {}
    assert _total(saga, "health") == 1


# -- Upkeep unpaid (DE p. 288) --


def test_a_broke_covenants_laboratories_go_unmaintained():
    saga = _saga()
    covenant = saga.covenants[0]
    assert economics.neglected_laboratories(saga, covenant) == []
    covenant.economics.wealth = -5
    assert economics.neglected_laboratories(saga, covenant) == [saga.laboratories[0]]


# -- Fixing an Arcane Connection (DE p. 250) --


def test_a_connection_that_has_lapsed_cant_be_fixed():
    connection = ArcaneConnection(
        "ac", "a lock of hair", lasts_season="Winter", lasts_year=1219
    )
    assert lab_seasons.lapsed(connection, "Spring", 1220)
    assert not lab_seasons.lapsed(connection, "Winter", 1219)
    connection.lasts_season = ""
    connection.lasts_year = 1220
    assert not lab_seasons.lapsed(connection, "Winter", 1220)
    assert not lab_seasons.lapsed(ArcaneConnection("x", "y"), "Spring", 1300)
    saga = _saga()
    saga.laboratories[0].arcane_connections = [
        ArcaneConnection("ac", "a lock of hair", lasts_season="Winter", lasts_year=1219)
    ]
    saga.laboratories[0].raw_vis = {"Vim": 2}
    problems, _ = lab_seasons.work(
        saga, saga.character("m"), _plan(lab_seasons.FIX_AC, connection_id="ac")
    )
    assert problems and "no longer active" in problems[0]
