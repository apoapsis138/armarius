"""The content packs built from the Tribunal sourcebooks: each builds,
is shipped up to date, imports clean into a new saga, and puts its book
in play."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from ars_magica_manager import book_packs, catalog, packs, sourcebooks, transfer
from ars_magica_manager.book_packs import builder, overlays
from ars_magica_manager.forms import creation as creation_forms
from ars_magica_manager.models import Character, Saga
from ars_magica_manager.models.common import split_secrets
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


#: The records that keep their secrets apart, and the texts that once
#: held them under a Secrets heading.
_SECRET_KEEPERS = {
    "covenants": ("notes", "summary"),
    "characters": ("summary",),
    "neighbours": ("summary",),
    "tribunals": ("summary", "history"),
    "creatures": ("notes",),
}


def _secrets_kept(saga: dict) -> int:
    """How many of the pack's records have secrets, checking that none is
    left under a heading in the text the players see."""
    kept = 0
    for kind, keys in _SECRET_KEEPERS.items():
        for record in saga[kind]:
            for key in keys:
                assert split_secrets(record.get(key) or "")[1] == "", (
                    record["name"],
                    key,
                )
            kept += bool(record.get("secrets"))
    return kept


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


def test_the_pack_keeps_its_secrets_apart():
    data = book_packs.data(RHINE)
    texts = _texts(data["saga"])
    assert not [t for t in texts if "SECRET" in t]
    assert _secrets_kept(data["saga"]) >= 10
    assert data["book"] == "GotF" and "Creative Commons" in data["source"]


def _content(data: dict[str, Any]) -> dict[str, Any]:
    """What a pack holds, read through the models so a field added since
    it was written reads as its default on both sides of a comparison."""
    saga = Saga.from_dict(data["saga"], lab_feature_names=catalog.lab_feature_names())
    sketches = {
        key: asdict(Character.from_dict(dict(sketch)))
        for key, sketch in (data.get(packs.GENERATED) or {}).items()
    }
    return packs.without_random_ids(
        {
            "name": data["name"],
            "book": data.get("book"),
            "links": data.get("links"),
            "saga": asdict(saga),
            "generated": sketches,
        }
    )


def _sections(data: dict[str, Any]) -> list[dict[str, Any]]:
    """An overlay's sections, each pack read as _content reads one."""
    return [
        packs.without_random_ids({**section, "pack": _content(section["pack"])})
        for section in data[packs.OVERLAY]
    ]


def test_every_shipped_pack_is_what_its_module_builds():
    """data/packs holds what book_packs builds, so a fix to a book's module
    can't sit unshipped: rebuild with tools/build_packs.py."""
    stale = [
        key
        for key, pack in book_packs.PACKS.items()
        if _content(transfer.read(book_packs.path_of(pack)))
        != _content(json.loads(json.dumps(book_packs.data(pack))))
    ]
    assert not stale, f"rebuild with tools/build_packs.py: {stale}"
    for overlay in overlays.OVERLAYS.values():
        shipped = _sections(transfer.read(overlays.path_of(overlay)))
        built = _sections(json.loads(json.dumps(overlays.data(overlay))))
        assert shipped == built, overlay.key


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


def test_through_the_aegis_covenants_are_in_their_tribunals():
    """Each developed covenant is a full record in its Tribunal's pack,
    with its magi's printed stats."""
    for key, name, magus in (
        ("provence", "Jardin", "Joia du Lua"),
        ("theban", "Didyma", "Nikola"),
        ("hibernia", "Longmist", "Conchobor Crosach"),
        ("rhine", "Collem Leonis", "Ferra of Bonisagus"),
    ):
        saga = book_packs.PACKS[key].assemble(("TtA",)).saga
        covenant = next(c for c in saga.covenants if c.name == name)
        character = next(c for c in saga.characters if c.name.startswith(magus))
        assert covenant.detail == "Full" and covenant.tribunal_id
        assert character.covenant_id == covenant.id
        assert character.detail == "Full" and character.abilities


def test_through_the_aegis_stays_out_of_the_tribunal_packs_until_it_is_on():
    """A Tribunal pack matches its own book; the overlay overwrites it."""
    alone = book_packs.PACKS["provence"].build()
    assert "Jardin" not in {c.name for c in alone.covenants}
    (tribunal,) = alone.tribunals
    falls = {e.title: e.year for e in tribunal.diary}
    assert falls["Bellaquin falls"] == 1200
    assert falls["Montgey and the fall of Lariander"] == 1211
    (with_it,) = book_packs.PACKS["provence"].assemble(("TtA",)).saga.tribunals
    falls = {e.title: e.year for e in with_it.diary}
    assert falls["Bellaquin falls"] == 1202
    assert falls["Montgey and the fall of Lariander"] == 1209


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


def test_the_rhine_peregrinatores_have_the_book_s_blocks():
    saga = RHINE.build()
    by_name = {c.name: c for c in saga.characters}
    tabanus, felicia = by_name["Tabanus"], by_name["Felicia"]
    assert saga.current_year - tabanus.background.year_born == 38
    assert saga.current_year - felicia.background.year_born == 24
    for magus in (tabanus, felicia):
        assert magus.detail == "Full" and magus.spells_known
        assert packs.INFERRED not in magus.description.biography
    assert tabanus.characteristics.perception == 3
    # The printed In 10+3 is the score plus Puissant Intellego.
    assert tabanus.arts["intellego"].level == 10


