"""Default Interests: the interests a new character starts with, by its
type (the approved design, not a book rule), with Session & Reputation
always on."""

from __future__ import annotations

import pytest

from ars_magica_manager import (
    catalog,
    character_templates,
    creation,
    deeds,
    default_interests,
    storage,
)
from ars_magica_manager import grog_templates as gt
from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.forms import character as character_forms
from ars_magica_manager.forms import interests, menu_steps, more
from ars_magica_manager.forms import world as world_forms
from ars_magica_manager.models import (
    SKETCH,
    Agent,
    AnimalForm,
    Character,
    CharacterType,
    Saga,
)


def _new(character_type: CharacterType, *, animal: bool = False) -> Character:
    character = Character(id="c", name="C", type=character_type)
    if animal:
        character.animal = AnimalForm(species="Dog")
    return character


@pytest.mark.parametrize(
    ("character_type", "animal", "expected"),
    [
        ("magus", False, {deeds.RESEARCH, deeds.TRIBUNAL}),
        ("companion", False, {deeds.RELIGION}),
        ("mythic companion", False, {deeds.RELIGION}),
        ("grog", False, {deeds.COVENFOLK, deeds.CRAFT}),
        ("grog", True, {deeds.COVENFOLK}),
    ],
)
def test_each_type_starts_with_its_own_interests_and_the_session(
    character_type: CharacterType, animal: bool, expected: set[str]
):
    found = default_interests.defaults(_new(character_type, animal=animal))
    assert {interest for interest, _ in found} == expected | {deeds.SESSION}


def test_each_default_says_why_it_is_on():
    assert default_interests.defaults(_new("grog", animal=True)) == [
        (deeds.SESSION, "every character"),
        (deeds.COVENFOLK, "an animal grog"),
    ]


@pytest.mark.parametrize("in_creation", [True, False])
def test_a_save_from_before_defaults_keeps_its_own_interests(in_creation: bool):
    old = Character.from_dict(
        {
            "id": "k",
            "name": "K",
            "type": "grog",
            "in_creation": in_creation,
            "interests_off": [deeds.SCHOLARLY],
        }
    )
    assert old.interests_chosen
    assert deeds.interests_off(old) == [deeds.SCHOLARLY]


def test_a_save_whose_interests_chosen_isnt_a_yes_or_no_is_refused():
    with pytest.raises(ValueError, match="interests_chosen"):
        storage.saga_from_data(
            {
                "id": "s",
                "name": "S",
                "characters": [
                    {"id": "k", "name": "K", "type": "grog", "interests_chosen": "no"}
                ],
            }
        )


def test_a_character_made_in_code_keeps_every_interest_on():
    made = Character(id="p", name="P", type="grog", in_creation=True)
    assert made.interests_chosen and deeds.interests_off(made) == []


def _unchosen(character_type: CharacterType) -> Character:
    character = _new(character_type)
    character.in_creation = True
    character.interests_chosen = False
    return character


def _on(character: Character) -> list[str]:
    off = deeds.interests_off(character)
    return [i for i in deeds.OPTIONAL if deeds.applies(character, i) and i not in off]


def test_an_unchosen_character_in_creation_has_only_its_defaults_on():
    grog = _unchosen("grog")
    grog.interests_off = [deeds.COVENFOLK]
    assert _on(grog) == [deeds.CRAFT, deeds.COVENFOLK]
    magus = _unchosen("magus")
    assert _on(magus) == [deeds.RESEARCH, deeds.TRIBUNAL]
    assert deeds.HERMETIC_MYSTERIES in deeds.interests_off(magus)


def test_a_record_still_keeps_its_interest_on_over_the_defaults():
    grog = _unchosen("grog")
    grog.agents = [Agent(name="A")]
    assert deeds.AGENTS not in deeds.interests_off(grog)


def _with_agent(character: Character) -> Character:
    character.agents = [Agent(name="A")]
    return character


def test_keeping_the_defaults_keeps_what_a_record_held_on():
    saga = Saga(id="s", name="S")
    grog = _with_agent(creation.add_character(saga, "New", "grog", None))
    creation.set_in_creation(saga, grog, False)
    grog.agents = []
    assert deeds.AGENTS not in deeds.interests_off(grog)


def test_saving_edit_interests_keeps_what_a_record_held_on():
    grog = _with_agent(_unchosen("grog"))
    form = interests.interests_form(Saga(id="s", name="S"), grog, more.LABELS)
    form.apply({f.key: f.value for f in form.fields()})
    grog.agents = []
    assert deeds.AGENTS not in deeds.interests_off(grog)


def test_a_ready_to_play_template_keeps_what_a_record_holds_on():
    template = character_templates.find("tpl_grizzled_veteran")
    assert template is not None
    saga = Saga(id="s", name="S", current_year=1220)
    made = _with_agent(creation.add_character(saga, "New", "grog", None))
    character_templates.apply(saga, made, template, {})
    made.agents = []
    assert deeds.AGENTS not in deeds.interests_off(made)
    assert deeds.KNIGHTLY in deeds.interests_off(made)


def test_a_sketch_covenants_new_magus_starts_with_the_magus_defaults():
    saga = Saga(id="s", name="S")
    covenant = creation.add_covenant(saga, "Fengheld")
    add = world_forms.magus_ops(saga, covenant).add
    assert add is not None
    form = add()
    assert isinstance(form, Form)
    form.apply({f.key: f.value for f in form.fields()} | {"name": "Tytus"})
    (magus,) = saga.characters
    assert magus.interests_chosen and _on(magus) == ON["magus"]


