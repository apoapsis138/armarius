"""Shaping the land by magic (Transforming Mythic Europe pp. 54-67, 71-77,
Errata p. 84; DE pp. 213, 310-311, 359; RoP: Magic p. 10): the Rituals
that raise an island, their levels and vis, what the land is worth, the
season that casts them and the More form that plans and settles it."""

from __future__ import annotations

import random

import pytest

from ars_magica_manager import actions, manors
from ars_magica_manager.forms import land_seasons
from ars_magica_manager.forms import land_shaping as land_forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    LAND_KIND,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    LandProject,
    Progress,
    Saga,
    SeasonPlan,
)
from ars_magica_manager.models.land_shaping import (
    BASE_METAL,
    PRECIOUS_METAL,
    RING,
    SOLID,
    SQUARE,
    STONE_FILL,
)
from ars_magica_manager.rules import land_shaping as ls
from ars_magica_manager.rules.season_work import base as season_base
from ars_magica_manager.rules.season_work import land_shaping as lw
from ars_magica_manager.rules.xp import art_xp

MILE = ls.PACES_PER_MILE


# -- making stuff (DE p. 359; TME pp. 55-59) ----------------------------------


@pytest.mark.parametrize(
    ("level", "stone", "soil"),
    [
        (20, 10_000, 10_000_000),
        (25, 100_000, 100_000_000),
        (30, 1_000_000, 1_000_000_000),
        (35, 10_000_000, 10_000_000_000),
        (40, 100_000_000, 100_000_000_000),
    ],
)
def test_ritual_volumes_match_the_book(level: int, stone: int, soil: int) -> None:
    # TME p. 55 (the walls' spells) and p. 59 (the soil levels).
    assert ls.created_volume(ls.STONE_STUFF, level) == pytest.approx(stone)
    assert ls.created_volume(ls.EARTH, level) == pytest.approx(soil)


def test_a_ritual_is_never_below_level_20() -> None:
    # A 100-cubic-pace wall is level 20, as one of 10,000 (TME p. 55).
    assert ls.creation_level(ls.STONE_STUFF, 100) == 20
    assert ls.creation_level(ls.STONE_STUFF, 10_000) == 20
    assert ls.creation_level(ls.STONE_STUFF, 10_001) == 25
    assert ls.created_volume(ls.STONE_STUFF, 15) == 0


def test_metals_are_harder() -> None:
    # Base metal: two magnitudes higher and 1/27 the volume (TME p. 58);
    # precious metal three magnitudes more (DE p. 359 agrees).
    metal = ls.created_volume(ls.METAL, 45)
    assert metal == pytest.approx(ls.created_volume(ls.STONE_STUFF, 35) / 27)
    assert ls.created_volume(ls.NOBLE, 60) == pytest.approx(metal)
    # A level 45 metal ring wall, 30 high and 2 thick, is about 1.1 miles across.
    across = ls.wall_reach(RING, metal, 30, 2) / MILE
    assert across == pytest.approx(1.1, abs=0.05)


def test_complexity_adds_magnitudes() -> None:
    plain = LandProject("p", "P")
    fortified = LandProject("f", "F", features=["crenellations", "machicolations"])
    assert ls.complexity(plain) == 0
    assert ls.complexity(fortified) == 2
    # A fire step and hoardings cost no levels (p. 57).
    assert (
        ls.complexity(LandProject("h", "H", features=["fire_step", "hoardings"])) == 0
    )
    every = LandProject(
        "e", "E", features=[f.key for f in ls.WALL_FEATURES], unnatural=True
    )
    assert ls.complexity(every) == 5
    every.cap_complexity = True
    assert ls.complexity(every) == ls.COMPLEXITY_CAP


# -- the island's measures (TME pp. 55-62) ------------------------------------


@pytest.mark.parametrize(("level", "miles"), [(30, 3), (35, 30), (40, 301)])
def test_ring_walls(level: int, miles: float) -> None:
    volume = ls.created_volume(ls.STONE_STUFF, level)
    reach = ls.wall_reach(RING, volume, 30, 2) / MILE
    assert reach == pytest.approx(miles, rel=0.01)


def test_other_shapes() -> None:
    # A square of 4,166 paces a side at level 30, a solid cylinder 206 across.
    million = ls.created_volume(ls.STONE_STUFF, 30)
    assert ls.wall_reach(SQUARE, million, 30, 2) == pytest.approx(4166, abs=1)
    assert ls.wall_reach(SOLID, million, 30, 2) == pytest.approx(206, abs=1)


@pytest.mark.parametrize(
    ("shape", "miles", "height", "cubic"),
    [
        (RING, 3, 30, 657e6),
        (RING, 30, 30, 65.7e9),
        (RING, 3.8, 240, 8.43e9),
        (SQUARE, 2.4, 30, 535e6),
    ],
)
def test_fill_volumes(shape: str, miles: float, height: int, cubic: float) -> None:
    # TME p. 59's soil figures.
    assert ls.fill_volume(shape, miles * MILE, height) == pytest.approx(cubic, rel=0.01)