def test_the_rhine_pack_corrects_the_slips_its_review_found():
    saga = RHINE.build()
    by_name = {c.name: c for c in saga.characters}
    assert "leader of the Oak Gild" not in by_name["Stentorius"].summary
    roznov = next(c for c in saga.covenants if c.name == "Roznov")
    assert roznov.unnamed_magi == 5 and "Seven magi" in roznov.summary


def test_a_stat_block_names_only_catalog_virtues():
    import pytest

    with pytest.raises(KeyError):
        builder._virtue_flaw("No Such Virtue")


def _a_builder() -> tuple[builder.Builder, object]:
    b = builder.Builder("Test", source="B&S")
    tribunal = b.tribunal(
        "The Levant Tribunal",
        package="levant",
        summary="",
        meets_every=7,
        next_year=1221,
        next_season="Summer",
        meeting_place="Domus Pacis",
    )
    return b, tribunal


def test_a_covenant_takes_the_aegis_the_book_gives():
    b, tribunal = _a_builder()
    warded = b.covenant("Warded", tribunal=tribunal, founded=1200, summary="", aegis=35)
    plain = b.covenant("Plain", tribunal=tribunal, founded=1200, summary="")
    assert warded.aegis_of_the_hearth == 35
    assert plain.aegis_of_the_hearth == 0


def test_a_stat_block_from_another_book_cites_that_book():
    from ars_magica_manager.models import Character

    b, _ = _a_builder()
    block = {"spells": [("A Spell No Book Prints", "CrIg", 10, 0)]}
    elsewhere = b.stats(Character(id="a", name="A", type="magus"), block, source="SiS")
    (spell,) = elsewhere.invented_spells
    assert spell.source == "SiS" and "Secrets in Sand" in spell.description
    own = b.stats(Character(id="b", name="B", type="magus"), block)
    (spell,) = own.invented_spells
    assert spell.source == "B&S" and "Blood and Sand" in spell.description


def test_a_creature_from_another_book_cites_that_book():
    b, _ = _a_builder()
    assert b.creature("Jinni", page="p. 3", source="SiS").source == (
        "Secrets in Sand p. 3"
    )
    assert b.creature("Ghul", page="p. 9").source.startswith("Blood and Sand")


def test_a_creature_prices_an_art_table_ability_as_stats_does():
    from ars_magica_manager.rules.xp import ability_xp, art_xp

    b, _ = _a_builder()
    block = {"abilities": [("Sihr", 10, ""), ("Awareness", 3, "")]}
    sihr, awareness = b.creature("Jinni", page="p. 1", block=block).abilities
    assert (sihr.xp, sihr.xp_table) == (art_xp(10), "art") == (55, "art")
    assert awareness.xp == ability_xp(3)


def test_a_sketch_belongs_to_the_traditions_it_is_given():
    b, _ = _a_builder()
    sahir = b.magus(
        "Niya",
        covenant=None,
        house="",
        age=50,
        summary="",
        type="companion",
        traditions=["trad_sahirs"],
    )
    assert sahir.type == "companion" and sahir.traditions == ["trad_sahirs"]
    assert (
        b.magus("Plain", covenant=None, house="", age=None, summary="").traditions == []
    )
    # A stat block that names no traditions keeps the sketch's.
    b.stats(sahir, {"abilities": [("Sihr", 6, "")]})
    assert sahir.traditions == ["trad_sahirs"]


def test_a_stat_block_carries_tradition_effects_and_bound_beings():
    from ars_magica_manager.models import Character

    b, _ = _a_builder()
    jinni = b.creature("Kharrat", page="p. 2")
    block = {
        "traditions": ["trad_sahirs"],
        "effects": [
            b.effect("Call Kharrat", rule="Summoning", uses=["Sihr"], level=15),
            b.effect("A Naranj", rule="Naranj", level=20, tradition="trad_mobeds"),
        ],
        "bound_beings": [
            b.bound_being("Kharrat", kind="Bargained jinni", creature=jinni)
        ],
    }
    sahir = b.stats(Character(id="a", name="'Arkhaman", type="companion"), block)
    call, naranj = sahir.tradition_effects
    assert (call.tradition, call.rule, call.uses, call.level) == (
        "trad_sahirs",
        "Summoning",
        ["Sihr"],
        15,
    )
    assert naranj.tradition == "trad_mobeds"
    (bound,) = sahir.bound_beings
    assert (bound.tradition, bound.kind, bound.creature_id) == (
        "trad_sahirs",
        "Bargained jinni",
        jinni.id,
    )


def _a_region_pack() -> builder.Builder:
    """A pack with no Tribunal: a covenant outside every Tribunal, its
    history in that covenant's Diary, a yearly council in the calendar,
    and a place known in the region."""
    b = builder.Builder("Region", source="TC&TC", known="In the region")
    city = b.place("Baghdad", summary="A city.", realm="Divine", aura=4)
    house = b.covenant("Dar al-Hikma", founded=805, summary="An academy.", place=city)
    b.chronicle(house, 805, "The Order is founded", "Its first council.")
    b.calendar("The Majlis", 1220, "Summer", repeats="Each year", note="In Baghdad.")
    return b


