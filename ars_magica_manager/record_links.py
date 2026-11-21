"""The ids one record keeps of another, in one list (ADR 0004: flat
records linked by id).

LINKS says, for each kind of entry that names other records, which of its
fields name which kinds of record, and what becomes of each when the
record it names is deleted:

- DROP: the entry goes (a charter seal, a link, a pin, the magus's own
  season plans); one id in a list goes from the list;
- CLEAR: the field is emptied, and a list of ids loses the one (a lab's
  owner, a ship's `aboard`);
- NAME: the record is remembered by its name, in the field itself or a
  sibling (a neighbour's ruler, a device's maker, a favour's names);
- KEEP: history, left as it was on purpose, because the entry keeps the
  name as written beside the id (a played Session's castings, a season's
  record).

A field's `kept_while` keeps it instead while its entry is history (a
planned Session's castings go, a played one's stay).

Deleting a record forgets it through the list (forget); a sheet's Linked
from follows it back (pointing_at, links_naming); an export's pictures
are its PICTURES fields (pictures, pictures_in_data). Deleting a record
keeps its Picture file: only tidying unused pictures removes one.

Pattern: Strategy dict keyed by record type, as in section_verbs: LINKS
maps an entry's type to its link fields; each user brings its own action
(forget, follow, list pictures) and the list stays data, so a new linked
field is one entry. Entries are found by walking the saga's dataclasses,
so no field's place in the saga is written down twice."""

from __future__ import annotations

import copy
from collections.abc import Callable, Iterator, Mapping
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from functools import cache
from typing import Any, get_args, get_origin, get_type_hints

from .models import (
    Agent,
    Argument,
    AtlasMap,
    Attitude,
    Background,
    Battle,
    BattleEvent,
    BattleSide,
    Beast,
    Book,
    BoundBeing,
    CalendarEntry,
    Casting,
    Censure,
    Character,
    CharterSeal,
    Combatant,
    Covenant,
    CovenantDiaryEntry,
    CovenantStop,
    Creature,
    Digestion,
    EnchantedDevice,
    Enigma,
    Familiar,
    Favour,
    Fight,
    FightSide,
    GuestStay,
    HermeticProject,
    Inhabitant,
    Laboratory,
    LabProject,
    Link,
    Marriage,
    MysteryCult,
    Neighbour,
    Pin,
    PolemicText,
    Possession,
    ResearchAttempt,
    RouteStop,
    Saga,
    Scene,
    SceneUse,
    SeasonPlan,
    SeasonRecordLine,
    Session,
    Ship,
    Siege,
    TeachRequest,
    Tribunal,
)
from .paths import MAPS, PORTRAITS

# -- the kinds of record, as the saga lists them --

CHARACTERS = "characters"
COVENANTS = "covenants"
LABORATORIES = "laboratories"
FAMILIARS = "familiars"
TRIBUNALS = "tribunals"
NEIGHBOURS = "neighbours"
CREATURES = "creatures"
BOOKS = "books"
PLAYERS = "players"
SESSIONS = "sessions"
MAPS_KIND = "maps"
BATTLES = "battles"
FIGHTS = "fights"
SIEGES = "sieges"
#: A covenant's possession (its Possessions entries are kept on it).
POSSESSIONS = "possessions"
#: A Picture, by file name in its folder (LinkField.folder).
PICTURES = "pictures"
#: The saga's Scenes library (scenes.py).
SCENES = "scenes"
#: What a Scene's actors may be, as "kind:id": who can rule a neighbour
#: (references.RULER_KINDS, which sits a layer above; a test keeps the
#: two the same).
ACTORS: tuple[str, ...] = (CHARACTERS, NEIGHBOURS, CREATURES)
#: What a Scene may show, as "kind:id": a record with a page
#: (references.KINDS, kept the same by the same test), or a map.
SHOWABLE: tuple[str, ...] = (
    CHARACTERS,
    COVENANTS,
    LABORATORIES,
    FAMILIARS,
    TRIBUNALS,
    NEIGHBOURS,
    CREATURES,
    MAPS_KIND,
)

#: What becomes of a field when the record it names is deleted.
DROP, CLEAR, NAME, KEEP = "drop", "clear", "name", "keep"

#: A holder's singular kind word (a book's owner_kind, a device's
#: holder_kind, a vis store's location_kind, a spouse's ref) as the saga's.
SINGULAR: Mapping[str, str] = {
    "character": CHARACTERS,
    "covenant": COVENANTS,
    "laboratory": LABORATORIES,
    "neighbour": NEIGHBOURS,
}

#: A Link's kind as the saga's: a place is a neighbour.
LINK_KIND: Mapping[str, str] = {
    "characters": CHARACTERS,
    "covenants": COVENANTS,
    "familiars": FAMILIARS,
    "places": NEIGHBOURS,
    "creatures": CREATURES,
    "books": BOOKS,
    "possessions": POSSESSIONS,
}


def _in_played_session(entry: Any, above: tuple[Any, ...]) -> bool:
    """Whether the entry is (in) a played Session: history."""
    return any(isinstance(a, Session) and a.played for a in (entry, *above))


