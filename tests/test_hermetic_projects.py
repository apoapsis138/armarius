"""Hermetic Projects: a covenant's Great Tower (Hermetic Projects pp.
36-41; City & Guild p. 77), the master mason's season, and Open a Tunnel
(HP pp. 78-81; DE p. 219, errata p. 81)."""

import random

import pytest

from ars_magica_manager import hermetic_projects as hpc
from ars_magica_manager import storage
from ars_magica_manager.commands import Act, Confirm, Form, Refuse
from ars_magica_manager.form_spec import DialogField
from ars_magica_manager.forms import tunnel as tunnel_forms
from ars_magica_manager.models import (
    Ability,
    Book,
    Character,
    Characteristics,
    Covenant,
    CraftDevice,
    HermeticProject,
    KnownSpell,
    Neighbour,
    ProjectWork,
    Saga,
    SeasonPlan,
)
from ars_magica_manager.models.hermetic_projects import (
    BUILDING,
    BUTTRESS,
    INNOVATION,
    REBUILD,
    REPAIR,
    RITUAL,
    SHODDY,
    STANDARD,
    STRESS,
    SUPERIOR,
)
from ars_magica_manager.rules import hermetic_projects as hp
from ars_magica_manager.rules import season_work as sw
from ars_magica_manager.seasons import lab_apply

PLACE = "place_spur"


def tower(**changes) -> HermeticProject:
    """The Schattenbach Spire, the preview's sample: two rituals (one
    failed), a mason's eight seasons, two craft devices and a buttress."""
    project = HermeticProject(
        id="spire",
        name="The Schattenbach Spire",
        season="Summer",
        year=1210,
        mason_id="gregor",
        place_id=PLACE,
        innovation=1,
        raw_materials=3,
        works=[
            ProjectWork(
                id="w1",
                kind=RITUAL,
                name="Conjuring the Great Tower",
                season="Summer",
                year=1210,
                levels=2,
                quality=STANDARD,
                who="tandaline",
            ),
            ProjectWork(
                id="w2",
                kind=RITUAL,
                name="Heights of the Great Tower",
                season="Spring",
                year=1212,
                levels=4,
                quality=SHODDY,
                who="tandaline",
            ),
            ProjectWork(
                id="w3",
                kind=BUILDING,
                name="Gregor builds",
                season="Winter",
                year=1219,
                levels=8,
                quality=SUPERIOR,
                seasons=8,
                who="gregor",
            ),
        ],
        devices=[
            CraftDevice(id="d1", name="The Arms of Hercules", effect="ReHe 40"),
            CraftDevice(id="d2", name="True Falsework", effect="ReHe 30"),
            CraftDevice(id="d3", name="The Flying Buttress", kind=BUTTRESS),
        ],
    )
    for key, value in changes.items():
        setattr(project, key, value)
    return project


def tower_saga(project: HermeticProject | None = None) -> Saga:
    return Saga(
        id="hp_saga",
        name="Hermetic Projects",
        storyguide="Hedda",
        current_season="Spring",
        current_year=1220,
        covenants=[
            Covenant(
                id="dam",
                saga_id="hp_saga",
                name="Dammerstein",
                place_id=PLACE,
                hermetic_projects=[project or tower()],
            )
        ],
        neighbours=[
            Neighbour(id=PLACE, name="The Spur", kind="place", details={"aura": 0})
        ],
        characters=[
            Character(
                id="gregor",
                name="Gregor",
                type="companion",
                covenant_id="dam",
                characteristics=Characteristics(intelligence=1),
                abilities=[Ability(name="Craft: Mason", category="General", xp=105)],
            ),
            Character(
                id="tandaline",
                name="Tandaline",
                type="magus",
                covenant_id="dam",
                characteristics=Characteristics(intelligence=2),
                abilities=[Ability(name="Finesse", category="General", xp=50)],
                spells_known=[KnownSpell("spell_heights_of_the_great_tower")],
            ),
        ],
    )


def _project(saga: Saga) -> HermeticProject:
    return saga.covenants[0].hermetic_projects[0]


