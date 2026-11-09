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
else carries `known` (models), which Reveal ticks."""

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
    Neighbour,
    Player,
    Saga,
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
    def label(self) -> str:
        """How a header names who is reading: "" for the storyguide."""
        if self.kind == TABLE:
            return "Player view"
        if self.player is not None:
            return self.player.name
        return ""


STORYGUIDE_VIEWER = Viewer(STORYGUIDE)
TABLE_VIEWER = Viewer(TABLE)


def viewer_for(
    player: Player | None, *, player_view: bool = False, hosts: bool = True
) -> Viewer:
    """The viewer of a copy: the player signed in (a storyguide among them
    reads everything), else the storyguide's own window, which is the
    table while Player view is on. `hosts`: whether this copy is the
    host's, not one joined from a Remote seat."""
    if player is not None and player.role != STORYGUIDE:
        return Viewer(PLAYER, player, hosts)
    if player_view:
        return TABLE_VIEWER
    return STORYGUIDE_VIEWER if hosts else Viewer(STORYGUIDE, None, False)


# -- who is looking now --

_in_use: Viewer = STORYGUIDE_VIEWER
_saga: Saga | None = None


def use(viewer: Viewer, saga: Saga | None = None) -> None:
    """Set who is looking at `saga` in this copy of the app. Each copy
    (the storyguide's window, each player's browser) is its own process,
    so one viewer at a time is enough."""
    global _in_use, _saga
    _in_use, _saga = viewer, saga


def current() -> Viewer:
    """Who is looking in this copy of the app."""
    return _in_use


def in_use_saga() -> Saga | None:
    """The saga `use` was last given."""
    return _saga


def storyguide_reads() -> bool:
    """Whether whoever is looking now reads everything."""
    return _in_use.is_storyguide


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
        # The editing side of Rules and Content: who plays and their
        # passcodes. The books in play, the catalogs, goods, House Rules,
        # cults and spells stay public (a player can't change them).
        "tab-content-players",
        "section-players",
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

#: What only the storyguide may do, so Player view leaves it off the
#: storyguide's own window too (a signed-in player is refused much more:
#: see the workspace's own list). Each is an actions.MORE_MENU action.
STORYGUIDE_ONLY_ACTIONS: frozenset[str] = frozenset(
    {
        "roll_table",
        "reveal",
        "conceal",
        "mark_unknown",
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
        "player_view",
        "take_up_tale",
        "take_up_story",
        "create_character",
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
    if viewer.is_storyguide:
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
    """may_read for whoever is looking now."""
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
    if looking.is_storyguide:
        return list(records)
    return [
        r for r in records if is_known(r) or (keep and getattr(r, "id", None) == keep)
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
    if looking.is_storyguide or _saga is None:
        return True
    return ref_known(_saga, found)


def about_known(saga: Saga, about: Iterable[str]) -> bool:
    """Whether every record a line is about ("kind:id") is known."""
    for each in about:
        kind, _, record_id = each.partition(":")
        record = find(saga, kind, record_id)
        if record is not None and not is_known(record):
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
    if looking.is_storyguide:
        return True
    if entry.threat_id:
        threat = saga.neighbour(entry.threat_id)
        if threat is not None and not is_known(threat):
            return False
    return about_known(saga, entry.about)


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
    if looking.is_storyguide:
        return True
    found = line.get("about") or []
    return about_known(saga, found if isinstance(found, list) else [])


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
    if looking.is_storyguide or not fact.refs:
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
