"""Default Interests: the interests a new character starts with, by its
type (the approved design, not a book rule), its House and its Virtues
and Flaws (default_interests.SOURCE), with Session & Reputation always
on."""

from __future__ import annotations

import pytest

from ars_magica_manager import (
    catalog,
    character_templates,
    creation,
    deeds,
    default_interests,
    storage,
    worksheet,
)
from ars_magica_manager import grog_templates as gt
from ars_magica_manager.commands import Confirm, Finished, Form, drive
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
    VirtueFlawInstance,
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
        # Only a grog with an animal form is an animal grog; anyone else
        # with one keeps the defaults of its type.
        ("magus", True, {deeds.RESEARCH, deeds.TRIBUNAL}),
        ("companion", True, {deeds.RELIGION}),
        ("mythic companion", True, {deeds.RELIGION}),
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


def _added(character: Character) -> list[default_interests.Reason]:
    """What `character`'s defaults add to its type's and the session's."""
    plain = Character(id="p", name="P", type=character.type, animal=character.animal)
    already = default_interests.defaults(plain)
    return [r for r in default_interests.defaults(character) if r not in already]


def _magus_of(house: str) -> Character:
    magus = _new("magus")
    magus.hermetic.house = house
    return magus


#: What each House adds to a magus's defaults (DE pp. 12-17, 46).
@pytest.mark.parametrize(
    ("house", "expected"),
    [
        ("house_bjornaer", [deeds.MYSTERY_CULTS]),
        ("house_criamon", [deeds.MYSTERY_CULTS]),
        ("house_merinita", [deeds.MYSTERY_CULTS, deeds.FAERIE]),
        ("house_verditius", [deeds.MYSTERY_CULTS, deeds.CRAFT]),
        ("house_jerbiton", [deeds.SCHOLARLY]),
        ("house_flambeau", [deeds.KNIGHTLY]),
        ("house_bonisagus", []),
        ("house_guernicus", []),
        ("house_mercere", []),
        ("house_tremere", []),
        ("house_tytalus", []),
        ("house_ex_miscellanea", []),
    ],
)
def test_a_magus_takes_up_what_its_house_does(house: str, expected: list[str]):
    added = _added(_magus_of(house))
    name = catalog.load_house_catalog_by_id()[house].name
    assert added == [(interest, f"House {name}") for interest in expected]


def test_only_a_magus_takes_up_what_a_house_does():
    companion = _new("companion")
    companion.hermetic.house = "house_merinita"
    assert _added(companion) == []


def _with(character: Character, *vf_ids: str) -> Character:
    character.virtues_flaws += [VirtueFlawInstance(vf_id=v) for v in vf_ids]
    return character


#: One Virtue or Flaw of each interest's group (default_interests.SOURCE).
@pytest.mark.parametrize(
    ("vf_id", "interest", "why"),
    [
        ("vf_knight", deeds.KNIGHTLY, "Knight"),  # DE p. 88
        ("vf_educated", deeds.SCHOLARLY, "Educated"),  # DE p. 77
        ("vf_font_of_knowledge", deeds.INSIGHT, "Font of Knowledge"),  # DE p. 82
        ("vf_priest", deeds.RELIGION, "Priest"),  # DE p. 104
        ("vf_faerie_sight", deeds.FAERIE, "Faerie Sight"),  # RoP:F p. 50
        ("vf_craftsman", deeds.CRAFT, "Craftsman"),  # DE p. 75
        ("vf_diabolist", deeds.INFERNAL, "Diabolist"),  # RoP:I p. 112
        ("vf_redcap", deeds.TRIBUNAL, "Redcap"),  # DE p. 91
        ("vf_custos", deeds.COVENFOLK, "Custos"),  # DE p. 75
        ("vf_apprentice", deeds.APPRENTICESHIP, "Apprentice"),  # DE p. 70
    ],
)
def test_a_virtue_takes_up_what_it_is_about(vf_id: str, interest: str, why: str):
    assert _added(_with(_new("companion"), vf_id)) == [(interest, why)]


#: Every kind of Faerie Blood (DE pp. 79, 110; HoH:TL p. 104; Lion &
#: Lily p. 97; Faith & Flame p. 91), named as the sheet names it.
@pytest.mark.parametrize(
    ("vf_id", "why"),
    [
        ("vf_faerie_blood", "Faerie Blood"),
        ("vf_faerie_blood_bloodcap", "Faerie Blood (Bloodcap)"),
        ("vf_faerie_blood_jentil", "Faerie Blood (Jentil)"),
        ("vf_faerie_blood_jentil_major", "Faerie Blood (Jentil)"),
        ("vf_faerie_blood_laminak", "Faerie Blood (Laminak)"),
        ("vf_faerie_blood_spinnen", "Faerie Blood (Spinnen)"),
        ("vf_strong_faerie_blood", "Strong Faerie Blood"),
    ],
)
def test_faerie_blood_of_every_kind_deals_with_faerie(vf_id: str, why: str):
    assert _added(_with(_new("grog"), vf_id)) == [(deeds.FAERIE, why)]


