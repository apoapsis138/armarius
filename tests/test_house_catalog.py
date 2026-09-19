from ars_magica_manager import catalog


def test_house_catalog_loads_all_twelve_houses():
    entries = catalog.load_house_catalog()
    assert len(entries) == 12


def test_house_catalog_ids_are_unique():
    entries = catalog.load_house_catalog()
    ids = [entry.id for entry in entries]
    assert len(ids) == len(set(ids))


def test_house_catalog_entries_have_descriptions():
    entries = catalog.load_house_catalog()
    assert all(entry.description for entry in entries)


def test_house_catalog_by_id_contains_bonisagus():
    by_id = catalog.load_house_catalog_by_id()
    assert by_id["house_bonisagus"].name == "Bonisagus"
