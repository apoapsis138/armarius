"""A faction's members: kept once on its roster, each with a role, the
way back worked out; older saves' links and lieges moved to the roster."""

from __future__ import annotations

from ars_magica_manager import connections, memberships
from ars_magica_manager.models import Character, Creature, Link, Neighbour, Saga


def _court() -> tuple[Saga, Neighbour]:
    saga = Saga(id="s", name="S")
    court = Neighbour(id="court", name="The Spinner's Court", kind="faction")
    saga.neighbours.append(court)
    return saga, court


def test_older_saves_move_a_courts_factions_to_its_roster():
    data = {
        "id": "s",
        "name": "S",
        "characters": [{"id": "jorg", "name": "Jorg", "type": "companion"}],
        "neighbours": [
            {
                "id": "court",
                "name": "The Court",
                "kind": "faction",
                "links": [
                    {"kind": "characters", "target_id": "jorg", "note": "their foe"}
                ],
            },
            {"id": "haspel", "name": "Dame Haspel", "answers_to": "court"},
            {"id": "plot", "name": "A Plot", "kind": "threat", "answers_to": "court"},
            {"id": "lord", "name": "A Lord", "kind": "lord", "answers_to": "duke"},
            {"id": "duke", "name": "A Duke", "kind": "lord"},
        ],
    }
    saga = Saga.from_dict(data)
    court = saga.neighbour("court")
    assert court is not None
    assert memberships.roster(court) == [{"who": "neighbours:haspel", "role": ""}]
    assert [link.note for link in court.links] == ["their foe"]
    for record_id, liege in (("haspel", None), ("plot", "court"), ("lord", "duke")):
        found = saga.neighbour(record_id)
        assert found is not None and found.answers_to == liege


def test_a_member_lists_every_faction_it_belongs_to():
    saga, court = _court()
    gild = Neighbour(id="gild", name="The Weavers", kind="faction")
    jorg = Character(id="jorg", name="Jorg", type="companion")
    saga.neighbours.append(gild)
    saga.characters.append(jorg)
    memberships.roster(court).append({"who": "characters:jorg", "role": "fiddler"})
    memberships.roster(gild).append({"who": memberships.who_of(jorg), "role": ""})
    assert [(f.name, role) for f, role in memberships.factions_of(saga, jorg)] == [
        ("The Spinner's Court", "fiddler"),
        ("The Weavers", ""),
    ]
    (fact,) = connections.member_of(saga, jorg)
    assert fact.value == "The Spinner's Court (fiddler), The Weavers"


def test_a_member_since_deleted_shows_as_gone():
    saga, court = _court()
    hush = Creature(id="hush", name="Hush")
    saga.creatures.append(hush)
    memberships.roster(court).append({"who": "creatures:hush", "role": "watcher"})
    assert memberships.members_grid(saga, court).rows == [
        ["Hush", "Bestiary", "watcher"]
    ]
    saga.creatures.remove(hush)
    assert memberships.members_grid(saga, court).rows == [
        ["(no longer in the saga)", "", "watcher"]
    ]
    assert memberships.members(saga, court) == []


def test_the_chooser_offers_records_but_not_places_or_the_faction():
    saga, court = _court()
    saga.neighbours.append(Neighbour(id="hollow", name="The Hollow", kind="place"))
    saga.characters.append(Character(id="jorg", name="Jorg", type="companion"))
    saga.creatures.append(Creature(id="hush", name="Hush"))
    offered = {c.value for c in memberships.choose_member(saga, court).choices()}
    assert offered == {"characters:jorg", "creatures:hush"}


def test_a_link_from_a_faction_is_no_longer_a_membership():
    saga, court = _court()
    jorg = Character(id="jorg", name="Jorg", type="companion")
    saga.characters.append(jorg)
    court.links.append(Link("characters", "jorg", "owes us"))
    assert connections.member_of(saga, jorg) == []
    (fact,) = connections.linked_from(saga, jorg)
    assert fact.value == "The Spinner's Court (owes us)"