def test_a_region_pack_builds_with_no_tribunal():
    import pytest

    b = _a_region_pack()
    (house,) = b.saga.covenants
    assert house.tribunal_id is None and b.saga.tribunals == []
    (entry,) = house.diary
    assert (entry.year, entry.season, entry.name) == (
        805,
        "Spring",
        "The Order is founded",
    )
    (council,) = b.saga.calendar
    assert (council.title, council.season, council.repeats, council.covenant_id) == (
        "The Majlis",
        "Summer",
        "Each year",
        None,
    )
    (city,) = b.saga.neighbours
    assert city.details["known"] == "In the region"
    assert b.place("Elsewhere", summary="", known="Locally").details["known"] == (
        "Locally"
    )
    # A Tribunal's book keeps its default.
    rhine, _ = _a_builder()
    assert rhine.place("A wood", summary="").details["known"] == "In the Tribunal"
    with pytest.raises(ValueError):
        b.chronicle(house, 806, "No season", season="")
    with pytest.raises(ValueError):
        b.calendar("Never", 1221, repeats="Sometimes")


def test_a_region_pack_imports_clean_and_is_listed_by_name():
    pack = book_packs.BookPack(
        key="region", book="TC&TC", name="A Region", assemble=_a_region_pack, source=""
    )
    data = book_packs.data(pack)
    assert data["saga"]["tribunals"] == []
    assert packs.choice_label(data, "fallback") == (
        "A Region: 1 covenant, 1 place or neighbour, 1 calendar entry"
    )
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    transfer.apply(target, transfer.plan_import(target, data))
    (house,) = target.covenants
    assert house.tribunal_id is None and target.tribunals == []
    assert [e.name for e in house.diary] == ["The Order is founded"]
    assert [e.title for e in target.calendar] == ["The Majlis"]
    assert house.place_id == target.neighbours[0].id
    notes = packs.after_import(target, data)
    assert "The Cradle and the Crescent is now in play." in notes[0]
    assert target.books_in_play is not None and "TC&TC" in target.books_in_play
    # Leaving the history out leaves out the covenant's Diary too.
    fields = {f.key for f in packs.import_fields(data)}
    assert "history" in fields
    bare = packs.narrow(data, {key: False for key in fields})
    assert [c["diary"] for c in bare["saga"]["covenants"]] == [[]]
    assert bare["saga"]["calendar"] == []


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
    assert _secrets_kept(data["saga"]) >= 10
    assert data["book"] == "L&L" and "Creative Commons" in data["source"]


def test_the_northern_seas_sail_with_the_normandy_pack():
    """Through the Aegis's flotilla: a covenant with no site of its own, the
    Hook that says it moves, six ships, and stat blocks as printed."""
    saga = NORMANDY.assemble(("TtA",)).saga
    fleet = next(c for c in saga.covenants if c.name == "The Northern Seas")
    assert fleet.place_id is None and fleet.aura == 0
    assert "covbh_hook_minor_erratically_mobile" in {
        held.vf_id for held in builder.boons_hooks_from(fleet.what_matters)
    }
    assert len([p for p in fleet.possessions if p.kind == "ship"]) == 6
    carles = next(c for c in saga.characters if c.name == "Carles Magnus")
    assert carles.covenant_id == fleet.id and carles.detail == "Full"
    assert (carles.characteristics.presence, carles.characteristics.strength) == (2, 0)
    assert any(f.character_id == carles.id for f in saga.familiars)


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
    assert _secrets_kept(data["saga"]) >= 10
    assert data["book"] == "F&F" and "Creative Commons" in data["source"]


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
    for tremere in ("Boustaphan", "Monorchis", "Allectores"):
        assert "Dead Language: Latin" in languages(tremere), tremere
    # Artoud's old Tribunal goes by the Levant pack's name for it.
    artoud = next(c for c in saga.characters if c.name == "Artoud")
    assert "Area Lore: Levant Tribunal" in {a.name for a in artoud.abilities}
    assert "the Levant Tribunal" in artoud.summary


def test_the_theban_pack_keeps_its_secrets_and_credit():
    data = book_packs.data(THEBAN)
    assert _secrets_kept(data["saga"]) >= 10
    assert data["book"] == "TSE" and "Creative Commons" in data["source"]


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


def test_the_hedge_factions_name_their_traditions():
    from ars_magica_manager import traditions
    from ars_magica_manager.rules import hedge_casting as hc

    saga = TRANSYLVANIA.build()
    factions = {n.name: n for n in saga.neighbours if n.kind == "faction"}
    assert factions["The Storm Wizards"].details["tradition"] == "trad_storm_wizards"
    assert factions["The Taltós"].details["tradition"] == "trad_nightwalkers"
    assert "tradition" not in factions["The Wolf Brotherhoods"].details
    for faction in factions.values():
        named = faction.details.get("tradition")
        assert named is None or traditions.find(named) is not None, faction.name
    tibor = next(c for c in saga.characters if c.name == "Tibor of Borša")
    assert tibor.traditions == ["trad_hunters"]
    assert hc.score(tibor, "Slay") == 5
    thietmar = next(c for c in saga.characters if c.name == "Thietmar")
    assert thietmar.traditions == ["trad_storm_wizards"]
    assert hc.score(thietmar, "Storm Calling") >= 5


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
    assert _secrets_kept(data["saga"]) >= 10
    assert data["book"] == "AtD" and "Creative Commons" in data["source"]


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
    assert _secrets_kept(data["saga"]) >= 10
    assert data["book"] == "TCI" and "Creative Commons" in data["source"]


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


