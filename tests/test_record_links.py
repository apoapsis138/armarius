"""Deleting a record leaves no ids pointing at it (STORY-2366): the links
list (record_links.LINKS) covers every field that names a record, and
each Delete forgets the record through it."""

import copy
import importlib
import pkgutil
import re
from collections.abc import Callable
from dataclasses import fields, is_dataclass
from typing import Any

import pytest

from ars_magica_manager import (
    books,
    creatures,
    deletion,
    models,
    neighbours,
    players,
    record_links,
    sessions,
    tribunals,
)
from ars_magica_manager.models import (
    AtlasMap,
    Attitude,
    Background,
    Book,
    Casting,
    Censure,
    Character,
    CharterClause,
    CharterSeal,
    Covenant,
    CovenantCharter,
    CovenantDiaryEntry,
    CovenantStop,
    Creature,
    EnchantedDevice,
    Familiar,
    Favour,
    GuestStay,
    Inhabitant,
    Laboratory,
    LabTextAccess,
    Link,
    Marriage,
    Neighbour,
    Pin,
    Player,
    Possession,
    Saga,
    SeasonPlan,
    Session,
    Ship,
    TeachRequest,
    Tribunal,
)

# -- an independent look: every place a record's id still appears --


def pointers_to(saga: Saga, record_id: str) -> list[str]:
    """Every field in the saga, as "Owner.field" (with where it is), whose
    value, list item, dict key or "kind:id" names `record_id`, leaving out
    history: the fields the links list keeps (KEEP, or kept while their
    entry is history). Walks every dataclass, list and dict, so a field
    the links list doesn't know still shows."""
    found: list[str] = []

    def names(value: Any) -> bool:
        return isinstance(value, str) and (
            value == record_id or value.endswith(":" + record_id)
        )

    def kept(entry: Any, name: str, above: tuple[Any, ...]) -> bool:
        for link in record_links.LINKS.get(type(entry), ()):
            if link.name != name:
                continue
            if link.on_delete == record_links.KEEP:
                return True
            if link.kept_while is not None and link.kept_while(entry, above):
                return True
        return False

    def walk(value: Any, where: str, owner: Any, name: str, above: tuple) -> None:
        if is_dataclass(value) and not isinstance(value, type):
            for each in fields(value):
                walk(
                    getattr(value, each.name),
                    f"{where}.{each.name}",
                    value,
                    each.name,
                    (*above, value),
                )
            return
        hit = (
            names(value)
            or (isinstance(value, list) and any(names(v) for v in value))
            or (isinstance(value, dict) and any(names(k) for k in value))
        )
        if hit and not kept(owner, name, above[:-1]):
            found.append(f"{type(owner).__name__}.{name} at {where}")
        if isinstance(value, list):
            for at, item in enumerate(value):
                if not isinstance(item, str):
                    walk(item, f"{where}[{at}]", owner, name, above)
        elif isinstance(value, dict):
            for key, item in value.items():
                if not isinstance(item, str):
                    walk(item, f"{where}[{key!r}]", owner, name, above)

    walk(saga, "saga", saga, "", ())
    return found


# -- a saga where every kind of record is named everywhere it can be --


