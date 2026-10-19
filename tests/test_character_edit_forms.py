"""The Character sheet's Add, Edit and Delete beyond its Description
chapter, without a front-end: Character Info, Characteristics, Abilities
(ability_forms), Virtues & Flaws (virtue_forms), Arts, Known Spells
(spell_forms), Research Goals and Personal Gear (character_forms)."""

from __future__ import annotations

import copy
from typing import Any

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import form_spec
from ars_magica_manager.commands import Choose, Confirm, Form, Refuse
from ars_magica_manager.forms import ability as ability_forms
from ars_magica_manager.forms import character as cf
from ars_magica_manager.forms import spell as spell_forms
from ars_magica_manager.forms import virtue as virtue_forms
from ars_magica_manager.models import (
    Breakthrough,
    Laboratory,
    Possession,
    VirtueFlawInstance,
)


def _magus():
    saga = _sample_saga_with_covenant()
    return saga, next(c for c in saga.characters if c.type == "magus")


def _wanted(value: Any, answer: Any) -> bool:
    if callable(answer):
        return bool(answer(value))
    return value == answer or getattr(value, "id", None) == answer


def _held(spec: Any, values: dict[str, Any]) -> Any:
    """What a field's widget would hold: a typed field's text, a choice's
    value."""
    value = values[spec.key]
    if spec.kind in ("select", "check", "picker"):
        return value
    return "" if value is None else str(value)


def run(step: Any, *answers: Any) -> Any:
    """Answer each step as a front-end would: a dict (typed over the form
    as it opens), a value or id to choose (or a test of the value), a bool
    for a confirmation, None to cancel. Returns what the last step led to:
    None, notes, a Refuse, or ("refused", why) for a form that would not
    save."""
    queue = list(answers)
    while isinstance(step, Form | Choose | Confirm):
        answer = queue.pop(0)
        if answer is None:
            return "cancelled"
        if isinstance(step, Form):
            fields = [spec for spec in step.fields() if spec.kind != "info"]
            values = {spec.key: spec.value for spec in fields}
            values.update(answer)
            try:
                result = form_spec.result(
                    fields, lambda spec, values=values: _held(spec, values)
                )
            except form_spec.FieldError as error:
                return ("refused", str(error))
            why = step.validate(result) if step.validate else None
            if why:
                return ("refused", why)
            step = step.apply(result)
        elif isinstance(step, Choose):
            chosen = [c for c in step.choices() if _wanted(c.value, answer)]
            assert chosen, f"{answer!r} is not offered"
            step = step.apply(chosen[0].value)
        else:
            if not answer:
                return "cancelled"
            step = step.apply()
    assert not queue, f"Unanswered: {queue}"
    return step


# -- Character Info and Characteristics --


def test_character_info_saves_the_name_covenant_and_background_figures():
    saga, magus = _magus()
    run(
        cf.character_info_form(saga, magus),
        {"name": "Leandro of Bonisagus", "covenant_id": None, "confidence_score": "2"},
    )
    assert magus.name == "Leandro of Bonisagus"
    assert magus.covenant_id is None
    assert magus.background.confidence_score == 2


def test_only_a_companion_may_change_type_and_only_a_magus_has_a_laboratory():
    saga, magus = _magus()
    keys = [spec.key for spec in cf.character_info_fields(saga, magus)]
    assert "laboratory_id" in keys and "type" not in keys
    magus.type = "companion"
    keys = [spec.key for spec in cf.character_info_fields(saga, magus)]
    assert "type" in keys and "laboratory_id" not in keys
    run(cf.character_info_form(saga, magus), {"type": "mythic companion"})
    assert magus.type == "mythic companion"


def test_the_true_faith_score_warns_without_a_true_faith_virtue():
    _, magus = _magus()
    live = cf.character_info_live(magus)
    assert live({"true_faith_score": 0}) == ""
    assert live({"true_faith_score": 1})


def test_characteristics_save_all_eight():
    saga, magus = _magus()
    run(cf.characteristics_form(saga, magus), {"presence": "-2", "strength": "1"})
    assert magus.characteristics.presence == -2
    assert magus.characteristics.strength == 1
    assert magus.characteristics.intelligence == 3


def test_characteristics_count_points_only_in_creation():
    saga, magus = _magus()
    assert cf.characteristics_form(saga, magus).live is None


# -- Abilities --


def test_adding_a_templated_ability_names_it_then_asks_its_xp():
    _, magus = _magus()
    ops = ability_forms.ability_ops(magus.abilities, magus.virtues_flaws)
    assert ops.add is not None
    before = len(magus.abilities)
    assert run(ops.add(), "ab_craft", {"craft": "Smith"}, None) == "cancelled"
    assert len(magus.abilities) == before
    run(ops.add(), "ab_craft", {"craft": "Smith"}, {"xp": "15", "specialty": "Nails"})
    added = magus.abilities[-1]
    assert (added.name, added.xp, added.specialty) == ("Craft: Smith", 15, "Nails")