@dataclass(frozen=True)
class Slot:
    """One value a link field holds on one entry, as stored ("kind:id" for
    a prefixed field), with how to change it or take it out. `alone`: the
    field holds only this value (not one of a list, dict or roster)."""

    raw: str
    put: Callable[[str], None]
    take: Callable[[], None]
    alone: bool


@dataclass(frozen=True)
class LinkField:
    """One field of an entry that names records: its name, the kinds it
    may name, and what deleting the named record does (DROP, CLEAR, NAME
    or KEEP).

    - `kind_from`: a sibling whose value says which kind it names (a
      Link's `kind`), read through `kind_names`;
    - `prefixed`: each value is "kind:id" (a Marriage's spouse refs), the
      kind read through `kind_names`;
    - `keys`: the ids are the keys of a dict (lab text access by author);
    - `within`: the field is a dict (a neighbour's details) and the value
      is under this key; with `row_key`, that key holds a list of rows
      (dicts), each naming a record under `row_key` (a faction's roster);
    - `name_into`: for NAME, the sibling that takes the name when empty
      ("" for the field itself);
    - `clears_too`: siblings set back to their defaults when it is
      cleared (a place's level);
    - `kept_while`: KEEP instead while this says the entry is history;
    - `folder`: for PICTURES, the folder the file is in;
    - `noun`, `nouns`: what a Delete's warning counts it as, one and
      many ("map pin", "map pins"; "laboratory's owner", "laboratories'
      owners")."""

    name: str
    kinds: tuple[str, ...]
    noun: str = ""
    nouns: str = ""
    on_delete: str = CLEAR
    kind_from: str = ""
    kind_names: Mapping[str, str] = field(default_factory=dict)
    prefixed: bool = False
    keys: bool = False
    within: str = ""
    row_key: str = ""
    name_into: str = ""
    clears_too: tuple[str, ...] = ()
    kept_while: Callable[[Any, tuple[Any, ...]], bool] | None = None
    folder: str = ""

    def kind_of(self, entry: Any, raw: str) -> str | None:
        """The kind of record the stored value `raw` names; None when the
        field names one of several kinds without saying which."""
        if self.prefixed:
            prefix = raw.partition(":")[0]
            return self.kind_names.get(prefix, prefix)
        if self.kind_from:
            said = getattr(entry, self.kind_from, None) or ""
            return self.kind_names.get(said, said) or None
        return self.kinds[0] if len(self.kinds) == 1 else None

    def id_in(self, raw: str) -> str:
        return raw.partition(":")[2] if self.prefixed else raw

    def with_id(self, raw: str, new_id: str) -> str:
        return f"{raw.partition(':')[0]}:{new_id}" if self.prefixed else new_id

    def slots(self, entry: Any) -> list[Slot]:
        """Each value the field holds on `entry`."""
        value = getattr(entry, self.name)
        if self.within:
            if not isinstance(value, dict):
                return []
            if self.row_key:
                rows = value.get(self.within)
                return _row_slots(rows, self.row_key) if isinstance(rows, list) else []
            return _key_slot(value, self.within)
        if self.keys:
            return _dict_key_slots(value) if isinstance(value, dict) else []
        if isinstance(value, list):
            return _list_slots(value)
        if isinstance(value, str) and value:
            return [
                Slot(
                    value,
                    lambda new: setattr(entry, self.name, new),
                    lambda: setattr(entry, self.name, _empty(entry, self.name)),
                    alone=True,
                )
            ]
        return []

    def ids(self, entry: Any) -> list[str]:
        """The ids (or names) the field holds on `entry`."""
        return [self.id_in(s.raw) for s in self.slots(entry)]


def _list_slots(values: list[Any]) -> list[Slot]:
    def put(old: str) -> Callable[[str], None]:
        return lambda new: values.__setitem__(values.index(old), new)

    def take(old: str) -> Callable[[], None]:
        return lambda: values.remove(old)

    return [
        Slot(v, put(v), take(v), alone=False)
        for v in values
        if isinstance(v, str) and v
    ]


def _dict_key_slots(values: dict[str, Any]) -> list[Slot]:
    def put(old: str) -> Callable[[str], None]:
        return lambda new: values.__setitem__(new, values.pop(old))

    def take(old: str) -> Callable[[], None]:
        return lambda: values.pop(old, None)

    return [Slot(k, put(k), take(k), alone=False) for k in list(values) if k]


def _key_slot(values: dict[str, Any], key: str) -> list[Slot]:
    found = values.get(key)
    if not isinstance(found, str) or not found:
        return []
    return [
        Slot(
            found,
            lambda new: values.__setitem__(key, new),
            lambda: values.pop(key, None),
            alone=True,
        )
    ]


def _row_slots(rows: list[Any], key: str) -> list[Slot]:
    def put(row: dict[str, Any]) -> Callable[[str], None]:
        return lambda new: row.__setitem__(key, new)

    def take(row: dict[str, Any]) -> Callable[[], None]:
        return lambda: rows.__setitem__(slice(None), [r for r in rows if r is not row])

    return [
        Slot(row[key], put(row), take(row), alone=False)
        for row in rows
        if isinstance(row, dict) and isinstance(row.get(key), str) and row[key]
    ]


