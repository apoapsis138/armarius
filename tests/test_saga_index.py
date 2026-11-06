"""Find's index of the saga's records (saga_index.py): every kind lists
itself, a name ranks above a member, a place or a Tribunal's lands, and
Secrets and notes are not searched."""

from __future__ import annotations

from ars_magica_manager import references, saga_index
from ars_magica_manager.models import (
    Book,
    Character,
    Covenant,
    Creature,
    EnchantedDevice,
    Familiar,
    KnownSpell,
    Laboratory,
    Neighbour,
    Saga,
    Spell,
    Tribunal,
)


def _saga() -> Saga:
    saga = Saga(id="s", name="S")
    saga.tribunals.append(Tribunal(id="rhine", name="Rhine"))
    saga.neighbours += [
        Neighbour(
            id="drachenfels",
            name="The Drachenfels",
            kind="place",
            details={"tribunal": "rhine"},
        ),
        Neighbour(
            id="gottfried",
            name="Gottfried of Arnsberg",
            kind="lord",
            place_id="drachenfels",
            secrets="Secretly a werewolf",
            summary="A grasping lord",
        ),
        Neighbour(
            id="court",
            name="The Court of Thorns",
            kind="faction",
            details={"roster": [{"who": "neighbours:gottfried", "role": "knight"}]},
        ),
    ]
    saga.covenants.append(
        Covenant(id="cov", saga_id="s", name="Fengheld", place_id="drachenfels")
    )
    magus = Character(
        id="mag", name="Arn of Bonisagus", type="magus", covenant_id="cov"
    )
    magus.spells_known.append(KnownSpell(spell_id="own-spell"))
    magus.invented_spells.append(
        Spell(id="own-spell", name="Ward of the Thorn", technique="Re", form="He")
    )
    saga.characters.append(magus)
    saga.laboratories.append(
        Laboratory(id="lab", name="Arn's Sanctum", covenant_id="cov")
    )
    saga.familiars.append(Familiar(id="fam", character_id="mag", name="Corvus"))
    saga.creatures.append(Creature(id="wyrm", name="The Wyrm", place_id="drachenfels"))
    saga.books += [
        Book(
            id="b1",
            name="Thorns and Roses",
            type="Art Summa",
            owner_kind="covenant",
            owner_id="cov",
        ),
        Book(id="b2", name="A Lost Book", type="Art Summa"),
    ]
    saga.enchanted_devices.append(
        EnchantedDevice(
            id="d1", name="Ring of Embers", holder_kind="character", holder_id="mag"
        )
    )
    return saga


def _found(saga: Saga, query: str) -> list[str]:
    return [m.entry.name for m in saga_index.search(saga_index.entries(saga), query)]


def _match(saga: Saga, name: str, query: str) -> saga_index.Match:
    found = saga_index.search(saga_index.entries(saga), query)
    return next(m for m in found if m.entry.name == name)


def test_every_kind_lists_itself_and_opens_a_page():
    saga = _saga()
    found = {e.name: e for e in saga_index.entries(saga)}
    kinds = {name: (e.kind, e.ref.kind, e.ref.id) for name, e in found.items()}
    assert kinds == {
        "Arn of Bonisagus": ("Magus", "characters", "mag"),
        "Fengheld": ("Covenant", "covenants", "cov"),
        "Arn's Sanctum": ("Laboratory", "laboratories", "lab"),
        "Corvus": ("Familiar", "familiars", "fam"),
        "Rhine": ("Tribunal", "tribunals", "rhine"),
        "The Drachenfels": ("Place", "neighbours", "drachenfels"),
        "Gottfried of Arnsberg": ("Lord", "neighbours", "gottfried"),
        "The Court of Thorns": ("Faction", "neighbours", "court"),
        "The Wyrm": ("Creature", "creatures", "wyrm"),
        # A book, spell or device opens the page that holds it.
        "Thorns and Roses": ("Book", "covenants", "cov"),
        "Ward of the Thorn": ("Spell", "characters", "mag"),
        "Ring of Embers": ("Enchanted device", "characters", "mag"),
    }
    # ... at its row there.
    spots = {name: e.spot for name, e in found.items() if e.spot is not None}
    assert spots == {
        "Thorns and Roses": saga_index.Spot(saga_index.BOOKS, "b1"),
        "Ward of the Thorn": saga_index.Spot(saga_index.SPELLS, "own-spell"),
        "Ring of Embers": saga_index.Spot(saga_index.DEVICES, "d1"),
    }
    magus = found["Ring of Embers"].ref
    assert saga_index.spot_row(saga, magus, spots["Ring of Embers"]) == 0
    assert saga_index.spot_row(saga, magus, spots["Ward of the Thorn"]) == 0
    # A book's row is the page's to find: each sets its own order.
    assert saga_index.spot_row(saga, magus, spots["Thorns and Roses"]) is None
    # One held by nobody has no page to open.
    assert "A Lost Book" not in found
    for entry in found.values():
        assert entry.ref.kind in references.KINDS.values()


