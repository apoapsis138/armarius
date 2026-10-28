"""A cleric's career (The Church pp. 33-38, 46-48; DE pp. 74, 104, 106,
107, 411): the grades and their examinations, what ordination brings,
exorcism, the canon courts and petitions, the Ordination season, and where
the Church tab and its commands are offered."""

import random
from dataclasses import asdict, replace

import pytest

from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Form
from ars_magica_manager.forms import church as church_forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import religion as religion_forms
from ars_magica_manager.models import (
    Ability,
    CanonCase,
    Character,
    ChurchCareer,
    Ordination,
    Petition,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.models.clergy import (
    ACCUSED,
    AUDIENCE,
    EXCOMMUNICATED,
    GUILTY,
    IRREGULAR,
    WRITTEN,
)
from ars_magica_manager.rules import activities
from ars_magica_manager.rules import clergy as cl
from ars_magica_manager.rules.season_work import work as season_work
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.seasons.lab_apply import apply_supplement


class Faces(random.Random):
    """A Random whose d10 faces come from a list (0-9)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *_args, **_kwargs) -> int:  # type: ignore[override]
        return self.faces.pop(0)


def _clerk(*vfs: str) -> Character:
    """Int +1, Church Lore 2 (as Organization Lore), Civil and Canon Law 1."""
    c = Character(id="c", name="Leandro", type="companion")
    c.characteristics.intelligence = 1
    c.characteristics.communication = 1
    c.characteristics.presence = 3
    c.abilities = [
        Ability("Organization Lore: Church", xp=ability_xp(2)),
        Ability("Civil and Canon Law", xp=ability_xp(1)),
    ]
    c.virtues_flaws = [VirtueFlawInstance(v) for v in vfs]
    return c


def _saga(character: Character) -> Saga:
    saga = Saga(id="s", name="S")
    saga.characters.append(character)
    return saga


# -- the grades and the examination (pp. 33-34) --


def test_the_grades_and_their_ease_factors():
    assert [(g.name, g.ability, g.ease) for g in cl.GRADES] == [
        ("Doorkeeper", cl.CHURCH_LORE, 3),
        ("Lector", cl.CHURCH_LORE, 6),
        ("Exorcist", cl.CANON_LAW, 3),
        ("Acolyte", cl.CANON_LAW, 6),
        ("Sub-deacon", cl.CHURCH_LORE, 9),
        ("Deacon", cl.CANON_LAW, 9),
        ("Priest", cl.CHURCH_LORE, 12),
        ("Bishop", "", 0),
    ]
    assert [g.minor for g in cl.GRADES[:5]] == [True] * 4 + [False]


@pytest.mark.parametrize(
    ("total", "result"),
    [
        (19, cl.LEARNED),  # more than double 9
        (18, cl.ORDAINED),  # exactly double: no Reputation
        (9, cl.ORDAINED),
        (8, cl.IGNORANT),
        (3, cl.IGNORANT),  # missed by exactly 6: a house ruling, passes
        (2, cl.FAILED),  # missed by 7
    ],
)
def test_the_examination_result_bands(total, result):
    assert cl.exam_result(total, 9) == result


def test_a_botch_is_its_own_result():
    assert cl.exam_result(30, 3, botched=True) == cl.BOTCHED


def test_the_next_grade_and_the_examination_terms():
    c = _clerk()
    c.church.grade = "Exorcist"
    grade = cl.next_grade(c.church)
    assert grade is not None and grade.name == "Acolyte"
    terms = cl.exam_terms(c, grade)
    assert (terms.intelligence, terms.score, terms.base) == (1, 1, 2)
    c.church.grade = "Priest"
    assert cl.next_grade(c.church) is None  # a bishop is elected
    assert cl.examinable(ChurchCareer())[0].name == "Doorkeeper"


def test_examining_with_a_typed_die():
    c = _clerk()
    record = cl.examine_with(c, cl.BY_NAME["Lector"], 4)
    assert (record.total, record.ease, record.result) == (7, 6, cl.ORDAINED)
    botched = cl.examine(None, c, cl.BY_NAME["Lector"], Faces(0, 0))
    assert botched.botched and botched.result == cl.BOTCHED and botched.total == 0


# -- what ordination brings (pp. 25-26, 34; DE pp. 74, 104, 106, 107) --


def _ordained(c: Character, grade: str, result: str = cl.ORDAINED) -> list[str]:
    g = cl.BY_NAME[grade]
    return cl.ordain(
        c, Ordination(grade, ability=g.ability, ease=g.ease, result=result)
    )


def test_a_first_ordination_gives_clerk_a_faith_point_and_the_grade():
    c = _clerk()
    said = _ordained(c, "Doorkeeper")
    assert c.church.grade == "Doorkeeper"
    assert c.background.faith_points == 1
    assert [vf.vf_id for vf in c.virtues_flaws] == [cl.CLERK]
    assert "Social Status: Clerk." in said
    assert cl.faith_points_from_orders(c.church) == 1


def test_another_social_status_is_swapped_never_kept_beside_clerk():
    c = _clerk("vf_covenfolk")
    change = cl.status_change(c, "Doorkeeper")
    assert change.swaps and cl.swap_names(change) == ("Covenfolk", "Clerk")
    said = _ordained(c, "Doorkeeper")
    assert [vf.vf_id for vf in c.virtues_flaws] == [cl.CLERK]
    assert "Social Status: Clerk." in said


def test_a_declined_swap_leaves_his_own_status_alone():
    c = _clerk("vf_covenfolk")
    g = cl.BY_NAME["Doorkeeper"]
    said = cl.ordain(
        c,
        Ordination("Doorkeeper", ability=g.ability, ease=g.ease, result=cl.ORDAINED),
        swap=False,
    )
    assert [vf.vf_id for vf in c.virtues_flaws] == ["vf_covenfolk"]
    assert any("swap it for Clerk" in line for line in said)


@pytest.mark.parametrize("old", [cl.CLERK, cl.RELIGIOUS])
def test_a_priest_ordination_replaces_clerk_or_religious(old):
    c = _clerk(old, "vf_wealthy")
    _ordained(c, "Priest")
    assert sorted(vf.vf_id for vf in c.virtues_flaws) == [
        cl.PRIEST_STATUS,
        "vf_wealthy",
    ]


def test_a_friar_becomes_a_priest_and_a_bishop_is_warned():
    friar = _clerk(cl.MENDICANT_FRIAR)
    _ordained(friar, "Priest")
    assert [vf.vf_id for vf in friar.virtues_flaws] == [cl.PRIEST_STATUS]
    bishop = _clerk(cl.PRIEST_STATUS)
    said = _ordained(bishop, "Bishop", cl.ELECTED)
    assert any("Senior Clergy" in line for line in said)
    assert [vf.vf_id for vf in bishop.virtues_flaws] == [cl.PRIEST_STATUS]


def test_reputations_for_learning_and_ignorance():
    c = _clerk()
    _ordained(c, "Doorkeeper", cl.LEARNED)
    [rep] = c.reputations
    assert (rep.name, rep.score, rep.type) == (
        "Learned in Church Lore",
        1,
        "Ecclesiastical",
    )
    _ordained(c, "Lector", cl.IGNORANT)
    # A Reputation experience point taken off the good one: 1 level is 5 xp.
    assert (rep.score, rep.deeds) == (0, 4)
    _ordained(c, "Exorcist", cl.IGNORANT)
    assert [r.name for r in c.reputations][-1] == "Learned in Civil and Canon Law"
    assert c.reputations[-1].score == -1


def test_a_failure_and_a_botch_ordain_no_one():
    c = _clerk()
    _ordained(c, "Doorkeeper", cl.FAILED)
    assert c.church.grade == "" and c.background.faith_points == 0
    assert len(c.church.ordinations) == 1
    _ordained(c, "Doorkeeper", cl.BOTCHED)
    assert c.church.barred


def test_a_major_order_is_celibate():
    c = _clerk(cl.CLERK)
    c.church.grade = "Acolyte"
    assert "A major order: celibate from now on." in _ordained(c, "Sub-deacon")


# -- toward the priesthood (p. 35) --


def test_the_priests_requirements_are_warned():
    c = _clerk("vf_dwarf", "vf_bastard")
    found = {r.label: r for r in cl.priest_requirements(_saga(c), c, 22)}
    assert found["22 years old"].met is False
    assert found["freeborn"].met is True
    assert found["legitimate"].met is False
    assert "Dwarf" in found["sound of body and mind"].why
    assert found["a benefice or curacy"].met is None
    c.church.benefice = "Curate of St Martin"
    assert cl.priest_requirements(_saga(c), c, None)[-1].met is True


# -- exorcism (p. 34; DE p. 411) --


def test_the_exorcism_total():
    total, terms = cl.exorcism_bonus(
        "Priest", 2, holy_water=True, crucifix=True, aura_realm="Divine", aura=3
    )
    # 2 Points +6, an exorcist (every grade from Exorcist up) +1, water and
    # cross +2, a Divine aura +3.
    assert total == 12
    assert "ordained exorcist +1" in terms
    lay, _ = cl.exorcism_bonus(
        "", 0, holy_water=False, crucifix=False, aura_realm="Infernal", aura=5
    )
    # At least one Point; other realms' auras don't hinder a Divine power.
    assert lay == 3
    lector, _ = cl.exorcism_bonus(
        "Lector", 1, holy_water=False, crucifix=False, aura_realm="Magic", aura=4
    )
    assert lector == 3


def test_the_exorcism_form_rolls_against_the_might():
    c = _clerk()
    c.church.grade = "Exorcist"
    form = church_forms.exorcism_form(_saga(c), c, Faces(9))
    values = {f.key: f.value for f in form.fields()}
    assert "= [b]6 + die[/]" in form.live(values)  # type: ignore[misc]
    said = form.apply(values)
    assert said[0] == "Exorcism: the die shows 9, total 15 against 10."
    assert said[1] == "The demon is exorcised."


# -- the canon courts (pp. 35-38) --


def test_an_excommunication_shows_as_his_standing():
    c = _clerk()
    form = church_forms.canon_form(_saga(c), c)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    values |= {"verdict": GUILTY, "punishment": cl.EXCOMMUNICATION, "role": ACCUSED}
    assert "Shown on Holy Orders as his standing." in form.live(values)  # type: ignore[misc]
    form.apply(values)
    assert c.church.standing == EXCOMMUNICATED
    assert c.church.cases[0].punishment == cl.EXCOMMUNICATION


def test_compurgation_and_guilty_together_are_questioned():
    text = church_forms.canon_live({"compurgation": True, "verdict": GUILTY})
    assert "is Guilty right?" in text


def test_an_irregular_cleric_is_warned_off_his_faith_points():
    c = _clerk()
    c.church.standing = IRREGULAR
    assert not cl.may_use_faith_points(c.church)
    form = church_forms.exorcism_form(_saga(c), c)
    values = {f.key: f.value for f in form.fields()}
    assert "Irregular" in form.live(values)  # type: ignore[misc]


# -- petitions (pp. 46-48) --


def test_a_written_petition_with_its_modifiers():
    p = Petition(
        "Rent the mill-land",
        ease=12,
        method=WRITTEN,
        characteristic=1,
        lore=2,
        testimony=True,
        lay=1,
        donation=5,  # no more than +3 counts
        arguments={cl.CANON_LAW: 2, "Intrigue": 1},
        argument_rolls={cl.CANON_LAW: 11, "Intrigue": 8},
    )
    # 1 + 2 + 1 + 1 + 3 + 2 (argued, rolled 11) + 0 (Intrigue rolled 8).
    assert cl.petition_total(p) == 10
    assert cl.petition_result(p) == cl.REFUSED
    assert cl.decider(12) == "the bishop"


def test_an_audience_bears_the_gift_and_a_scribe_stands_in_for_a_letter():
    audience = Petition("x", ease=6, method=AUDIENCE, characteristic=3, lore=2, gift=3)
    assert cl.petition_total(audience) == 2
    letter = replace(audience, method=WRITTEN, scribe="Calum", scribe_total=4)
    assert cl.petition_total(letter) == 4  # the Gift doesn't touch a letter
    assert cl.decider(6) == "the local priest"
    assert cl.decider(16) == "the papal curia"


def test_a_botched_argument_is_a_penalty():
    p = Petition("x", arguments={"Intrigue": 2}, argument_botches=["Intrigue"])
    assert cl.argument_counts(p, "Intrigue") == -2


def test_an_appeal_overturns_compromises_or_fails():
    p = Petition("x", appeal=True, original=10, characteristic=13)
    assert cl.petition_ease(p) == 13
    assert cl.petition_result(p) == cl.OVERTURNED
    assert cl.petition_result(replace(p, characteristic=8)) == cl.COMPROMISE
    assert cl.petition_result(replace(p, characteristic=7)) == cl.REFUSED
    late = replace(p, late=True)
    assert cl.petition_total(late) == 10  # -3 in a later season


def test_petition_the_church_rolls_the_arguments_when_made():
    c = _clerk()
    saga = _saga(c)
    form = church_forms.petition_form(saga, c, rng=Faces(7))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    values |= {
        "ask": "Access to the cathedral library",
        "example": "Access to the cathedral library",
        "argue_law": 2,
        "clergy": "3",
    }
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    [made] = c.church.petitions
    assert made.ease == 9
    # Int 1 + Civil and Canon Law 1 + die 7 = 9: the argument counts.
    assert made.argument_rolls == {cl.CANON_LAW: 9}
    # Com 1 + Church Lore 2 + clergy 3 + argument 2.
    assert cl.petition_total(made) == 8


def test_a_petition_needs_its_ease_factor():
    assert church_forms._petition_problem({"example": ""}) is not None
    assert church_forms._petition_problem({"example": "", "ease": 9}) is None


# -- the Ordination season (p. 33) --


def _plan(saga: Saga, c: Character, **kwargs) -> SeasonPlan:
    return SeasonPlan(
        c.id,
        saga.current_year,
        saga.current_season,
        "ordination",
        [XpAllocation("ability:Civil and Canon Law")],
        **kwargs,
    )


def test_the_ordination_season_previews_the_examination():
    c = _clerk()
    c.church.grade = "Exorcist"
    saga = _saga(c)
    found = season_work(saga, c, _plan(saga, c), None)
    assert found.ordination is None
    assert found.notes[0].startswith(
        "Examination for Acolyte: Intelligence +1 + Civil and Canon Law 1"
    )


def test_the_ordination_season_examines_and_ordains():
    c = _clerk(cl.CLERK)
    c.church.grade = "Exorcist"
    saga = _saga(c)
    plan = _plan(saga, c, die=9, examiner="The bishop")
    found = season_work(saga, c, plan, random.Random(1))
    assert found.ordination is not None
    assert (found.ordination.total, found.ordination.result) == (11, cl.ORDAINED)
    apply_supplement(saga, c, plan, found)
    assert c.church.grade == "Acolyte"
    assert c.church.ordinations[-1].examiner == "The bishop"
    assert c.background.faith_points == 1
    assert c.diary[-1].name == "Ordination: Acolyte"


def test_a_barred_or_finished_cleric_cant_plan_an_ordination():
    c = _clerk()
    saga = _saga(c)
    c.church.barred = True
    assert activities.problems(c, _plan(saga, c), saga)
    c.church.barred = False
    c.church.grade = "Priest"
    assert activities.problems(c, _plan(saga, c), saga)


def test_the_season_form_reads_the_grade_sought():
    c = _clerk()
    fields = church_forms.season_fields(c, None, lambda *_a: lambda _v: True)
    grade = next(f for f in fields if f.key == "ordination_grade")
    assert grade.value == "Doorkeeper"
    [(_, read)] = church_forms.READS
    assert read({"ordination_grade": "Lector", "ordination_die": 4})["title"] == (
        "Lector"
    )


# -- the tab and where its commands are offered --


def test_the_church_tab_shows_only_with_a_grade_a_petition_or_a_case():
    c = _clerk()
    assert not cl.has_church_tab(c)
    c.church.petitions.append(Petition("x"))
    assert cl.has_church_tab(c)
    c.church.petitions.clear()
    c.church.cases.append(CanonCase("Tithes"))
    assert cl.has_church_tab(c)
    c.church.cases.clear()
    c.church.grade = "Doorkeeper"
    assert cl.has_church_tab(c)


def test_the_church_sections_follow_faith_on_the_religion_tab():
    c = _clerk()
    saga = _saga(c)
    saga.books_in_play = ["TC"]
    # A layman Christian: Petitions and the Canon Court, but no orders.
    assert religion_forms.church_shown(saga, c)
    assert not religion_forms.orders_shown(saga, c)
    c.virtues_flaws.append(VirtueFlawInstance(cl.CLERK))
    assert religion_forms.orders_shown(saga, c)
    # Not a Christian's: none, until he has a career on record.
    c.background.religion = "Jewish"
    assert not religion_forms.church_shown(saga, c)
    c.church.cases.append(CanonCase("Usury"))
    assert religion_forms.church_shown(saga, c)
    # More no longer offers them: Add on the lists and Edit Holy Orders do.
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="c")
    offered = {i.action for i in menu_forms.more_items(page)}
    assert not offered & {"petition_church", "canon_case", "holy_orders"}


def test_the_lists_say_when_they_are_empty():
    c = _clerk()
    assert church_forms.ordination_rows(c)[0][0] is None
    assert church_forms.petition_rows(c)[0][0] is None
    assert church_forms.canon_rows(c)[0][0] is None
    assert church_forms.petitions_title(c.church) == "Petitions"


def test_the_holy_orders_text_shows_the_ladder_and_the_next_grade():
    c = _clerk(cl.CLERK, "vf_dwarf")
    c.church.grade = "Exorcist"
    c.background.year_born = 1192
    saga = _saga(c)
    text = church_forms.orders_text(saga, c)
    assert "Grade:[/] Exorcist (minor orders)" in text
    assert "Social Status:[/] Clerk" in text
    assert "[b]→ Acolyte[/]" in text
    assert "Next:[/] Acolyte: Intelligence +1 + Civil and Canon Law 1" in text
    assert "28 years old (25 needed) ✓" in text
    assert "sound of body and mind (Dwarf): a dispensation" in text


# -- saving --


def test_a_career_round_trips_and_a_bad_value_is_named():
    career = ChurchCareer(
        grade="Lector",
        ordinations=[Ordination("Doorkeeper", die=4)],
        petitions=[Petition("x", arguments={cl.CANON_LAW: 2})],
        cases=[CanonCase("Slander")],
    )
    assert ChurchCareer.from_dict(asdict(career)) == career
    with pytest.raises(ValueError, match="The petition 'x': ease"):
        Petition.from_dict({"ask": "x", "ease": "lots"})
    with pytest.raises(ValueError, match="verdict"):
        CanonCase.from_dict({"charge": "Slander", "verdict": "maybe"})