def _f(name: str, *kinds: str, noun: str | tuple[str, str], **how: Any) -> LinkField:
    """A link field; `noun` is what the warning calls it, with its plural
    when that isn't the noun and an "s"."""
    one, many = noun if isinstance(noun, tuple) else (noun, noun + "s")
    return LinkField(name, kinds, one, many, **how)


def _of(owner: str, owners: str, what: str, whats: str = "") -> tuple[str, str]:
    """An emptied field's noun: "laboratory's owner", "laboratories'
    owners"."""
    return f"{owner}'s {what}", f"{owners}' {whats or what + 's'}"


_ANY_HOLDER = (CHARACTERS, COVENANTS, LABORATORIES)
#: Who may owe or be owed a favour, in the order an id is looked for
#: (as import maps them).
_PERSON = (COVENANTS, CHARACTERS, NEIGHBOURS)
#: What a neighbour's ruler may be, in the order references.ruler looks.
_RULER = (CHARACTERS, NEIGHBOURS, CREATURES)


def _storyguide(owner: str, owners: str) -> LinkField:
    """Who runs a record as its storyguide."""
    return _f("storyguide_id", PLAYERS, noun=_of(owner, owners, "storyguide"))


def _place(owner: str, owners: str, name: str = "place_id", **how: Any) -> LinkField:
    """A place (a place neighbour) and which of its levels."""
    return _f(
        name,
        NEIGHBOURS,
        noun=_of(owner, owners, "place"),
        clears_too=("place_level",),
        **how,
    )


_CHARACTER = ("character", "characters")
_COVENANT = ("covenant", "covenants")
_LAB = ("laboratory", "laboratories")
_NEIGHBOUR = ("neighbour", "neighbours")
_POSSESSION = ("possession", "possessions")
_PLAN = ("season plan", "season plans")
_SESSION = ("Session", "Sessions")

