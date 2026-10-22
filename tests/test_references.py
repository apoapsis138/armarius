"""Records a page names, as links: a neighbour's ruler (a record, or a
name typed), who it answers to and who answers to it, a place's
claimant and what is found there, a creature's place and what it rules;
Go To and a Links row's Open, which end with a commands.Go; and the
ruler's id kept through deleting the ruler and importing the saga."""

from __future__ import annotations

import json

from support import everything_saga

from ars_magica_manager import (
    actions,
    creatures,
    deletion,
    neighbours,
    places,
    references,
    transfer,
)
from ars_magica_manager.commands import Act, Choose, Form, Go, Picked, Refuse
from ars_magica_manager.forms import go_to as go_to_forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import neighbour as neighbour_forms
from ars_magica_manager.models import Link, Saga
from ars_magica_manager.references import Ref
from ars_magica_manager.sheets import creature as creature_sheet
from ars_magica_manager.sheets import region as region_sheet


def _fact(facts, label):
    return next(f for f in facts if f.label == label)


def _court() -> Saga:
    """The sample saga, with the Black Pool Coven led by Aeolus (a
    creature) and the Hollow Crown answering to it."""
    saga = everything_saga()
    coven = saga.neighbour("coven")
    crown = saga.neighbour("crown")
    assert coven is not None and crown is not None
    coven.ruler = "aeolus"
    crown.answers_to = "coven"
    return saga


def test_a_ruler_is_a_record_by_id_or_by_its_one_name():
    saga = _court()
    coven = saga.neighbour("coven")
    gottfried = saga.neighbour("gottfried")
    assert coven is not None and gottfried is not None
    aeolus = saga.creature("aeolus")
    assert references.ruler(saga, coven) is aeolus
    assert references.ruler_name(saga, coven) == "Aeolus"
    # A name typed: no record has it, so it is only a name.
    assert references.ruler(saga, gottfried) is None
    assert references.ruler_name(saga, gottfried) == "Count Gottfried"
    # The one record with that name.
    gottfried.ruler = "Archbishop of Cologne"
    assert references.ruler(saga, gottfried) is saga.neighbour("cologne")
    # Two records of the name: neither.
    saga.characters[0].name = "Archbishop of Cologne"
    assert references.ruler(saga, gottfried) is None
    assert references.ruler_name(saga, gottfried) == "Archbishop of Cologne"


def test_a_neighbour_s_facts_name_its_ruler_liege_place_and_who_answer_to_it():
    saga = _court()
    coven = saga.neighbour("coven")
    crown = saga.neighbour("crown")
    assert coven is not None and crown is not None
    crown.place_id = "drachenfels"
    facts = region_sheet.neighbour_facts(saga, coven)
    assert _fact(facts, "Ruler or leader").refs == (
        Ref("creatures", "aeolus", "Aeolus"),
    )
    below = _fact(facts, "Answer to it")
    assert (below.value, below.refs) == (
        "The Hollow Crown",
        (Ref("neighbours", "crown", "The Hollow Crown"),),
    )
    shown = region_sheet.neighbour_facts(saga, crown)
    assert _fact(shown, "Answers to").refs == (
        Ref("neighbours", "coven", "The Black Pool Coven"),
    )
    assert _fact(shown, "Place").refs == (
        Ref("neighbours", "drachenfels", "The Drachenfels"),
    )
    # A neighbour no one answers to lists no one.
    assert all(f.label != "Answer to it" for f in shown)


def test_a_place_links_where_it_is_its_claimant_and_what_is_here():
    saga = everything_saga()
    drachenfels = saga.neighbour("drachenfels")
    assert drachenfels is not None
    inside = _fact(region_sheet.neighbour_facts(saga, drachenfels), "Inside")
    assert inside.refs == (Ref("neighbours", "siebengebirge", "The Siebengebirge"),)
    facts = places.facts(saga, drachenfels)
    claimed = _fact(facts, "Claimed by")
    assert claimed.refs == (Ref("covenants", "cov1", claimed.value),)
    here = _fact(facts, "Here")
    assert Ref("creatures", "aeolus", "Aeolus") in here.refs
    assert here.value == ", ".join(r.name for r in here.refs)


def test_a_creature_links_its_place_and_lists_what_it_rules():
    saga = _court()
    aeolus = saga.creature("aeolus")
    assert aeolus is not None
    facts = creature_sheet.facts(saga, aeolus)
    rules = _fact(facts, "Rules")
    assert rules.refs == (Ref("neighbours", "coven", "The Black Pool Coven"),)
    assert _fact(facts, "Found at").refs[0].id == aeolus.place_id


def test_segments_cut_a_value_into_text_and_the_names_it_links():
    a = Ref("neighbours", "a", "Arnsberg")
    b = Ref("neighbours", "b", "Berg")
    assert references.segments("Arnsberg, inside Berg", (a, b)) == [
        ("Arnsberg", a),
        (", inside ", None),
        ("Berg", b),
    ]
    # A name the value doesn't hold is passed over.
    assert references.segments("Soest", (a,)) == [("Soest", None)]
    assert references.segments("", ()) == []