def _everything() -> Saga:
    """One of each kind of record Delete removes, each named by the
    others in as many places as the saga allows."""
    magus = Character(
        id="id-mag",
        name="Aldo",
        type="magus",
        covenant_id="id-cov",
        assigned_lab_id="id-lab",
        away_place_id="id-place",
        storyguide_id="id-pl",
        tractatus_read=["id-book"],
        lab_text_access={"id-com": LabTextAccess(level=10)},
        background=Background(player_ids=["id-pl"], steward_id="id-pl"),
        stay=GuestStay(host_id="id-cov2"),
        links=[
            Link(kind="creatures", target_id="id-beast"),
            Link(kind="places", target_id="id-place"),
            Link(kind="familiars", target_id="id-fam"),
            Link(kind="books", target_id="id-book"),
            Link(kind="covenants", target_id="id-cov2"),
            Link(kind="characters", target_id="id-com"),
            Link(kind="possessions", target_id="ship1"),
            Link(kind="possessions", target_id="sanctum1"),
        ],
        favours=[
            Favour(what="a horse", owed_by="id-lord", owed_to="id-cov2"),
            Favour(what="a book", owed_by="id-com", owed_to="id-mag"),
        ],
    )
    companion = Character(
        id="id-com",
        name="Brother Anselm",
        type="companion",
        covenant_id="id-cov",
        links=[Link(kind="characters", target_id="id-mag")],
    )
    covenant = Covenant(
        id="id-cov",
        saga_id="s",
        name="Dammerstein",
        tribunal_id="id-trib",
        place_id="id-place",
        storyguide_id="id-pl",
        charter_of_covenant=CovenantCharter(
            seals=[CharterSeal(character_id="id-mag")],
            clauses=[CharterClause(number="1", censure=Censure(character_id="id-mag"))],
        ),
        possessions=[
            Possession(
                id="ship1",
                kind="ship",
                name="Hansa",
                ship=Ship(captain_id="id-mag", aboard=["id-mag", "id-com"]),
            ),
            Possession(
                id="store1",
                kind="vis_store",
                location_kind="character",
                location_id="id-mag",
            ),
            Possession(id="sanctum1", kind="sanctum", lab_id="id-lab"),
            Possession(id="source1", kind="vis_source", place_id="id-place"),
        ],
        inhabitants=[Inhabitant(id="i1", kind="turb", character_id="id-com")],
        stops=[CovenantStop(year=1220, season="Spring", place_id="id-place")],
        diary=[
            CovenantDiaryEntry(
                year=1220,
                name="The tower",
                cast=["id-mag"],
                session_id="id-ses",
                about=["characters:id-mag"],
                concerns="laboratories:id-lab",
            )
        ],
        links=[Link(kind="characters", target_id="id-mag")],
    )
    other = Covenant(
        id="id-cov2",
        saga_id="s",
        name="Fengheld",
        liege_id="id-cov",
        attitudes=[Attitude(covenant_id="id-cov")],
    )
    tribunal = Tribunal(
        id="id-trib",
        name="Rhine",
        praeco_id="id-mag",
        quaesitor_id="id-com",
        proxies={"id-cov": 2},
        storyguide_id="id-pl",
    )
    tribunal.maps = [AtlasMap(id="id-map", name="Rhine", picture="rhine.png")]
    lord = Neighbour(
        id="id-lord",
        name="Count Otto",
        kind="lord",
        ruler="id-mag",
        place_id="id-place",
        storyguide_id="id-pl",
        attitudes=[Attitude(covenant_id="id-cov")],
        favours=[Favour(what="a hawk", owed_by="id-cov", owed_to="id-com")],
    )
    place = Neighbour(
        id="id-place",
        name="Black Fen",
        kind="place",
        details={
            "travels_with": "id-cov",
            "claimed_by": "id-cov",
            "tribunal": "id-trib",
        },
    )
    vassal = Neighbour(
        id="id-vassal", name="Sir Gerd", kind="lord", answers_to="id-lord"
    )
    faction = Neighbour(
        id="id-faction",
        name="The Lantern",
        kind="faction",
        details={
            "roster": [
                {"who": "characters:id-mag", "role": "Master"},
                {"who": "covenants:id-cov", "role": ""},
                {"who": "creatures:id-beast", "role": ""},
                {"who": "neighbours:id-lord", "role": ""},
            ]
        },
    )
    return Saga(
        id="s",
        name="Saga",
        covenants=[covenant, other],
        tribunals=[tribunal],
        neighbours=[lord, place, vassal, faction],
        characters=[magus, companion],
        laboratories=[
            Laboratory(
                id="id-lab",
                covenant_id="id-cov",
                name="Tower",
                owner_id="id-mag",
                place_id="id-place",
            )
        ],
        familiars=[Familiar(id="id-fam", character_id="id-mag", name="Ashwing")],
        creatures=[
            Creature(
                id="id-beast", name="Wyrm", place_id="id-place", storyguide_id="id-pl"
            )
        ],
        books=[
            Book(
                id="id-book",
                name="Summa",
                type="Summa",
                owner_kind="character",
                owner_id="id-mag",
                author_id="id-mag",
            ),
            Book(
                id="id-gloss", name="Gloss", type="Tractatus", commentary_on="id-book"
            ),
        ],
        enchanted_devices=[
            EnchantedDevice(
                id="d1",
                name="Wand",
                holder_kind="laboratory",
                holder_id="id-lab",
                maker_id="id-mag",
            )
        ],
        season_plans=[
            SeasonPlan(
                character_id="id-mag",
                year=1220,
                season="Spring",
                activity="Practice",
                lab_id="id-lab",
                book_id="id-book",
            ),
            SeasonPlan(
                character_id="id-com",
                year=1220,
                season="Spring",
                activity="Taught",
                teacher_id="id-mag",
                assistant_ids=["id-mag"],
            ),
        ],
        teach_requests=[
            TeachRequest(
                id="t1",
                student_id="id-com",
                teacher_id="id-mag",
                subject="ability:Latin",
                season="Summer",
                year=1220,
            )
        ],
        marriages=[
            Marriage(
                bride_ref="character:id-com",
                groom_ref="neighbour:id-lord",
                bride_house="id-lord",
            )
        ],
        players=[Player(id="id-pl", name="Pat")],
        sessions=[
            Session(
                id="id-ses",
                storyguide_id="id-pl",
                coming=["id-pl"],
                castings=[Casting(player_id="id-pl", character_id="id-mag")],
                names={"id-pl": "Pat"},
            ),
            Session(
                id="id-played",
                played=True,
                storyguide_id="id-pl",
                coming=["id-pl"],
                castings=[
                    Casting(
                        player_id="id-pl",
                        character_id="id-mag",
                        player_name="Pat",
                        character_name="Aldo",
                    )
                ],
                names={"id-pl": "Pat"},
            ),
        ],
        pins=[
            Pin(map_id="id-map", kind="characters", record_id="id-mag", x=0.1, y=0.1),
            Pin(map_id="id-map", kind="neighbours", record_id="id-lord", x=0.2, y=0.2),
            Pin(map_id="id-map", kind="creatures", record_id="id-beast", x=0.3, y=0.3),
            Pin(map_id="id-map", kind="laboratories", record_id="id-lab", x=0.4, y=0.4),
            Pin(map_id="id-map", kind="covenants", record_id="id-cov", x=0.5, y=0.5),
        ],
    )