#: Each kind of entry that names records, and its fields that do.
LINKS: dict[type, tuple[LinkField, ...]] = {
    # -- a character and what hangs off one --
    Character: (
        _f("covenant_id", COVENANTS, noun=_of(*_CHARACTER, "covenant")),
        _f(
            "assigned_lab_id",
            LABORATORIES,
            noun=_of(*_CHARACTER, "laboratory", "laboratories"),
        ),
        _f("away_place_id", NEIGHBOURS, noun=_of(*_CHARACTER, "place away")),
        _f(
            "lab_text_access",
            CHARACTERS,
            noun="Lab Text a character may copy",
            on_delete=NAME,
            keys=True,
        ),
        _f(
            "tractatus_read",
            BOOKS,
            noun=_of(*_CHARACTER, "tractatus read", "tractatus read"),
        ),
        _f("summae_read", BOOKS, noun=_of(*_CHARACTER, "summa read", "summae read")),
        _storyguide(*_CHARACTER),
        _f("portrait", PICTURES, noun="portrait", on_delete=KEEP, folder=PORTRAITS),
    ),
    Background: (
        _f("player_ids", PLAYERS, noun=_of(*_CHARACTER, "Player")),
        _f("steward_id", PLAYERS, noun=_of(*_CHARACTER, "steward")),
    ),
    GuestStay: (_f("host_id", COVENANTS, noun="guest's stay", on_delete=DROP),),
    BoundBeing: (_f("creature_id", CREATURES, noun=_of(*_CHARACTER, "bound being")),),
    ResearchAttempt: (
        _f(
            "lab_id",
            LABORATORIES,
            noun=_of(
                "research attempt", "research attempts", "laboratory", "laboratories"
            ),
        ),
    ),
    Enigma: (_f("guide_id", CHARACTERS, noun=_of(*_CHARACTER, "Enigma guide")),),
    Familiar: (_f("character_id", CHARACTERS, noun="Familiar", on_delete=DROP),),
    # -- covenants --
    Covenant: (
        _f("tribunal_id", TRIBUNALS, noun=_of(*_COVENANT, "Tribunal")),
        _f("liege_id", COVENANTS, noun=_of(*_COVENANT, "liege")),
        _place(*_COVENANT),
        _storyguide(*_COVENANT),
    ),
    CharterSeal: (_f("character_id", CHARACTERS, noun="charter seal", on_delete=DROP),),
    Censure: (_f("character_id", CHARACTERS, noun="censure", on_delete=DROP),),
    Inhabitant: (
        _f(
            "character_id",
            CHARACTERS,
            noun=_of("inhabitant", "inhabitants", "character"),
        ),
    ),
    Possession: (
        _f(
            "lab_id", LABORATORIES, noun=_of(*_POSSESSION, "laboratory", "laboratories")
        ),
        _f(
            "location_id",
            *_ANY_HOLDER,
            noun=_of(*_POSSESSION, "keeper"),
            kind_from="location_kind",
            kind_names=SINGULAR,
        ),
        _place(*_POSSESSION),
    ),
    Ship: (
        _f("captain_id", CHARACTERS, noun=_of("ship", "ships", "captain")),
        _f("aboard", CHARACTERS, noun=_of("ship", "ships", "crew", "crews")),
    ),
    CovenantStop: (
        _f("place_id", NEIGHBOURS, noun="covenant's route stop", on_delete=DROP),
    ),
    RouteStop: (_f("place_id", NEIGHBOURS, noun="route stop", on_delete=DROP),),
    CovenantDiaryEntry: (
        # What a line the app wrote is about: kept, so it stays hidden
        # from players as it was (viewing.py).
        _f(
            "about",
            *_RULER,
            COVENANTS,
            LABORATORIES,
            noun="diary line",
            on_delete=KEEP,
            prefixed=True,
        ),
        _f(
            "concerns",
            CHARACTERS,
            LABORATORIES,
            noun=_of("diary line", "diary lines", "subject"),
            prefixed=True,
        ),
        _f("cast", CHARACTERS, noun=_of("diary line", "diary lines", "cast", "casts")),
        _f("session_id", SESSIONS, noun=_of("Chapter", "Chapters", "Session")),
    ),
    # -- laboratories, books, devices --
    Laboratory: (
        _f("covenant_id", COVENANTS, noun=_of(*_LAB, "covenant")),
        _f("owner_id", CHARACTERS, noun=_of(*_LAB, "owner")),
        _place(*_LAB),
    ),
    Book: (
        _f(
            "owner_id",
            *_ANY_HOLDER,
            noun=_of("book", "books", "owner"),
            kind_from="owner_kind",
            kind_names=SINGULAR,
        ),
        _f(
            "author_id",
            CHARACTERS,
            noun=_of("book", "books", "author"),
            on_delete=NAME,
            name_into="author",
        ),
        _f("commentary_on", BOOKS, noun="gloss"),
    ),
    EnchantedDevice: (
        _f(
            "holder_id",
            *_ANY_HOLDER,
            noun=_of("enchanted device", "enchanted devices", "holder"),
            kind_from="holder_kind",
            kind_names=SINGULAR,
        ),
        _f(
            "maker_id",
            CHARACTERS,
            noun=_of("enchanted device", "enchanted devices", "maker"),
            on_delete=NAME,
            name_into="maker_name",
        ),
    ),
    Digestion: (
        _f(
            "lab_id",
            LABORATORIES,
            noun=_of("vis digestion", "vis digestions", "laboratory", "laboratories"),
        ),
    ),
    # -- the world: neighbours, creatures, standing, links, the Atlas --
    Neighbour: (
        _f("ruler", *_RULER, noun=_of(*_NEIGHBOUR, "ruler"), on_delete=NAME),
        _f("answers_to", NEIGHBOURS, noun=_of(*_NEIGHBOUR, "lord")),
        _place(*_NEIGHBOUR),
        _storyguide(*_NEIGHBOUR),
        # Its kind's own fields (neighbour_lists, places, ruins).
        _f(
            "details",
            COVENANTS,
            noun=_of(*_NEIGHBOUR, "travelling companion"),
            within="travels_with",
        ),
        _f(
            "details", COVENANTS, noun=_of(*_NEIGHBOUR, "claimant"), within="claimed_by"
        ),
        _f("details", TRIBUNALS, noun=_of(*_NEIGHBOUR, "Tribunal"), within="tribunal"),
        _f(
            "details",
            CHARACTERS,
            COVENANTS,
            CREATURES,
            NEIGHBOURS,
            noun="faction member",
            on_delete=DROP,
            prefixed=True,
            within="roster",
            row_key="who",
        ),
    ),
    Creature: (_place("creature", "creatures"), _storyguide("creature", "creatures")),
    Agent: (_f("neighbour_id", NEIGHBOURS, noun=_of("agent", "agents", "neighbour")),),
    Attitude: (_f("covenant_id", COVENANTS, noun="attitude", on_delete=DROP),),
    Favour: (
        _f("owed_by", *_PERSON, noun="favour", on_delete=NAME),
        _f("owed_to", *_PERSON, noun="favour", on_delete=NAME),
    ),
    Link: (
        _f(
            "target_id",
            *LINK_KIND.values(),
            noun="link",
            on_delete=DROP,
            kind_from="kind",
            kind_names=LINK_KIND,
        ),
    ),
    Marriage: (
        _f(
            "bride_ref",
            CHARACTERS,
            NEIGHBOURS,
            noun="marriage",
            on_delete=NAME,
            prefixed=True,
            kind_names=SINGULAR,
            name_into="bride",
        ),
        _f(
            "groom_ref",
            CHARACTERS,
            NEIGHBOURS,
            noun="marriage",
            on_delete=NAME,
            prefixed=True,
            kind_names=SINGULAR,
            name_into="groom",
        ),
        _f(
            "bride_house",
            NEIGHBOURS,
            noun=_of("marriage", "marriages", "bride's house", "brides' houses"),
        ),
        _f(
            "groom_house",
            NEIGHBOURS,
            noun=_of("marriage", "marriages", "groom's house", "grooms' houses"),
        ),
    ),
    AtlasMap: (
        _f("picture", PICTURES, noun="map picture", on_delete=KEEP, folder=MAPS),
    ),
    Pin: (
        _f("map_id", MAPS_KIND, noun="map pin", on_delete=DROP),
        _f(
            "record_id",
            COVENANTS,
            NEIGHBOURS,
            CREATURES,
            LABORATORIES,
            CHARACTERS,
            noun="map pin",
            on_delete=DROP,
            kind_from="kind",
        ),
    ),
    Tribunal: (
        _f(
            "praeco_id",
            CHARACTERS,
            noun=_of("Tribunal", "Tribunals", "Praeco", "Praecones"),
        ),
        _f(
            "quaesitor_id",
            CHARACTERS,
            noun=_of("Tribunal", "Tribunals", "Quaesitor", "Quaesitores"),
        ),
        _f(
            "proxies",
            COVENANTS,
            noun=_of("Tribunal", "Tribunals", "proxy", "proxies"),
            keys=True,
        ),
        _storyguide("Tribunal", "Tribunals"),
    ),
    # -- Hermetic Projects, cults, Polemic --
    HermeticProject: (
        _f(
            "mason_id",
            CHARACTERS,
            noun=_of("Hermetic Project", "Hermetic Projects", "mason"),
        ),
        _f(
            "place_id",
            NEIGHBOURS,
            noun=_of("Hermetic Project", "Hermetic Projects", "place"),
        ),
        _f(
            "handler_ids",
            CHARACTERS,
            noun=_of("Hermetic Project", "Hermetic Projects", "handler"),
        ),
        _f(
            "owner_id",
            CHARACTERS,
            noun=_of("Hermetic Project", "Hermetic Projects", "owner"),
        ),
    ),
    Beast: (
        _f("creature_id", CREATURES, noun=_of("beast", "beasts", "creature")),
        _f("tamer_id", CHARACTERS, noun=_of("beast", "beasts", "tamer")),
    ),
    MysteryCult: (
        _f(
            "founder_id",
            CHARACTERS,
            noun=_of("Mystery Cult", "Mystery Cults", "founder"),
        ),
    ),
    PolemicText: (
        _f("book_id", BOOKS, noun=_of("polemic", "polemics", "book")),
        _f("author_id", CHARACTERS, noun=_of("polemic", "polemics", "author")),
        _f(
            "circulated_by_id",
            CHARACTERS,
            noun=_of("polemic", "polemics", "circulator"),
        ),
    ),
    Argument: (
        _f("proponent_id", CHARACTERS, noun=_of("argument", "arguments", "proponent")),
    ),
    # -- seasons and the table --
    SeasonPlan: (
        _f("character_id", CHARACTERS, noun=_PLAN, on_delete=DROP),
        _f("book_id", BOOKS, noun=_of(*_PLAN, "book")),
        _f("more_book_ids", BOOKS, noun=_of(*_PLAN, "book")),
        _f("teacher_id", CHARACTERS, noun=_of(*_PLAN, "teacher")),
        _f("lab_id", LABORATORIES, noun=_of(*_PLAN, "laboratory", "laboratories")),
        _f("subject_id", CHARACTERS, noun=_of(*_PLAN, "subject")),
        _f("assistant_ids", CHARACTERS, noun=_of(*_PLAN, "assistant")),
        _f("partner_id", CHARACTERS, noun=_of(*_PLAN, "partner")),
    ),
    LabProject: (_f("character_id", CHARACTERS, noun="lab project", on_delete=DROP),),
    CalendarEntry: (
        _f(
            "covenant_id",
            COVENANTS,
            noun=_of("calendar entry", "calendar entries", "covenant"),
        ),
    ),
    SeasonRecordLine: (
        _f("character_id", CHARACTERS, noun="season record", on_delete=KEEP),
        _f("covenant_id", COVENANTS, noun="season record", on_delete=KEEP),
    ),
    TeachRequest: (
        _f("student_id", CHARACTERS, noun="request to be taught", on_delete=DROP),
        _f("teacher_id", CHARACTERS, noun="request to be taught", on_delete=DROP),
    ),
    Session: (
        _f(
            "storyguide_id",
            PLAYERS,
            noun=_of(*_SESSION, "storyguide"),
            kept_while=_in_played_session,
        ),
        _f(
            "coming",
            PLAYERS,
            noun=_of(*_SESSION, "Player coming", "Players coming"),
            kept_while=_in_played_session,
        ),
        _f(
            "away",
            PLAYERS,
            noun=_of(*_SESSION, "Player away", "Players away"),
            kept_while=_in_played_session,
        ),
        # The names as written, by Player: what a played Session reads.
        _f(
            "names",
            PLAYERS,
            noun=_of(*_SESSION, "Player's name", "Players' names"),
            keys=True,
            kept_while=_in_played_session,
        ),
    ),
    Scene: (
        _place("Scene", "Scenes"),
        _f("covenant_id", COVENANTS, noun=_of("Scene", "Scenes", "covenant")),
        _f("regulars", *ACTORS, noun=_of("Scene", "Scenes", "regular"), prefixed=True),
        _f(
            "to_show",
            *SHOWABLE,
            noun=_of("Scene", "Scenes", "thing to show", "things to show"),
            prefixed=True,
        ),
        _f("picture", PICTURES, noun="Scene picture", on_delete=KEEP, folder=MAPS),
    ),
    SceneUse: (
        # A use of a Scene since deleted goes with it (scenes.delete refuses
        # one playing or played).
        _f(
            "scene_id",
            SCENES,
            noun="Scene in a Session",
            on_delete=DROP,
            kept_while=_in_played_session,
        ),
        # Who was there stays in a played Session, named as written.
        _f(
            "present",
            *ACTORS,
            noun=_of(
                "Scene in a Session", "Scenes in Sessions", "who's there", "who's there"
            ),
            prefixed=True,
            kept_while=_in_played_session,
        ),
        _f(
            "names",
            *ACTORS,
            noun=_of("Scene in a Session", "Scenes in Sessions", "name", "names"),
            prefixed=True,
            keys=True,
            kept_while=_in_played_session,
        ),
    ),
    Casting: (
        _f(
            "player_id",
            PLAYERS,
            noun="casting in a Session",
            on_delete=DROP,
            kept_while=_in_played_session,
        ),
        _f(
            "character_id",
            CHARACTERS,
            noun="casting in a Session",
            on_delete=DROP,
            kept_while=_in_played_session,
        ),
    ),
    # -- conflicts: each side and fighter keeps its name --
    Combatant: (
        _f(
            "ref_id",
            CHARACTERS,
            CREATURES,
            noun=_of("combatant", "combatants", "sheet"),
            kind_from="kind",
            kind_names={"character": CHARACTERS, "creature": CREATURES},
        ),
    ),
    FightSide: (
        _f(
            "covenant_id",
            COVENANTS,
            noun=_of("fight's side", "fights' sides", "covenant"),
        ),
    ),
    Fight: (_f("battle_id", BATTLES, noun=_of("fight", "fights", "battle")),),
    Siege: (
        _f("covenant_id", COVENANTS, noun=_of("siege", "sieges", "covenant")),
        _f("castle_id", NEIGHBOURS, noun=_of("siege", "sieges", "castle")),
        _f("besieger_id", NEIGHBOURS, noun=_of("siege", "sieges", "besieger")),
    ),
    BattleSide: (
        _f(
            "neighbour_id",
            NEIGHBOURS,
            noun=_of("battle's side", "battles' sides", "neighbour"),
        ),
        _f(
            "covenant_id",
            COVENANTS,
            noun=_of("battle's side", "battles' sides", "covenant"),
        ),
        _f(
            "pilot_id",
            CHARACTERS,
            noun=_of("battle's side", "battles' sides", "commander"),
        ),
    ),
    BattleEvent: (
        _f("fight_id", FIGHTS, noun=_of("battle event", "battle events", "fight")),
    ),
    Battle: (_f("siege_id", SIEGES, noun=_of("battle", "battles", "siege")),),
}