def test_an_ability_already_held_is_not_offered_again():
    _, magus = _magus()
    ops = ability_forms.ability_ops(magus.abilities, magus.virtues_flaws)
    assert ops.add is not None
    step = ops.add()
    assert isinstance(step, Choose)
    offered = {choice.value.name for choice in step.choices()}
    assert "Magic Theory" not in offered and "Craft: {craft}" in offered


def test_editing_an_ability_keeps_its_name_and_refuses_negative_xp():
    _, magus = _magus()
    ops = ability_forms.ability_ops(magus.abilities, magus.virtues_flaws)
    assert ops.edit is not None and ops.remove is not None
    assert run(ops.edit(0), {"xp": "-1"}) == ("refused", "XP can't be negative.")
    run(ops.edit(0), {"xp": "30", "specialty": ""})
    assert magus.abilities[0].name == "Magic Theory"
    assert (magus.abilities[0].xp, magus.abilities[0].specialty) == (30, None)
    step = ops.remove(0)
    assert isinstance(step, Confirm) and step.question == "Delete Magic Theory?"
    run(step, True)
    assert not any(a.name == "Magic Theory" for a in magus.abilities)


# -- Virtues & Flaws --


def test_adding_a_virtue_with_a_parameter_picks_it_from_its_choices():
    saga, magus = _magus()
    ops = virtue_forms.virtue_flaw_ops(saga, magus, "Virtue")
    assert ops.add is not None
    step = ops.add()
    assert isinstance(step, Choose) and step.title == "Add a Virtue"
    assert all(choice.value.side == "Virtue" for choice in step.choices())
    run(step, "vf_affinity_with_art", {"art": "creo"})
    assert magus.virtues_flaws[-1] == VirtueFlawInstance(
        "vf_affinity_with_art", {"art": "creo"}
    )
    assert "Affinity with Creo" in ops.rows()


def test_a_repeat_the_book_forbids_is_refused_and_changes_nothing():
    saga, magus = _magus()
    magus.virtues_flaws = [VirtueFlawInstance("vf_affinity_with_art", {"art": "creo"})]
    before = list(magus.virtues_flaws)
    ops = virtue_forms.virtue_flaw_ops(saga, magus, "Virtue")
    assert ops.add is not None
    step = ops.add()
    assert isinstance(step, Choose)
    form = step.apply(
        next(c.value for c in step.choices() if c.value.id == "vf_affinity_with_art")
    )
    assert isinstance(form, Form)
    # Creo is already taken, so it isn't offered.
    art = next(spec for spec in form.fields() if spec.key == "art")
    assert "creo" not in [value for _, value in art.options]
    assert form.validate is not None and form.validate({"art": "creo"})
    assert magus.virtues_flaws == before


def test_a_virtue_taken_once_is_not_offered_again():
    saga, magus = _magus()
    magus.virtues_flaws.append(VirtueFlawInstance("vf_the_gift"))
    step = virtue_forms.virtue_flaw_ops(saga, magus, "Virtue").add
    assert step is not None
    choose = step()
    assert isinstance(choose, Choose)
    assert "vf_the_gift" not in [c.value.id for c in choose.choices()]


def test_great_characteristic_moves_its_characteristic_both_ways():
    saga, magus = _magus()
    ops = virtue_forms.virtue_flaw_ops(saga, magus, "Virtue")
    assert ops.add is not None and ops.remove is not None
    run(ops.add(), "vf_great_characteristic", {"characteristic": "intelligence"})
    assert magus.characteristics.intelligence == 4
    row = ops.rows().index("Great Intelligence")
    step = ops.remove(row)
    assert isinstance(step, Confirm)
    assert (
        step.question == "Delete Great Intelligence? Intelligence goes from +4 to +3."
    )
    run(step, True)
    assert magus.characteristics.intelligence == 3
    assert "Great Intelligence" not in ops.rows()


