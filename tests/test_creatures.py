"""The Bestiary's creatures: the record, what is worked out from it, and
how it travels in exports and packs."""

from __future__ import annotations

from dataclasses import asdict

from support import aeolus, everything_saga

from ars_magica_manager import (
    creature_forms,
    creature_sheet,
    creatures,
    packs,
    places,
    sections,
    transfer,
)
from ars_magica_manager.character_sheet import Fact
from ars_magica_manager.commands import Choose, Confirm, Form
from ars_magica_manager.models import (
    Ability,
    Creature,
    Link,
    Saga,
    VirtueFlawInstance,
)


def _with_creature() -> tuple[Saga, Creature]:
    saga = everything_saga()
    creature = saga.creature("aeolus")
    assert creature is not None
    return saga, creature


def test_a_creature_saves_and_loads_unchanged():
    saga, creature = _with_creature()
    creature.virtues_flaws = [VirtueFlawInstance("vf_magic_animal")]
    creature.links = [Link("covenants", "cov1", "Grazes its meadows")]
    loaded = Saga.from_dict(asdict(saga))
    assert loaded.creature("aeolus") == creature
    assert loaded.creature("nobody") is None


def test_an_older_save_has_an_empty_bestiary():
    data = asdict(Saga(id="s", name="Old"))
    del data["creatures"]
    assert Saga.from_dict(data).creatures == []


def test_might_and_penetration_are_worked_out():
    creature = aeolus()
    assert creatures.might_text(creature) == "Magic Might 8 (Animal)"
    power = creature.powers[0]
    assert creatures.penetration(creature, power) == 8
    power.might_cost, power.penetration_bonus = 1, 4
    # Might less five per Might Point, plus the bonus.
    assert creatures.penetration(creature, power) == 7
    # The Penetration Ability adds as for a magus, +1 when its specialty
    # is the power's Form.
    creature.abilities.append(Ability("Penetration", xp=30, specialty=power.form))
    assert creatures.penetration(creature, power) == 7 + 3 + 1
    power.might_cost = 20
    # It may go below zero: then it affects only what has no Magic Resistance.
    assert creatures.penetration(creature, power) < 0
    beast = Creature(id="wolf", name="Wolf")
    assert not creatures.has_might(beast)
    assert creatures.might_text(beast) == "Mundane"


def test_wound_ranges_follow_size():
    # Size +2: each band is seven points wide, Dead from 29, as the book prints.
    ranges = creatures.wound_ranges(aeolus())
    assert ranges[0] == ("Light", 1, 7)
    assert ranges[-1] == ("Dead", 29, None)


def test_a_creature_is_found_at_its_place_and_the_places_round_it():
    saga, creature = _with_creature()
    drachenfels = places.place(saga, "drachenfels")
    outer = places.place(saga, "siebengebirge")
    assert drachenfels is not None and outer is not None
    assert creatures.found_at(saga, drachenfels) == [creature]
    assert creatures.found_at(saga, outer) == [creature]
    assert "Aeolus" in places.here(saga, drachenfels)


def test_a_creature_in_a_deleted_place_is_placed_nowhere():
    saga, creature = _with_creature()
    saga.neighbours = [n for n in saga.neighbours if n.id != "drachenfels"]
    places.sync(saga)
    assert creature.place_id is None and creature.place_level == 0


def test_adding_gives_a_free_id_and_deleting_drops_the_links_to_it():
    saga, creature = _with_creature()
    other = creatures.add(saga, "Aeolus")
    assert other.id != creature.id and other in saga.creatures
    cologne = saga.neighbour("cologne")
    assert cologne is not None
    cologne.links.append(Link("creatures", creature.id, "Stabled here"))
    assert creatures.deletion_consequences(saga, creature) == [
        f"The links to it from {cologne.name}, The Hollow Crown go; nothing else "
        "changes."
    ]
    creatures.delete(saga, creature)
    assert creature not in saga.creatures
    assert all(link.kind != "creatures" for link in cologne.links)


def test_a_whole_saga_export_carries_the_bestiary():
    saga, _ = _with_creature()
    target = Saga(id="dst", name="Target")
    plan = transfer.plan_import(target, transfer.export_saga_data(saga))
    assert "  Creature: Aeolus" in transfer.preview(plan)
    transfer.apply(target, plan)
    (imported,) = target.creatures
    assert imported.might == 8 and imported.powers[0].name == "From Nag to Charger"
    place = target.neighbour(imported.place_id)
    assert place is not None and place.name == "The Drachenfels"


def _rhine_pack(saga: Saga) -> dict:
    rhine = saga.tribunal("rhine")
    assert rhine is not None
    keep = saga.covenant("cov1")
    assert keep is not None
    keep.place_id = "drachenfels"
    return packs.pack_data(saga, "The Rhine", [rhine], [], [])


def test_a_pack_takes_the_creatures_of_its_places_once():
    saga, _ = _with_creature()
    stray = creatures.add(saga, "Stray")
    data = _rhine_pack(saga)
    assert [c["name"] for c in data["saga"]["creatures"]] == ["Aeolus"]
    assert stray.name not in str(data["saga"]["creatures"])
    assert "1 creature" in packs.summary(data)
    target = Saga(id="dst", name="Target")
    transfer.apply(target, transfer.plan_import(target, data))
    again = transfer.plan_import(target, data)
    assert "Creature Aeolus" in again.already
    transfer.apply(target, again)
    assert [c.name for c in target.creatures] == ["Aeolus"]