# -- finding the entries --


@dataclass(frozen=True)
class Found:
    """An entry that names records: the entry, the entries it is inside
    (outermost first), and the list, dict or entry that holds it."""

    entry: Any
    above: tuple[Any, ...]
    holder: Any


def entries(root: Any) -> Iterator[Found]:
    """Every entry under `root` (a saga, or any record) that LINKS knows,
    outermost first."""
    yield from _walk(root, (), None)


def _walk(value: Any, above: tuple[Any, ...], holder: Any) -> Iterator[Found]:
    if type(value) in LINKS:
        yield Found(value, above, holder)
    inside = (*above, value)
    for name in _nested(type(value)):
        child = getattr(value, name)
        if isinstance(child, list):
            for item in child:
                if is_dataclass(item):
                    yield from _walk(item, inside, child)
        elif isinstance(child, dict):
            for item in child.values():
                if is_dataclass(item):
                    yield from _walk(item, inside, child)
        elif is_dataclass(child):
            yield from _walk(child, inside, value)


@dataclass(frozen=True)
class _Naming:
    """One value of one field that names the record looked for."""

    found: Found
    link: LinkField
    slot: Slot


def _naming(saga: Saga, kind: str, record_ids: set[str]) -> Iterator[_Naming]:
    """Every value in the saga that names one of the records `kind`
    `record_ids`."""
    for found in entries(saga):
        for link in LINKS[type(found.entry)]:
            if kind not in link.kinds:
                continue
            for slot in link.slots(found.entry):
                if link.id_in(slot.raw) in record_ids and _names_kind(
                    saga, link, found.entry, slot.raw, kind
                ):
                    yield _Naming(found, link, slot)


