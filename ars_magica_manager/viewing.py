"""Who may read what: the one check every page, list, search and export
asks before it shows a player anything.

A viewer is the storyguide, a named player signed in to a hosted copy,
or the table: the storyguide's own window in Player view, a generic
player, for a screen the players watch. The storyguide reads everything.
Any other viewer reads a record only while it is known to the players,
and a part of a page (a section, tab or chapter, by its id) unless
STORYGUIDE_ONLY lists it.

Pattern: Protection Proxy, the read-side partner of players.guard_changes.
Each front-end tells this module once who is looking (`use`), and every
page, list and export asks `may_read` (or one of the helpers built on it)
instead of deciding for itself, so what a player may read is decided in
one place. A front-end draws a record's page from the same saga either
way; what changes is what it is allowed to put on it.

A record the troupe plays (a player character, a troupe covenant, their
laboratories and familiars) is always known, as are Tribunals; anything
else carries `known` (models), which Reveal ticks.

With more than one storyguide (troupe-style play, ADR 0015), a record can
have its own storyguide (`storyguide_of`). A storyguide reads their own
records and those with none as the storyguide does; a record another
storyguide runs they read as a player would, the host included. Each
storyguide's window opens Playing, Player view by another name: their
characters as a player sees them, until they switch to their storyguide
role."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from typing import Any

from . import settings
from .models import (
    Character,
    Covenant,
    CovenantDiaryEntry,
    Creature,
    Familiar,
    Laboratory,
    Neighbour,
    Player,
    Saga,
    Tribunal,
)
from .models import (
    secret_words as words_of,
)
from .references import KINDS, Fact, Ref, find

STORYGUIDE = "storyguide"
PLAYER = "player"
TABLE = "table"


@dataclass(frozen=True)
class Viewer:
    """Who is reading: STORYGUIDE, PLAYER (with the Player signed in) or
    TABLE (Player view: any player)."""

    kind: str
    player: Player | None = None
    #: Whether this copy is the host's (it keeps the saga): a storyguide
    #: joined from a Remote seat isn't, and is offered nothing in HOST_ONLY.
    hosts: bool = True

    @property
    def is_storyguide(self) -> bool:
        return self.kind == STORYGUIDE

    @property
    def storyguide_id(self) -> str:
        """Which storyguide sits here, as a record names its own
        (storyguide_of), whether reading as one or Playing: a
        Storyguide-role Player's id, HOST for the host's own window, ""
        for anyone else."""
        if self.player is not None:
            return self.player.id if self.player.role == STORYGUIDE else ""
        if self.hosts:
            return HOST
        # A storyguide's seat that doesn't say who: the records with no
        # storyguide are theirs to run, and no one else's.
        return UNNAMED if self.kind == STORYGUIDE else ""

    @property
    def label(self) -> str:
        """How a header names who is reading: "" for the storyguide."""
        if self.kind == TABLE:
            return "Player view"
        if self.player is not None and self.kind == PLAYER:
            return self.player.name
        return ""


STORYGUIDE_VIEWER = Viewer(STORYGUIDE)
TABLE_VIEWER = Viewer(TABLE)


def viewer_for(
    player: Player | None, *, player_view: bool = False, hosts: bool = True
) -> Viewer:
    """The viewer of a copy: the player signed in, else a storyguide (the
    host's own window, or a Storyguide-role Player). With `player_view`
    (Playing, with more than one storyguide) a storyguide reads as a
    player would: the host's own window as the table, a Storyguide-role
    Player as themselves. `hosts`: whether this copy is the host's, not
    one joined from a Remote seat."""
    if player is not None and player.role != STORYGUIDE:
        return Viewer(PLAYER, player, hosts)
    if player_view:
        if player is not None:
            return Viewer(PLAYER, player, hosts)
        return TABLE_VIEWER if hosts else Viewer(TABLE, None, False)
    if player is not None:
        return Viewer(STORYGUIDE, player, hosts)
    return STORYGUIDE_VIEWER if hosts else Viewer(STORYGUIDE, None, False)


# -- whose record it is --

#: A record's storyguide when the host runs it: never a Player's id, which
#: is a slug of their name (storage.slugify).
HOST = "@host"
#: A storyguide's seat that doesn't say which storyguide sits there.
UNNAMED = "@storyguide"


def storyguide_ids(saga: Saga) -> set[str]:
    """Who may run a record as storyguide: the host and each
    Storyguide-role Player."""
    return {HOST, *(p.id for p in saga.players if p.role == STORYGUIDE)}


def troupe_style(saga: Saga | None) -> bool:
    """Whether `saga` has a second storyguide (a Storyguide-role Player
    beside the host), so records may have their own storyguide and every
    storyguide switches between Playing and their storyguide role."""
    return saga is not None and any(p.role == STORYGUIDE for p in saga.players)


#: The records that can have their own storyguide (each holds Secrets).
ASSIGNABLE = (Character, Covenant, Neighbour, Creature, Tribunal)


def storyguide_of(record: Any, saga: Saga | None = None) -> str:
    """Who runs `record` as storyguide: "" for no one (any storyguide reads
    it), HOST, or a Storyguide-role Player's id. A laboratory or familiar
    is its character's; a record naming someone no longer a storyguide is
    no one's. `saga`: by default the one in use."""
    found = saga if saga is not None else _saga
    if found is None:
        return ""
    if isinstance(record, Laboratory):
        record = found.character(record.owner_id) if record.owner_id else None
    elif isinstance(record, Familiar):
        record = found.character(record.character_id)
    if not isinstance(record, ASSIGNABLE):
        return ""
    owner = record.storyguide_id
    return owner if owner in storyguide_ids(found) else ""


def runs(viewer: Viewer, record: Any = None, saga: Saga | None = None) -> bool:
    """Whether the storyguide sitting as `viewer` (reading as one or
    Playing) may change `record`: one of their own, or one with no
    storyguide (None: the saga itself). False for anyone else."""
    me = viewer.storyguide_id
    if not me:
        return False
    if record is None:
        return True
    return storyguide_of(record, saga) in ("", me)


def holds(viewer: Viewer, record: Any = None, saga: Saga | None = None) -> bool:
    """Whether `viewer`, reading as a storyguide, reads `record` whole:
    Secrets, Roll Tables, a threat's stages to come and all."""
    return viewer.is_storyguide and runs(viewer, record, saga)


def readable(viewer: Viewer, record: Any, saga: Saga | None = None) -> bool:
    """Whether `viewer` may read `record` at all: a storyguide's own (or
    no one's), else while the players know of it."""
    return holds(viewer, record, saga) or is_known(record)


#: others_run_any's answers, by saga and storyguide, while a page is drawn:
#: forgotten whenever another page is (on_page) or another reader (use).
_others: dict[tuple[int, str], bool] = {}


def others_run_any(viewer: Viewer, saga: Saga) -> bool:
    """Whether some record of `saga` is another storyguide's, so the
    storyguide `viewer` doesn't read the whole saga."""
    if not troupe_style(saga) and viewer.storyguide_id == HOST:
        return False
    key = (id(saga), viewer.storyguide_id)
    found = _others.get(key)
    if found is None:
        found = _others[key] = _others_run_any(viewer.storyguide_id, saga)
    return found


def _others_run_any(me: str, saga: Saga) -> bool:
    live = storyguide_ids(saga)
    return any(
        r.storyguide_id and r.storyguide_id != me and r.storyguide_id in live
        for kind in (
            saga.characters,
            saga.covenants,
            saga.neighbours,
            saga.creatures,
            saga.tribunals,
        )
        for r in kind
    )


def reads_everything(viewer: Viewer, saga: Saga) -> bool:
    """Whether `viewer` reads the whole of `saga`: a storyguide, and no
    record of it another storyguide's."""
    return viewer.is_storyguide and not others_run_any(viewer, saga)


def records_of(saga: Saga, storyguide_id: str) -> list[Any]:
    """The records `storyguide_id` runs, for a warning that names them."""
    return [
        r
        for kind in (
            saga.covenants,
            saga.characters,
            saga.neighbours,
            saga.creatures,
            saga.tribunals,
        )
        for r in kind
        if storyguide_id and r.storyguide_id == storyguide_id
    ]


def reads_private(
    viewer: Viewer, character: Character, saga: Saga | None = None
) -> bool:
    """Whether `viewer` reads `character`'s private notes and unshared
    goals: its storyguide (among several, only its own), its players (all
    of them, for a shared one) and its Steward; no one else."""
    if holds(viewer, character, saga):
        return True
    player = viewer.player
    if player is None or viewer.kind == TABLE:
        return False
    b = character.background
    return (
        player.id in b.player_ids
        or (b.everyone_plays and player.role == PLAYER)
        or (bool(b.steward_id) and b.steward_id == player.id)
    )


def free_records(saga: Saga, storyguide_id: str) -> list[Any]:
    """Leave `storyguide_id`'s records with no storyguide (they were
    deleted, or made a player again); the records freed."""
    found = records_of(saga, storyguide_id)
    for record in found:
        record.storyguide_id = ""
    _others.clear()
    return found


def assign(record: Any, storyguide_id: str) -> None:
    """Make `storyguide_id` ("": no one) `record`'s storyguide."""
    record.storyguide_id = storyguide_id
    _others.clear()


def storyguide_name(saga: Saga, storyguide_id: str) -> str:
    """How a page names a record's storyguide."""
    if not storyguide_id:
        return "(none)"
    if storyguide_id == HOST:
        return "The host"
    return next((p.name for p in saga.players if p.id == storyguide_id), "(none)")


# -- who is looking now --

_in_use: Viewer = STORYGUIDE_VIEWER
_saga: Saga | None = None


def use(viewer: Viewer, saga: Saga | None = None) -> None:
    """Set who is looking at `saga` in this copy of the app. Each copy
    (the storyguide's window, each player's browser) is its own process,
    so one viewer at a time is enough."""
    global _in_use, _saga
    _in_use, _saga = viewer, saga
    _others.clear()


def current() -> Viewer:
    """Who is looking in this copy of the app."""
    return _in_use


def seated_player() -> Player | None:
    """The Player seated in this copy, while they sit as a player (not a
    storyguide, not the table): whose a character they make is."""
    viewer = _in_use
    if viewer.kind != PLAYER or viewer.player is None:
        return None
    return viewer.player if viewer.player.role != STORYGUIDE else None


def in_use_saga() -> Saga | None:
    """The saga `use` was last given."""
    return _saga


def storyguide_reads(record: Any = None) -> bool:
    """Whether whoever is looking now reads `record` whole, as its
    storyguide (None: the saga's own pages)."""
    return holds(_in_use, record)


#: The record the page being drawn is of (None: the saga's own pages), so
#: a part of the page asks about it (`reads(part=...)`).
_page: Any = None


def on_page(record: Any) -> None:
    """Note the record the page being drawn is of, set by each front-end
    as it builds a page."""
    global _page
    _page = record
    _others.clear()


# -- what is storyguide-only --

#: The parts of a page only the storyguide reads, by their section or tab
#: id (the shape of actions.SECTION_VERBS's keys; a desktop chapter is
#: the help topic it opens). A part not listed is shown to everyone, so a
#: new section is public until it is added here; tests/test_viewing.py
#: fails if an id here names no section, tab or chapter.
STORYGUIDE_ONLY: frozenset[str] = frozenset(
    {
        # A record's Secrets (the tab is everyone's: for anyone else it
        # holds the Known section, the secrets revealed).
        "section-secrets",
        # A place's or lord's Roll Tables.
        "tab-nb-tables",
        "section-nb-tables",
        # Needs You, on the Seasons sheet.
        "section-attention",
        # Saga Management and Saga Settings (the saga page's chapters).
        "saga-management",
        "saga-settings",
        # The editing side of Saga Content: who plays and their
        # passcodes. The books in play, the catalogs, goods, House Rules,
        # cults and spells stay public (a player can't change them).
        "tab-content-players",
        "section-players",
        # The Armarium and the Custodia Mirabilium (stores.py): every book
        # and device, the unassigned ones the storyguide keeps for the
        # players to find among them.
        "section-armarium",
        "section-custodia",
    }
)

#: The parts only the host's own copy shows: who may join, and as what
#: (ADR 0014). A storyguide joined from a Remote seat reads all else.
HOST_ONLY: frozenset[str] = frozenset({"tab-content-players", "section-players"})
#: What only the host's own copy does: hosting (and with it Host for
#: Players: invites, approvals, seats, the log).
#: A downtime run is the host's too: it plays many seasons at once,
#: each kept as it goes.
HOST_ONLY_ACTIONS: frozenset[str] = frozenset(
    {"host_saga", "stop_hosting", "downtime_run"}
)

#: What changes every record of the saga at once. A Remote seat holds
#: another storyguide's records only as the players have them, so while
#: there are any, its storyguide leaves these to the host's computer,
#: which holds them whole (ADR 0015).
SEASON_WIDE: frozenset[str] = frozenset({"advance_season"})

#: What only the storyguide may do, so Player view leaves it off the
#: storyguide's own window too (a signed-in player is refused much more:
#: see the workspace's own list). Each is an actions.MORE_MENU action.
STORYGUIDE_ONLY_ACTIONS: frozenset[str] = frozenset(
    {
        "roll_table",
        "reveal",
        "conceal",
        "mark_unknown",
        "assign_storyguide",
        "reveal_secret",
        "conceal_secret",
        "split_secret",
        "hold_tribunal",
        "tribunal_ruling",
        "host_saga",
        "stop_hosting",
        "import_data",
        "export_pack",
        "edit_saga",
        "begin_story",
        "delay_threat",
        "grow_story",
        "take_up_tale",
        "take_up_story",
    }
)


#: What only the storyguide may do, whatever a player owns: making records,
#: the saga's calendar, reading files on the host's disk, writing out the
#: whole saga, and moving vis or spells between characters. A signed-in
#: player is refused these; Player view leaves off only
#: STORYGUIDE_ONLY_ACTIONS, which hide what the players must not read.
PLAYER_BARRED_ACTIONS: frozenset[str] = frozenset(
    {
        "new",
        "create_covenant",
        "create_tribunal",
        "create_neighbour",
        "create_creature",
        "roll_fair",
        "court_roll",
        "roll_table",
        "battle_event",
        "redeem_gratitude",
        "buy_manor",
        "assart",
        "winter_roll",
        "settle_inheritance",
        "conflict_battle_event",
        "battle_muster",
        "next_blow",
        "next_round",
        "add_combatant",
        "edit_combatant",
        "remove_combatant",
        "form_group",
        "break_group",
        "restart_fight",
        "fight_options",
        "group_morale",
        "rally_group",
        "next_siege_event",
        "siege_actions",
        "found_covenant",
        "begin_story",
        "delay_threat",
        "grow_story",
        "merge_doubles",
        "reveal",
        "conceal",
        "mark_unknown",
        "assign_storyguide",
        "player_view",
        "take_up_tale",
        "take_up_story",
        "create_laboratory",
        "create_familiar",
        "advance_season",
        "set_date",
        "undo_season",
        "downtime_run",
        "import_data",
        "give",
        "give_silver",
        "share_spell",
        "update_record",
        "export_saga",
        "export_cult",
        "export_pack",
        "host_saga",
        "stop_hosting",
        # The Byzantine customs that lay a curse on a sheet.
        "invoke_oath",
        "mothers_curse",
        # A hunt on a lord's or covenant's manor.
        "hunt_on_manor",
        "area_lore_on_manor",
        # A lord's marriages: ending one.
        "end_marriage",
    }
)

#: What a signed-in player may make wherever it is offered, whatever the
#: record on show: what they make is theirs (players.guard_changes lets a
#: player add a new character only while it names them alone).
PLAYER_MAKES_ACTIONS: frozenset[str] = frozenset({"create_character"})

#: What anyone signed in may do anywhere: move around, read, and export
#: (which only reads the saga).
LOOKING_ACTIONS: frozenset[str] = frozenset(
    {
        "filter",
        "toggle_section",
        "show_tab",
        "help",
        "step_out",
        "quit",
        "more",
        "export_record",
        "go_to",
        "find",
        # A character's changes since the last Session: it only reads.
        "what_changed",
        "cast_glance",
        "previously_on",
        # A calculator: it records nothing.
        "plan_journey",
        "craft_by_magic",
        # A calculator too (HoH:S): casting in a lacuna.
        "cast_in_lacuna",
        # Wizard's War's tunnel (Hermetic Projects): a calculator too.
        "open_tunnel",
    }
)


def may_read(viewer: Viewer, record: Any = None, part: str = "") -> bool:
    """Whether `viewer` may read `record` (None: something of the whole
    saga) and, on its page, the part `part` (a section, tab or chapter id;
    "": the page itself). The storyguide reads everything; anyone else a
    known record's parts not in STORYGUIDE_ONLY. A copy that isn't the
    host's never reads the HOST_ONLY parts."""
    if not viewer.hosts and part in HOST_ONLY:
        return False
    # A storyguide reads another storyguide's record as a player would
    # (ADR 0015).
    if holds(viewer, record):
        return True
    if part and part in STORYGUIDE_ONLY:
        return False
    return record is None or is_known(record)


def may_do(viewer: Viewer, action: str) -> bool:
    """Whether `viewer`'s copy offers `action` at all: the storyguide
    anything; the table (Player view) all but STORYGUIDE_ONLY_ACTIONS; a
    player signed in also not PLAYER_BARRED_ACTIONS. Whether a player may
    change the record on show is players.may_change. A copy that isn't
    the host's is never offered HOST_ONLY_ACTIONS."""
    if not viewer.hosts and action in HOST_ONLY_ACTIONS:
        return False
    if (
        action in SEASON_WIDE
        and not viewer.hosts
        and _saga is not None
        and others_run_any(viewer, _saga)
    ):
        return False
    if viewer.is_storyguide:
        return True
    if action in STORYGUIDE_ONLY_ACTIONS:
        return False
    return viewer.kind != PLAYER or action not in PLAYER_BARRED_ACTIONS


def is_looking(action: str) -> bool:
    """Whether `action` only moves around or reads, so anyone signed in may
    run it on any record."""
    return action in LOOKING_ACTIONS


def reads(record: Any = None, part: str = "") -> bool:
    """may_read for whoever is looking now; a part with no record named
    is of the page being drawn (on_page)."""
    if record is None and part:
        record = _page
    return may_read(_in_use, record, part)


def offers(action: str) -> bool:
    """may_do for whoever is looking now."""
    return may_do(_in_use, action)


# -- known to the players --

#: The kinds of record that can be unknown to the players.
REVEALABLE = (Character, Covenant, Neighbour, Creature)


def troupes_own(record: Any) -> bool:
    """Whether the troupe plays `record`, so it is always known: a player
    character or a troupe covenant."""
    if isinstance(record, Character):
        # As seasons.defaults.is_player_character, which this module sits
        # below.
        b = record.background
        # A Steward keeps it between Sessions (sessions.py), so their seat
        # must see it to plan its seasons.
        return bool(
            b.player.strip() or b.player_ids or b.everyone_plays or b.steward_id
        )
    if isinstance(record, Covenant):
        return record.played
    return False


def can_be_unknown(record: Any) -> bool:
    """Whether Reveal applies to `record`: a record of the world the
    troupe doesn't play (a neighbour, creature, sketch covenant or
    non-player character)."""
    return isinstance(record, REVEALABLE) and not troupes_own(record)


def is_known(record: Any) -> bool:
    """Whether the players know of `record`. Anything Reveal doesn't apply
    to is known."""
    return not can_be_unknown(record) or bool(getattr(record, "known", True))


def shown[R](
    records: Iterable[R], viewer: Viewer | None = None, *, keep: str | None = None
) -> list[R]:
    """The records of `records` the viewer (by default whoever is
    looking) may read, in order. `keep` is the id of a record to list
    anyway: the one a form already holds, so opening it never loses its
    value."""
    looking = viewer or _in_use
    if looking.is_storyguide and (_saga is None or reads_everything(looking, _saga)):
        return list(records)
    return [
        r
        for r in records
        if readable(looking, r) or (keep and getattr(r, "id", None) == keep)
    ]


def unknown_names(saga: Saga) -> set[str]:
    """The names of the records the players don't know of, for words that
    name a record without a Ref (a list's "at", a date's source)."""
    return {
        r.name
        for r in (*saga.characters, *saga.covenants, *saga.neighbours, *saga.creatures)
        if not is_known(r)
    }


def ref_known(saga: Saga, found: Ref) -> bool:
    """Whether the record `found` names is known (a record gone is)."""
    record = find(saga, found.kind, found.id)
    return record is None or is_known(record)


def ref_readable(found: Ref, viewer: Viewer | None = None) -> bool:
    """Whether the viewer (by default whoever is looking) may read the
    record `found` names, in the saga in use."""
    looking = viewer or _in_use
    if _saga is None:
        return True
    record = find(_saga, found.kind, found.id)
    return record is None or readable(looking, record, _saga)


def ref_held(saga: Saga, found: Ref, viewer: Viewer | None = None) -> bool:
    """Whether the viewer reads the record `found` names whole, as its
    storyguide (a record gone: as for the saga)."""
    looking = viewer or _in_use
    record = find(saga, found.kind, found.id)
    return holds(looking, record, saga)


def about_known(saga: Saga, about: Iterable[str], viewer: Viewer | None = None) -> bool:
    """Whether every record a line is about ("kind:id") is known (or, for
    a storyguide `viewer`, theirs to read)."""
    for each in about:
        kind, _, record_id = each.partition(":")
        record = find(saga, kind, record_id)
        if record is None:
            continue
        if viewer is not None and holds(viewer, record, saga):
            continue
        if not is_known(record):
            return False
    return True


def about(*records: Any) -> list[str]:
    """What a line the app writes is about: "kind:id" for each record
    Reveal applies to (the others are always known)."""
    return [
        f"{KINDS[type(r)]}:{r.id}"
        for r in records
        if type(r) in KINDS and can_be_unknown(r)
    ]


def diary_readable(
    saga: Saga, entry: CovenantDiaryEntry, viewer: Viewer | None = None
) -> bool:
    """Whether the viewer may read a covenant's Diary line: a line the
    app wrote about an unknown record (or a threat's chapter) is the
    storyguide's until it is revealed."""
    looking = viewer or _in_use
    if reads_everything(looking, saga):
        return True
    if entry.threat_id:
        threat = saga.neighbour(entry.threat_id)
        if threat is not None and not readable(looking, threat, saga):
            return False
    return about_known(saga, entry.about, looking)


def shows_entry(entry: CovenantDiaryEntry) -> bool:
    """diary_readable for whoever is looking now, in the saga in use."""
    return _saga is None or diary_readable(_saga, entry)


def shows_line(line: dict[str, Any]) -> bool:
    """line_readable for whoever is looking now, in the saga in use."""
    return _saga is None or line_readable(_saga, line)


def line_readable(
    saga: Saga, line: dict[str, Any], viewer: Viewer | None = None
) -> bool:
    """Whether the viewer may read a neighbour's Diary line (a dict; its
    "about" lists the records it is about)."""
    looking = viewer or _in_use
    if reads_everything(looking, saga):
        return True
    found = line.get("about") or []
    return about_known(saga, found if isinstance(found, list) else [], looking)


def secret_words(record: Any) -> str:
    """The record's Secrets, every one, as words the storyguide's Find
    looks in ("" for a record that keeps none)."""
    found = getattr(record, "secrets", None)
    return words_of(found) if isinstance(found, list) else ""


# -- facts that name records --

_TIDY = re.compile(r"(?:\s*[,;·]\s*){2,}")


def _without(value: str, name: str) -> str:
    """`value` with `name` taken out, and the separators it leaves tidied."""
    cut = value.replace(name, "")
    cut = _TIDY.sub(", ", cut)
    return cut.strip(" ,;·")


def scrub(fact: Fact, viewer: Viewer | None = None) -> Fact | None:
    """`fact` as the viewer may read it: each unknown record it names
    taken out, name and link; None when it names nothing else."""
    looking = viewer or _in_use
    if not fact.refs or (
        looking.is_storyguide and (_saga is None or reads_everything(looking, _saga))
    ):
        return fact
    hidden = [r for r in fact.refs if not ref_readable(r, looking)]
    if not hidden:
        return fact
    kept = tuple(r for r in fact.refs if r not in hidden)
    if not kept:
        return None
    value = fact.value
    for found in hidden:
        value = _without(value, found.name)
    return replace(fact, value=value, refs=kept)


def facts(found: Sequence[Fact], viewer: Viewer | None = None) -> list[Fact]:
    """`found` as the viewer may read them (see scrub)."""
    return [f for f in (scrub(fact, viewer) for fact in found) if f is not None]


# -- Player view, remembered per saga --

#: The settings key Player view is kept under: {saga id: True}.
PLAYER_VIEW = "player_view"


def player_view_on(saga_id: str) -> bool:
    """Whether this computer last left `saga_id` in Player view."""
    filed = settings.load_settings().get(PLAYER_VIEW)
    return isinstance(filed, dict) and filed.get(saga_id) is True


def set_player_view(saga_id: str, on: bool) -> None:
    """Remember Player view for `saga_id`, leaving every other saga's."""
    filed = settings.load_settings().get(PLAYER_VIEW)
    filed = dict(filed) if isinstance(filed, dict) else {}
    if on:
        filed[saga_id] = True
    else:
        filed.pop(saga_id, None)
    settings.update_settings(**{PLAYER_VIEW: filed})