def test_editing_puissant_changes_its_ability_in_place():
    saga, magus = _magus()
    magus.virtues_flaws = [
        VirtueFlawInstance("vf_the_gift"),
        VirtueFlawInstance("vf_puissant_ability", {"ability": "magic theory"}),
        VirtueFlawInstance("vf_affinity_with_art", {"art": "creo"}),
    ]
    puissant = magus.virtues_flaws[1]
    ops = virtue_forms.virtue_flaw_ops(saga, magus, "Virtue")
    assert ops.edit is not None
    row = ops.rows().index("Puissant Magic Theory")
    form = ops.edit(row)
    assert isinstance(form, Form) and form.title == "Change Puissant Magic Theory"
    ability = next(spec for spec in form.fields() if spec.key == "ability")
    # Opens on what it names now, which is still offered.
    assert ability.value == "magic theory"
    assert "magic theory" in [value for _, value in ability.options]
    assert run(form, {"ability": "finesse"}) == []
    assert magus.virtues_flaws[1] is puissant
    assert puissant.params == {"ability": "finesse"}
    assert ops.rows()[row] == "Puissant Finesse"


def test_editing_refuses_a_choice_another_copy_already_holds():
    saga, magus = _magus()
    magus.virtues_flaws = [
        VirtueFlawInstance("vf_affinity_with_art", {"art": "creo"}),
        VirtueFlawInstance("vf_affinity_with_art", {"art": "rego"}),
    ]
    ops = virtue_forms.virtue_flaw_ops(saga, magus, "Virtue")
    assert ops.edit is not None
    form = ops.edit(1)
    assert isinstance(form, Form)
    art = next(spec for spec in form.fields() if spec.key == "art")
    offered = [value for _, value in art.options]
    assert "rego" in offered and "creo" not in offered
    assert run(form, {"art": "creo"})[0] == "refused"
    assert magus.virtues_flaws[1].params == {"art": "rego"}


def test_editing_great_characteristic_moves_both_characteristics():
    saga, magus = _magus()
    magus.characteristics.stamina = 3
    ops = virtue_forms.virtue_flaw_ops(saga, magus, "Virtue")
    assert ops.add is not None and ops.edit is not None
    run(ops.add(), "vf_great_characteristic", {"characteristic": "intelligence"})
    assert magus.characteristics.intelligence == 4
    form = ops.edit(ops.rows().index("Great Intelligence"))
    assert isinstance(form, Form) and form.live is not None
    assert form.live({"characteristic": "stamina"}) == (
        "Moves Intelligence +4 to +3, Stamina +3 to +4."
    )
    assert run(form, {"characteristic": "stamina"}) == [
        "Moved Intelligence +4 to +3, Stamina +3 to +4."
    ]
    assert (magus.characteristics.intelligence, magus.characteristics.stamina) == (
        3,
        4,
    )
    assert "Great Stamina" in ops.rows()


def test_editing_great_characteristic_refuses_a_characteristic_below_plus_3():
    saga, magus = _magus()
    ops = virtue_forms.virtue_flaw_ops(saga, magus, "Virtue")
    assert ops.add is not None and ops.edit is not None
    run(ops.add(), "vf_great_characteristic", {"characteristic": "intelligence"})
    form = ops.edit(ops.rows().index("Great Intelligence"))
    assert isinstance(form, Form)
    options = next(s for s in form.fields() if s.key == "characteristic").options
    assert [value for _, value in options] == ["intelligence"]
    assert run(form, {"characteristic": "perception"})[0] == "refused"
    assert magus.characteristics.intelligence == 4


def test_a_virtue_naming_nothing_cannot_be_edited():
    saga, magus = _magus()
    magus.virtues_flaws = [VirtueFlawInstance("vf_the_gift")]
    ops = virtue_forms.virtue_flaw_ops(saga, magus, "Virtue")
    assert ops.edit is not None
    step = ops.edit(0)
    assert isinstance(step, Refuse)
    assert "names nothing to change" in step.why


def test_a_free_text_value_from_an_old_save_opens_on_the_list():
    saga, magus = _magus()
    magus.virtues_flaws = [
        VirtueFlawInstance("vf_puissant_ability", {"ability": "magic theroy"})
    ]
    ops = virtue_forms.virtue_flaw_ops(saga, magus, "Virtue")
    assert ops.edit is not None
    form = ops.edit(0)
    assert isinstance(form, Form)
    ability = next(spec for spec in form.fields() if spec.key == "ability")
    assert ability.value == "magic theroy"
    run(form, {"ability": "magic theory"})
    assert magus.virtues_flaws[0].params == {"ability": "magic theory"}


def test_deleting_a_flaw_counts_rows_on_the_flaws_side_only():
    saga, magus = _magus()
    magus.virtues_flaws = [
        VirtueFlawInstance("vf_the_gift"),
        VirtueFlawInstance("vf_abandoned_apprentice"),
    ]
    flaws = virtue_forms.virtue_flaw_ops(saga, magus, "Flaw")
    assert flaws.rows() == ["Abandoned Apprentice"]
    assert flaws.remove is not None
    run(flaws.remove(0), True)
    assert magus.virtues_flaws == [VirtueFlawInstance("vf_the_gift")]