def _names_kind(saga: Saga, link: LinkField, entry: Any, raw: str, kind: str) -> bool:
    said = link.kind_of(entry, raw)
    if said is not None:
        return said == kind
    # A field that may name several kinds without saying which (a
    # neighbour's ruler, a favour's owed_by) names the first of its kinds,
    # in order, that has a record with the id (ids come from names, so
    # two kinds may share one); `kind`'s record may be gone already.
    record_id = link.id_in(raw)
    named = next(
        (k for k in link.kinds if k == kind or _exists(saga, k, record_id)), None
    )
    return named == kind


def _exists(saga: Saga, kind: str, record_id: str) -> bool:
    records = getattr(saga, kind, None)
    return isinstance(records, list) and any(
        getattr(r, "id", None) == record_id for r in records
    )


# -- follow: who points at a record --


@dataclass(frozen=True)
class Pointer:
    """An entry naming a record: the top-level record it is kept on (the
    magus whose Links, the covenant whose seal; an entry kept on the saga
    itself is its own), the entry, and the field that names it."""

    record: Any
    entry: Any
    link: LinkField


def _record_of(found: Found) -> Any:
    # above[0] is the saga; the record kept in one of its lists follows.
    return found.above[1] if len(found.above) > 1 else found.entry


def pointing_at(saga: Saga, kind: str, record_id: str) -> list[Pointer]:
    """Each entry and field in the saga that names the record `kind`
    `record_id`, with the record holding it, history (KEEP) included; an
    entry naming it twice in one field is listed once."""
    found: list[Pointer] = []
    for naming in _naming(saga, kind, {record_id}):
        entry, link = naming.found.entry, naming.link
        if not any(p.entry is entry and p.link is link for p in found):
            found.append(Pointer(_record_of(naming.found), entry, link))
    return found


