"""The content packs built from the Tribunal sourcebooks: each builds,
is shipped up to date, imports clean into a new saga, and puts its book
in play."""

from __future__ import annotations

import json

from ars_magica_manager import book_packs, packs, sourcebooks, transfer
from ars_magica_manager.book_packs import builder
from ars_magica_manager.forms import creation as creation_forms
from ars_magica_manager.models import Saga
from ars_magica_manager.tribunal_packages import normandy as normandy_package
from ars_magica_manager.tribunal_packages import rhine as rhine_package

RHINE = book_packs.PACKS["rhine"]
NORMANDY = book_packs.PACKS["normandy"]


def _texts(value) -> list[str]:
    """Every string in a JSON-ready structure."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [t for v in value.values() for t in _texts(v)]
    if isinstance(value, list):
        return [t for v in value for t in _texts(v)]
    return []


def test_the_rhine_pack_holds_the_tribunal_of_1220():
    saga = RHINE.build()
    (tribunal,) = saga.tribunals
    assert tribunal.package == rhine_package.KEY
    assert (tribunal.next_year, tribunal.meets_every) == (1221, 7)
    names = {c.name for c in saga.covenants}
    assert names >= {
        "Durenmar",
        "Crintera",
        "Irencillia",
        "Fengheld",
        "Dankmar",
        "Roznov",
        "Oculus Septentrionalis",
        "Triamore",
        "Waddenzee",
        "Heorot",
    }
    assert all(c.tribunal_id == tribunal.id and not c.played for c in saga.covenants)
    founded = {c.name: c.year_founded for c in saga.covenants}
    assert founded["Durenmar"] == 767 and founded["Heorot"] == 1215
    gilds = {g["name"].split(" (")[0]: g for g in rhine_package.gilds(tribunal)}
    assert set(gilds) == {
        "Oak Gild",
        "Hawthorn Gild",
        "Ash Gild",
        "Elder Gild",
        "Linden Gild",
        "Apple Gild",
    }
    durenmar = next(c for c in saga.covenants if c.name == "Durenmar")
    assert durenmar.id in gilds["Oak Gild"]["members"]
    praeco = saga.character(tribunal.praeco_id or "")
    quaesitor = saga.character(tribunal.quaesitor_id or "")
    assert praeco is not None and praeco.name == "Murion"
    assert quaesitor is not None and quaesitor.name == "Caecilius"
    assert praeco.covenant_id == durenmar.id
    assert praeco.hermetic.house == "house_bonisagus"
    assert len([c for c in saga.characters if c.type == "magus"]) >= 60
    assert len(tribunal.rulings) >= 10 and len(tribunal.cases) >= 8
    assert all(case.status == "open" for case in tribunal.cases)
    # Hermetic history only, in order, and up to the pack's date.
    years = [e.year for e in tribunal.diary]
    assert years == sorted(years) and years[-1] <= 1220 and len(years) >= 50
    # The Great Library comes as Book records owned by Durenmar.
    owned = [b for b in saga.books if b.owner_id == durenmar.id]
    assert len(owned) >= 10
    assert all(b.owner_kind == "covenant" for b in saga.books)


def test_the_rhine_pack_places_its_covenants_in_the_forests():
    saga = RHINE.build()
    place_ids = {n.id for n in saga.neighbours if n.kind == "place"}
    kinds = {n.kind for n in saga.neighbours}
    assert kinds >= {"place", "town", "lord", "church", "faction", "threat"}
    for covenant in saga.covenants:
        if covenant.name == "Oculus Septentrionalis":
            continue
        assert covenant.place_id in place_ids, covenant.name
    for neighbour in saga.neighbours:
        assert neighbour.place_id is None or neighbour.place_id in place_ids
        if neighbour.answers_to is not None:
            assert any(n.id == neighbour.answers_to for n in saga.neighbours)
    threats = [n for n in saga.neighbours if n.kind == "threat"]
    assert any(n.name == "The Curse of the Rhine Gorge" for n in threats)
    gorge = next(n for n in threats if n.name == "The Curse of the Rhine Gorge")
    assert len(gorge.details["stages"]) >= 5
    regios = [n for n in saga.neighbours if n.kind == "place" and n.details["levels"]]
    assert len(regios) >= 5
    for place in regios:
        for level in place.details["levels"]:
            assert level["realm"] in ("Magic", "Faerie", "Divine", "Infernal")


def test_the_pack_text_keeps_its_secrets_under_the_heading():
    data = book_packs.data(RHINE)
    texts = _texts(data["saga"])
    assert not [t for t in texts if "SECRET" in t]
    hidden = [t for t in texts if builder.SECRETS + "\n" in t]
    assert len(hidden) >= 10
    assert data["book"] == "GotF" and "Creative Commons" in data["source"]


def test_the_shipped_rhine_pack_is_up_to_date():
    """data/packs/rhine.amm.json is what the module builds (rebuild it
    with tools/build_packs.py after changing the module)."""
    shipped = json.loads(book_packs.path_of(RHINE).read_text(encoding="utf-8"))
    built = book_packs.data(RHINE)
    assert shipped["name"] == built["name"] and shipped["book"] == built["book"]
    assert packs.summary(shipped) == packs.summary(built)
    for kind in ("covenants", "characters", "neighbours", "books", "tribunals"):
        assert {(r["name"], r.get("detail")) for r in shipped["saga"][kind]} == {
            (r["name"], r.get("detail")) for r in built["saga"][kind]
        }, kind


def test_the_rhine_pack_imports_clean_into_a_new_saga():
    data = book_packs.data(RHINE)
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    plan = transfer.plan_import(target, data)
    transfer.apply(target, plan)
    assert packs.after_import(target, data) == [
        "Guardians of the Forests: The Rhine Tribunal is now in play.",
        packs.assumptions_note("Guardians of the Forests: The Rhine Tribunal"),
    ]
    assert target.books_in_play is not None and "GotF" in target.books_in_play
    assert len(target.covenants) == len(data["saga"]["covenants"])
    assert len(target.neighbours) == len(data["saga"]["neighbours"])
    ids = {n.id for n in target.neighbours}
    for record in [*target.covenants, *target.neighbours]:
        assert record.place_id is None or record.place_id in ids
    (tribunal,) = target.tribunals
    assert tribunal.praeco_id in {c.id for c in target.characters}
    # Importing it again adds nothing.
    again = transfer.plan_import(target, data)
    assert not again.covenants and not again.characters and not again.neighbours


def test_a_saga_with_every_book_in_play_stays_so():
    saga = Saga(id="s", name="S")
    assert not sourcebooks.put_in_play(saga, "GotF") and saga.books_in_play is None


def test_new_saga_offers_the_shipped_packs_first():
    fields = {f.key: f for f in creation_forms.saga_fields(None)}
    options = fields["pack"].options or []
    assert options[0] == ("None", "")
    shipped = {path: label for label, path in options[1:]}
    assert shipped[str(book_packs.path_of(RHINE))].startswith(
        "Rhine Tribunal: 10 covenants, "
    )
    assert shipped[str(book_packs.path_of(NORMANDY))].startswith(
        "Normandy Tribunal: 15 covenants, "
    )


def test_masters_and_archmagi_carry_retired_magi_s_sigils():
    saga = RHINE.build()
    (tribunal,) = saga.tribunals
    held = {c.name: tribunal.proxies.get(c.id, 0) for c in saga.covenants}
    # Murion, Caecilius and Philippus Niger two each, eight masters one;
    # Fengheld's exarch also holds Triamore's two Tremere sigils, and
    # Roznov's Hygwald Veritas's.
    assert held["Durenmar"] == 12
    assert held["Fengheld"] == 12
    assert held["Roznov"] == 4
    assert held["Waddenzee"] == 0


def test_a_magus_s_rank_decides_the_sigils_they_hold():
    from ars_magica_manager.book_packs.rhine import tribunal

    assert tribunal.sigils_by_rank("Archmage of House Flambeau, ...") == 2
    assert tribunal.sigils_by_rank("Archmaga of House Merinita") == 2
    assert tribunal.sigils_by_rank("Master of House Bjornaer") == 1
    assert tribunal.sigils_by_rank("Journeyman of House Tremere") == 0
    assert tribunal.sigils_by_rank("Maga of House Bjornaer (rank not given)") == 0


def test_the_characters_the_book_prints_stat_blocks_for_are_full():
    saga = RHINE.build()
    by_name = {c.name: c for c in saga.characters}
    philippus = by_name["Philippus Niger"]
    assert philippus.detail == "Full"
    assert philippus.characteristics.intelligence == 5
    assert philippus.arts["perdo"].level > 0 and philippus.spells_known
    # The Minor printing of a Flaw the catalog has at both tiers.
    assert "vf_ambitious" in {v.vf_id for v in philippus.virtues_flaws}
    for name in ("Imanitos Mendax", "Falke", "Ioannes Acer", "Hilda", "Torven"):
        assert by_name[name].detail == "Full" and by_name[name].abilities
    assert packs.INFERRED not in by_name["Philippus Niger"].description.biography


def test_a_stat_block_names_only_catalog_virtues():
    import pytest

    with pytest.raises(KeyError):
        builder._virtue_flaw("No Such Virtue")


# -- The Lion and the Lily --


def test_the_normandy_pack_holds_the_tribunal_of_1220():
    saga = NORMANDY.build()
    (tribunal,) = saga.tribunals
    assert tribunal.package == "normandy"
    by_name = {c.name: c for c in saga.covenants}
    assert len(by_name) == 15
    # The Praeco's seat is vacant, and its succession heads the docket.
    assert tribunal.praeco_id is None
    assert tribunal.cases[0].title == "The Praeco's succession"
    quaesitor = saga.character(tribunal.quaesitor_id)
    assert quaesitor is not None and quaesitor.name.startswith("Proctor")
    # The lines of fealty, each sworn with the oath's Boons and Hooks.
    liege = {c.name: by_name_id for c in saga.covenants if (by_name_id := c.liege_id)}
    assert liege["Exspectatio"] == by_name["Fudarus"].id
    assert liege["Dragon's Rest"] == by_name["Confluensis"].id
    assert liege["Requies Aeterna"] == by_name["Florum"].id
    assert "covbh_hook_major_beholden" in {b.vf_id for b in by_name["Nidi"].boons_hooks}
    # The fallen covenants are ruins; Branugurix keeps its regio.
    ruins = {n.name: n for n in saga.neighbours if n.details.get("ruined")}
    assert len(ruins) >= 15
    assert any(n.details.get("levels") for n in ruins.values())
    # The stories, every one offered to begin on import.
    threats = {n.name for n in saga.neighbours if n.kind == "threat"}
    assert "The Boar King's Hunt" in threats and "A Romantic Saga" in threats
    assert normandy_package.tenures(tribunal)


def test_the_normandy_pack_keeps_its_secrets_and_credit():
    data = book_packs.data(NORMANDY)
    texts = _texts(data["saga"])
    assert len([t for t in texts if builder.SECRETS + "\n" in t]) >= 10
    assert data["book"] == "L&L" and "Creative Commons" in data["source"]


def test_the_shipped_normandy_pack_is_up_to_date():
    shipped = json.loads(book_packs.path_of(NORMANDY).read_text(encoding="utf-8"))
    built = book_packs.data(NORMANDY)
    assert packs.summary(shipped) == packs.summary(built)
    for kind in ("covenants", "characters", "neighbours", "books", "tribunals"):
        assert {(r["name"], r.get("detail")) for r in shipped["saga"][kind]} == {
            (r["name"], r.get("detail")) for r in built["saga"][kind]
        }, kind


def test_the_normandy_pack_imports_clean_into_a_new_saga():
    data = book_packs.data(NORMANDY)
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    transfer.apply(target, transfer.plan_import(target, data))
    assert packs.after_import(target, data) == [
        "The Lion and the Lily: The Normandy Tribunal is now in play.",
        packs.assumptions_note("The Lion and the Lily: The Normandy Tribunal"),
    ]
    assert target.books_in_play is not None and "L&L" in target.books_in_play
    assert len(target.characters) == len(data["saga"]["characters"])
    ids = {n.id for n in target.neighbours}
    for record in [*target.covenants, *target.neighbours]:
        assert record.place_id is None or record.place_id in ids
    covenants = {c.id for c in target.covenants}
    assert all(c.liege_id in covenants for c in target.covenants if c.liege_id)
    # Its wandering magus, printed in full, comes too.
    anacron = next(c for c in target.characters if c.name.startswith("Anacr"))
    assert anacron.detail == "Full"


# -- Faith & Flame --

PROVENCE = book_packs.PACKS["provence"]


def test_the_provence_pack_holds_the_tribunal_of_1220():
    saga = PROVENCE.build()
    (tribunal,) = saga.tribunals
    assert tribunal.package == "provence"
    assert (tribunal.next_year, tribunal.meets_every) == (1221, 7)
    names = {c.name for c in saga.covenants}
    assert names >= {
        "Tolosa Paratge",
        "Ostal des Exiles",
        "Castra Solis",
        "Tres' Band",
        "Aedes Mercurii",
        "Bellaquin",
        "Miniata Sophia",
        "Stella Durus",
        "Ara Maxima Nova",
        "The Coenobium Rhodanien",
        "Fraxinetum Redux",
    }
    # Dama is Praeco, printed in full; the Presiding Quaesitor's seat is empty.
    praeco = saga.character(tribunal.praeco_id or "")
    assert praeco is not None and praeco.name.startswith("Dama")
    assert praeco.detail == "Full" and praeco.spells_known
    assert tribunal.quaesitor_id is None
    assert len(tribunal.rulings) >= 10 and len(tribunal.cases) >= 8
    years = [e.year for e in tribunal.diary]
    assert years == sorted(years) and years[-1] <= 1220 and len(years) >= 50
    # Val-Negra is a ruin with its regio, and its demon sleeps.
    ruins = {n.name: n for n in saga.neighbours if n.details.get("ruined")}
    assert len(ruins) >= 25
    assert ruins["Val-Negra"].details.get("levels")
    threats = {n.name: n for n in saga.neighbours if n.kind == "threat"}
    assert "The Albigensian Crusade" in threats
    assert threats["The Adulteration of Flambeau"].details.get("dormant")
    # No record is made twice by two regions.
    keys = [(n.name, n.kind) for n in saga.neighbours]
    assert len(keys) == len(set(keys))


def test_the_provence_pack_keeps_its_secrets_and_credit():
    data = book_packs.data(PROVENCE)
    texts = _texts(data["saga"])
    assert len([t for t in texts if builder.SECRETS + "\n" in t]) >= 10
    assert data["book"] == "F&F" and "Creative Commons" in data["source"]


def test_the_shipped_provence_pack_is_up_to_date():
    shipped = json.loads(book_packs.path_of(PROVENCE).read_text(encoding="utf-8"))
    built = book_packs.data(PROVENCE)
    assert packs.summary(shipped) == packs.summary(built)
    for kind in ("covenants", "characters", "neighbours", "books", "tribunals"):
        assert {(r["name"], r.get("detail")) for r in shipped["saga"][kind]} == {
            (r["name"], r.get("detail")) for r in built["saga"][kind]
        }, kind


def test_the_provence_pack_imports_clean_into_a_new_saga():
    data = book_packs.data(PROVENCE)
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    transfer.apply(target, transfer.plan_import(target, data))
    assert packs.after_import(target, data) == [
        "Faith & Flame: The Provençal Tribunal is now in play.",
        packs.assumptions_note("Faith & Flame: The Provençal Tribunal"),
    ]
    assert target.books_in_play is not None and "F&F" in target.books_in_play
    assert len(target.characters) == len(data["saga"]["characters"])
    ids = {n.id for n in target.neighbours}
    for record in [*target.covenants, *target.neighbours]:
        assert record.place_id is None or record.place_id in ids


# -- The Sundered Eagle --

THEBAN = book_packs.PACKS["theban"]


def test_the_theban_pack_holds_the_tribunal_of_1220():
    from ars_magica_manager.tribunal_packages import theban as theban_package

    saga = THEBAN.build()
    (tribunal,) = saga.tribunals
    assert tribunal.package == "theban"
    assert (tribunal.next_year, tribunal.meets_every) == (1221, 7)
    assert tribunal.meeting_place == "Delos"
    assert len(saga.covenants) == 13
    # Each covenant is in its phyle, four phylai in all.
    phylai = theban_package.phylai(tribunal)
    assert {phylai[c.id] for c in saga.covenants} == set(theban_package.PHYLAI)
    assert phylai[next(c.id for c in saga.covenants if c.name == "Hedyosmos")] == (
        "Ionian"
    )
    # The archon is the Praeco; there is no Presiding Quaesitor.
    praeco = saga.character(tribunal.praeco_id or "")
    assert praeco is not None and praeco.name.startswith("Aiakia")
    assert tribunal.quaesitor_id is None
    offices = {o["office"] for o in theban_package.archai(tribunal)}
    assert {"Archon", "Polemarch", "Logothete"} <= offices
    # Tokens as the book implies them, and the incomers are metoikoi.
    entries = {
        saga.character(e["character_id"]).name.split(" ")[0]: e
        for e in theban_package.magi(tribunal)
    }
    assert entries["Caterina"].get("status") == "metoikos"
    assert entries["Ioannes"]["tokens"] > 0
    assert len(tribunal.rulings) >= 20 and len(tribunal.cases) >= 9
    years = [e.year for e in tribunal.diary]
    assert years == sorted(years) and years[-1] <= 1220 and len(years) >= 60
    ruins = [n for n in saga.neighbours if n.details.get("ruined")]
    assert len(ruins) == 12
    threats = {n.name: n for n in saga.neighbours if n.kind == "threat"}
    assert "An Enemy Within" in threats
    assert not threats["An Enemy Within"].details.get("dormant")
    assert len(saga.creatures) >= 14
    keys = [(n.name, n.kind) for n in saga.neighbours]
    assert len(keys) == len(set(keys))


def test_theban_magi_learn_the_art_in_greek_and_incomers_in_latin():
    saga = THEBAN.build()

    def languages(name: str) -> set[str]:
        magus = next(c for c in saga.characters if c.name.startswith(name))
        return {a.name for a in magus.abilities if a.name.startswith("Dead Language")}

    assert "Dead Language: Classical Greek" in languages("Aiakia")
    assert "Dead Language: Latin" in languages("Wilrich")


def test_the_theban_pack_keeps_its_secrets_and_credit():
    data = book_packs.data(THEBAN)
    texts = _texts(data["saga"])
    assert len([t for t in texts if builder.SECRETS + "\n" in t]) >= 10
    assert data["book"] == "TSE" and "Creative Commons" in data["source"]


def test_the_shipped_theban_pack_is_up_to_date():
    shipped = json.loads(book_packs.path_of(THEBAN).read_text(encoding="utf-8"))
    built = book_packs.data(THEBAN)
    assert packs.summary(shipped) == packs.summary(built)
    for kind in ("covenants", "characters", "neighbours", "books", "tribunals"):
        assert {(r["name"], r.get("detail")) for r in shipped["saga"][kind]} == {
            (r["name"], r.get("detail")) for r in built["saga"][kind]
        }, kind


def test_the_theban_pack_imports_clean_into_a_new_saga():
    data = book_packs.data(THEBAN)
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    transfer.apply(target, transfer.plan_import(target, data))
    assert packs.after_import(target, data) == [
        "The Sundered Eagle: The Theban Tribunal is now in play.",
        packs.assumptions_note("The Sundered Eagle: The Theban Tribunal"),
    ]
    assert target.books_in_play is not None and "TSE" in target.books_in_play
    assert len(target.characters) == len(data["saga"]["characters"])
    ids = {n.id for n in target.neighbours}
    for record in [*target.covenants, *target.neighbours]:
        assert record.place_id is None or record.place_id in ids


# -- Against the Dark --

TRANSYLVANIA = book_packs.PACKS["transylvania"]


def test_the_transylvania_pack_holds_the_tribunal_of_1220():
    from ars_magica_manager.tribunal_packages import transylvania as package

    saga = TRANSYLVANIA.build()
    (tribunal,) = saga.tribunals
    assert tribunal.package == "transylvania"
    assert (tribunal.next_year, tribunal.meets_every) == (1221, 7)
    assert tribunal.meeting_place == "the Shipka Pass"
    # The oppida are the covenants; the five legal covenants are not.
    names = {c.name for c in saga.covenants}
    assert len(names) == 12 and {"Coeris", "Tablinum", "Kezdö Válasz"} <= names
    assert not {"Domostron", "Asclepius", "Diodorus", "Pannonia"} & names
    praeco = saga.character(tribunal.praeco_id or "")
    quaesitor = saga.character(tribunal.quaesitor_id or "")
    assert praeco is not None and praeco.name.startswith("Albertus")
    assert quaesitor is not None and quaesitor.name.startswith("Benilda")
    # Every named magus holds a privilege, mostly as the book gives it.
    members = package.members(saga, tribunal)
    assert len(members) == 42
    entries = {saga.character(e["character_id"]).name.split(" ")[0]: e for e in members}
    assert entries["Neculai"]["privilege"] == "socii"
    assert entries["Oeagrus"]["privilege"] == "foederati"
    coeris = next(c for c in saga.covenants if c.name == "Coeris")
    assert package.aediles_text(saga, tribunal, coeris).startswith("Dominic")
    assert len(tribunal.rulings) >= 25 and len(tribunal.cases) == 7
    years = [e.year for e in tribunal.diary]
    assert years == sorted(years) and years[-1] <= 1220 and len(years) >= 40
    tablinum = next(c for c in saga.covenants if c.name == "Tablinum")
    site = saga.neighbour(tablinum.place_id or "")
    assert site is not None and len(site.details["levels"]) >= 10
    threats = {n.name: n for n in saga.neighbours if n.kind == "threat"}
    assert not threats["The Dragon War"].details.get("dormant")
    assert len(saga.creatures) >= 17
    keys = [(n.name, n.kind) for n in saga.neighbours]
    assert len(keys) == len(set(keys))


def test_monica_ierne_is_entered_as_the_book_prints_her():
    data = book_packs.data(TRANSYLVANIA)
    sketches = data[packs.GENERATED]
    monica = next(
        c for c in data["saga"]["characters"] if c["name"].startswith("Monica")
    )
    assert monica["id"] not in sketches
    assert len(sketches) >= 40


def test_the_transylvania_pack_keeps_its_secrets_and_credit():
    data = book_packs.data(TRANSYLVANIA)
    texts = _texts(data["saga"])
    assert len([t for t in texts if builder.SECRETS + "\n" in t]) >= 10
    assert data["book"] == "AtD" and "Creative Commons" in data["source"]


def test_the_shipped_transylvania_pack_is_up_to_date():
    shipped = json.loads(book_packs.path_of(TRANSYLVANIA).read_text(encoding="utf-8"))
    built = book_packs.data(TRANSYLVANIA)
    assert packs.summary(shipped) == packs.summary(built)
    for kind in ("covenants", "characters", "neighbours", "books", "tribunals"):
        assert {(r["name"], r.get("detail")) for r in shipped["saga"][kind]} == {
            (r["name"], r.get("detail")) for r in built["saga"][kind]
        }, kind


def test_the_transylvania_pack_imports_clean_into_a_new_saga():
    from ars_magica_manager.tribunal_packages import transylvania as package

    data = book_packs.data(TRANSYLVANIA)
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    transfer.apply(target, transfer.plan_import(target, data))
    assert packs.after_import(target, data) == [
        "Against the Dark: The Transylvanian Tribunal is now in play.",
        packs.assumptions_note("Against the Dark: The Transylvanian Tribunal"),
    ]
    assert target.books_in_play is not None and "AtD" in target.books_in_play
    assert len(target.characters) == len(data["saga"]["characters"])
    ids = {n.id for n in target.neighbours}
    for record in [*target.covenants, *target.neighbours]:
        assert record.place_id is None or record.place_id in ids
    # The privileges and aediles come with the Tribunal, pointing at the
    # imported magi.
    (tribunal,) = target.tribunals
    people = {c.id for c in target.characters}
    assert all(e["character_id"] in people for e in package.members(target, tribunal))
    assert all(
        i in people for found in package.aediles(tribunal).values() for i in found
    )


# -- The Contested Isle --

HIBERNIA = book_packs.PACKS["hibernia"]


def test_the_hibernia_pack_holds_the_tribunal_of_1220():
    from ars_magica_manager.tribunal_packages import hibernia as package

    saga = HIBERNIA.build()
    (tribunal,) = saga.tribunals
    assert tribunal.package == "hibernia"
    assert (tribunal.next_year, tribunal.meets_every) == (1221, 7)
    assert tribunal.meeting_place == "the Hill of Tara"
    # Nine covenants at law, and the two Mercer Houses beside them.
    names = {c.name for c in saga.covenants}
    assert len(names) == 11 and {"Circulus Ruber", "Praesis", "Vigil"} <= names
    assert {"Leth Moga", "Leth Cuinn"} <= names
    assert tribunal.covenants_total == 9
    praeco = saga.character(tribunal.praeco_id or "")
    quaesitor = saga.character(tribunal.quaesitor_id or "")
    assert praeco is not None and praeco.name.startswith("Milvia")
    assert quaesitor is not None and quaesitor.name.startswith("Visioturpis")
    # Every covenant at law has its cathach; the Mercer Houses keep none.
    cathaigh = package.cathaigh(tribunal)
    houses = {c.id for c in saga.covenants if c.name.startswith("Leth ")}
    assert set(cathaigh) == {c.id for c in saga.covenants} - houses
    praesis = next(c for c in saga.covenants if c.name == "Praesis")
    assert "Gáe Bulg" in cathaigh[praesis.id]["cathach"]
    ambassadors = {a["name"] for a in package.ambassadors(tribunal)}
    assert len(ambassadors) == 5 and {"Fothaid", "Ainid", "Mug Ruith"} <= ambassadors
    assert all(a["confirmed"] for a in package.ambassadors(tribunal))
    treaties = {t["title"] for t in package.treaties(tribunal)}
    assert "The Treaty of Cnoc Maol Réidh" in treaties
    assert len(package.tuatha(tribunal)) == 4
    assert len(tribunal.rulings) >= 25 and len(tribunal.cases) >= 12
    years = [e.year for e in tribunal.diary]
    assert years == sorted(years) and years[-1] <= 1220 and len(years) >= 80
    threats = {n.name: n for n in saga.neighbours if n.kind == "threat"}
    active = [n for n in threats.values() if not n.details.get("dormant")]
    assert len(threats) >= 9 and len(active) == 3
    assert len(saga.creatures) >= 22
    keys = [(n.name, n.kind) for n in saga.neighbours]
    assert len(keys) == len(set(keys))


def test_indrechtach_is_entered_as_the_book_prints_him():
    data = book_packs.data(HIBERNIA)
    sketches = data[packs.GENERATED]
    indrechtach = next(
        c for c in data["saga"]["characters"] if c["name"].startswith("Indrechtach")
    )
    assert indrechtach["id"] not in sketches
    assert len(sketches) >= 45


def test_the_hibernia_pack_keeps_its_secrets_and_credit():
    data = book_packs.data(HIBERNIA)
    texts = _texts(data["saga"])
    assert len([t for t in texts if builder.SECRETS + "\n" in t]) >= 10
    assert data["book"] == "TCI" and "Creative Commons" in data["source"]


def test_the_shipped_hibernia_pack_is_up_to_date():
    shipped = json.loads(book_packs.path_of(HIBERNIA).read_text(encoding="utf-8"))
    built = book_packs.data(HIBERNIA)
    assert packs.summary(shipped) == packs.summary(built)
    for kind in ("covenants", "characters", "neighbours", "books", "tribunals"):
        assert {(r["name"], r.get("detail")) for r in shipped["saga"][kind]} == {
            (r["name"], r.get("detail")) for r in built["saga"][kind]
        }, kind


def test_the_hibernia_pack_imports_clean_into_a_new_saga():
    from ars_magica_manager.tribunal_packages import hibernia as package

    data = book_packs.data(HIBERNIA)
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    transfer.apply(target, transfer.plan_import(target, data))
    assert packs.after_import(target, data) == [
        "The Contested Isle: The Hibernian Tribunal is now in play.",
        packs.assumptions_note("The Contested Isle: The Hibernian Tribunal"),
    ]
    assert target.books_in_play is not None and "TCI" in target.books_in_play
    assert len(target.characters) == len(data["saga"]["characters"])
    ids = {n.id for n in target.neighbours}
    for record in [*target.covenants, *target.neighbours]:
        assert record.place_id is None or record.place_id in ids
    # The cathaigh come with the Tribunal, keyed by the imported covenants.
    (tribunal,) = target.tribunals
    covenants = {c.id for c in target.covenants}
    assert set(package.cathaigh(tribunal)) <= covenants
    assert len(package.cathaigh(tribunal)) == 9


def test_every_pack_names_a_help_page_of_its_assumptions():
    from ars_magica_manager import help_text

    for front_end in help_text.FRONT_ENDS:
        pages = help_text.load(front_end).pages
        for pack in book_packs.PACKS.values():
            topic = book_packs.assumptions_topic(pack)
            assert topic in pages, (front_end, topic)
            assert pages[topic].title.startswith("Assumptions made for ")
    for pack in book_packs.PACKS.values():
        shipped = json.loads(book_packs.path_of(pack).read_text(encoding="utf-8"))
        assert shipped[packs.ASSUMPTIONS] == book_packs.assumptions_topic(pack)