@pytest.mark.parametrize(
    ("vf_id", "expected"),
    [
        # RoP:F p. 113: faeries summoned.
        ("vf_faerie_summoning", [(deeds.FAERIE, "(Faerie) Summoning")]),
        # RoP:I pp. 87, 114-115: the Goetic Art.
        ("vf_summoning", [(deeds.INFERNAL, "Summoning")]),
        # Hedge Magic, Revised: spirits of any realm, so nothing.
        ("vf_type_summoning", []),
        ("vf_type_summoning_major", []),
    ],
)
def test_each_summoning_deals_with_the_realm_it_calls_on(
    vf_id: str, expected: list[default_interests.Reason]
):
    assert _added(_with(_new("companion"), vf_id)) == expected


def test_a_flaw_counts_as_well_as_a_virtue():
    # Diabolic Past, DE p. 126.
    added = _added(_with(_new("companion"), "vf_diabolic_past"))
    assert added == [(deeds.INFERNAL, "Diabolic Past")]


def test_the_defaults_are_the_union_of_type_and_virtues():
    grog = _with(_new("grog"), "vf_custos", "vf_educated")
    assert default_interests.defaults(grog) == [
        (deeds.SESSION, "every character"),
        (deeds.COVENFOLK, "a grog"),
        (deeds.CRAFT, "a grog"),
        (deeds.COVENFOLK, "Custos"),
        (deeds.SCHOLARLY, "Educated"),
    ]


def test_a_rhine_apprentice_is_an_apprentice():
    # Guardians of the Forests p. 19: the DE's Apprentice, for any Tribunal.
    added = _added(_with(_new("companion"), "vf_apprentice_rhine_tribunal"))
    assert added == [(deeds.APPRENTICESHIP, "Apprentice (Rhine Tribunal)")]


def test_a_virtue_taken_twice_gives_its_reason_once():
    added = _added(_with(_new("companion"), "vf_knight", "vf_knight"))
    assert added == [(deeds.KNIGHTLY, "Knight")]


def test_a_sagas_own_virtue_takes_up_nothing():
    assert _added(_with(_new("companion"), "vf_saga_custom")) == []


def test_every_virtue_and_house_in_the_rules_is_in_the_catalogs():
    virtues = catalog.load_virtue_flaw_catalog_by_id()
    houses = catalog.load_house_catalog_by_id()
    missing = [v for v in default_interests.BY_VIRTUE if v not in virtues]
    missing += [h for h in default_interests.BY_HOUSE if h not in houses]
    assert missing == []


def test_every_interest_the_rules_take_up_is_one_of_the_interests():
    named = set(default_interests.BY_VIRTUE.values())
    named |= {i for interests in default_interests.BY_HOUSE.values() for i in interests}
    assert named <= set(deeds.INTERESTS)


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


def test_a_sketch_covenants_new_magus_starts_with_its_houses_defaults():
    saga = Saga(id="s", name="S")
    covenant = creation.add_covenant(saga, "Fengheld")
    add = world_forms.magus_ops(saga, covenant).add
    assert add is not None
    form = add()
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    form.apply(values | {"name": "Ysolde", "house": "house_merinita"})
    (magus,) = saga.characters
    assert magus.interests_chosen
    assert {deeds.MYSTERY_CULTS, deeds.FAERIE} <= set(_on(magus))


def test_a_house_change_in_creation_moves_the_interests_until_chosen():
    magus = _unchosen("magus")
    magus.hermetic.house = "house_flambeau"
    assert _on(magus) == [deeds.KNIGHTLY, deeds.RESEARCH, deeds.TRIBUNAL]
    magus.hermetic.house = "house_jerbiton"
    assert _on(magus) == [deeds.SCHOLARLY, deeds.RESEARCH, deeds.TRIBUNAL]
    deeds.keep_interests(magus)
    magus.hermetic.house = "house_verditius"
    assert _on(magus) == [deeds.SCHOLARLY, deeds.RESEARCH, deeds.TRIBUNAL]