def links_naming(saga: Saga, link_kind: str, record_id: str) -> list[Pointer]:
    """The Links a person typed in to the record `record_id`, of the Link
    kind `link_kind` ("places" for a place), each with the record keeping
    it. Only a Link saying that kind counts: one with no kind, or some
    other word, isn't to this record, whatever its id."""
    return [
        p
        for p in pointing_at(saga, LINK_KIND[link_kind], record_id)
        if isinstance(p.entry, Link) and p.entry.kind == link_kind
    ]


# -- delete: forget a record --


#: What a Delete's warning says happens to an entry, in the order it
#: says them.
GOES, EMPTIED, KEEPS_NAME = "Goes", "Emptied", "Keeps the name"
_GROUP = {DROP: GOES, CLEAR: EMPTIED, NAME: KEEPS_NAME}
_GROUPS = (GOES, EMPTIED, KEEPS_NAME)


@dataclass(frozen=True)
class Change:
    """What forget did to one entry: it went, a field was emptied, or it
    kept the record's name, by the field that named it."""

    group: str
    link: LinkField
    entry: Any


#: A Delete: removes the record from the saga and says what forget
#: changed besides.
Delete = Callable[[Saga, Any], list[Change]]


def forget(saga: Saga, kind: str, *records: Any) -> list[Change]:
    """Once `records` (of `kind`) are taken out of the saga: every value
    that names one is dropped, cleared or turned into its name, as LINKS
    says; history stays. One walk of the saga, however many. Returns
    what it changed."""
    names = {r.id: getattr(r, "name", "") for r in records if r.id}
    if not names:
        return []
    todo = list(_naming(saga, kind, set(names)))
    dropped: list[Any] = []
    changes: list[Change] = []
    for naming in todo:
        found, link, slot = naming.found, naming.link, naming.slot
        if any(found.entry is d for d in dropped):
            continue
        how = link.on_delete
        if link.kept_while is not None and link.kept_while(found.entry, found.above):
            how = KEEP
        if how == KEEP:
            continue
        changes.append(Change(_GROUP[how], link, found.entry))
        if how == DROP and slot.alone:
            _drop(found)
            dropped.append(found.entry)
        elif how == NAME:
            _remember_name(found.entry, link, slot, names[link.id_in(slot.raw)])
        else:
            _clear(found.entry, link, slot)
    return changes


def change_lines(changes: list[Change]) -> list[str]:
    """The warning's lines for `changes`: "Goes: 2 map pins, 1 charter
    seal.", then what is emptied, then what keeps the name, each left out
    when it has nothing. An entry counts once, for the most it undergoes
    (going before emptied before keeping the name)."""
    kept: dict[int, Change] = {}
    for change in changes:
        held = kept.get(id(change.entry))
        if held is None or _GROUPS.index(change.group) < _GROUPS.index(held.group):
            kept[id(change.entry)] = change
    lines: list[str] = []
    for group in _GROUPS:
        counts: dict[tuple[str, str], int] = {}
        for change in kept.values():
            if change.group == group:
                noun = (change.link.noun, change.link.nouns)
                counts[noun] = counts.get(noun, 0) + 1
        if counts:
            said = ", ".join(
                f"{n} {one if n == 1 else many}" for (one, many), n in counts.items()
            )
            lines.append(f"{group}: {said}.")
    return lines


def warning(saga: Saga, record: Any, delete: Delete) -> list[str]:
    """What deleting `record` with `delete` would change besides, as the
    confirmation's lines: the Delete runs on a copy of the saga, so the
    counts are what it then does, and the saga is left as it was."""
    copied, gone = copy.deepcopy((saga, record))
    return change_lines(delete(copied, gone))


def _drop(found: Found) -> None:
    holder = found.holder
    if isinstance(holder, list):
        holder[:] = [e for e in holder if e is not found.entry]
    elif isinstance(holder, dict):
        for key in [k for k, v in holder.items() if v is found.entry]:
            del holder[key]
    elif holder is not None:
        for each in fields(holder):
            if getattr(holder, each.name) is found.entry:
                setattr(holder, each.name, _empty(holder, each.name))


def _empty(entry: Any, name: str) -> Any:
    """The field's value when nothing is named: its default, else ""."""
    for each in fields(entry):
        if each.name != name:
            continue
        if each.default is not MISSING:
            return each.default
        if each.default_factory is not MISSING:
            return each.default_factory()
    return ""


