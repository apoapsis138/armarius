"""Moving raw vis between holders, and where a vis store is kept
(STORY-412)."""

from __future__ import annotations

from dataclasses import asdict

from support import wait_until
from test_list_flows import ListCase, _open

from ars_magica_manager import possessions as pos
from ars_magica_manager import storage, vis
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import (
    Character,
    Covenant,
    Laboratory,
    Possession,
    Saga,
)
from ars_magica_manager.screens import FieldsDialog


def _saga() -> Saga:
    covenant = Covenant(id="cov1", saga_id="test_saga", name="Keep")
    covenant.possessions = [
        Possession(id="v1", kind="vis_store", name="Cask", art="Vim", pawns=5),
        Possession(id="p1", kind="item", name="Bell"),
    ]
    magus = Character(id="mag1", name="Leandro", type="magus", covenant_id="cov1")
    magus.raw_vis = {"creo": 3, "vim": 1}
    grog = Character(id="grog1", name="Hugo", type="grog", covenant_id="cov1")
    lab = Laboratory(id="lab1", covenant_id="cov1", name="Tower", owner_id="mag1")
    return Saga(
        id="test_saga",
        name="Saga",
        current_year=1225,
        current_season="Summer",
        covenants=[covenant, Covenant(id="cov2", saga_id="test_saga", name="Far")],
        characters=[magus, grog],
        laboratories=[lab],
    )


def test_held_lists_a_pool_by_art_and_a_covenants_stores():
    saga = _saga()
    assert [h.label for h in vis.held(saga.characters[0])] == [
        "Creo: 3 pawn(s)",
        "Vim: 1 pawn(s)",
    ]
    assert [h.label for h in vis.held(saga.covenants[0])] == ["Cask (Vim: 5 pawn(s))"]


def test_destinations_are_everyone_else_who_holds_vis():
    saga = _saga()
    magus = saga.characters[0]
    # Not himself, and not the grog (only a magus's sheet has Raw Vis).
    assert vis.destinations(saga, magus) == [
        ("Covenant: Keep", "covenant:cov1"),
        ("Covenant: Far", "covenant:cov2"),
        ("Laboratory: Tower", "laboratory:lab1"),
    ]
    assert ("Leandro", "character:mag1") in vis.destinations(saga, saga.covenants[0])
    assert vis.parse_destination(saga, "laboratory:lab1") is saga.laboratories[0]


def test_a_move_between_pools_records_both_diaries():
    saga = _saga()
    magus, lab = saga.characters[0], saga.laboratories[0]
    creo = vis.held(magus)[0]
    assert vis.move_problem(creo, 4) == "Only 3 pawn(s) of Creo vis to move."
    assert vis.move_problem(creo, 0) == "Move at least 1 pawn."
    assert vis.move_problem(creo, 3) is None
    vis.move(saga, magus, creo, 3, lab)
    # An emptied Art leaves the pool.
    assert magus.raw_vis == {"vim": 1}
    assert lab.raw_vis == {"creo": 3}
    [sent] = magus.diary
    assert (sent.year, sent.season) == (1225, "Summer")
    assert sent.name == "Moved 3 pawns of Creo vis to Tower"
    assert lab.diary[-1].name == "Received 3 pawns of Creo vis from Leandro"


def test_a_covenant_takes_vis_into_its_store_of_that_art():
    saga = _saga()
    magus, keep, far = saga.characters[0], saga.covenants[0], saga.covenants[1]
    vis.move(saga, magus, vis.held(magus)[1], 1, keep)
    assert keep.possessions[0].pawns == 6
    entry = keep.diary[-1]
    assert (entry.category, entry.vis_pawns, entry.vis_art) == ("Vis", 1, "Vim")
    assert entry.name == "Received 1 pawn of Vim vis from Leandro"
    # With no store of the Art, the covenant gets a new one, kept there.
    vis.move(saga, magus, vis.held(magus)[0], 2, far)
    [store] = far.possessions
    assert (store.name, store.art, store.pawns) == ("Creo vis", "Creo", 2)
    assert (store.location_kind, store.location_id) == ("covenant", "cov2")
    assert vis.location_label(saga, far, store) == "Far"


def test_emptying_a_covenants_store_removes_it():
    saga = _saga()
    keep, lab = saga.covenants[0], saga.laboratories[0]
    [cask] = vis.held(keep)
    vis.move(saga, keep, cask, 2, lab)
    assert keep.possessions[0].pawns == 3
    assert (keep.diary[-1].vis_pawns, keep.diary[-1].vis_art) == (-2, "Vim")
    vis.move(saga, keep, vis.held(keep)[0], 3, lab)
    assert [p.name for p in keep.possessions] == ["Bell"]
    assert lab.raw_vis == {"vim": 5}