def _find(saga: Saga, kind: str, record_id: str) -> Any:
    return next(r for r in getattr(saga, kind) if r.id == record_id)


#: Each kind of record, and how Delete removes one.
DELETES: dict[str, tuple[str, Callable[[Saga, Any], None]]] = {
    "characters": ("id-mag", deletion.delete_character),
    "familiars": ("id-fam", deletion.delete_familiar),
    "laboratories": ("id-lab", deletion.delete_laboratory),
    "covenants": ("id-cov", deletion.delete_covenant),
    "creatures": ("id-beast", creatures.delete),
    "neighbours": ("id-lord", neighbours.delete),
    "tribunals": ("id-trib", tribunals.delete),
    "books": ("id-book", books.delete),
    "players": ("id-pl", players.remove),
    "sessions": ("id-ses", sessions.delete),
}


def test_the_saga_names_every_kind_before_any_delete() -> None:
    saga = _everything()
    for kind, (record_id, _delete) in DELETES.items():
        assert pointers_to(saga, record_id), kind


@pytest.mark.parametrize("kind", DELETES)
def test_after_deleting_a_record_nothing_points_at_it(kind: str) -> None:
    saga = _everything()
    record_id, delete = DELETES[kind]
    delete(saga, _find(saga, kind, record_id))
    assert pointers_to(saga, record_id) == []