def _clear(entry: Any, link: LinkField, slot: Slot) -> None:
    slot.take()
    if slot.alone and not link.within:
        for sibling in (link.kind_from, *link.clears_too):
            if sibling:
                setattr(entry, sibling, _empty(entry, sibling))


def _remember_name(entry: Any, link: LinkField, slot: Slot, name: str) -> None:
    if link.name_into:
        if not getattr(entry, link.name_into):
            setattr(entry, link.name_into, name)
        slot.take()
    else:
        slot.put(name)


# -- import: map ids through --

#: An import's id map: the id here of the file's record `kind` `old`, or
#: None when the saga has no copy of it.
Mapped = Callable[[str, str], str | None]


def map_ids(
    root: Any,
    mapped: Mapped,
    kinds: frozenset[str],
    *,
    skip: frozenset[tuple[type, str]] = frozenset(),
    name_of: Mapped | None = None,
) -> None:
    """Map each id under `root` that names one of `kinds` through `mapped`.
    One with no copy here goes as deleting its record would: dropped or
    cleared, or for a NAME field the record's name (`name_of`; left as it
    was when that has none). History (KEEP), the other kinds and the
    fields in `skip` (owner type, field), which the caller maps itself,
    are left as they are."""
    dropped: list[Any] = []
    for found in list(entries(root)):
        if any(found.entry is d for d in dropped):
            continue
        for link in LINKS[type(found.entry)]:
            if link.on_delete == KEEP or (type(found.entry), link.name) in skip:
                continue
            if not kinds.intersection(link.kinds):
                continue
            if _map_field(found, link, mapped, kinds, name_of):
                dropped.append(found.entry)
                break


def _map_field(
    found: Found,
    link: LinkField,
    mapped: Mapped,
    kinds: frozenset[str],
    name_of: Mapped | None,
) -> bool:
    """Map one field's values; True when the entry was dropped."""
    entry = found.entry
    for slot in link.slots(entry):
        old = link.id_in(slot.raw)
        said = link.kind_of(entry, slot.raw)
        candidates = [k for k in ([said] if said else link.kinds) if k in kinds]
        if not candidates:
            continue
        new = next((n for k in candidates if (n := mapped(k, old)) is not None), None)
        if new is not None:
            slot.put(link.with_id(slot.raw, new))
            continue
        if link.on_delete == NAME:
            name = next(
                (n for k in candidates if name_of and (n := name_of(k, old))), ""
            )
            if name:
                _remember_name(entry, link, slot, name)
        elif link.on_delete == DROP and slot.alone:
            _drop(found)
            return True
        else:
            _clear(entry, link, slot)
    return False


# -- export: the pictures records name --


def pictures(root: Any) -> list[tuple[str, str]]:
    """The pictures the records under `root` name, as (folder, file name),
    each once, in the order found."""
    found: list[tuple[str, str]] = []
    for each in entries(root):
        for link in LINKS[type(each.entry)]:
            if PICTURES in link.kinds:
                found += [(link.folder, name) for name in link.ids(each.entry)]
    return list(dict.fromkeys(found))


def pictures_in_data(
    data: Mapping[str, Any], cls: type = Saga
) -> list[tuple[str, str]]:
    """pictures() of a record kept as plain data (an export's or a seat's
    saga, as asdict made it): its fields are read by `cls`'s types."""
    found: list[tuple[str, str]] = []
    _data_pictures(data, cls, found)
    return list(dict.fromkeys(found))


def _data_pictures(data: Any, cls: type, found: list[tuple[str, str]]) -> None:
    if not isinstance(data, Mapping):
        return
    for link in LINKS.get(cls, ()):
        value = data.get(link.name)
        if PICTURES in link.kinds and isinstance(value, str) and value:
            found.append((link.folder, value))
    for name, (inner, by_key) in _nested(cls).items():
        value = data.get(name)
        if isinstance(value, list):
            items = value
        elif by_key and isinstance(value, Mapping):
            items = list(value.values())
        else:
            items = [value]
        for item in items:
            _data_pictures(item, inner, found)


@cache
def _nested(cls: type) -> dict[str, tuple[type, bool]]:
    """`cls`'s fields that hold entries (one, a list or a dict of them):
    the entry's type, and whether they are a dict's values. What a walk
    descends into; nothing for a type that isn't a dataclass."""
    if not is_dataclass(cls):
        return {}
    hints = get_type_hints(cls)
    nested: dict[str, tuple[type, bool]] = {}
    for each in fields(cls):
        hint = hints[each.name]
        inner = _entry_type(hint)
        if inner is not None:
            nested[each.name] = (inner, get_origin(hint) is dict)
    return nested


def _entry_type(hint: Any) -> type | None:
    """The dataclass `hint` holds: itself, or in a list, dict or Optional."""
    if isinstance(hint, type) and is_dataclass(hint):
        return hint
    args = [a for a in get_args(hint) if a is not type(None)]
    if get_origin(hint) is dict and len(args) == 2:
        return _entry_type(args[1])
    if len(args) == 1:
        return _entry_type(args[0])
    return None
