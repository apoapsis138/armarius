from ars_magica_manager import catalog


def test_house_catalog_loads_all_twelve_houses():
    entries = catalog.load_house_catalog()
    assert len(entries) == 12


def test_house_catalog_by_id_contains_bonisagus():
    by_id = catalog.load_house_catalog_by_id()
    assert by_id["house_bonisagus"].name == "Bonisagus"


def test_every_house_names_its_creation_benefit_from_the_virtue_catalog():
    # STORY-1315: a named Virtue (one or a choice), or a free kind of Virtue.
    virtues = catalog.load_virtue_flaw_catalog_by_id()
    abilities = {a.name for a in catalog.load_ability_catalog()}
    for house in catalog.load_house_catalog():
        assert house.benefit, house.id
        assert bool(house.virtues) != bool(house.free), house.id
        for option in house.virtues:
            entry = virtues[option["vf_id"]]
            assert set(option["params"]) == set(entry.parameters), house.id
        assert not house.ability or house.ability in abilities, house.id
    by_id = catalog.load_house_catalog_by_id()
    assert [o["params"] for o in by_id["house_bonisagus"].virtues] == [
        {"ability": "magic theory"},
        {"ability": "intrigue"},
    ]