def test_the_basic_quote() -> None:
    # A 30-mile ring of stone filled with soil: a level 35 wall and a level
    # 40 fill, 15 pawns of vis, under four hours (TME p. 59); the slope
    # three magnitudes below the wall (p. 56).
    project = LandProject("q", "Quote", across_miles=30, grassland=False)
    found = ls.works(project)
    assert [(w.name, w.level) for w in found] == [
        ("The island's wall", 35),
        ("The ablative slope", 20),
        ("The fill", 40),
    ]
    wall, _, fill = found
    assert wall.pawns + fill.pawns == 15
    assert wall.minutes + fill.minutes < 4 * 60


def test_a_stone_fill_is_three_magnitudes_harder() -> None:
    soil = LandProject("a", "A", grassland=False, slope=False)
    stone = LandProject("b", "B", grassland=False, slope=False, fill=STONE_FILL)
    mixed = LandProject(
        "c", "C", grassland=False, slope=False, fill=STONE_FILL, mixed_stone=True
    )
    assert ls.works(soil)[1].level + 15 == ls.works(stone)[1].level
    assert ls.works(mixed)[1].level == ls.works(stone)[1].level + 5


def test_a_solid_cylinder_has_no_fill_or_slope() -> None:
    found = ls.works(LandProject("s", "S", shape=SOLID, across_miles=0.1))
    assert [w.name for w in found] == ["The island's wall", "Verdant grassland"]


def test_wall_materials_take_their_form() -> None:
    wood = ls.works(LandProject("w", "W", wall_material="Wood"))[0]
    assert wood.form == "Herbam"
    gold = ls.works(LandProject("g", "G", wall_material=PRECIOUS_METAL))[0]
    iron = ls.works(LandProject("i", "I", wall_material=BASE_METAL))[0]
    assert gold.level == iron.level + 15


# -- surface life (TME p. 62, by the DE's arithmetic) -------------------------


def test_grassland_and_forest() -> None:
    # +1 size covers 1.25 acres and each magnitude ten times that; a
    # Ritual is at least level 20, which covers 1,250 acres.
    assert ls.grass_acres(20) == pytest.approx(1250)
    assert ls.grass_acres(25) == pytest.approx(12_500)
    assert ls.grass_level(6000) == 25
    # 1,000 mature trees (+3 size): level 25 by the DE's arithmetic.
    assert ls.forest_level(1000) == 25
    assert ls.forest_trees(30) == 10_000


# -- the land (TME p. 62) -----------------------------------------------------


@pytest.mark.parametrize(("miles", "manors"), [(30, 753), (300, 75_398)])
def test_manors_the_land_supports(miles: float, manors: int) -> None:
    # The book: about 755 and 75,428 (its round figures).
    area = ls.acres(RING, miles * MILE)
    assert ls.manors_supported(area) == manors


def test_fertile_land_needs_a_third_less() -> None:
    assert ls.manors_supported(1200) == 2
    assert ls.manors_supported(1200, fertile=True) == 3
    assert ls.yearly_pounds(3) == 60


# -- Boundary spells (TME pp. 71-77; DE p. 310) -------------------------------


def test_boundary_magnitudes_multiply_area() -> None:
    # Each magnitude ten times the area (DE p. 310): 3 miles needs 4, not
    # TME p. 74's 2.
    assert ls.boundary_magnitudes(ls.land_area(RING, 100)) == 0
    assert ls.boundary_magnitudes(ls.land_area(RING, 316)) == 1
    assert ls.island_boundary(LandProject("a", "A", across_miles=3)) == 4
    assert ls.island_boundary(LandProject("b", "B", across_miles=30)) == 6


def test_the_books_boundary_spells_keep_their_levels() -> None:
    levels = {s.name: s.book_level for s in ls.BOUNDARY_SPELLS}
    assert levels == {
        "Weather Made Good": 40,
        "The Command of Every Beast": 20,
        "The Eyes of Every Beast": 40,
        "The Lost City": 45,
        "Murderous Woodland": 55,
        "Remembered Messages": 20,
        "Strange Tricks Using Canal Contents": 25,
    }


def test_an_intellego_spell_ignores_size() -> None:
    eyes = ls.SPELLS_BY_NAME["The Eyes of Every Beast"]
    weather = ls.SPELLS_BY_NAME["Weather Made Good"]
    assert eyes.level(4) == 40
    assert weather.level(4) == 60