def _values(form: Form, **changes) -> dict:
    values = {f.key: f.value for f in form.fields() if isinstance(f, DialogField)}
    values.update(changes)
    return values


class Dice(random.Random):
    """A Random whose d10s come in the order given (0 a zero face)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *_args, **_kwargs) -> int:  # type: ignore[override]
        return self.faces.pop(0)


# -- the tower ----------------------------------------------------------------


def test_height_is_twenty_feet_a_level():
    project = tower()
    assert hp.height_levels(project) == 14
    assert hp.feet(14) == 280


def test_the_weakest_section_sets_the_quality_and_damage_levels():
    # A failed Finesse roll built a shoddy section: 1 x 4 (HP pp. 38-39).
    project = tower()
    assert hp.quality(project) == SHODDY
    assert hp.damage_levels(project) == 4
    # Rebuilt as standard, the weakest is standard: 2 x 4.
    project.works.append(ProjectWork(kind=REBUILD, rebuilt="w2", year=1220))
    assert hp.quality(project) == STANDARD
    assert hp.damage_levels(project) == 8
    assert hp.previously_repaired(project)


def test_damage_levels_by_quality_are_four_eight_twelve_sixteen():
    assert [hp.BASE_DAMAGE[q] * hp.SIZE_MULTIPLIER for q in hp.BASE_DAMAGE] == [
        4,
        8,
        12,
        16,
    ]


def test_damage_lost_and_repaired():
    project = tower()
    project.works.append(ProjectWork(kind=STRESS, damage=3))
    assert hp.damage_left(project) == 1
    project.works.append(ProjectWork(kind=REPAIR, seasons=2))
    assert hp.damage_lost(project) == 1
    assert hp.damage_left(project) == 3


def test_tethers_count_the_rituals_and_failed_rolls_their_shoddy_levels():
    project = tower()
    assert hp.tethers(project) == 2
    # One failed ritual, but each of its shoddy levels is a botch die.
    shoddy = [w for w in project.works if w.kind == hp.RITUAL and w.quality == SHODDY]
    assert len(shoddy) == 1
    assert hp.failed_finesse(project) == shoddy[0].levels


def test_heights_botch_dice_add_one_for_each_failed_level_and_three_a_magnitude():
    heights = hp.RITUAL_BY_KEY["heights"]
    larger = hp.RITUAL_BY_KEY["heights_55"]
    assert hp.ritual_botch_dice(heights, 0) == 1
    assert hp.ritual_botch_dice(heights, 2) == 3
    assert hp.ritual_botch_dice(larger, 1) == 5
    assert (larger.levels, larger.ease) == (40, 15)
    assert hp.RITUAL_BY_KEY["heights_60"].levels == 400


def test_the_masons_rate_counts_each_kind_of_device_once_up_to_his_score():
    saga = tower_saga()
    project = _project(saga)
    # Two devices of one kind count once.
    project.devices.append(CraftDevice(name="True Falsework", effect="ReHe 30"))
    mason = hp.mason_of(saga, project, "dam")
    assert mason is not None
    assert (mason.craft, mason.devices, mason.effective) == (6, 2, 8)
    assert mason.levels_a_season == 1
    # At most his Craft: Mason.
    capped = hp.Mason("x", 0, 2, 5, 0, 0)
    assert capped.effective == 4
    assert hp.levels_a_season(10) == 2 and hp.levels_a_season(15) == 3


def test_workshop_total_uses_intelligence_and_the_craft_levels():
    saga = tower_saga()
    mason = hp.mason_of(saga, _project(saga), "dam")
    assert mason is not None
    # Int 1 + Craft 6 + Innovation 1 + Raw Materials 3 = 11: standard.
    assert mason.workshop_total == 11
    assert mason.quality == STANDARD
    assert [hp.workshop_quality(t) for t in (2, 3, 6, 12, 15)] == [
        "",
        SHODDY,
        STANDARD,
        SUPERIOR,
        "Excellent",
    ]


def test_innovation_gains_de_architectura_and_the_water_wheel_up_to_three():
    saga = tower_saga()
    project = _project(saga)
    saga.books.append(
        Book(
            id="vitruvius",
            name="De Architectura",
            type="Tractatus",
            owner_kind="covenant",
            owner_id="dam",
        )
    )
    assert hp.innovation(saga, project, "dam") == 2
    project.devices.append(CraftDevice(name="The Water Wheel", kind=INNOVATION))
    assert hp.innovation(saga, project, "dam") == 3
    project.innovation = 3
    assert hp.innovation(saga, project, "dam") == 3


def test_the_stress_check_modifiers():
    saga = tower_saga()
    project = _project(saga)
    check = hp.stress_check(saga, project)
    # Craft 6, shoddy -1, one Flying Buttress +1.
    assert check.total == 6
    assert check.needed == 9
    severe = hp.stress_check(saga, project, severity=-3, repaired=True)
    assert severe.total == 2


def test_buttresses_count_up_to_the_masons_craft():
    saga = tower_saga()
    project = _project(saga)
    project.devices[2].count = 9
    assert hp.stress_check(saga, project).total == 5 + 6


def test_stress_damage_one_level_and_one_more_a_botch():
    assert hp.stress_damage(True, 0) == 0
    assert hp.stress_damage(False, 0) == 1
    assert hp.stress_damage(False, 2) == 3


# -- the forms ----------------------------------------------------------------


def test_stress_check_form_rolls_and_keeps_the_work():
    saga = tower_saga()
    covenant = saga.covenants[0]
    form = hpc.stress_form(saga, covenant, Dice(2))
    assert isinstance(form, Form)
    said = form.apply(_values(form))
    project = _project(saga)
    work = project.works[-1]
    assert (work.kind, work.outcome, work.damage) == (STRESS, "Damaged", 1)
    assert hp.damage_left(project) == 3
    assert "loses 1 damage level" in " ".join(said)


def test_stress_check_holds_on_a_good_die():
    saga = tower_saga()
    form = hpc.stress_form(saga, saga.covenants[0], Dice(9))
    assert isinstance(form, Form)
    form.apply(_values(form))
    assert _project(saga).works[-1].outcome == "Held"


def test_stress_check_refused_before_anything_is_built():
    saga = tower_saga(tower(works=[]))
    assert isinstance(hpc.stress_form(saga, saga.covenants[0]), Refuse)


def test_conjure_levels_rolls_finesse_and_tethers_the_place():
    saga = tower_saga()
    covenant = saga.covenants[0]
    form = hpc.conjure_form(saga, covenant, Dice(9))
    assert isinstance(form, Form)
    values = _values(form)
    assert values["ritual"] == "heights"
    said = form.apply(values)
    work = _project(saga).works[-1]
    # Int 2 + Finesse 4 + 9 = 15 against 12: standard, four levels.
    assert (work.kind, work.levels, work.quality) == (RITUAL, 4, STANDARD)
    place = saga.neighbour(PLACE)
    assert place is not None
    assert "(preternatural 1)" in place.details["tethers"]
    assert place.details["aura_adjust"] == 1
    assert any("tether" in line for line in said)


def test_a_failed_finesse_roll_builds_shoddy_and_adds_its_levels_as_botch_dice():
    saga = tower_saga()
    before = hp.failed_finesse(_project(saga))
    form = hpc.conjure_form(saga, saga.covenants[0], Dice(2))
    assert isinstance(form, Form)
    form.apply(_values(form))
    project = _project(saga)
    assert project.works[-1].quality == SHODDY
    # The failed Heights leaves 4 shoddy levels on top of the earlier ones.
    assert hp.failed_finesse(project) == before + 4


def test_conjuring_the_great_tower_makes_an_aura_where_there_was_none():
    saga = tower_saga(tower(works=[]))
    form = hpc.conjure_form(saga, saga.covenants[0], Dice(9))
    assert isinstance(form, Form)
    values = _values(form)
    assert values["ritual"] == "conjuring"
    form.apply(values)
    place = saga.neighbour(PLACE)
    assert place is not None
    assert place.details["aura"] == 1 and place.realm == "Magic"
    assert hp.height_levels(_project(saga)) == 2
    # The foundations stand now: Conjuring again is refused.
    again = hpc.conjure_form(saga, saga.covenants[0])
    assert isinstance(again, Form) and again.validate is not None
    assert again.validate(_values(again, ritual="conjuring"))


def test_projects_ops_add_edit_delete_and_show():
    saga = tower_saga()
    covenant = saga.covenants[0]
    ops = hpc.covenant_ops(saga, covenant)
    add = ops[hpc.PROJECTS_SECTION].add
    assert add is not None
    form = add()
    assert isinstance(form, Form)
    form.apply(_values(form, name="The Second Tower"))
    assert len(covenant.hermetic_projects) == 2
    assert covenant.project_shown == covenant.hermetic_projects[1].id
    shown = hpc.show_project(saga, covenant, 0)
    assert isinstance(shown, Act)
    shown.apply()
    assert hp.shown_project(covenant) is covenant.hermetic_projects[0]
    remove = ops[hpc.PROJECTS_SECTION].remove
    assert remove is not None
    confirm = remove(1)
    assert isinstance(confirm, Confirm)
    confirm.apply()
    assert len(covenant.hermetic_projects) == 1


def test_project_form_refuses_innovation_above_three():
    saga = tower_saga()
    form = hpc.project_form(saga, saga.covenants[0], None)
    assert form.validate is not None
    assert form.validate(_values(form, name="x", innovation=4))
    assert form.validate(_values(form, name="x")) is None


def test_works_and_devices_ops_act_on_the_shown_project():
    saga = tower_saga()
    ops = hpc.covenant_ops(saga, saga.covenants[0])
    add = ops[hpc.PROJECT_WORKS_SECTION].add
    assert add is not None
    form = add()
    assert isinstance(form, Form)
    form.apply(_values(form, kind=REPAIR, seasons=1))
    assert _project(saga).works[-1].kind == REPAIR
    add_device = ops[hpc.PROJECT_DEVICES_SECTION].add
    assert add_device is not None
    device = add_device()
    assert isinstance(device, Form)
    device.apply(_values(device, name="The Laborer's Rest", effect="ReTe 25"))
    assert hp.craft_devices(_project(saga)) == 3


def test_the_tab_shows_the_tower_facts_and_the_masons_lines():
    saga = tower_saga()
    holder = hpc.manors_of(saga.covenants[0])
    facts = {f.label: f.value for f in hpc.tower_facts(saga, holder)}
    assert facts["Height"] == "280 ft (14 levels)"
    assert facts["Damage levels"] == "4 of 4 (Shoddy 1 x 4)"
    assert facts["Failed Finesse"] == "4 levels: next Heights 5 botch dice"
    text = hpc.tower_block_text(saga, holder)
    assert "Gregor" in text and "= [b]8[/]" in text
    grid = hpc.works_grid(saga, holder)
    assert grid.rows[1][3] == SHODDY
    assert hpc.devices_title(saga, holder) == "Craft Devices (+2, at most +6)"


# -- the mason's season -------------------------------------------------------


def _plan(title: str = BUILDING) -> SeasonPlan:
    return SeasonPlan(
        character_id="gregor",
        year=1220,
        season="Summer",
        activity="build_great_tower",
        title=title,
    )


def test_the_masons_season_builds_levels_of_his_workshops_quality():
    saga = tower_saga()
    gregor = saga.character("gregor")
    assert gregor is not None
    plan = _plan()
    assert not sw.problems(saga, gregor, plan)
    work = sw.work(saga, gregor, plan, None)
    lab_apply.apply_supplement(saga, gregor, plan, work)
    made = _project(saga).works[-1]
    assert (made.kind, made.levels, made.quality) == (BUILDING, 1, STANDARD)


def test_a_repair_season_needs_damage_and_restores_a_level():
    saga = tower_saga()
    gregor = saga.character("gregor")
    assert gregor is not None
    assert sw.problems(saga, gregor, _plan(REPAIR))
    _project(saga).works.append(ProjectWork(kind=STRESS, damage=1))
    plan = _plan(REPAIR)
    assert not sw.problems(saga, gregor, plan)
    lab_apply.apply_supplement(saga, gregor, plan, sw.work(saga, gregor, plan, None))
    assert hp.damage_lost(_project(saga)) == 0


def test_a_rebuild_season_makes_the_first_shoddy_section_standard():
    saga = tower_saga()
    gregor = saga.character("gregor")
    assert gregor is not None
    plan = _plan(REBUILD)
    lab_apply.apply_supplement(saga, gregor, plan, sw.work(saga, gregor, plan, None))
    assert hp.quality(_project(saga)) == STANDARD


def test_a_season_with_no_project_is_stopped():
    saga = tower_saga()
    tandaline = saga.character("tandaline")
    assert tandaline is not None
    found = sw.problems(saga, tandaline, _plan())
    assert found and "master mason of no Hermetic Project" in found[0]


# -- saving -------------------------------------------------------------------


def test_projects_survive_a_save_and_reload():
    saga = tower_saga()
    storage.save_saga(saga)
    loaded = storage.load_saga(saga.id)
    assert loaded.covenants[0].hermetic_projects == saga.covenants[0].hermetic_projects


def test_a_damaged_project_record_is_reported_by_name():
    with pytest.raises(ValueError, match="Spire"):
        Covenant.from_dict(
            {
                "id": "c",
                "saga_id": "s",
                "name": "C",
                "hermetic_projects": [
                    {"name": "Spire", "works": [{"kind": "flying", "year": 1}]}
                ],
            }
        )


def test_an_older_save_loads_with_no_projects():
    covenant = Covenant.from_dict({"id": "c", "saga_id": "s", "name": "C"})
    assert covenant.hermetic_projects == []
    assert covenant.project_shown == ""


# -- tunnels ------------------------------------------------------------------


def test_tunnel_limits():
    by = {t.name: t for t in hp.TUNNELS}
    assert hp.tunnel_limit(by["Opening the Intangible Tunnel"], 20) == 20
    assert hp.tunnel_limit(by["The Cursèd Day"], 25) == 20
    assert hp.tunnel_limit(by["Wizard's Siege"], 30) == 20
    assert hp.tunnel_limit(by["The Evil Eye"], 15) == 20


def test_break_the_siege_reaches_below_its_level_and_two_magnitudes():
    # Errata p. 81: less than the level of this spell + 2 magnitudes.
    assert hp.break_the_siege_reaches(20, 29)
    assert not hp.break_the_siege_reaches(20, 30)


def test_spells_through_a_tunnel_are_touch_or_more_and_within_its_limit():
    spells = [
        ("a", 5, "Touch"),
        ("b", 25, "Voice"),
        ("c", 10, "Personal"),
        ("d", None, "Touch"),
    ]
    assert hp.through(spells, 20) == [0]


def test_an_aegis_must_be_penetrated_too_without_a_token():
    assert hp.penetrates(30, 20, None)
    assert not hp.penetrates(30, 20, 35)


def _magus(**spells: int) -> Character:
    return Character(
        id="corvinus",
        name="Corvinus",
        type="magus",
        characteristics=Characteristics(stamina=2),
        abilities=[Ability(name="Penetration", category="Arcane", xp=15)],
        spells_known=[KnownSpell("spell_the_curs_d_day")],
    )


def test_open_a_tunnel_is_offered_to_a_magus_who_knows_one():
    saga = Saga(id="s", name="S", characters=[_magus()])
    corvinus = saga.characters[0]
    assert tunnel_forms.offers(saga, corvinus)
    corvinus.spells_known = []
    assert isinstance(tunnel_forms.tunnel_form(saga, corvinus), Refuse)


def test_open_a_tunnel_multiplies_penetration_with_the_connection():
    saga = Saga(id="s", name="S", characters=[_magus()])
    corvinus = saga.characters[0]
    form = tunnel_forms.tunnel_form(saga, corvinus, Dice(5))
    assert isinstance(form, Form) and form.live is not None
    values = _values(form, level=25, lasts="Years or decades", sympathy_5=True)
    text = form.live(values)
    # Penetration 2 x (1 + 3 + 2) = 12; limit 20 for The Cursèd Day 25.
    assert "Penetration 2 x 6" in text and "+12" in text
    assert "up to level 20" in text
    said = form.apply(values)
    assert said and "The Cursèd Day" in said[0]