# -- Blood and Sand --

LEVANT = book_packs.PACKS["levant"]


def test_the_levant_pack_holds_the_tribunal_of_1220():
    from ars_magica_manager.tribunal_packages import levant as package

    saga = LEVANT.build()
    (tribunal,) = saga.tribunals
    assert tribunal.name == "The Levant Tribunal"
    assert tribunal.package == package.LEVANT.key
    assert (tribunal.next_year, tribunal.meets_every) == (1221, 7)
    assert tribunal.meeting_place == "Domus Pacis"
    assert (tribunal.covenants_total, tribunal.magi_total) == (15, 59)
    quaesitor = saga.character(tribunal.quaesitor_id or "")
    assert quaesitor is not None and quaesitor.name == "Scipio"
    titles = {r.title for r in tribunal.rulings}
    assert {"The Treaty of Baghdad", "The Treaty's term", "The chair"} <= titles
    # The renewal is a motion whose parties lean their own way.
    (renewal,) = [c for c in tribunal.cases if c.kind == "motion"]
    assert "1228" in renewal.charge and renewal.term_ends_year is None
    for name in ("The Hermetic Embassy", "Domus Pacis", "Aedes Veritatis"):
        assert name in renewal.brought_by
    for name in ("Foothold", "Para Belli", "The True Cross"):
        assert name in renewal.against
    keys = [(n.name, n.kind) for n in saga.neighbours]
    assert len(keys) == len(set(keys))


def test_the_levant_and_theban_packs_build_their_shared_lords_alike():
    def lords(pack: book_packs.BookPack) -> dict[str, tuple[str, str, dict]]:
        return {
            n.name: (n.summary, n.ruler, n.details)
            for n in pack.build().neighbours
            if n.name in ("Sultan of Rum", "Emperor of Trebizond")
        }

    theban = lords(THEBAN)
    assert len(theban) == 2 and lords(LEVANT) == theban


def test_the_levant_pack_holds_the_shared_middle_east():
    from ars_magica_manager.book_packs import east

    saga = LEVANT.build()
    shared = east.middle_east(builder.Builder("Probe", source="TC&TC"))
    names = {n.name for n in saga.neighbours} | {c.name for c in saga.creatures}
    assert {r.name for r in shared.values()} <= names
    order = next(n for n in saga.neighbours if n.name == "The Order of Suleiman")
    assert order.details["tradition"] == "trad_sahirs"
    families = [n for n in saga.neighbours if n.answers_to == order.id]
    assert len(families) == 2


def test_the_levant_pack_converts_its_printed_magi():
    data = book_packs.data(LEVANT)
    sketches = data[packs.GENERATED]
    printed = [
        c for c in data["saga"]["characters"] if c["id"] not in sketches and c["arts"]
    ]
    assert len(printed) == 7 and len(sketches) == 30
    saga = LEVANT.build()
    umar = next(c for c in saga.characters if c.name == "Sharaf al-Din 'Umar")
    assert umar.hermetic.house == "house_jerbiton"
    # Twilight Points become Warping, a third of them.
    assert umar.aging.warping_score == 4
    # The printed age stands, and Confidence is the DE baseline, +1 for a
    # Tytalus apprenticeship.
    assert saga.current_year - (umar.background.year_born or 0) == 72
    assert (umar.background.confidence_score, umar.background.confidence_points) == (
        1,
        3,
    )
    rufus = next(c for c in saga.characters if c.name == "Rufus de Clary")
    assert rufus.background.confidence_score == 2
    # A spell the catalog lacks stays his own, at its printed level.
    own = {s.name: s.level for s in umar.invented_spells}
    assert own["The Wrath of Allah"] and own["Breaking the Perpetual Drought"] == 30
    assert len(umar.spells_known) == 39


def test_wardat_is_a_hermetic_sahir():
    from ars_magica_manager.rules import hedge_casting as hc

    saga = LEVANT.build()
    wardat = next(c for c in saga.characters if c.name == "Wardat al-Quds")
    assert wardat.hermetic.house == "house_ex_miscellanea"
    assert wardat.traditions == ["trad_hermetic_sahirs"]
    assert hc.score(wardat, "Sihr") == 6 and not wardat.arts
    held = {v.vf_id for v in wardat.virtues_flaws}
    assert {"vf_sihr", "vf_minor_magical_focus", "vf_twilight_prone"} <= held
    creatures = {c.id for c in saga.creatures}
    assert {b.name for b in wardat.bound_beings} == {"Al-Manqa'i", "Sharif"}
    assert all(b.creature_id in creatures for b in wardat.bound_beings)


def test_the_levant_pack_keeps_its_secrets_and_credit():
    data = book_packs.data(LEVANT)
    assert _secrets_kept(data["saga"]) >= 10
    assert data["book"] == "B&S" and "Creative Commons" in data["source"]
    assert "Secrets in Sand" in data["source"]


