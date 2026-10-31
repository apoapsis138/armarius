"""The ports, anchorages and open water the book packs mark for ships."""

from ars_magica_manager import book_packs
from ars_magica_manager.book_packs import waters
from ars_magica_manager.models import CovenantStop
from ars_magica_manager.places import sync
from ars_magica_manager.rules import mobile, sites


def _named(saga, name, kind="place"):
    return next(n for n in saga.neighbours if n.kind == kind and n.name == name)


def test_every_row_of_the_tables_finds_its_record_with_supplements_in_play():
    for key in {*waters.PORT_TOWNS, *waters.NAMED_PORTS, *waters.MARKS}:
        pack = book_packs.PACKS[key]
        args = (pack.supplements,) if pack.supplements else ()
        assert pack.assemble(*args).saga.neighbours


def test_a_port_town_links_to_a_divine_harbour_beside_it_in_its_region():
    saga = book_packs.PACKS["hibernia"].build()
    town, harbour = (
        _named(saga, "Dublin", "town"),
        _named(saga, "The harbour of Dublin"),
    )
    assert harbour.place_id == town.place_id
    assert sites.waters_of(harbour) == mobile.PORT
    assert sites.aura_at(harbour) == (3, "Divine")
    assert [(link.kind, link.target_id) for link in town.links] == [
        ("places", harbour.id)
    ]


def test_a_printed_aura_wins_over_the_default_and_a_village_has_two():
    assert sites.aura_at(
        _named(book_packs.PACKS["provence"].build(), "The harbour of Narbonne")
    ) == (2, "Divine")
    assert sites.aura_at(
        _named(book_packs.PACKS["africa"].build(), "The harbour of Sidi Rafaa")
    ) == (2, "Divine")
    assert sites.aura_at(
        _named(book_packs.PACKS["levant"].build(), "The harbour of Damietta")
    ) == (1, "Divine")


def test_a_supplement_town_gets_its_harbour_only_with_the_supplement():
    pack = book_packs.PACKS["theban"]
    name = "The harbour of Miletos"
    assert name not in [n.name for n in pack.build().neighbours]
    found = _named(pack.assemble(("TtA",)).saga, name)
    assert sites.aura_at(found) == (2, "Divine")


def test_marks_keep_a_printed_aura_and_fill_a_blank_one():
    saga = book_packs.PACKS["theban"].build()
    thera = _named(saga, "The Bay of Thera")
    assert sites.waters_of(thera) == mobile.ANCHORAGE
    assert sites.aura_at(thera)[0] == 7
    assert sites.aura_at(_named(saga, "The Harbours of Constantinople")) == (
        3,
        "Divine",
    )


def _stopped_at_andros(name):
    saga = book_packs.PACKS["theban"].build()
    covenant = next(c for c in saga.covenants if c.name == name)
    harbour = _named(saga, "The harbour of Andros")
    covenant.stops.append(
        CovenantStop(saga.current_year, saga.current_season, harbour.id)
    )
    sync(saga)
    return covenant.aura, covenant.aura_realm


def test_a_covenant_stopping_at_a_harbour_takes_its_aura():
    assert _stopped_at_andros("Polyaigos") == (3, "Divine")


def test_a_stronger_port_overrides_a_ship_aura_on_the_surface():
    assert _stopped_at_andros("Favonius") == (3, "Divine")