def test_a_virtue_added_then_removed_in_creation_moves_the_interests_until_chosen():
    companion = _unchosen("companion")
    _with(companion, "vf_knight")
    assert _on(companion) == [deeds.KNIGHTLY, deeds.RELIGION]
    companion.virtues_flaws.clear()
    assert _on(companion) == [deeds.RELIGION]
    deeds.keep_interests(companion)
    _with(companion, "vf_knight")
    assert _on(companion) == [deeds.RELIGION]


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
    advisor = catalog.load_grog_template_catalog()[0]
    assert advisor.id == "gt_advisor"  # Educated, so Scholarly too
    grog = _made_from(advisor)
    assert grog.in_creation and not grog.interests_chosen
    assert _on(grog) == [deeds.SCHOLARLY, *ON["grog"]]


@pytest.mark.parametrize(
    ("template_id", "expected"),
    [
        ("tpl_knight", [deeds.KNIGHTLY, deeds.RELIGION]),
        ("tpl_tremere", ON["magus"]),
    ],
)
def test_a_ready_to_play_template_starts_in_play_with_its_defaults(
    template_id: str, expected: list[str]
):
    template = character_templates.find(template_id)
    assert template is not None
    made = _made_from(template)
    assert not made.in_creation and made.interests_chosen
    assert _on(made) == expected


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


@pytest.mark.parametrize("character_type", ["companion", "mythic companion"])
def test_an_animal_grog_made_a_companion_takes_up_the_companion_defaults(
    character_type: CharacterType,
):
    hound = _made_from(catalog.load_animal_template_catalog()[0])
    assert hound.animal is not None and _on(hound) == [deeds.COVENFOLK]
    _edit_info(Saga(id="s", name="S"), hound, type=character_type)
    assert hound.animal is not None and _on(hound) == ON[character_type]


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


def _review(character: Character) -> str:
    """The Review Interests step's text for `character`."""
    saga = Saga(id="s", name="S")
    return worksheet.panel_for(character, "interests").budget(saga, character)


def test_review_interests_says_where_each_default_comes_from(
    monkeypatch: pytest.MonkeyPatch,
):
    def by_house(character: Character) -> list[default_interests.Reason]:
        return [
            (deeds.MYSTERY_CULTS, "House Merinita"),
            (deeds.FAERIE, "House Merinita"),
        ]

    monkeypatch.setattr(
        default_interests, "RULES", [*default_interests.RULES, by_house]
    )
    text = _review(_unchosen("magus"))
    assert "From being a magus: Research, Tribunal & Order." in text
    assert "From House Merinita: Mystery Cults, Dealings with Faerie." in text
    assert "every character" not in text


def test_review_interests_says_when_the_session_is_the_only_default(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(default_interests, "RULES", [])
    assert "Reputation:\nNone.\n" in _review(_unchosen("magus"))


def test_review_interests_says_whether_they_are_the_defaults_or_the_players():
    grog = _unchosen("grog")
    assert "follow the character's type, House and Virtues" in _review(grog)
    deeds.keep_interests(grog)
    assert "the player's own" in _review(grog)
    assert "follow the character's type" not in _review(grog)


def test_review_interests_lists_the_defaults_in_the_order_of_the_cards():
    text = _review(_unchosen("grog"))
    assert "From being a grog: Craft & Trade, Covenfolk.\n" in text
    assert "\nOn: Craft & Trade, Covenfolk." in text


def test_review_interests_names_the_few_on_rather_than_the_many_off():
    text = _review(_unchosen("magus"))
    assert "On: Research, Tribunal & Order. The rest are off." in text
    assert "Turned off" not in text


def _actions(character: Character) -> dict[str, worksheet.Action]:
    saga = Saga(id="s", name="S")
    panel = worksheet.panel_for(character, "interests")
    return {action.label: action for action in panel.actions(saga, character)}


def test_restore_the_defaults_hands_the_interests_back_and_says_whats_on():
    grog = _unchosen("grog")
    grog.interests_off = [deeds.CRAFT]
    deeds.keep_interests(grog)
    outcome = drive(_actions(grog)["Restore the defaults"].start(), lambda _: None)
    assert outcome == Finished(["C is back to the defaults: Craft & Trade, Covenfolk."])
    assert not grog.interests_chosen and grog.interests_off == []
    assert _on(grog) == ON["grog"]


def test_restore_the_defaults_is_offered_only_in_creation():
    grog = _unchosen("grog")
    assert list(_actions(grog)) == ["Edit Interests", "Restore the defaults"]
    grog.in_creation = False
    assert list(_actions(grog)) == ["Edit Interests"]


def test_every_default_is_one_of_the_interests():
    named = {
        interest
        for _, interests in default_interests.BY_TYPE.values()
        for interest in interests
    }
    assert named | {default_interests.SESSION} <= set(deeds.INTERESTS)