def test_the_levant_pack_imports_clean_into_a_new_saga():
    data = book_packs.data(LEVANT)
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    transfer.apply(target, transfer.plan_import(target, data))
    assert packs.after_import(target, data) == [
        "Blood and Sand: The Levant Tribunal is now in play.",
        packs.assumptions_note("Blood and Sand: The Levant Tribunal"),
    ]
    assert target.books_in_play is not None and "B&S" in target.books_in_play
    assert len(target.characters) == len(data["saga"]["characters"])
    ids = {n.id for n in target.neighbours}
    for record in [*target.covenants, *target.neighbours]:
        assert record.place_id is None or record.place_id in ids
    # The Tribunal's officers and the motion's parties are the imported
    # records.
    (tribunal,) = target.tribunals
    people = {c.id for c in target.characters}
    assert {tribunal.praeco_id, tribunal.quaesitor_id} <= people
    covenants = {c.name for c in target.covenants}
    (renewal,) = [c for c in tribunal.cases if c.kind == "motion"]
    for name in covenants & {"The Hermetic Embassy", "Foothold", "Para Belli"}:
        assert name in renewal.brought_by or name in renewal.against
    assert {"The Hermetic Embassy", "Foothold", "Para Belli"} <= covenants


# -- The Cradle and the Crescent --

CRADLE = book_packs.PACKS["cradle"]


def test_the_cradle_pack_holds_its_region_with_no_tribunal():
    data = book_packs.data(CRADLE)
    held = data["saga"]
    assert held["tribunals"] == [] and data["book"] == "TC&TC"
    assert {c["tribunal_id"] for c in held["covenants"]} == {None}
    saga = CRADLE.build()
    houses = {c.name: c for c in saga.covenants}
    assert len(houses) == 13
    assert {
        "Dar al-Hikma",
        "The House of Wisdom of Savah",
        "The House of Healing",
        "Dayr Qunna",
        "The House of Wisdom of Damascus",
        "The House of Wisdom of Cairo",
    } <= set(houses)
    # No house of wisdom is left without an aura.
    assert all(c.aura > 0 for c in saga.covenants)
    assert (houses["Dayr Qunna"].aura, houses["Dayr Qunna"].aura_realm) == (
        3,
        "Magic",
    )
    assert (houses["The House of Wisdom of Savah"].aura_realm) == "Magic"
    # The Order's history is the Dar al-Hikma's Diary.
    assert len(houses["Dar al-Hikma"].diary) >= 20
    (majlis,) = [e for e in saga.calendar if e.title == "The Majlis al-Sulayman"]
    assert (majlis.season, majlis.repeats) == ("Summer", "Each year")
    keys = [(n.name, n.kind) for n in saga.neighbours]
    assert len(keys) == len(set(keys))
    order = next(n for n in saga.neighbours if n.name == "The Order of Suleiman")
    families = [n for n in saga.neighbours if n.answers_to == order.id]
    assert len(families) == 6
    names = {n.name for n in saga.neighbours}
    assert {"Iraq", "Baghdad", "The Mazdeans", "The Mongol Conquest"} <= names


def test_the_cradle_pack_s_sahirs_are_companions_and_arkhaman_is_printed():
    from ars_magica_manager.rules import hedge_casting as hc

    data = book_packs.data(CRADLE)
    saga = CRADLE.build()
    sahirs = [c for c in saga.characters if "trad_sahirs" in c.traditions]
    assert len(sahirs) == 5 and {c.type for c in sahirs} == {"companion"}
    arkhaman = next(c for c in sahirs if c.name.startswith("'Arkhaman"))
    assert arkhaman.id not in data.get(packs.GENERATED, {})
    chars = arkhaman.characteristics
    assert (chars.intelligence, chars.presence, chars.strength) == (2, 2, -1)
    assert hc.score(arkhaman, "Sihr") == 10
    # The book's 10+2: Puissant adds its 2.
    assert hc.score(arkhaman, "Solomonic Travel") == 12
    held = {v.vf_id for v in arkhaman.virtues_flaws}
    assert {"vf_the_gift", "vf_sahir", "vf_vizier", "vf_sihr"} <= held
    effects = arkhaman.tradition_effects
    assert len(effects) == 7
    assert [e.rule for e in effects].count("Summoning") == 1
    assert {e.tradition for e in effects} == {"trad_sahirs"}
    (kharrat,) = arkhaman.bound_beings
    creature = next(c for c in saga.creatures if c.name.startswith("Kharrat"))
    assert (kharrat.name, kharrat.creature_id) == ("Kharrat", creature.id)


def test_the_cradle_pack_keeps_its_secrets_and_credit():
    data = book_packs.data(CRADLE)
    assert _secrets_kept(data["saga"]) >= 10
    assert data["book"] == "TC&TC" and "Creative Commons" in data["source"]
    assert "The Cradle and the Crescent" in data["source"]