def test_a_covenants_stores_read_and_spend_as_one_pool():
    saga = _saga()
    keep = saga.covenants[0]
    keep.possessions.append(
        Possession(id="v2", kind="vis_store", name="Jar", art="Vim", pawns=2)
    )
    pool = vis.covenant_pool(saga, "cov1", "Leandro")
    assert dict(pool) == {"vim": 7}
    assert pool.get("creo", 0) == 0
    # Spending takes from the stores in order, removing the emptied.
    pool["vim"] = 1
    assert [p.name for p in keep.possessions] == ["Bell", "Jar"]
    assert keep.possessions[1].pawns == 1
    assert keep.diary[-1].name == "Leandro used 6 pawns of Vim vis"
    pool["creo"] = pool.get("creo", 0) + 3
    assert keep.possessions[-1].name == "Creo vis" and pool["creo"] == 3
    del pool["vim"]
    assert sorted(pool) == ["creo"] and len(keep.diary) == 3
    # No covenant: nothing to draw on.
    assert vis.covenant_pool(saga, None, "Leandro") == {}


def test_an_old_saves_location_text_becomes_a_link():
    saga = _saga()
    keep = saga.covenants[0]
    keep.possessions += [
        Possession(id="v2", kind="vis_store", name="Jar", art="Creo", location="tower"),
        Possession(
            id="v3", kind="vis_store", name="Box", art="Ignem", location=" Leandro "
        ),
        Possession(
            id="v4", kind="vis_store", name="Urn", art="Terram", location="The vault"
        ),
        Possession(id="s1", kind="vis_source", name="Well", location="Tower"),
    ]
    loaded = Saga.from_dict(asdict(saga))
    stores = {p.name: p for p in loaded.covenants[0].possessions}

    def link(name: str) -> tuple[str, str | None, str]:
        store = stores[name]
        return (store.location_kind, store.location_id, store.location)

    # Named a laboratory or a character of the covenant: linked, text gone.
    assert link("Jar") == ("laboratory", "lab1", "")
    assert link("Box") == ("character", "mag1", "")
    # Anything else: the covenant keeps it, and the text stays as the note.
    assert link("Urn") == ("covenant", "cov1", "The vault")
    assert link("Cask") == ("covenant", "cov1", "")
    # A vis source's location is still free text.
    assert link("Well") == ("", None, "Tower")
    keep = loaded.covenants[0]
    assert vis.location_label(loaded, keep, stores["Jar"]) == "Laboratory: Tower"
    assert vis.location_label(loaded, keep, stores["Box"]) == "With Leandro"
    assert vis.location_label(loaded, keep, stores["Urn"]) == "Keep"
    # Loading again changes nothing.
    again = Saga.from_dict(asdict(loaded))
    assert asdict(again) == asdict(loaded)


def test_a_store_whose_keeper_is_gone_falls_back_to_the_covenant():
    saga = _saga()
    keep = saga.covenants[0]
    store = keep.possessions[0]
    store.location_kind, store.location_id = "laboratory", "gone"
    assert vis.location_label(saga, keep, store) == "Keep"
    [entry] = pos.entries_for_kind(saga, keep, "vis_store")
    assert "Kept at:[/] Keep" in pos.detail_text(entry)
    assert vis.location_options(saga, keep) == [
        ("Keep (the covenant)", "covenant:cov1"),
        ("Laboratory: Tower", "laboratory:lab1"),
        ("With Leandro", "character:mag1"),
        ("With Hugo", "character:grog1"),
    ]


async def test_m_on_a_vis_store_moves_pawns_to_a_laboratory():
    saga = _saga()
    storage.save_saga(saga)
    case = ListCase(
        ("covenant", "cov1"),
        "section-pos-vis_store",
        "pos-vis_store-list",
        lambda s: [p for p in s.covenants[0].possessions if p.kind == "vis_store"],
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace, _ = await _open(pilot, app, case)
        assert workspace.check_action("move_vis", ())
        assert not workspace.check_action("share_spell", ())
        await pilot.press("m")  # the chosen (only) store: no picker
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        dialog = app.screen
        dialog.query_one("#fld-pawns").value = "2"
        dialog.query_one("#fld-destination").value = "laboratory:lab1"
        await pilot.pause()
        dialog.query_one("#btn-save").press()
        assert await wait_until(
            pilot,
            lambda: (
                storage.load_saga("test_saga").laboratories[0].raw_vis == {"vim": 2}
            ),
        )
    saved = storage.load_saga("test_saga")
    assert saved.covenants[0].possessions[0].pawns == 3
    assert saved.covenants[0].diary[-1].name == "Moved 2 pawns of Vim vis to Tower"
    assert (
        saved.laboratories[0].diary[-1].name == "Received 2 pawns of Vim vis from Keep"
    )
