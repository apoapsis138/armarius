"""Merge Doubled Records: a faction that shares its name with one
character or creature becomes part of that record, and goes."""

from __future__ import annotations

from ars_magica_manager import memberships, merges
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.models import (
    AtlasMap,
    Attitude,
    Character,
    Covenant,
    Creature,
    Favour,
    Link,
    Neighbour,
    Pin,
    Saga,
    as_secrets,
    secret_words,
)


def _saga() -> tuple[Saga, Neighbour, Creature]:
    saga = Saga(id="s", name="S")
    saga.covenants.append(Covenant(id="home", saga_id="s", name="Home"))
    court = Neighbour(id="court", name="The Court", kind="faction")
    hush = Neighbour(
        id="hush-n",
        name="Hush",
        kind="faction",
        summary="A tall figure among the webs.",
        secrets=as_secrets("It is the Spinner's eyes."),
        place_id="hollow",
        attitudes=[Attitude("home", -1)],
        favours=[Favour("A riddle answered")],
        details={"wants": "Whatever the Spinner wants", "offers": "Questions"},
    )
    creature = Creature(id="hush", name="Hush", notes="Might 15.")
    hush.links.append(Link("creatures", "hush", "its stat block"))
    hush.links.append(Link("places", "hollow", "where it stands"))
    court.details["roster"] = [{"who": "neighbours:hush-n", "role": "watcher"}]
    puppet = Neighbour(id="puppet", name="A Puppet", kind="lord", ruler="hush-n")
    hollow = Neighbour(id="hollow", name="The Hollow", kind="place")
    saga.neighbours += [court, hush, puppet, hollow]
    saga.creatures.append(creature)
    saga.maps.append(AtlasMap(id="m", name="Map"))
    saga.pins.append(Pin("m", "neighbours", "hush-n", 0.5, 0.5))
    return saga, hush, creature


def test_a_faction_named_for_one_creature_is_a_double():
    saga, hush, creature = _saga()
    lord = Neighbour(id="w", name="Wolfram", kind="lord")
    saga.neighbours.append(lord)
    saga.characters.append(Character(id="w", name="Wolfram", type="companion"))
    (found,) = merges.doubles(saga)
    assert (found.neighbour, found.record, found.kind) == (hush, creature, "creature")
    assert merges.brings(saga, found) == (
        "attitude toward 1 covenant; 1 favour; 1 link; its summary, wants and "
        "offers; member of The Court; rules A Puppet"
    )


def test_two_records_of_the_name_are_not_guessed_between():
    saga, _hush, _creature = _saga()
    saga.characters.append(Character(id="h2", name="Hush", type="grog"))
    assert merges.doubles(saga) == []


def test_merging_moves_everything_onto_the_creature():
    saga, hush, creature = _saga()
    (found,) = merges.doubles(saga)
    merges.merge(saga, found)
    assert hush not in saga.neighbours
    assert [a.covenant_id for a in creature.attitudes] == ["home"]
    assert [f.what for f in creature.favours] == ["A riddle answered"]
    assert [link.note for link in creature.links] == ["where it stands"]
    assert creature.notes == (
        "Might 15.\n\nA tall figure among the webs.\n\n"
        "Wants: Whatever the Spinner wants\n\nOffers: Questions"
    )
    assert secret_words(creature.secrets) == "It is the Spinner's eyes."
    assert creature.place_id == "hollow"
    court, puppet = saga.neighbour("court"), saga.neighbour("puppet")
    assert court is not None and puppet is not None
    assert memberships.roster(court) == [{"who": "creatures:hush", "role": "watcher"}]
    assert puppet.ruler == "hush"
    assert [(p.kind, p.record_id) for p in saga.pins] == [("creatures", "hush")]


def test_a_character_takes_the_words_but_no_pins():
    saga, hush, creature = _saga()
    saga.creatures.remove(creature)
    jorg = Character(id="hush", name="Hush", type="companion", summary="")
    saga.characters.append(jorg)
    (found,) = merges.doubles(saga)
    merges.merge(saga, found)
    assert jorg.summary.startswith("A tall figure among the webs.")
    assert saga.pins == []
    assert hush not in saga.neighbours


def test_the_form_merges_only_the_ticked_pairs():
    saga, hush, _creature = _saga()
    form = merges.merge_form(saga)
    assert isinstance(form, Form)
    labels = [f.key for f in form.fields()]
    assert "merge_0" in labels
    assert form.apply({"merge_0": False}) == ["Nothing merged."]
    assert hush in saga.neighbours
    assert form.apply({"merge_0": True}) == ["Merged Hush into the creature."]
    assert hush not in saga.neighbours
    assert isinstance(merges.merge_form(saga), Refuse)