def test_a_familiar_and_a_laboratory_use_the_same_ops():
    saga, _ = _magus()
    lab = Laboratory(id="lab1", name="Tower", covenant_id="cov1")
    ops = virtue_forms.virtue_flaw_ops(saga, lab, "Virtue")
    assert ops.add is not None and ops.remove is not None
    step = ops.add()
    assert isinstance(step, Choose) and step.title == "Add a Laboratory Virtue"
    entry = next(c.value for c in step.choices() if not c.value.choices)
    run(step, entry.id)
    assert lab.virtues_flaws[-1].vf_id == entry.id and lab.virtues_flaws[-1].id
    run(ops.remove(0), True)
    assert not lab.virtues_flaws


# -- Arts --


def test_the_arts_form_saves_every_arts_xp_and_refuses_negative_xp():
    _, magus = _magus()
    form = cf.arts_form(magus)
    assert len(form.fields()) == 15
    assert run(form, {"art_ignem": "-5"}) == (
        "refused",
        "Ignem's XP can't be negative.",
    )
    run(cf.arts_form(magus), {"art_ignem": "21", "art_vim": "6"})
    assert magus.arts["ignem"].xp == 21 and magus.arts["vim"].xp == 6
    assert magus.arts["creo"].xp == 55
    assert form.live is not None and "Cr 10" in form.live({"art_creo": 55})


# -- Known Spells --


def test_adding_editing_and_deleting_a_known_spell():
    saga, magus = _magus()
    ops = spell_forms.known_spell_ops(saga, magus)
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    step = ops.add()
    assert isinstance(step, Choose)
    known = {k.spell_id for k in magus.spells_known}
    first = step.choices()[0].value
    assert first not in known
    run(step, first)
    assert magus.spells_known[-1].spell_id == first
    index = len(magus.spells_known) - 1
    form = ops.edit(index)
    assert isinstance(form, Form) and form.title.startswith("Mastery: ")
    run(form, {"mastery_score": "2", "mastery_xp": "10"})
    assert (
        magus.spells_known[index].mastery_score,
        magus.spells_known[-1].mastery_xp,
    ) == (
        2,
        10,
    )
    name = ops.rows()[index]
    remove = ops.remove(index)
    assert isinstance(remove, Confirm) and name in remove.question
    run(remove, True)
    assert first not in {k.spell_id for k in magus.spells_known}


# -- Research Goals --


def test_research_goals_add_edit_and_delete():
    _, magus = _magus()
    magus.breakthroughs = []
    ops = cf.research_goal_ops(magus)
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    assert run(ops.add(), {"name": "Aegis", "target": "0"}) == (
        "refused",
        "The target is at least 1 point.",
    )
    assert not magus.breakthroughs
    run(ops.add(), {"name": "Aegis", "kind": "Major", "target": "45"})
    assert magus.breakthroughs[0].name == "Aegis"
    assert magus.breakthroughs[0].target == 45
    magus.breakthroughs[0].reached = True
    magus.breakthroughs[0].points = 45
    run(ops.edit(0), {"target": "50", "grant_kind": "Ability", "grant_ability": "X"})
    goal = magus.breakthroughs[0]
    assert (goal.target, goal.reached, goal.grant) == (50, False, "X")
    run(ops.remove(0), True)
    assert magus.breakthroughs == []


def test_a_research_goal_keeps_what_its_form_does_not_show():
    existing = Breakthrough(name="Old", target=30)
    made = cf.research_goal_from(
        existing,
        {"name": "New", "kind": "Minor", "target": 30, "points": 0},
    )
    assert made is not existing and made.name == "New"
    assert existing.name == "Old"


# -- Personal Gear --


def test_personal_gear_asks_the_kind_then_its_form():
    _, magus = _magus()
    magus.inventory = []
    ops = cf.inventory_ops(magus)
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    assert run(ops.add(), "item", None) == "cancelled"
    assert not magus.inventory
    run(ops.add(), "item", {"name": "Lantern"})
    assert [(i.kind, i.name) for i in magus.inventory] == [("item", "Lantern")]
    step = ops.edit(0)
    assert isinstance(step, Form) and step.title == "Edit Lantern"
    run(step, {"name": "Brass Lantern"})
    assert magus.inventory[0].name == "Brass Lantern"
    run(ops.remove(0), True)
    assert magus.inventory == []


def test_cancelling_a_delete_changes_nothing():
    _, magus = _magus()
    magus.inventory = [Possession(id="p1", kind="item", name="Rope")]
    before = copy.deepcopy(magus.inventory)
    ops = cf.inventory_ops(magus)
    assert ops.remove is not None
    assert run(ops.remove(0), False) == "cancelled"
    assert magus.inventory == before