def test_go_to_lists_what_the_page_names_and_ends_with_go():
    saga = _court()
    coven = saga.neighbour("coven")
    assert coven is not None
    coven.links = [
        Link("characters", saga.characters[0].id, "Her apprentice"),
        Link("books", saga.books[0].id),
        Link("creatures", "aeolus"),  # named already, as its leader
    ]
    named = go_to_forms.targets(saga, coven)
    assert [(label, r.kind) for label, r in named] == [
        ("Ruler or leader", "creatures"),
        ("Answer to it", "neighbours"),
        ("Links", "characters"),
    ]
    step = go_to_forms.go_to(saga, coven)
    assert isinstance(step, Choose)
    choices = step.choices()
    assert [c.value for c in choices] == [r for _label, r in named]
    assert step.apply(choices[0].value) == Go(Ref("creatures", "aeolus", "Aeolus"))
    # A page that names nothing has nothing to go to.
    studium = saga.neighbour("studium")
    assert studium is not None
    assert isinstance(go_to_forms.go_to(saga, studium), Refuse)


def test_a_links_row_opens_the_record_it_points_at():
    saga = everything_saga()
    crown = saga.neighbour("crown")
    assert crown is not None
    crown.links.append(Link("books", saga.books[0].id))
    assert go_to_forms.opens(saga, crown, 0)
    assert not go_to_forms.opens(saga, crown, 1)  # a book has no page
    step = go_to_forms.open_link(saga, crown, 0)
    assert isinstance(step, Act)
    assert step.apply() == Go(Ref("creatures", "aeolus", "Aeolus"))
    assert isinstance(go_to_forms.open_link(saga, crown, 1), Refuse)


def test_go_to_is_offered_in_more_only_where_the_page_names_a_record():
    saga = _court()
    coven = saga.neighbour("coven")
    studium = saga.neighbour("studium")
    assert coven is not None and studium is not None
    on = menu_forms.Page(saga, actions.NodeKind.NEIGHBOUR, neighbour=coven)
    off = menu_forms.Page(saga, actions.NodeKind.NEIGHBOUR, neighbour=studium)
    assert actions.available("go_to", on)
    assert not actions.available("go_to", off)
    # The desktop draws the names as links instead.
    assert "go_to" not in {item.action for item in menu_forms.more_items(on)}


def test_the_ruler_is_chosen_from_the_records_or_typed():
    saga = everything_saga()
    coven = saga.neighbour("coven")
    assert coven is not None
    field = neighbour_forms.ruler_field(saga, coven)
    assert field.kind == "picker" and field.choose is not None
    step = field.choose(None)
    assert isinstance(step, Choose)
    heads = {c.facets[0][1] for c in step.choices()}
    assert heads == {"A name", "Characters", "Neighbours", "Bestiary"}
    # It can't rule itself.
    assert all(c.value != "coven" for c in step.choices())
    assert step.apply("aeolus") == Picked("aeolus")
    assert field.display is not None and field.display("aeolus") == "Aeolus"
    typed = step.apply(neighbour_forms.TYPE_A_NAME)
    assert isinstance(typed, Form)
    assert typed.apply({"name": "The Spinner"}) == Picked("The Spinner")
    assert field.display("The Spinner") == "The Spinner"


def test_editing_keeps_the_ruler_chosen_and_clears_it():
    saga = everything_saga()
    coven = saga.neighbour("coven")
    assert coven is not None
    form = neighbour_forms.edit_neighbour_form(saga, coven)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    form.apply(values | {"ruler": "aeolus"})
    assert coven.ruler == "aeolus"
    form.apply(values | {"ruler": None})
    assert coven.ruler == ""


def test_deleting_the_ruler_leaves_their_name():
    saga = _court()
    coven = saga.neighbour("coven")
    aeolus = saga.creature("aeolus")
    assert coven is not None and aeolus is not None
    creatures.delete(saga, aeolus)
    assert coven.ruler == "Aeolus"
    magus = saga.characters[0]
    coven.ruler = magus.id
    deletion.delete_character(saga, magus)
    assert coven.ruler == magus.name
    cologne = saga.neighbour("cologne")
    assert cologne is not None
    coven.ruler = "cologne"
    neighbours.delete(saga, cologne)
    assert coven.ruler == "Archbishop of Cologne"


def test_importing_the_saga_keeps_the_ruler_s_record():
    source = _court()
    gottfried = source.neighbour("gottfried")
    assert gottfried is not None
    gottfried.ruler = source.characters[0].id
    data = json.loads(json.dumps(transfer.export_saga_data(source)))
    target = Saga(id="dst", name="Target")
    plan = transfer.plan_import(target, data)
    transfer.apply(target, plan)
    coven = next(n for n in target.neighbours if n.name == "The Black Pool Coven")
    lord = next(n for n in target.neighbours if n.name == "Gottfried of Arnsberg")
    assert references.ruler_name(target, coven) == "Aeolus"
    assert references.ruler(target, lord) is next(
        c for c in target.characters if c.name == source.characters[0].name
    )