def test_wards() -> None:
    # The level chosen + 35 for Touch, Sun and Boundary (TME p. 71).
    assert ls.ward_level(10, 0) == 45
    assert ls.ward_level(10, 2) == 55
    assert ls.aegis_level(20, 4) == 40
    assert ls.fumigant_might(45, 0) == 20


# -- casting and auras ----------------------------------------------------------


def test_ritual_vis_and_time() -> None:
    assert ls.ritual_pawns(35) == 7
    assert ls.ritual_minutes(40) == 120
    assert ls.vis_limit(12, 10) == 22


@pytest.mark.parametrize(("level", "tether"), [(40, 0), (49, 0), (50, 1), (75, 3)])
def test_residue_tethers(level: int, tether: int) -> None:
    # RoP: Magic p. 10: (level - 40) / 10, rounded down.
    assert ls.residue_tether(level) == tether


def test_monuments_and_beings() -> None:
    assert ls.monument_tether(450) == 4
    assert ls.being_tether(45) == 4


def test_a_vast_island_leaves_a_tether() -> None:
    huge = LandProject("h", "Huge", across_miles=300, grassland=False, slope=False)
    assert ls.tethers(huge) == [("The fill", 1)]
    assert ls.tethers(LandProject("s", "Small")) == []


# -- the model ------------------------------------------------------------------


def test_project_round_trip_and_checks() -> None:
    project = LandProject("x", "Isle", features=["sea_gate"], forest_trees=1000)
    data = {**project.__dict__, "retired": 1}
    assert LandProject.from_dict(data) == project
    with pytest.raises(ValueError, match="shape"):
        LandProject.from_dict({"id": "x", "name": "Isle", "shape": "Hexagon"})
    with pytest.raises(ValueError, match="size"):
        LandProject.from_dict({"id": "x", "name": "Isle", "across_miles": 0})
    with pytest.raises(ValueError, match="wall"):
        LandProject.from_dict({"id": "x", "name": "Isle", "features": ["moat"]})
    with pytest.raises(ValueError, match="trees"):
        LandProject.from_dict({"id": "x", "name": "Isle", "forest_trees": "many"})


def test_an_older_covenant_loads_without_projects() -> None:
    covenant = Covenant.from_dict({"id": "c", "saga_id": "s", "name": "Keep"})
    assert covenant.land_projects == []
    with pytest.raises(ValueError, match="land projects"):
        Covenant.from_dict({"id": "c", "saga_id": "s", "name": "K", "land_projects": 3})


# -- the season -----------------------------------------------------------------