def test_a_match_shows_its_name_kind_and_place():
    saga = _saga()
    assert (
        _match(saga, "Gottfried of Arnsberg", "gott").line
        == "Gottfried of Arnsberg · Lord · The Drachenfels"
    )
    assert _match(saga, "Arn of Bonisagus", "arn").line == (
        "Arn of Bonisagus · Magus · Fengheld"
    )
    assert _match(saga, "Ward of the Thorn", "ward").line == (
        "Ward of the Thorn · Spell · known by Arn of Bonisagus"
    )


def test_a_name_ranks_first_any_case():
    saga = _saga()
    # Names starting with it, then a word starting with it, then any part;
    # then the faction Gottfried is a member of.
    assert _found(saga, "THORN") == [
        "Thorns and Roses",
        "The Court of Thorns",
        "Ward of the Thorn",
    ]
    assert _found(saga, "gottfried") == ["Gottfried of Arnsberg", "The Court of Thorns"]


def test_a_faction_is_found_by_its_members():
    saga = _saga()
    match = _match(saga, "The Court of Thorns", "arnsberg")
    assert match.why == "member Gottfried of Arnsberg"


def test_a_record_is_found_by_its_place_and_its_tribunals_lands():
    saga = _saga()
    at_the_rock = _found(saga, "drachenfels")
    assert at_the_rock[0] == "The Drachenfels"
    assert {"Gottfried of Arnsberg", "Fengheld", "The Wyrm"} <= set(at_the_rock)
    at = _match(saga, "The Wyrm", "drachenfels")
    assert at.why == "at The Drachenfels"
    assert at.note == ""  # its place says so already
    assert _match(saga, "The Court of Thorns", "arnsberg").note == (
        "member Gottfried of Arnsberg"
    )
    in_the_rhine = _found(saga, "rhine")
    assert in_the_rhine[0] == "Rhine"
    # The covenant lies in the Rhine's lands, and its magus with it.
    assert {"Fengheld", "Arn of Bonisagus", "The Wyrm"} <= set(in_the_rhine)
    assert _match(saga, "Fengheld", "rhine").why == "in the lands of Rhine"
    # A place's match outranks a Tribunal's.
    ranks = {
        m.entry.name: m.rank
        for m in saga_index.search(saga_index.entries(saga), "the drachenfels")
    }
    assert ranks["The Drachenfels"] < ranks["The Wyrm"]


def test_secrets_and_notes_are_not_searched():
    saga = _saga()
    assert _found(saga, "werewolf") == []
    assert _found(saga, "grasping") == []


def test_no_words_lists_everything_and_unknown_words_nothing():
    saga = _saga()
    every = saga_index.entries(saga)
    assert len(saga_index.search(every, "  ")) == len(every)
    assert saga_index.search(every, "zzz") == []


def test_a_name_that_is_the_words_exactly_comes_first_in_its_rank():
    saga = _saga()
    saga.neighbours += [
        Neighbour(id="gorge", name="The Rhine Gorge", kind="place"),
        Neighbour(id="league", name="The Rhine League", kind="faction"),
    ]
    # "Rhine" is the Tribunal's whole name; alphabetically it'd come last.
    assert _found(saga, "rhine")[:3] == ["Rhine", "The Rhine Gorge", "The Rhine League"]
    saga.neighbours.append(Neighbour(id="rh", name="Rhine", kind="place"))
    saga.tribunals[0].name = "The Rhine Tribunal"
    # A whole name, any case, its article aside, comes first; then a name
    # that is the words and the kind it ends with.
    assert _found(saga, "THE RHINE")[:4] == [
        "Rhine",
        "The Rhine Tribunal",
        "The Rhine Gorge",
        "The Rhine League",
    ]
    assert _found(saga, "the rhine tribunal")[0] == "The Rhine Tribunal"


def test_a_leading_the_and_accents_are_passed_over():
    saga = _saga()
    saga.covenants[0].name = "Dammërstein"
    assert _found(saga, "dammerstein")[0] == "Dammërstein"
    assert _found(saga, "DAMMËR")[0] == "Dammërstein"
    # "court" opens The Court of Thorns' name, as "drach" The Drachenfels'.
    assert _match(saga, "The Court of Thorns", "court").rank == 0
    assert _found(saga, "drach")[0] == "The Drachenfels"
