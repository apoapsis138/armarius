"""The staged Hermetic Projects (Hermetic Projects pp. 9-118): a Burning
City, an Intangible Assassin and a Living Corpse. Their stages and the
lab seasons spent on them, a volcano's hazards on Take Harm, Vulcan's
Warning Bell, gathering an Arcane Connection, the Aegis problem, a
magus's death roll, and the Projects tab's sections for them."""

import random

from ars_magica_manager import actions, health, staged_projects
from ars_magica_manager import hermetic_projects as hpc
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.form_spec import DialogField
from ars_magica_manager.manors import manors_of
from ars_magica_manager.models import (
    Ability,
    Character,
    Covenant,
    HermeticProject,
    Laboratory,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.models.hermetic_projects import (
    BURNING_CITY,
    INTANGIBLE_ASSASSIN,
    LIVING_CORPSE,
    STAGED_KINDS,
)
from ars_magica_manager.models.traits import ScoredTrait
from ars_magica_manager.rules import dice, harm
from ars_magica_manager.rules import staged_projects as sp
from ars_magica_manager.sections import (
    PROJECTS_SECTION,
    STAGE_WORKS_SECTION,
    STAGED_SECTION,
    STAGED_STAGES_SECTION,
)


class Dice(random.Random):
    """A Random whose d10s come in the order given (0 a zero face)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *_args, **_kwargs) -> int:  # type: ignore[override]
        return self.faces.pop(0)


def project(kind: str = BURNING_CITY) -> HermeticProject:
    return HermeticProject(
        id="city", name="Vulcan's Hearth", kind=kind, stages=staged_projects.seed(kind)
    )


def saga(kind: str = BURNING_CITY) -> Saga:
    return Saga(
        id="staged",
        name="Staged",
        storyguide="Hedda",
        current_season="Spring",
        current_year=1220,
        covenants=[
            Covenant(
                id="cov",
                saga_id="staged",
                name="Etna",
                aegis_of_the_hearth=30,
                hermetic_projects=[project(kind)],
            )
        ],
        laboratories=[Laboratory(id="lab", covenant_id="cov", name="The Crater Lab")],
        characters=[
            Character(
                id="magus",
                name="Aelius",
                type="magus",
                covenant_id="cov",
                virtues_flaws=[VirtueFlawInstance(vf_id="vf_the_gift")],
                abilities=[Ability(name="Magic Lore", category="Arcane", xp=75)],
                personality_traits=[
                    ScoredTrait("Proud", 3),
                    ScoredTrait("Kind", -1),
                ],
            ),
            Character(id="grog", name="Brand", type="grog", covenant_id="cov"),
        ],
    )


def _values(form: Form, **changes) -> dict:
    values = {f.key: f.value for f in form.fields() if isinstance(f, DialogField)}
    values.update(changes)
    return values


def _covenant(found: Saga) -> Covenant:
    return found.covenants[0]


# -- the stages -----------------------------------------------------------------


def test_each_staged_project_starts_with_its_chapters_stages():
    for kind in STAGED_KINDS:
        stages = staged_projects.seed(kind)
        assert [s.name for s in stages] == sp.stage_names(kind)
        assert all(sp.stage_pages(kind, s.name) for s in stages)
    assert sp.stage_names(BURNING_CITY)[0] == "Find a volcano"


def test_beginning_a_staged_project_seeds_its_stages():
    found = saga()
    covenant = _covenant(found)
    form = hpc.begin_form(found, covenant)
    assert isinstance(form, Form)
    form.apply(_values(form, name="The Necropolis", kind=LIVING_CORPSE))
    made = covenant.hermetic_projects[-1]
    assert made.kind == LIVING_CORPSE
    assert [s.name for s in made.stages] == sp.stage_names(LIVING_CORPSE)
    assert covenant.project_shown == made.id


def test_a_staged_project_round_trips_with_its_stages_and_works():
    found = project()
    found.stages[0].done = True
    found.works.append(
        staged_projects.ProjectWork(name="Scent of Ash", stage=found.stages[0].id)
    )
    again = HermeticProject.from_dict(
        {
            **found.__dict__,
            "stages": [s.__dict__ for s in found.stages],
            "works": [w.__dict__ for w in found.works],
        },
        "Etna",
    )
    assert again.stages[0].done and again.works[0].stage == found.stages[0].id


def test_the_projects_tab_shows_a_staged_projects_sections():
    found = saga()
    tab = hpc.projects_tab(found, _covenant(found))
    ids = [part.section_id for part in tab.parts()]
    assert ids == [
        PROJECTS_SECTION,
        STAGED_SECTION,
        STAGED_STAGES_SECTION,
        STAGE_WORKS_SECTION,
    ]
    holder = manors_of(_covenant(found))
    facts = {f.label: f.value for f in staged_projects.staged_facts(found, holder)}
    assert facts["Stages done"] == "0 of 8"
    assert facts["Now"].startswith("Find a volcano (Hermetic Projects pp. 12-13)")
    assert hpc.progress(_covenant(found).hermetic_projects[0]) == "0 of 8"


def test_a_lab_season_spent_on_a_stage_goes_into_its_works():
    found = saga()
    city = _covenant(found).hermetic_projects[0]
    stage = city.stages[0]
    magus = found.character("magus")
    assert (stage.name, stage.id) in [
        (label.split(": ", 1)[1], value)
        for label, value in staged_projects.stage_options(found, magus)
    ]
    staged_projects.spend_season(found, magus, stage.id, "Scent of Ash", "Summer", 1220)
    work = city.works[-1]
    assert (work.name, work.stage, work.who, work.seasons) == (
        "Scent of Ash",
        stage.id,
        "magus",
        1,
    )
    holder = manors_of(_covenant(found))
    assert staged_projects.stages_grid(found, holder).rows[0][2:4] == ["1", "1"]


def test_the_plan_keeps_the_stage_it_is_spent_on():
    plan = SeasonPlan(
        character_id="magus",
        year=1220,
        season="Spring",
        activity="invent_spell",
        project_stage="abc",
    )
    assert SeasonPlan.from_dict(dict(plan.__dict__)).project_stage == "abc"


# -- the Burning City -------------------------------------------------------------


def test_lava_is_on_take_harm_with_hermetic_projects_in_play():
    found = saga()
    assert harm.volcanoes(found)
    names = [name for name, _ in harm.heat_table(found)]
    assert harm.LAVA in names
    assert harm.ALL_PRESETS[harm.LAVA] == 15
    assert any(p[0].startswith("Volcanic fumes") for p in harm.poison_table(found))
    found.books_in_play = []
    assert not harm.volcanoes(found)
    assert harm.LAVA not in [name for name, _ in harm.heat_table(found)]


def test_armour_is_no_help_once_lava_covers_half_the_body():
    assert harm.armour_counts({"preset": harm.LAVA, "coverage": "2", "armour": True})
    assert not harm.armour_counts(
        {"preset": harm.LAVA, "coverage": "3", "armour": True}
    )
    assert harm.armour_counts(
        {"preset": "Boiling mud", "coverage": "4", "armour": True}
    )


def test_take_harm_reads_lavas_bonus_and_its_fire():
    values = health._values({"kind": harm.INJURY, "preset": harm.LAVA, "coverage": "4"})
    assert values["bonus"] == 15 and values["harm_from"] == "fire"


def test_the_bell_warns_days_ahead_or_hours_or_not_at_all():
    assert sp.warning_bell(Dice(6)).words() == (
        "The bell rings 6 days before the eruption."
    )
    assert sp.warning_bell(Dice(0, 4)).words() == (
        "The bell rings 4 hours before the eruption."
    )
    assert sp.warning_bell(Dice(0, 0)).unit == ""


def test_warning_bell_keeps_its_roll_in_the_covenants_diary():
    found = saga()
    form = staged_projects.bell_form(found, _covenant(found), Dice(3))
    assert isinstance(form, Form)
    form.apply({})
    entry = _covenant(found).diary[-1]
    assert entry.name == "Warning Bell: Vulcan's Hearth"
    assert entry.details.startswith("The bell rings 3 days")


# -- the Intangible Assassin ---------------------------------------------------


def test_the_aegis_reaches():
    assert sp.guttering_reach(30) == 30
    assert sp.keystone_reach(20, 4) == 39


def test_gather_a_connection_keeps_it_in_a_laboratory():
    found = saga(INTANGIBLE_ASSASSIN)
    form = staged_projects.gather_form(found, _covenant(found))
    assert isinstance(form, Form)
    values = _values(form, quarry="grog", how="text")
    assert "weeks or months" in (form.live or (lambda _v: ""))(values)
    form.apply(values)
    held = found.laboratories[0].arcane_connections[-1]
    assert (held.to, held.lasts) == (
        "Brand: a book or lab text he has written lately",
        "Weeks or months",
    )
    work = _covenant(found).hermetic_projects[0].works[-1]
    stage = next(
        s for s in _covenant(found).hermetic_projects[0].stages if s.id == work.stage
    )
    assert (stage.name, work.seasons) == ("Gathering connections", 0)


def test_lower_an_aegis_works_out_both_spells():
    found = saga(INTANGIBLE_ASSASSIN)
    form = staged_projects.aegis_form(found, _covenant(found), Dice(5))
    assert isinstance(form, Form)
    live = form.live or (lambda _v: "")
    gutter = _values(form, level=30)
    assert "under 30: against 30" in live(gutter) and "too strong" in live(gutter)
    assert form.apply(gutter) == ["The Aegis holds."]
    keystone = _values(form, spell=sp.KEYSTONE, level=10, penetration=40)
    assert "a die of 6 or more" in live(keystone)
    assert form.apply(keystone)[0].endswith("under 30. The Aegis holds.")
    again = staged_projects.aegis_form(found, _covenant(found), Dice(7))
    assert isinstance(again, Form)
    assert again.apply(keystone)[0].endswith("under 32. The Aegis falls.")


def test_the_staged_commands_are_offered_only_on_their_kind():
    found = saga(INTANGIBLE_ASSASSIN)
    covenant = _covenant(found)

    class Facts:
        selected_covenant = covenant

        def active_section(self) -> str:
            return STAGED_SECTION

    def offered(action: str) -> bool:
        return actions._RECORD_RULES[action](Facts())  # type: ignore[arg-type]

    assert offered("gather_connection") and offered("lower_aegis")
    assert not offered("warning_bell") and not offered("death_roll")
    assert isinstance(staged_projects.bell_form(found, covenant), Refuse)


# -- the Living Corpse ----------------------------------------------------------


def test_the_death_chart():
    assert [sp.chart(n) for n in (1, 2, 3, 5, 7, 8, 10)] == [
        sp.NO_SPIRIT,
        sp.OTHER_REALM,
        sp.MINDLESS,
        sp.ANIMATING,
        sp.SPECTER,
        sp.SHADE,
        sp.APPARITION,
    ]


def test_the_death_contest():
    assert sp.contest(10, 12, False) == sp.OTHER_REALM
    assert sp.contest(10, 10, False) == sp.SPECTER
    assert sp.contest(16, 10, False) == sp.SHADE
    assert sp.contest(19, 10, False) == sp.APPARITION
    assert sp.contest(30, 10, True) == sp.NO_SPIRIT
    assert sp.ungifted(sp.APPARITION) == sp.SPECTER


def test_might_vis_and_decay():
    assert sp.starting_might("Medium", sp.SHADE) == 10
    assert sp.starting_might("Legendary", sp.APPARITION) == 50
    assert sp.vis_pawns(21) == 5
    assert (sp.decay(0), sp.decay(3), sp.decay(40), sp.decay(400)) == (0, -3, -5, None)
    assert sp.magical_air("Gentle") == ""
    assert sp.magical_air("Blatant") == "Blatant Magical Air"


def test_a_death_roll_is_kept_in_his_diary_and_on_the_transformation():
    found = saga(LIVING_CORPSE)
    form = staged_projects.death_form(found, _covenant(found), Dice(8))
    assert isinstance(form, Form)
    lines = form.apply(_values(form, who="magus", option="chart", days=2))
    assert lines[1] == "[b]A magic ghost: a shade.[/]"
    assert "Magic Might 10" in lines[2] and "720 experience" in lines[2]
    assert "Proud +6" in lines[3]
    assert "-2 each" in lines[4]
    entry = found.character("magus").diary[-1]
    assert entry.name == "Death Roll: Vulcan's Hearth"
    work = _covenant(found).hermetic_projects[0].works[-1]
    assert work.name == "Aelius's death"


def test_option_two_rolls_his_lore_against_his_traits():
    found = saga(LIVING_CORPSE)
    magus = found.character("magus")
    # His die 9 + Magic Lore 5 = 14; the storyguide's 2 + traits 4 = 6:
    # eight higher, a shade.
    lines = staged_projects.death_lines(
        found, magus, {"option": "contest", "power": "Medium"}, Dice(9, 2)
    )
    assert "= 14" in lines[0] and "= 6" in lines[0]
    assert lines[1] == "[b]A magic ghost: a shade.[/]"
    assert dice.simple_die(Dice(0)) == 10