def test_after_deleting_a_place_nothing_points_at_it() -> None:
    saga = _everything()
    neighbours.delete(saga, _find(saga, "neighbours", "id-place"))
    assert pointers_to(saga, "id-place") == []


def test_a_tribunals_maps_and_their_pins_go_with_it() -> None:
    saga = _everything()
    tribunals.delete(saga, _find(saga, "tribunals", "id-trib"))
    assert saga.pins == []
    assert pointers_to(saga, "id-map") == []


# -- what each field keeps --


def _deleted_magus() -> Saga:
    saga = _everything()
    deletion.delete_character(saga, _find(saga, "characters", "id-mag"))
    return saga


def test_a_deleted_magus_is_remembered_by_name_where_a_name_does() -> None:
    saga = _deleted_magus()
    lord = _find(saga, "neighbours", "id-lord")
    assert lord.ruler == "Aldo"
    assert saga.enchanted_devices[0].maker_name == "Aldo"
    assert saga.enchanted_devices[0].maker_id is None
    assert saga.books[0].author == "Aldo"
    assert saga.books[0].author_id is None


def test_a_deleted_magus_leaves_the_entries_that_were_his_alone() -> None:
    saga = _deleted_magus()
    covenant = _find(saga, "covenants", "id-cov")
    assert covenant.charter_of_covenant.seals == []
    assert covenant.charter_of_covenant.clauses[0].censure is None
    assert [p.character_id for p in saga.season_plans] == ["id-com"]
    assert saga.teach_requests == []
    assert [p.record_id for p in saga.pins if p.kind == "characters"] == []


def test_a_deleted_magus_is_cleared_where_the_entry_stands_without_him() -> None:
    saga = _deleted_magus()
    ship = _find(saga, "covenants", "id-cov").possessions[0].ship
    assert ship.captain_id is None
    assert ship.aboard == ["id-com"]
    [plan] = saga.season_plans
    assert plan.teacher_id is None
    assert plan.assistant_ids == []
    assert _find(saga, "laboratories", "id-lab").owner_id is None


def test_a_played_session_keeps_who_played_whom() -> None:
    saga = _deleted_magus()
    planned, played = saga.sessions
    assert planned.castings == []
    assert [c.character_name for c in played.castings] == ["Aldo"]


def test_a_deleted_player_leaves_planned_sessions_and_stays_in_played_ones() -> None:
    saga = _everything()
    players.remove(saga, saga.players[0])
    planned, played = saga.sessions
    assert (planned.storyguide_id, planned.coming, planned.names) == ("", [], {})
    assert planned.castings == []
    assert played.names == {"id-pl": "Pat"}
    assert played.coming == ["id-pl"]


def test_a_deleted_lords_marriage_keeps_his_name() -> None:
    saga = _everything()
    neighbours.delete(saga, _find(saga, "neighbours", "id-lord"))
    [marriage] = saga.marriages
    assert (marriage.groom_ref, marriage.groom) == ("", "Count Otto")
    assert marriage.bride_house is None
    assert marriage.bride_ref == "character:id-com"


def test_favours_keep_the_name_of_whom_they_were_owed() -> None:
    saga = _everything()
    deletion.delete_covenant(saga, _find(saga, "covenants", "id-cov2"))
    magus = _find(saga, "characters", "id-mag")
    assert magus.favours[0].owed_to == "Fengheld"


def test_lab_text_access_is_kept_by_the_authors_name() -> None:
    saga = _everything()
    deletion.delete_character(saga, _find(saga, "characters", "id-com"))
    assert list(_find(saga, "characters", "id-mag").lab_text_access) == [
        "Brother Anselm"
    ]


# -- Find: who points at a record --