def _magus(creo: int = 15, terram: int = 15) -> Character:
    magus = Character(id="m", name="Terrena", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(stamina=2)
    magus.arts = {
        "creo": ArtScore(xp=art_xp(creo)),
        "terram": ArtScore(xp=art_xp(terram)),
        "herbam": ArtScore(xp=art_xp(10)),
    }
    magus.raw_vis = {"terram": 30, "creo": 10, "herbam": 5}
    return magus


def _saga(magus: Character, project: LandProject) -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep", aura=3)
    covenant.land_projects.append(project)
    return Saga(id="s", name="S", covenants=[covenant], characters=[magus])


def _plan(title: str = "Insula") -> SeasonPlan:
    return SeasonPlan("m", 1220, "Spring", lw.SHAPE_LAND, title=title)


def test_season_checks() -> None:
    magus = _magus()
    saga = _saga(magus, LandProject("i", "Insula"))
    assert season_base.problems(saga, magus, _plan("Atlantis"))
    assert season_base.problems(saga, magus, _plan()) == []
    magus.progress.append(Progress(LAND_KIND, "Insula", 4, 4, done=True))
    assert season_base.problems(saga, magus, _plan()) == [
        "Every Ritual of Insula is cast."
    ]


def test_season_preview_lists_the_rituals_and_their_vis() -> None:
    magus = _magus()
    saga = _saga(magus, LandProject("i", "Insula", grassland=False))
    work = season_base.work(saga, magus, _plan(), None)
    # The wall (CrTe 30, 6 pawns), slope (20, 4) and fill (30, 6): Terram
    # first, up to the magus's score of 15 in it.
    assert work.vis_cost == {"Terram": 16}
    assert work.progress == [(LAND_KIND, "Insula", 3, 3)]
    assert "The island's wall (CrTe 30, 90 minutes" in work.notes[0]
    # A Ritual still works down to 10 below its level (DE p. 213).
    assert "30+ casts it" in work.notes[0] and "down to 20" in work.notes[0]


def test_season_stops_where_the_vis_runs_out() -> None:
    magus = _magus()
    magus.raw_vis = {"terram": 8}
    saga = _saga(magus, LandProject("i", "Insula", grassland=False))
    work = season_base.work(saga, magus, _plan(), None)
    assert work.progress == [(LAND_KIND, "Insula", 3, 1)]
    assert "the season's casting stops there" in work.notes[-1]


def test_season_rolls_and_records_progress() -> None:
    magus = _magus(creo=20, terram=20)
    saga = _saga(magus, LandProject("i", "Insula", grassland=False))
    cast = [
        season_base.work(saga, magus, _plan(), random.Random(seed))
        for seed in range(30)
    ]
    # A Casting Score of 20 + 20 + 2 + 3 against level 30: cast unless botched.
    whole = [w for w in cast if w.progress == [(LAND_KIND, "Insula", 3, 3)]]
    assert whole
    assert all(sum(w.vis_cost.values()) == 16 for w in whole)


def test_cast_count_sums_every_magus_and_resumes() -> None:
    magus = _magus()
    project = LandProject("i", "Insula", grassland=False)
    saga = _saga(magus, project)
    other = Character(id="o", name="Other", type="magus")
    other.progress.append(Progress(LAND_KIND, "Insula", 3, 1))
    saga.characters.append(other)
    assert ls.cast_count(saga, project) == 1
    assert [w.name for w in ls.remaining(saga, project)] == [
        "The ablative slope",
        "The fill",
    ]
    assert not ls.land_made(saga, project)
    magus.progress.append(Progress(LAND_KIND, "Insula", 3, 2))
    assert ls.land_made(saga, project)


def test_the_season_form_offers_the_projects() -> None:
    magus = _magus()
    saga = _saga(magus, LandProject("i", "Insula"))
    (field,) = land_seasons.fields(saga, None, lambda *keys: lambda v: True)
    assert field.options[0][1] == "Insula"
    ((keys, read),) = land_seasons.READS
    assert keys == (lw.SHAPE_LAND,)
    assert read({"land_project": "Insula"}) == {"title": "Insula"}


# -- More's Shape the Land ------------------------------------------------------


def test_shape_form_makes_and_edits_a_project() -> None:
    magus = _magus()
    saga = _saga(magus, LandProject("i", "Insula"))
    covenant = saga.covenants[0]
    covenant.land_projects.clear()
    form = land_forms.shape_form(saga, covenant)
    assert isinstance(form, land_forms.Form)
    values = {f.key: f.value for f in form.fields()}
    values.update(name="Nova", across_miles=30.0)
    assert form.validate is not None and form.validate(values) is None
    assert form.live is not None and "The fill: CrTe 40 Ritual" in form.live(values)
    form.apply(values)
    (made,) = covenant.land_projects
    assert (made.name, made.across_miles) == ("Nova", 30.0)
    assert covenant.diary[-1].name == "Land project: Nova"
    # A second project can't take the name.
    again = land_forms.project_form(saga, covenant, None)
    assert again.validate is not None
    assert again.validate({**values, "name": "nova"}) is not None


def test_settling_the_land_adds_manors() -> None:
    magus = _magus()
    project = LandProject("i", "Insula", grassland=False)
    saga = _saga(magus, project)
    covenant = saga.covenants[0]
    assert ls.manors_left(saga, project) == 0
    magus.progress.append(Progress(LAND_KIND, "Insula", 3, 3, done=True))
    # 3 miles across: 4,524 acres, seven 600-acre manors.
    assert ls.manors_left(saga, project) == 7
    form = land_forms.settle_form(saga, covenant, project)
    assert form.validate is not None
    assert form.validate({"count": 8, "prefix": "Insula"}) is not None
    form.apply({"count": 2, "prefix": "Insula"})
    listed = manors.manor_list(manors.manors_of(covenant))
    assert [(m["name"], m["acres"], m["allod"]) for m in listed] == [
        ("Insula 1", 600, True),
        ("Insula 2", 600, True),
    ]
    assert ls.manors_left(saga, project) == 5


class _Facts:
    def __init__(self, saga: Saga, covenant: Covenant | None) -> None:
        self.saga = saga
        self.selected_covenant = covenant
        self.selected_character = None
        self.selected_laboratory = None
        self.selected_kind = actions.NodeKind.COVENANT

    def player_may(self, action: str) -> bool:
        return True

    def active_section(self) -> str:
        return "section-eco-income"


def test_offered_on_income_with_the_book_in_play() -> None:
    magus = _magus()
    saga = _saga(magus, LandProject("i", "Insula"))
    rule = actions._SECTION_RULES["shape_land"]
    facts = _Facts(saga, saga.covenants[0])
    saga.books_in_play = ["TME"]
    assert rule(facts, "section-eco-income")  # type: ignore[arg-type]
    assert not rule(facts, "section-eco-wealth")  # type: ignore[arg-type]
    saga.books_in_play = ["Covenants"]
    assert not rule(facts, "section-eco-income")  # type: ignore[arg-type]


def test_the_desktop_sets_it_beside_improve_income() -> None:
    assert menu_forms.lives_at("shape_land", actions.NodeKind.COVENANT, "Income")