def test_the_cradle_pack_imports_clean_into_a_new_saga():
    data = book_packs.data(CRADLE)
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    transfer.apply(target, transfer.plan_import(target, data))
    assert packs.after_import(target, data) == [
        "The Cradle and the Crescent is now in play.",
        packs.assumptions_note("The Cradle and the Crescent"),
    ]
    assert target.books_in_play is not None and "TC&TC" in target.books_in_play
    assert target.tribunals == []
    assert len(target.covenants) == len(data["saga"]["covenants"])
    assert len(target.characters) == len(data["saga"]["characters"])
    ids = {n.id for n in target.neighbours}
    for record in [*target.covenants, *target.neighbours]:
        assert record.place_id is None or record.place_id in ids
    dar = next(c for c in target.covenants if c.name == "Dar al-Hikma")
    assert dar.diary and target.calendar
    creatures = {c.id for c in target.creatures}
    arkhaman = next(c for c in target.characters if c.name.startswith("'Arkhaman"))
    assert all(b.creature_id in creatures for b in arkhaman.bound_beings)


def test_the_levant_and_cradle_packs_share_their_records_without_doubling():
    from collections import Counter

    from ars_magica_manager.book_packs import east

    shared = east.middle_east(builder.Builder("Probe", source="TC&TC"))
    names = {r.name for r in shared.values()}
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    for pack in (LEVANT, CRADLE):
        data = book_packs.data(pack)
        transfer.apply(target, transfer.plan_import(target, data))
    counts = Counter(
        [n.name for n in target.neighbours] + [c.name for c in target.creatures]
    )
    assert {name: counts[name] for name in names} == dict.fromkeys(names, 1)
    keys = [(n.name, n.kind) for n in target.neighbours]
    assert len(keys) == len(set(keys))
    covenants = [c.name for c in target.covenants]
    assert len(covenants) == len(set(covenants)) == 25
    # A record both packs hold stays where the first import put it: the
    # pit lies beneath the Levant pack's Babel.
    pit = next(n for n in target.neighbours if n.name == "The Pit of Harut and Marut")
    place = target.neighbour(pit.place_id or "")
    assert place is not None and place.name == "Babel"


def test_every_pack_names_a_help_page_of_its_assumptions():
    from ars_magica_manager import help_text

    shipped_packs = list(book_packs.PACKS.values())
    for front_end in help_text.FRONT_ENDS:
        pages = help_text.load(front_end).pages
        for pack in shipped_packs:
            topic = book_packs.assumptions_topic(pack)
            assert topic in pages, (front_end, topic)
            assert pages[topic].title.startswith("Assumptions made for ")
    for pack in shipped_packs:
        shipped = json.loads(book_packs.path_of(pack).read_text(encoding="utf-8"))
        assert shipped[packs.ASSUMPTIONS] == book_packs.assumptions_topic(pack)


def test_every_packs_hedge_factions_name_known_traditions():
    from ars_magica_manager import traditions

    named = {}
    for key, pack in book_packs.PACKS.items():
        for n in pack.build().neighbours:
            if n.kind == "faction" and n.details.get("tradition"):
                named[(key, n.name)] = n.details["tradition"]
    assert all(traditions.find(t) is not None for t in named.values()), named
    assert named[("hibernia", "The Céli Dé")] == "trad_celi_de"
    assert named[("provence", "The Sorginak Covens")] == "trad_sorginak"


# -- Sanctuary of Ice --

ALPS = book_packs.PACKS["alps"]


def test_the_alps_pack_holds_the_tribunal_of_1220():
    from ars_magica_manager.tribunal_packages import alps as package

    saga = ALPS.build()
    (tribunal,) = saga.tribunals
    assert tribunal.package == package.ALPS.key
    assert (tribunal.next_year, tribunal.next_season, tribunal.meets_every) == (
        1221,
        "Autumn",
        7,
    )
    assert tribunal.meeting_place == "The Covenant of the Icy North"
    assert tribunal.covenants_total == 7 and (tribunal.magi_total or 0) >= 100
    praeco = saga.character(tribunal.praeco_id or "")
    quaesitor = saga.character(tribunal.quaesitor_id or "")
    assert praeco is not None and praeco.name == "Constance"
    assert quaesitor is not None and quaesitor.name == "Athena Alpina"
    titles = {r.title: r.year for r in tribunal.rulings}
    assert titles["Andru's pardon"] == 1194 and titles["A sanctum a season"] == 1165
    # Every covenant but the blank seventh registers its chairs.
    chairs = package.chairs(tribunal)
    named = {c.name: chairs.get(c.id) for c in saga.covenants}
    assert named["The Cave of Twisting Shadows"] == 22 and named["Valnastium"] == 21
    keys = [(n.name, n.kind) for n in saga.neighbours]
    assert len(keys) == len(set(keys))