def test_pointing_at_lists_every_entry_that_names_a_record() -> None:
    saga = _everything()
    found = {
        (type(entry).__name__, link.name)
        for entry, link in record_links.pointing_at(saga, "creatures", "id-beast")
    }
    assert found == {
        ("Link", "target_id"),
        ("Pin", "record_id"),
        ("Neighbour", "details"),
    }


def test_a_deleted_covenants_possessions_lose_their_links() -> None:
    saga = _everything()
    deletion.delete_covenant(saga, _find(saga, "covenants", "id-cov"))
    kinds = [link.kind for link in _find(saga, "characters", "id-mag").links]
    assert "possessions" not in kinds


def test_a_deleted_laboratorys_sanctum_extras_lose_their_links() -> None:
    saga = _everything()
    deletion.delete_laboratory(saga, _find(saga, "laboratories", "id-lab"))
    targets = [link.target_id for link in _find(saga, "characters", "id-mag").links]
    assert "sanctum1" not in targets
    assert "ship1" in targets


def test_a_faction_loses_a_deleted_member_and_keeps_the_rest() -> None:
    saga = _everything()
    deletion.delete_character(saga, _find(saga, "characters", "id-mag"))
    roster = _find(saga, "neighbours", "id-faction").details["roster"]
    assert [m["who"] for m in roster] == [
        "covenants:id-cov",
        "creatures:id-beast",
        "neighbours:id-lord",
    ]


def test_an_id_shared_by_two_kinds_is_only_forgotten_for_its_own() -> None:
    """Ids come from names, so a neighbour and a character may share one."""
    saga = _everything()
    saga.neighbours.append(Neighbour(id="id-mag", name="Aldo's Mill", kind="place"))
    neighbours.delete(saga, saga.neighbours[-1])
    assert _find(saga, "covenants", "id-cov").charter_of_covenant.seals != []
    assert _find(saga, "neighbours", "id-lord").ruler == "id-mag"


# -- import: map ids through --


def _imported(saga: Saga, root: Any, here: dict[str, dict[str, str]]) -> None:
    """Map `root`'s ids as an import would, with `here`'s copies (kind ->
    old id -> new id) and the file's names for the rest."""
    names = {r.id: r.name for kind in here for r in getattr(saga, kind)}
    record_links.map_ids(
        root,
        lambda kind, old: here.get(kind, {}).get(old),
        frozenset({"characters", "covenants", "neighbours", "creatures"}),
        skip=frozenset({(Character, "lab_text_access")}),
        name_of=lambda _kind, old: names.get(old),
    )


def test_import_maps_ids_through_the_links_list() -> None:
    saga = _everything()
    covenant = _find(saga, "covenants", "id-cov")
    _imported(saga, covenant, {"characters": {"id-mag": "new-mag"}})
    ship = covenant.possessions[0].ship
    assert (ship.captain_id, ship.aboard) == ("new-mag", ["new-mag"])
    assert covenant.charter_of_covenant.seals[0].character_id == "new-mag"
    # Not here: the Tribunal isn't one of the kinds mapped, the place is gone.
    assert covenant.tribunal_id == "id-trib"
    assert covenant.place_id is None
    assert covenant.stops == []


def test_import_drops_or_names_what_has_no_copy_here() -> None:
    saga = _everything()
    lord = _find(saga, "neighbours", "id-lord")
    magus = _find(saga, "characters", "id-mag")
    _imported(saga, lord, {"characters": {}, "covenants": {}})
    _imported(saga, magus, {"characters": {}, "covenants": {}})
    assert lord.ruler == "Aldo"
    assert lord.attitudes == []
    assert magus.stay is None
    assert magus.favours[0].owed_to == "Fengheld"
    # Kinds the import doesn't map here (books, familiars, possessions) stay.
    assert [link.kind for link in magus.links] == [
        "familiars",
        "books",
        "possessions",
        "possessions",
    ]
    assert list(magus.lab_text_access) == ["id-com"]


# -- pictures --


