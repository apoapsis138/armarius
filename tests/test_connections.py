"""A character's, covenant's or laboratory's Connections: worked out from
the records that point at it (a faction's Links, a neighbour's ruler, a
gild's members) or that it sits in (its covenant, its place), never
stored; a place's or creature's Linked from; Go To lists them; and a
faction's Diary."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import connections, neighbours
from ars_magica_manager.forms import go_to as go_to_forms
from ars_magica_manager.forms import world as world_forms
from ars_magica_manager.models import Link, Saga
from ars_magica_manager.references import Ref
from ars_magica_manager.sheets import creature as creature_sheet
from ars_magica_manager.sheets import region as region_sheet


def _facts(saga: Saga, record) -> dict[str, tuple[str, tuple[Ref, ...]]]:
    return {f.label: (f.value, f.refs) for f in connections.facts(saga, record)}


def _court() -> Saga:
    """The sample saga, with Leandro a member of the Black Pool Coven and
    ruler of the Hollow Crown, and the Keep in the Drachenfels."""
    saga = everything_saga()
    coven = saga.neighbour("coven")
    crown = saga.neighbour("crown")
    keep = saga.covenant("cov1")
    assert coven is not None and crown is not None and keep is not None
    coven.details["roster"] = [
        {"who": "characters:mag1", "role": "its secret patron"},
        {"who": "covenants:cov1", "role": ""},
    ]
    crown.ruler = "mag1"
    keep.place_id = "drachenfels"
    return saga


def test_a_character_shows_their_covenant_factions_and_what_they_rule():
    saga = _court()
    leandro = saga.character("mag1")
    found = _facts(saga, leandro)
    assert list(found) == ["Covenant", "Member of", "Rules", "Linked from"]
    assert found["Covenant"] == ("Keep", (Ref("covenants", "cov1", "Keep"),))
    assert found["Member of"] == (
        "The Black Pool Coven (its secret patron)",
        (Ref("neighbours", "coven", "The Black Pool Coven"),),
    )
    assert found["Rules"] == (
        "The Hollow Crown",
        (Ref("neighbours", "crown", "The Hollow Crown"),),
    )
    # Aeolus's link to him is not a faction's: Linked from.
    assert found["Linked from"][1] == (Ref("creatures", "aeolus", "Aeolus"),)


def test_a_covenant_shows_where_it_is_its_gilds_and_its_factions():
    saga = _court()
    found = _facts(saga, saga.covenant("cov1"))
    assert list(found) == ["Located in", "Gilds", "Member of"]
    assert found["Located in"] == (
        "The Drachenfels, inside The Siebengebirge",
        (
            Ref("neighbours", "drachenfels", "The Drachenfels"),
            Ref("neighbours", "siebengebirge", "The Siebengebirge"),
        ),
    )
    assert found["Gilds"] == (
        "Hermetic, in Rhine",
        (Ref("tribunals", "rhine", "Rhine"),),
    )
    assert found["Member of"][0] == "The Black Pool Coven"


def test_a_laboratory_is_where_its_covenant_is_unless_placed_itself():
    saga = _court()
    tower = saga.laboratory("lab1")
    found = _facts(saga, tower)
    assert found["Covenant"][0] == "Keep"
    assert found["Located in"][0] == "The Drachenfels, inside The Siebengebirge"
    tower.place_id = "siebengebirge"
    assert _facts(saga, tower)["Located in"] == (
        "The Siebengebirge",
        (Ref("neighbours", "siebengebirge", "The Siebengebirge"),),
    )


def test_connections_follow_the_records_they_come_from():
    """Nothing is stored: unlinking, deleting or moving the other side
    changes them at once, and a record with none has none."""
    saga = _court()
    coven = saga.neighbour("coven")
    assert coven is not None
    coven.links.clear()
    saga.neighbours.remove(coven)
    found = _facts(saga, saga.character("mag1"))
    assert "Member of" not in found
    saga.neighbours = [n for n in saga.neighbours if n.id != "drachenfels"]
    assert "Located in" not in _facts(saga, saga.covenant("cov1"))
    alys = saga.character("comp1")
    assert alys is not None
    alys.covenant_id = None
    assert connections.facts(saga, alys) == []


def test_a_link_to_a_record_gone_names_nothing():
    saga = _court()
    coven = saga.neighbour("coven")
    assert coven is not None
    coven.links.append(Link("characters", "nobody"))
    assert _facts(saga, saga.character("comp1")).get("Member of") is None


def test_a_place_and_a_creature_list_what_links_to_them():
    saga = _court()
    coven = saga.neighbour("coven")
    drachenfels = saga.neighbour("drachenfels")
    aeolus = saga.creature("aeolus")
    assert coven is not None and drachenfels is not None and aeolus is not None
    coven.links.append(Link("places", "drachenfels", "meets here"))
    coven.links.append(Link("creatures", "aeolus"))
    place = {f.label: f for f in region_sheet.neighbour_facts(saga, drachenfels)}
    assert place["Linked from"].value == "The Black Pool Coven (meets here)"
    creature = {f.label: f for f in creature_sheet.facts(saga, aeolus)}
    # The Hollow Crown's link is the sample's own.
    assert creature["Linked from"].refs == (
        Ref("neighbours", "coven", "The Black Pool Coven"),
        Ref("neighbours", "crown", "The Hollow Crown"),
    )


def test_links_rows_list_only_the_record_s_own_links():
    """What links here is the page's Connections or Linked from, not more
    rows under Links."""
    saga = _court()
    keep = saga.covenant("cov1")
    assert keep is not None
    keep.links.append(Link("characters", "comp1", "steward"))
    rows = world_forms.link_rows(saga, keep)
    assert rows == [(0, "Character: Alys: steward")]


def test_go_to_lists_a_character_s_connections():
    saga = _court()
    leandro = saga.character("mag1")
    named = go_to_forms.targets(saga, leandro)
    assert ("Member of", Ref("neighbours", "coven", "The Black Pool Coven")) in named
    assert ("Rules", Ref("neighbours", "crown", "The Hollow Crown")) in named
    assert go_to_forms.has_targets(saga, saga.laboratory("lab1"))


def test_a_faction_keeps_a_diary_as_a_place_does():
    saga = _court()
    coven = saga.neighbour("coven")
    assert coven is not None
    kind = neighbours.kind_of(coven)
    assert [t.tab_id for t in kind.more] == ["tab-nb-faction-diary"]
    (diary,) = kind.more[0].lists
    assert diary.title(saga, coven) == "Diary (0)"
    assert diary.grid(saga, coven).rows == []
    coven.details["diary"] = [
        {"year": 1220, "season": "Spring", "text": "The coven courts the Count."}
    ]
    assert diary.grid(saga, coven).rows == [
        ["Spring 1220", "The coven courts the Count."]
    ]
