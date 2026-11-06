"""Vis sources at their places: a held source names its Place, a place
lists and totals its sources and those inside it, an aura not of Magic
taints the vis (DE p. 422), and an unclaimed source is claimed."""

from __future__ import annotations

from ars_magica_manager import places, vis_sites
from ars_magica_manager.models import Covenant, Neighbour, Possession, Saga
from ars_magica_manager.sheets import region


def _saga() -> tuple[Saga, Covenant, Neighbour, Neighbour]:
    saga = Saga(id="s", name="S")
    forest = Neighbour(id="forest", name="The Forest", kind="place")
    well = Neighbour(
        id="well",
        name="The Whispering Well",
        kind="place",
        realm="Faerie",
        place_id="forest",
        details={"aura": 4},
    )
    home = Covenant(id="home", saga_id="s", name="Home")
    home.possessions.append(
        Possession(
            id="silk",
            kind="vis_source",
            name="Well silk",
            art="Vim",
            pawns=4,
            season="Autumn",
            location="The Whispering Well",
        )
    )
    saga.neighbours += [forest, well]
    saga.covenants.append(home)
    return saga, home, forest, well


def test_an_older_save_places_a_source_by_its_location():
    saga, *_ = _saga()
    from dataclasses import asdict

    again = Saga.from_dict(asdict(saga))
    (source,) = again.covenants[0].possessions
    assert (source.place_id, source.place_level) == ("well", 0)


def test_a_place_lists_its_sources_and_taints_them():
    saga, home, forest, well = _saga()
    home.possessions[0].place_id = "well"
    grid = vis_sites.vis_grid(saga, well)
    assert grid.rows == [["Well silk", "Vim", "4", "Autumn", "Home", "Faerie vis"]]
    assert grid.keys == [None]  # edited on its covenant
    assert vis_sites.vis_text(saga, well) == "4 pawns a year (Vim 4)"
    assert vis_sites.vis_text(saga, forest) == "4 in the places inside"
    assert vis_sites.taint(saga, "forest") == ""


def test_an_unclaimed_source_is_claimed_by_a_covenant():
    saga, home, _forest, well = _saga()
    ops = vis_sites.vis_ops(saga, well)
    assert ops.add is not None
    form = ops.add()
    form.apply({"name": "Golden acorns", "art": "Creo", "pawns": 3, "season": "Autumn"})
    assert [e["name"] for e in vis_sites.unclaimed(well)] == ["Golden acorns"]
    assert vis_sites.vis_grid(saga, well).keys == [0]
    rows = region.by_place(saga)
    assert any(r.name == "Golden acorns" and "unclaimed" in r.what for r in rows)
    edit = ops.edit
    assert edit is not None
    edit(0).apply({"claim": "home"})
    assert vis_sites.unclaimed(well) == []
    claimed = home.possessions[-1]
    assert (claimed.name, claimed.art, claimed.place_id) == (
        "Golden acorns",
        "Creo",
        "well",
    )


def test_deleting_a_place_leaves_its_sources_placed_nowhere():
    saga, home, _forest, well = _saga()
    home.possessions[0].place_id = "well"
    saga.neighbours.remove(well)
    places.sync(saga)
    assert home.possessions[0].place_id is None