def test_the_alps_pack_converts_its_printed_magi_by_the_de_readings():
    saga = ALPS.build()
    by_name = {c.name: c for c in saga.characters}
    ragoneda, kentigern = by_name["Ragoneda"], by_name["Kentigern"]
    # Printed ages, Twilight / 3 as Warping, the DE Confidence (+1 Tytalus).
    assert saga.current_year - (ragoneda.background.year_born or 0) == 56
    assert ragoneda.aging.warping_score == 2 and kentigern.aging.warping_score == 3
    assert ragoneda.background.confidence_score == 2
    assert kentigern.background.confidence_score == 1
    held = {v.vf_id for v in ragoneda.virtues_flaws}
    assert {"vf_public_vis_source", "vf_deficient_form"} <= held
    deficient = [v for v in kentigern.virtues_flaws if v.vf_id == "vf_deficient_form"]
    assert sorted(v.params["form"] for v in deficient) == [
        "Aquam",
        "Auram",
        "Ignem",
        "Terram",
    ]
    # A magus's own spell is re-derived at the DE's level.
    basilisk = next(
        s for s in kentigern.invented_spells if s.name == "Call the Basilisk"
    )
    assert basilisk.level == 65 and basilisk.range == "Touch"
    # Andru's familiar is rebuilt by the DE's rules.
    andru = by_name["Andru"]
    (familiar,) = [f for f in saga.familiars if f.character_id == andru.id]
    assert (familiar.binding_lab_total, familiar.target_binding_level) == (59, 35)
    # The Larta are companions with no House.
    for name in ("Josephine", "François", "Chloe"):
        assert by_name[name].type == "companion" and not by_name[name].hermetic.house


def test_the_alps_pack_keeps_its_secrets_and_credit():
    data = book_packs.data(ALPS)
    assert _secrets_kept(data["saga"]) >= 4
    assert data["book"] == "SoI" and "Creative Commons" in data["source"]


def test_the_alps_pack_imports_clean_into_a_new_saga():
    from ars_magica_manager.tribunal_packages import alps as package

    data = book_packs.data(ALPS)
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    transfer.apply(target, transfer.plan_import(target, data))
    assert packs.after_import(target, data) == [
        "Sanctuary of Ice: The Greater Alps Tribunal is now in play.",
        packs.assumptions_note("Sanctuary of Ice: The Greater Alps Tribunal"),
    ]
    assert target.books_in_play is not None and "SoI" in target.books_in_play
    assert len(target.characters) == len(data["saga"]["characters"])
    ids = {n.id for n in target.neighbours}
    for record in [*target.covenants, *target.neighbours]:
        assert record.place_id is None or record.place_id in ids
    (tribunal,) = target.tribunals
    covenants = {c.id for c in target.covenants}
    assert set(package.chairs(tribunal)) <= covenants


# -- Heirs to Merlin --

STONEHENGE = book_packs.PACKS["stonehenge"]


def test_the_stonehenge_pack_holds_the_tribunal_of_1220():
    from ars_magica_manager.tribunal_packages import stonehenge as package

    saga = STONEHENGE.build()
    (tribunal,) = saga.tribunals
    assert tribunal.package == package.STONEHENGE.key
    assert (tribunal.next_year, tribunal.meeting_place) == (1222, "Blackthorn")
    assert (tribunal.covenants_total, tribunal.magi_total) == (9, 49)
    praeco = saga.character(tribunal.praeco_id or "")
    quaesitor = saga.character(tribunal.quaesitor_id or "")
    assert praeco is not None and praeco.name == "Talion"
    assert quaesitor is not None and quaesitor.name == "Iudicium"
    assert {r.year for r in tribunal.rulings if r.title == "Financial Matters"} == {
        1208
    }
    titles = {e.title for e in tribunal.diary}
    assert {"Immanola's Final Twilight", "The quorate meeting"} <= titles
    # Cad Gadu as Houses of Hermes: Societates has it.
    names = {c.name for c in saga.characters}
    assert "Ebroin" in names and "Immanola" not in names
    cad_gadu = next(c for c in saga.covenants if c.name == "Cad Gadu")
    assert (cad_gadu.aura, cad_gadu.covenant_season) == (8, "Winter")
    keys = [(n.name, n.kind) for n in saga.neighbours]
    assert len(keys) == len(set(keys))


def test_the_stonehenge_pack_generates_every_magus_and_shares_the_king():
    data = book_packs.data(STONEHENGE)
    sketches = data[packs.GENERATED]
    magi = [c for c in data["saga"]["characters"] if c["type"] == "magus"]
    assert len(magi) == 49 and len(sketches) == 49
    assert "Henry III of England" in {n["name"] for n in data["saga"]["neighbours"]}


def test_the_stonehenge_pack_imports_clean_into_a_new_saga():
    data = book_packs.data(STONEHENGE)
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    transfer.apply(target, transfer.plan_import(target, data))
    assert target.books_in_play is not None
    packs.after_import(target, data)
    assert "HtM" in target.books_in_play
    assert len(target.characters) == len(data["saga"]["characters"])
    ids = {n.id for n in target.neighbours}
    for record in [*target.covenants, *target.neighbours]:
        assert record.place_id is None or record.place_id in ids


# -- The Dragon and the Bear --

NOVGOROD = book_packs.PACKS["novgorod"]