def test_pictures_are_the_picture_fields_of_the_links_list() -> None:
    saga = _everything()
    saga.characters[0].portrait = "aldo.png"
    assert record_links.pictures(saga) == [
        ("maps", "rhine.png"),
        ("portraits", "aldo.png"),
    ] or record_links.pictures(saga) == [
        ("portraits", "aldo.png"),
        ("maps", "rhine.png"),
    ]


# -- the list is complete --

#: Fields named like ids that the links list leaves out, by why.
NOT_RECORD_LINKS: set[tuple[str, str]] = {
    # Catalog entries (Virtues, Flaws, features, goods, gear), not records.
    ("GrigoriSecret", "vf_id"),
    ("StationReached", "vf_id"),
    ("VirtueFlawInstance", "vf_id"),
    ("GoodPurity", "good_id"),
    ("Purchase", "good_id"),
    ("Possession", "gear_id"),
    ("Combatant", "weapon_id"),
    ("LabFeature", "feature_id"),
    ("LabFeature", "virtue_id"),
    ("LabItemBenefit", "virtue_id"),
    ("LabItemBenefit", "granted_id"),
    ("CultComponent", "flaw_id"),
    ("CultDegree", "virtue_id"),
    ("SeasonPlan", "taught_flaw_id"),
    ("SeasonPlan", "ordeal_lost_id"),
    # Entries inside one record, which go with it: a covenant's diary
    # lines, a Tribunal's cases, a menagerie's beasts, a lab's connections.
    ("CovenantDiaryEntry", "boon_hook_id"),
    ("CovenantDiaryEntry", "threat_id"),
    ("CovenantDiaryEntry", "story_id"),
    ("Censure", "case_id"),
    ("Argument", "case_id"),
    ("Ruling", "case_id"),
    ("TreasuryEntry", "case_id"),
    ("Breeding", "sire_id"),
    ("Breeding", "dam_id"),
    ("SeasonPlan", "connection_id"),
    ("Covenant", "saga_id"),
    # Spells, codices and enchanted devices: Delete doesn't remove them
    # (lab_items.forget_device and the spell and library forms do their
    # own forgetting).
    ("Book", "spell_id"),
    ("Book", "codex_id"),
    ("Book", "device_id"),
    ("KnownSpell", "spell_id"),
    ("LabProject", "spell_id"),
    ("SpellDesign", "source_spell_id"),
    ("SeasonPlan", "spell_id"),
    ("SeasonPlan", "similar_spell_id"),
    ("SeasonPlan", "taught_spell_ids"),
    ("SeasonPlan", "device_id"),
    ("SeasonPlan", "effect_id"),
    ("LabItemBenefit", "device_id"),
    ("LabItemBenefit", "effect_id"),
    ("Digestion", "device_id"),
}

_ID_LIKE = re.compile(r"(_id|_ids|_ref)$")


def _model_classes() -> list[type]:
    found = []
    for info in pkgutil.iter_modules(models.__path__):
        module = importlib.import_module(f"{models.__name__}.{info.name}")
        for value in vars(module).values():
            if (
                isinstance(value, type)
                and is_dataclass(value)
                and value.__module__ == module.__name__
            ):
                found.append(value)
    return found


def test_every_id_field_is_in_the_links_list_or_ruled_out() -> None:
    """A new field that names a record goes in record_links.LINKS (or, if
    it names none, NOT_RECORD_LINKS here), so deleting never misses it."""
    listed = {
        (owner.__name__, link.name)
        for owner, links in record_links.LINKS.items()
        for link in links
    }
    missing = sorted(
        (cls.__name__, f.name)
        for cls in _model_classes()
        for f in fields(cls)
        if _ID_LIKE.search(f.name)
        and (cls.__name__, f.name) not in listed
        and (cls.__name__, f.name) not in NOT_RECORD_LINKS
    )
    assert missing == []


def test_the_walk_finds_entries_inside_a_copy() -> None:
    """forget works on any saga: nothing is cached between calls."""
    saga = copy.deepcopy(_everything())
    assert record_links.pointing_at(saga, "players", "id-pl")
