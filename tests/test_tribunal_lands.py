"""A Tribunal's lands: set on a place, taken by everything inside it,
and kept apart from a covenant's membership of a Tribunal."""

from __future__ import annotations

from ars_magica_manager import connections, neighbour_filter, places
from ars_magica_manager.models import (
    Character,
    Covenant,
    Laboratory,
    Neighbour,
    Saga,
    Tribunal,
)


def _saga() -> Saga:
    saga = Saga(id="s", name="S")
    saga.tribunals += [
        Tribunal(id="rhine", name="Rhine"),
        Tribunal(id="alps", name="Alps"),
    ]
    forest = Neighbour(
        id="forest",
        name="The Black Forest",
        kind="place",
        details={"tribunal": "rhine"},
    )
    glade = Neighbour(id="glade", name="A Glade", kind="place", place_id="forest")
    pass_ = Neighbour(
        id="pass",
        name="The High Pass",
        kind="place",
        place_id="forest",
        details={"tribunal": "alps"},
    )
    lord = Neighbour(id="lord", name="A Lord", kind="lord", place_id="glade")
    saga.neighbours += [forest, glade, pass_, lord]
    saga.covenants += [
        Covenant(id="hopeful", saga_id="s", name="Hopeful", place_id="glade"),
        Covenant(
            id="member",
            saga_id="s",
            name="Member",
            place_id="glade",
            tribunal_id="rhine",
        ),
    ]
    saga.characters.append(
        Character(id="c", name="C", type="grog", covenant_id="hopeful")
    )
    saga.laboratories.append(Laboratory(id="lab", name="Lab", covenant_id="member"))
    return saga


def _lands(saga: Saga, record: object) -> str | None:
    found = places.lands_of(saga, record)  # type: ignore[arg-type]
    return found.id if found is not None else None


def test_whats_inside_takes_the_nearest_place_that_names_a_tribunal():
    saga = _saga()
    assert _lands(saga, saga.neighbour("glade")) == "rhine"
    assert _lands(saga, saga.neighbour("lord")) == "rhine"
    assert _lands(saga, saga.neighbour("pass")) == "alps"
    assert _lands(saga, saga.character("c")) == "rhine"
    assert _lands(saga, saga.laboratory("lab")) == "rhine"
    assert _lands(saga, Neighbour(id="x", name="Nowhere", kind="lord")) is None


def test_lying_in_a_tribunals_lands_is_not_belonging_to_it():
    saga = _saga()
    (hopeful,) = connections.lands_fact(saga, saga.covenant("hopeful"))
    (member,) = connections.lands_fact(saga, saga.covenant("member"))
    assert hopeful.value == "Rhine (not a member)"
    assert member.value == "Rhine"
    assert saga.covenant("hopeful").tribunal_id is None  # type: ignore[union-attr]


def test_the_region_filters_by_a_tribunals_lands():
    saga = _saga()
    assert [t.id for t in neighbour_filter.tribunals(saga)] == ["rhine", "alps"]
    neighbour_filter.choose(saga, neighbour_filter.Filter(tribunal="alps"))
    try:
        assert [n.id for n in neighbour_filter.shown(saga, "places")] == ["pass"]
        assert (
            neighbour_filter.describe(saga, neighbour_filter.current(saga))
            == "in the lands of Alps"
        )
    finally:
        neighbour_filter.choose(saga, neighbour_filter.Filter())


def test_the_place_form_asks_only_once_the_saga_has_a_tribunal():
    saga = _saga()
    keys = [f.key for f in places.fields(saga, saga.neighbour("forest"))]
    assert places.LANDS in keys
    saga.tribunals.clear()
    assert places.LANDS not in [f.key for f in places.fields(saga, None)]


def test_the_region_by_place_nests_what_rests_on_each_place():
    from ars_magica_manager.models import Creature
    from ars_magica_manager.sheets import region

    saga = _saga()
    saga.creatures.append(Creature(id="sprite", name="A Sprite", place_id="glade"))
    saga.neighbours.append(Neighbour(id="drifter", name="A Drifter", kind="faction"))
    shown = [(r.depth, r.name) for r in region.by_place(saga)]
    assert shown == [
        (0, "The Black Forest"),
        (1, "A Glade"),
        (2, "A Lord"),
        (2, "Hopeful"),
        (2, "Member"),
        (2, "A Sprite"),
        (1, "The High Pass"),
        (0, "Placed nowhere (1)"),
        (1, "A Drifter"),
    ]


def test_a_custom_is_lore_listed_by_itself_with_no_attitude():
    from ars_magica_manager import neighbours
    from ars_magica_manager.sheets import region

    saga = _saga()
    custom = neighbours.add(saga, "custom", "Honour among the Icelanders")
    custom.details["rules"] = "Hof and ohof. Pp. 22-23.\nMore."
    custom.place_id = "glade"
    assert neighbours.kind_of(custom).group == "customs"
    assert region.customs_grid(saga).rows == [
        ["Honour among the Icelanders", "A Glade", "Hof and ohof. Pp. 22-23."]
    ]
    assert neighbours.score(saga, custom) is None
    assert "customs" in [g.key for g in neighbours.groups_shown(saga)]
    assert region.card_subtitle(custom) == "Custom"
