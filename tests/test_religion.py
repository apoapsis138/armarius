"""A character's religion and the Religion chapter: the religion as a list
(old free-text saves read into it), what each faith offers and who may
take it (RoP: The Divine pp. 38-42, 87-88, 124-125; The Church pp. 11-13,
21, 26, 34-36, 46), and Edit Religion."""

from dataclasses import replace

import pytest

from ars_magica_manager import artwork
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import religion as religion_forms
from ars_magica_manager.models import (
    Character,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.models.character import Background
from ars_magica_manager.models.religion import RELIGIONS, religion_from_text
from ars_magica_manager.rules import faiths
from ars_magica_manager.rules.season_work import church as church_work
from ars_magica_manager.sections import FAITH_SECTION


def _person(religion: str = "", *vfs: str) -> Character:
    c = Character(id="c", name="Anna", type="companion")
    c.background.religion = religion
    c.background.confidence_points = 1
    c.virtues_flaws = [VirtueFlawInstance(v) for v in vfs]
    return c


def _faith_page(saga: Saga) -> menu_forms.Page:
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="c")
    return replace(page, section=FAITH_SECTION)


@pytest.mark.parametrize(
    ("typed", "read"),
    [
        ("", ""),
        ("Christian", "Christian"),
        ("Roman Catholic", "Christian"),
        ("Orthodox Christian, in name", "Christian"),
        ("Islam", "Muslim"),
        ("Judaism", "Jewish"),
        ("Zoroastrian", "Mazdean"),
        ("Norse", "Pagan"),
        ("Worships the sun", "Other"),
    ],
)
def test_a_religion_typed_before_the_list_is_read_into_it(typed, read):
    assert religion_from_text(typed) == read
    assert Background.from_dict({"religion": typed}).religion == read


def test_every_religion_has_a_faith_and_an_icon():
    assert set(faiths.FAITHS) == set(RELIGIONS)
    for faith in faiths.FAITHS.values():
        assert artwork.icon(faith.icon).exists()


def test_a_blank_religion_counts_as_christian():
    assert faiths.religion(_person()) == "Christian"
    assert faiths.faith(_person()).church


@pytest.mark.parametrize(
    ("religion", "offered"),
    [
        (
            "Christian",
            {
                "invoke_saint",
                "patron_saint",
                "act_of_piety",
                "gods_aid",
                # The path's own steps ask the path itself (mystic_paths).
                "spiritual_path",
                "monistic_revelation",
            },
        ),
        ("Muslim", {"invoke_baraka", "hajj", "gods_aid"}),
        ("Jewish", {"gods_aid"}),
        ("Mazdean", {"invoke_saint"}),
        ("Pagan", set()),
        ("Other", set()),
    ],
)
def test_each_faith_offers_its_own(religion, offered):
    person = _person(religion)
    may = {
        action
        for faith in faiths.FAITHS.values()
        for action in faith.actions
        if faiths.may(person, action)
    }
    assert may == offered


def test_the_checks_beyond_faith():
    person = _person()
    # A grog can't spend Confidence on God's aid; True Faith lets him.
    person.type = "grog"
    assert not faiths.may(person, "gods_aid")
    person.virtues_flaws.append(VirtueFlawInstance("vf_true_faith"))
    assert faiths.may(person, "gods_aid")
    # A mystic path: Pious and tied to the Divine (True Faith here).
    assert not faiths.may(person, "mystic_path")
    person.personality_traits = [ScoredTrait("Pious", 2)]
    assert faiths.may(person, "mystic_path")
    # Holy Orders: a clerical Social Status.
    assert not faiths.may_hold_orders(person)
    assert faiths.may_hold_orders(_person("", "vf_priest"))
    # Never an animal.
    person.animal = "a dog"
    assert not faiths.may(person, "invoke_saint")


def test_only_a_clergyman_exorcises_and_only_a_christian_is_ordained():
    layman = _person()
    assert not faiths.may_exorcise(layman)
    # A monk who is Religious only isn't clergy until ordained.
    monk = _person("", "vf_religious")
    assert faiths.may_hold_orders(monk) and not faiths.may_exorcise(monk)
    monk.church.grade = "Exorcist"
    assert faiths.may_exorcise(monk)
    assert faiths.may_exorcise(_person("", "vf_clerk"))
    plan = SeasonPlan("c", 1220, "Summer", "ordination")
    saga = Saga(id="s", name="S", characters=[layman])
    assert not church_work._ordination_check(saga, layman, plan)
    layman.background.religion = "Muslim"
    assert "Only a Christian" in church_work._ordination_check(saga, layman, plan)[0]


def test_the_chapter_shows_with_the_books_of_the_faiths():
    person = _person()
    saga = Saga(id="s", name="S", characters=[person], books_in_play=["HoH:S"])
    assert not religion_forms.shows(saga, person)
    saga.books_in_play = ["RoP:D"]
    assert religion_forms.shows(saga, person)
    assert not religion_forms.church_shown(saga, person)
    saga.books_in_play = ["TC"]
    assert religion_forms.church_shown(saga, person)


def test_the_faith_section_offers_what_his_faith_allows():
    person = _person()
    saga = Saga(id="s", name="S", characters=[person], books_in_play=["TC", "RoP:D"])
    page = _faith_page(saga)
    labels = [i.label for i in menu_forms.placed(page, "Faith")]
    assert labels == [
        "Invoke a Saint",
        "Patron Saint",
        "Indulgence, Vigil or Fast",
        "Invoke God's Aid",
    ]
    person.background.religion = "Muslim"
    assert [i.label for i in menu_forms.placed(page, "Faith")] == [
        "Invoke Baraka",
        "The Hajj",
        "Invoke God's Aid",
    ]
    assert not available("invoke_saint", page)


def test_the_faith_section_says_what_he_holds():
    person = _person()
    person.personality_traits = [ScoredTrait("Pious", 1)]
    facts = dict(religion_forms.faith_facts(person))
    assert facts["Religion"].startswith("Christian")
    assert "not set" in facts["Religion"]
    assert facts["Pious"] == "+1"
    person.background.religion = "Jewish"
    facts = dict(religion_forms.faith_facts(person))
    assert "Patron saint" not in facts and facts["Religion"] == "Jewish"
    assert "rabbi" in religion_forms.faith_text(person)


def test_edit_religion_sets_it_from_the_list():
    person = _person()
    saga = Saga(id="s", name="S", characters=[person])
    form = religion_forms.religion_form(saga, person)
    (field,) = form.fields()
    assert [v for _, v in field.options] == list(RELIGIONS)
    form.apply({"religion": "Jewish"})
    assert person.background.religion == "Jewish"
    form.apply({"religion": None})
    assert person.background.religion == ""