def test_the_novgorod_pack_holds_the_tribunal_of_1220():
    from ars_magica_manager.tribunal_packages import novgorod as package

    saga = NOVGOROD.build()
    (tribunal,) = saga.tribunals
    assert tribunal.package == package.NOVGOROD.key
    assert (tribunal.next_year, tribunal.next_season) == (1221, "Summer")
    assert tribunal.meeting_place == "Three Lakes"
    assert (tribunal.covenants_total, tribunal.magi_total) == (6, 30)
    praeco = saga.character(tribunal.praeco_id or "")
    quaesitor = saga.character(tribunal.quaesitor_id or "")
    assert praeco is not None and praeco.name == "Miya Cossuri"
    assert quaesitor is not None and quaesitor.name == "Andrei Soitkchin"
    assert {r.year for r in tribunal.rulings} == {1039, 1132, 1190}
    assert {c.kind for c in tribunal.cases} == {"charge", "motion"}
    assert len(tribunal.cases) == 3
    auras = {c.name: (c.aura, c.aura_realm) for c in saga.covenants}
    assert auras == {
        "Three Lakes": (4, "Magic"),
        "Thousand Caves": (6, "Faerie"),
        "Pripet Maior": (6, "Magic"),
        "Leczyca": (4, "Magic"),
    }
    names = {c.name for c in saga.characters}
    assert "Stolitzya the Swimmer" not in names
    assert "Stolitzya the Swimmer" in {c.name for c in saga.creatures}
    keys = [(n.name, n.kind) for n in saga.neighbours]
    assert len(keys) == len(set(keys))


def test_the_novgorod_pack_converts_its_printed_magi_by_the_de_readings():
    saga = NOVGOROD.build()
    magi = {c.name: c for c in saga.characters}
    andrei = magi["Andrei Soitkchin"]
    assert 1220 - (andrei.background.year_born or 0) == 122
    assert (
        andrei.background.confidence_score,
        andrei.background.confidence_points,
    ) == (1, 3)
    # Andrei prints no spells: he knows the listed ones of his Arts, mastered.
    assert len(andrei.spells_known) > 20
    assert all(k.mastery_score == 1 for k in andrei.spells_known)
    malincka = magi["Malincka Capcek"]
    own = {s.name: s.level for s in malincka.invented_spells}
    assert (
        own.items()
        >= {
            "Charge the Magical Circle": 25,
            "Read the Magic Sphere": 35,
            "Plumb the Magical Scent": 20,
            "Air of Friendly Magic": 30,
        }.items()
    )
    nastassia = magi["Nastassia Baramov"]
    assert {"Form of the Avenging Beast", "Echo of the Firebird"} <= {
        s.name for s in nastassia.invented_spells
    }
    assert magi["Rehamchi Danichev"].traditions == ["trad_volkhvy"]
    assert magi["Lelya Danichev"].traditions == ["trad_volkhvy"]
    # Batiba's shamanism is not Hermetic magic: he stays a sketch.
    assert magi["Batiba an Khatiba"].detail != "full"


def test_the_novgorod_pack_reprices_faerie_powers_by_rop_faerie():
    saga = NOVGOROD.build()
    creatures = {c.name: c for c in saga.creatures}
    assert len(creatures) == 22
    lord = creatures["Slavic Faerie Lord"]
    powers = {p.name: p for p in lord.powers}
    # Curse 10 on a Might 35 faerie: Grant (Major Flaw), 10 points, Init Qik - 20.
    assert (powers["Curse"].might_cost, powers["Curse"].init) == (10, -18)
    # Glamour 12 is a Focus Power capped at the Might: level 35.
    assert powers["Glamour"].level == 35
    assert creatures["Upiór (Vampire)"].realm == "Infernal"


def test_the_novgorod_pack_adds_its_stages_to_the_shared_mongols():
    data = book_packs.data(NOVGOROD)
    (mongols,) = [
        n for n in data["saga"]["neighbours"] if n["name"] == "The Mongol Conquest"
    ]
    titles = [s["title"] for s in mongols["details"]["stages"]]
    assert {"The Kalka", "Kiev falls", "Legnica and the Sajo"} <= set(titles)
    levant = book_packs.data(book_packs.PACKS["levant"])
    (same,) = [
        n for n in levant["saga"]["neighbours"] if n["name"] == "The Mongol Conquest"
    ]
    assert same["details"]["stages"] == mongols["details"]["stages"]


def test_the_novgorod_pack_keeps_its_secrets_and_credit():
    data = book_packs.data(NOVGOROD)
    assert _secrets_kept(data["saga"]) >= 4
    assert data["book"] == "D&B" and "Creative Commons" in data["source"]


def test_the_novgorod_pack_imports_clean_into_a_new_saga():
    data = book_packs.data(NOVGOROD)
    target = Saga(id="dst", name="Target", books_in_play=["Covenants"])
    transfer.apply(target, transfer.plan_import(target, data))
    assert packs.after_import(target, data) == [
        "The Dragon and the Bear: The Novgorod Tribunal is now in play.",
        packs.assumptions_note("The Dragon and the Bear: The Novgorod Tribunal"),
    ]
    assert target.books_in_play is not None and "D&B" in target.books_in_play
    assert len(target.characters) == len(data["saga"]["characters"])
    ids = {n.id for n in target.neighbours}
    for record in [*target.covenants, *target.neighbours]:
        assert record.place_id is None or record.place_id in ids


def test_no_pack_says_its_vis_or_books_in_public():
    found = []
    for pack in book_packs.PACKS.values():
        saga = pack.assemble().saga
        for records, name in (
            (saga.neighbours, "summary"),
            (saga.covenants, "what_matters"),
            (saga.creatures, "notes"),
        ):
            found += [
                f"{pack.key}: {r.name}"
                for r in records
                if any(
                    builder.HOLDINGS.match(line)
                    for line in getattr(r, name).split("\n")
                )
            ]
    assert not found, found
