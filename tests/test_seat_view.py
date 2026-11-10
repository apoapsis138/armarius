"""seat_view: what leaves the host for a reader who isn't the storyguide.

Two checks. Nothing hidden from the players leaves: each place the pages
hide something from them is seeded with a marked word, and none of the
words may be in the copy. Nothing they may read is lost: every sheet of
the one-of-everything saga, drawn in Player view, shows the same text from
the copy as from the whole saga.
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest
from support import NODES, everything_saga
from test_sheet_text import _all_tabs, _open_node

from ars_magica_manager import players, storage, transfer, viewing
from ars_magica_manager.models import (
    CovenantDiaryEntry,
    Link,
    Neighbour,
    Saga,
    Secret,
)
from ars_magica_manager.seat_view import seat_view
from ars_magica_manager.tui.app import ArsMagicaManagerApp

#: What the copy must not hold, each word seeded where the pages hide it.
LEAKS = {
    "an unknown record": "LEAK-UNKNOWN",
    "a secret not revealed": "LEAK-SECRET",
    "a place's Roll Table": "LEAK-TABLE",
    "a covenant Diary line about an unknown record": "LEAK-COVDIARY",
    "a place's Diary line about an unknown record": "LEAK-PLACEDIARY",
    "a link to an unknown record": "LEAK-LINK",
    "a threat's stage to come": "LEAK-STAGE",
    "a threat's antagonist": "LEAK-ANTAGONIST",
}


def hidden_saga() -> Saga:
    """The one-of-everything saga with something hidden in every place
    the pages hide something from the players."""
    saga = everything_saga()
    grove = Neighbour(
        id="grove", name="The LEAK-UNKNOWN Grove", kind="place", known=False
    )
    saga.neighbours.append(grove)
    saga.covenants[0].secrets.append(Secret("Plot", "LEAK-SECRET"))
    saga.covenants[0].secrets.append(Secret("Known", "shown", 1220, "Spring"))
    place = saga.neighbour("drachenfels")
    assert place is not None
    place.details["tables"] = [
        {"name": "Omens", "die": "simple", "rows": "1-10: LEAK-TABLE"}
    ]
    place.details.setdefault("diary", []).append(
        {
            "year": 1220,
            "season": "Spring",
            "text": "LEAK-PLACEDIARY",
            "about": ["neighbours:grove"],
        }
    )
    saga.covenants[0].diary.append(
        CovenantDiaryEntry(year=1220, name="LEAK-COVDIARY", about=["neighbours:grove"])
    )
    saga.characters[0].links.append(Link("places", "grove", "LEAK-LINK"))
    crown = saga.neighbour("crown")
    assert crown is not None
    crown.details["antagonist"] = "LEAK-ANTAGONIST"
    crown.details["stages"].append(
        {"title": "LEAK-STAGE", "year": 1300, "season": "Winter"}
    )
    players.add(saga, {"name": "Anna", "passcode": "a long enough passcode"})
    return saga


def _text(saga: Saga) -> str:
    return json.dumps(asdict(saga))


def test_nothing_hidden_from_the_players_leaves():
    saga = hidden_saga()
    full = _text(saga)
    assert all(word in full for word in LEAKS.values())  # the seeds are there
    copy = _text(seat_view(saga, viewing.TABLE_VIEWER))
    leaked = [where for where, word in LEAKS.items() if word in copy]
    assert not leaked, f"left in the copy: {leaked}"
    assert "scrypt$" not in copy  # passcode hashes
    assert "Anna" in copy and "shown" in copy  # names and revealed secrets stay


def test_a_players_export_carries_their_seat_view():
    saga = hidden_saga()
    viewing.use(viewing.TABLE_VIEWER, saga)
    try:
        exported = json.dumps(transfer.export_saga_data(saga))
        one = json.dumps(transfer.export_data(saga, saga.covenants[0]))
    finally:
        viewing.use(viewing.STORYGUIDE_VIEWER)
    for text in (exported, one):
        leaked = [where for where, word in LEAKS.items() if word in text]
        assert not leaked, f"left in the export: {leaked}"


def test_the_storyguide_gets_everything_but_the_passcode_hashes():
    saga = hidden_saga()
    copy = _text(seat_view(saga, viewing.STORYGUIDE_VIEWER))
    assert all(word in copy for word in LEAKS.values())
    assert "scrypt$" not in copy


def test_the_copy_leaves_the_saga_itself_alone():
    saga = hidden_saga()
    before = _text(saga)
    seat_view(saga, viewing.TABLE_VIEWER)
    assert _text(saga) == before


def test_a_hidden_research_target_stays_hidden_until_reached():
    from ars_magica_manager.models import Breakthrough

    saga = everything_saga()
    magus = saga.characters[0]
    magus.breakthroughs = [Breakthrough(name="A", hidden_target=True, target=41)]
    copy = seat_view(saga, viewing.TABLE_VIEWER)
    assert copy.characters[0].breakthroughs[0].target == 0
    magus.breakthroughs[0].reached = True
    assert (
        seat_view(saga, viewing.TABLE_VIEWER).characters[0].breakthroughs[0].target
        == 41
    )


async def _player_view_text(saga: Saga, node: str) -> str:
    storage.save_saga(saga)
    viewing.set_player_view(saga.id, True)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        workspace = await _open_node(pilot, app, node)
        return "\n".join(await _all_tabs(pilot, app, workspace))


#: The sheets a player never sees (viewing.STORYGUIDE_ONLY): no node in
#: Player view's tree.
STORYGUIDE_NODES = ("armarium", "custodia")


@pytest.mark.parametrize("node", sorted(n for n in NODES if n not in STORYGUIDE_NODES))
async def test_every_sheet_reads_the_same_from_the_copy(node: str):
    whole = await _player_view_text(hidden_saga(), node)
    copied = await _player_view_text(
        seat_view(hidden_saga(), viewing.TABLE_VIEWER), node
    )
    assert copied == whole