@pytest.mark.parametrize("why", ["chosen", "in play"])
def test_a_chosen_or_in_play_character_keeps_its_stored_interests(why: str):
    grog = _unchosen("grog")
    if why == "chosen":
        grog.interests_chosen = True
    else:
        grog.in_creation = False
    grog.interests_off = [deeds.KNIGHTLY]
    assert deeds.interests_off(grog) == [deeds.KNIGHTLY]


def test_edit_interests_opens_on_the_defaults_and_saving_makes_them_the_players():
    grog = _unchosen("grog")
    form = interests.interests_form(Saga(id="s", name="S"), grog, more.LABELS)
    values = {f.label: f.value for f in form.fields()}
    assert [label for label, ticked in values.items() if ticked] == [
        deeds.CRAFT,
        deeds.COVENFOLK,
    ]
    assert grog.interests_off == [] and not grog.interests_chosen
    form.apply({f.key: f.value or f.label == deeds.SCHOLARLY for f in form.fields()})
    assert grog.interests_chosen
    assert _on(grog) == [deeds.SCHOLARLY, deeds.CRAFT, deeds.COVENFOLK]


#: Each type's defaults besides Session & Reputation, in deeds' order.
ON = {
    "magus": [deeds.RESEARCH, deeds.TRIBUNAL],
    "companion": [deeds.RELIGION],
    "mythic companion": [deeds.RELIGION],
    "grog": [deeds.CRAFT, deeds.COVENFOLK],
}


@pytest.mark.parametrize("character_type", list(ON))
def test_a_new_character_starts_with_its_defaults(character_type: CharacterType):
    saga = Saga(id="s", name="S")
    made = creation.add_character(saga, "New", character_type, None)
    assert made.in_creation and not made.interests_chosen
    assert _on(made) == ON[character_type]


def test_a_new_grog_made_an_animal_starts_with_the_animal_defaults():
    saga = Saga(id="s", name="S")
    hound = creation.add_character(saga, "Hound", "grog", None)
    hound.animal = AnimalForm(species="Dog")
    assert _on(hound) == [deeds.COVENFOLK]


def _made_from(template: object) -> Character:
    saga = Saga(id="s", name="S", current_year=1220)
    if isinstance(template, gt.GrogTemplateDef):
        made = creation.add_character(saga, "New", "grog", None)
        variant = gt.variants(template)[0]
        choices = gt.Choices(
            variant=0,
            age=0,
            status=variant.statuses[0],
            virtues_flaws=[gt.instance(e) for e in variant.virtues_flaws],
        )
        names = {blank: "X" for blank in gt.blanks(template, choices)}
        gt.apply(saga, made, template, choices, names)
    else:
        assert isinstance(template, character_templates.CharacterTemplateDef)
        made = creation.add_character(saga, "New", template.type, None)
        names = {blank: "X" for blank in character_templates.blanks(template)}
        character_templates.apply(saga, made, template, names)
    return made


def test_a_grog_template_leaves_the_defaults_to_follow_the_grog():
    grog = _made_from(catalog.load_grog_template_catalog()[0])
    assert grog.in_creation and not grog.interests_chosen
    assert _on(grog) == ON["grog"]


@pytest.mark.parametrize("template_id", ["tpl_knight", "tpl_tremere"])
def test_a_ready_to_play_template_starts_in_play_with_its_defaults(template_id: str):
    template = character_templates.find(template_id)
    assert template is not None
    made = _made_from(template)
    assert not made.in_creation and made.interests_chosen
    assert _on(made) == ON[template.type]


def _edit_info(saga: Saga, character: Character, **changes: object) -> None:
    values = {
        f.key: f.value for f in character_forms.character_info_fields(saga, character)
    }
    character_forms.apply_character_info(saga, character, values | changes)


def test_a_type_change_in_creation_hands_the_interests_back_to_the_defaults():
    saga = Saga(id="s", name="S")
    made = creation.add_character(saga, "New", "grog", None)
    deeds.keep_interests(made)
    _edit_info(saga, made, name="Renamed")
    assert made.interests_chosen
    _edit_info(saga, made, type="companion")
    assert not made.interests_chosen and _on(made) == ON["companion"]


def test_a_type_change_in_play_keeps_the_interests():
    saga = Saga(id="s", name="S")
    made = creation.add_character(saga, "New", "grog", None)
    creation.set_in_creation(saga, made, False)
    _edit_info(saga, made, type="companion")
    assert made.interests_chosen and _on(made) == ON["grog"]


def test_moving_to_in_play_keeps_the_interests_where_they_are():
    saga = Saga(id="s", name="S")
    made = creation.add_character(saga, "New", "magus", None)
    creation.set_in_creation(saga, made, False)
    assert made.interests_chosen
    assert made.interests_off == deeds.defaults_off(made)
    made.interests_off.append(deeds.TRIBUNAL)
    creation.set_in_creation(saga, made, True)
    assert made.interests_chosen and _on(made) == [deeds.RESEARCH]


def test_demoting_a_new_character_keeps_its_interests_where_they_are():
    saga = Saga(id="s", name="S")
    made = creation.add_character(saga, "New", "grog", None)
    step = menu_steps.change_detail(saga, made, SKETCH)
    assert isinstance(step, Confirm)
    step.apply()
    assert made.interests_chosen and _on(made) == ON["grog"]


def test_every_default_is_one_of_the_interests():
    named = {
        interest
        for _, interests in default_interests.BY_TYPE.values()
        for interest in interests
    }
    assert named | {default_interests.SESSION} <= set(deeds.INTERESTS)
