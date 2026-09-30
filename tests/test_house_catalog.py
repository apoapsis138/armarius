from ars_magica_manager import catalog


def test_house_catalog_loads_all_twelve_houses():
    entries = catalog.load_house_catalog()
    assert len(entries) == 12


def test_house_catalog_by_id_contains_bonisagus():
    by_id = catalog.load_house_catalog_by_id()
    assert by_id["house_bonisagus"].name == "Bonisagus"