def test_a_pack_can_leave_its_bestiary_behind():
    saga, creature = _with_creature()
    cologne = saga.neighbour("cologne")
    assert cologne is not None
    data = _rhine_pack(saga)
    fields = {f.key: f for f in packs.import_fields(data)}
    assert fields["bestiary"].label == "The Bestiary (1)"
    bare = packs.narrow(data, {"bestiary": False})
    assert bare["saga"]["creatures"] == []
    assert bare["links"][transfer.CREATURE] == {creature.id: "Aeolus"}


# -- the forms --


def _values(fields) -> dict:
    return {f.key: f.value for f in fields}


def test_new_creature_makes_a_mundane_beast_until_a_realm_is_given():
    saga = Saga(id="s", name="S")
    form = creature_forms.new_creature_form(saga)
    values = {**_values(form.fields()), "name": "Wolf", "might": 7}
    form.apply(values)
    (wolf,) = saga.creatures
    # No realm: no Might, whatever was typed.
    assert (wolf.name, wolf.realm, wolf.might) == ("Wolf", "", 0)
    edit = creature_forms.edit_creature_form(saga, wolf)
    edit.apply(
        {
            **_values(edit.fields()),
            "realm": "Faerie",
            "might": 12,
            "might_form": "Animal",
        }
    )
    assert creatures.might_text(wolf) == "Faerie Might 12 (Animal)"


def test_the_info_form_shows_might_only_with_a_realm():
    saga = Saga(id="s", name="S")
    fields = {f.key: f for f in creature_forms.info_fields(saga, None)}
    might = fields["might"]
    assert might.show_if is not None
    assert not might.show_if({"realm": None}) and might.show_if({"realm": "Magic"})


def test_only_an_infernal_creature_keeps_a_demons_facts():
    saga = Saga(id="s", name="S")
    form = creature_forms.new_creature_form(saga)
    demon = {
        **_values(form.fields()),
        "name": "Adramelech",
        "realm": "Infernal",
        "might": 50,
        "order": "Prince of the False Gods",
        "hierarchy": 9,
        "weakness": "Running water",
        "confidence_score": 3,
        "confidence_points": 9,
    }
    form.apply(demon)
    (king,) = saga.creatures
    assert creature_sheet.infernal_facts(king) == [
        Fact("Order", "Prince of the False Gods"),
        Fact("Hierarchy", "9"),
        Fact("Weakness", "Running water"),
    ]
    assert creature_sheet.confidence_text(king) == "3 (9)"
    edit = creature_forms.edit_creature_form(saga, king)
    edit.apply({**demon, "realm": "Faerie", "confidence_score": None})
    assert (king.order, king.hierarchy, king.weakness) == ("", None, "")
    assert (king.confidence_score, king.confidence_points) == (None, 0)


def test_cunning_tiring_and_wounds_show_as_the_book_prints_them():
    creature = aeolus()
    assert creature_sheet.characteristics_text(creature).startswith("Int ")
    creature.cunning = True
    assert creature_sheet.characteristics_text(creature).startswith("Cun ")
    creature.tires = creature.can_be_wounded = False
    assert creature_sheet.fatigue_levels_text(creature) == "none: it never tires"
    assert creature_sheet.wounds_text(creature) == "none: it cannot be wounded"
    assert Creature.from_dict(asdict(creature)) == creature


def test_each_list_on_the_sheet_adds_edits_and_deletes():
    saga, creature = _with_creature()
    ops = creature_forms.creature_ops(saga, creature)
    powers = ops[sections.CREATURE_POWERS_SECTION]
    assert powers.add is not None and powers.edit is not None
    add = powers.add()
    assert isinstance(add, Form)
    add.apply(
        {**_values(add.fields()), "name": "Gallop", "might_cost": 1, "form": None}
    )
    assert creature.powers[-1].form == "" and creature.powers[-1].might_cost == 1
    edit = powers.edit(1)
    assert isinstance(edit, Form)
    edit.apply({**_values(edit.fields()), "form": "Auram"})
    assert creature.powers[1].form == "Auram"
    vis = ops[sections.CREATURE_VIS_SECTION]
    assert vis.rows is not None and vis.rows() == ["2 pawns of Animal, in head"]
    assert vis.add is not None
    form = vis.add()
    assert isinstance(form, Form) and form.validate is not None
    assert form.validate({"pawns": 0, "art": "Vim", "where": ""})
    attacks = ops[sections.CREATURE_ATTACKS_SECTION]
    assert attacks.remove is not None
    confirm = attacks.remove(0)
    assert isinstance(confirm, Confirm)
    confirm.apply()
    assert creature.attacks == []


def test_a_creature_is_offered_qualities():
    saga, creature = _with_creature()
    creature.virtues_flaws = []
    ops = creature_forms.creature_ops(saga, creature)
    add = ops[sections.CREATURE_VF_SECTION].add
    assert add is not None
    choose = add()
    assert isinstance(choose, Choose)
    names = " ".join(c.label for c in choose.choices())
    assert "Magic Animal" in names


def test_the_bestiary_lists_by_name_and_deletes_the_chosen_one():
    saga, _ = _with_creature()
    creatures.add(saga, "Boglin")
    ops = creature_forms.bestiary_ops(saga)[sections.BESTIARY_SECTION]
    assert ops.rows is not None and ops.rows() == ["Aeolus", "Boglin"]
    assert ops.remove is not None
    confirm = ops.remove(0)
    assert isinstance(confirm, Confirm)
    confirm.apply()
    assert [c.name for c in saga.creatures] == ["Boglin"]
