"""Tribunal packages: the customs a Tribunal keeps beyond the core rules,
each from its own sourcebook and never mixed. A package supplies the book
it needs, how long before a meeting notice of a case is due, the extra
columns it adds to the roster and the extra lists (tabs) it adds to the
sheet, each with its own data and forms.

Pattern: Strategy, as a registry (PACKAGES), the way rules/activities.py
registers the seasonal activities. The sheet asks the Tribunal's package
what to add; a package's data lives in Tribunal.package_data under its
key, so switching package hides the old package's data and switching
back finds it again. Nothing is deleted.

Each package is a module of this package that registers itself."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .. import sourcebooks
from ..commands import Command, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..models import CORE_PACKAGE, Character, Covenant, Meeting, Saga, Tribunal


@dataclass(frozen=True)
class RosterColumn:
    """A column a package adds to the roster: its title, a covenant's
    entry in it, and how wide it may be on a padded line. A column the
    storyguide enters has the field the roster's Edit shows for it, and
    how to keep what is entered."""

    title: str
    value: Callable[[Saga, Tribunal, Covenant], str]
    cap: int = 16
    field: Callable[[Saga, Tribunal, Covenant], DialogField] | None = None
    save: Callable[[Tribunal, Covenant, Any], None] | None = None


@dataclass(frozen=True)
class PackageVerb:
    """A More command a package's list offers (actions.MORE_MENU names
    it): the action, its label, and the first step it runs on the
    chosen row."""

    action: str
    label: str
    build: Callable[[Saga, Tribunal, int], Command]


@dataclass(frozen=True)
class LedgerCard:
    """A row of a package list as the desktop rules it off on the page: a
    mark in the margin, its heading, an italic line beside it, a badge
    (words and a palette key: "text-success"), its words and a note
    (markup)."""

    title: str
    meta: str = ""
    badge: tuple[str, str] | None = None
    body: str = ""
    note: str = ""
    rubric: str = "§"


@dataclass(frozen=True)
class PackageList:
    """A list a package adds to the sheet: its section's id and title, its
    rows and its Add, Edit and Delete, and its More commands. `info`, if
    given, is a chosen row's details (markup) for the tab's details panel
    and the desktop's inspector; `cards`, the rows as the desktop rules
    them off, in the grid's order (None: a table)."""

    section_id: str
    section_title: Callable[[Saga, Tribunal], str]
    grid: Callable[[Saga, Tribunal], Grid]
    ops: Callable[[Saga, Tribunal], SectionOps]
    more: tuple[PackageVerb, ...] = ()
    info: Callable[[Saga, Tribunal, int], str] | None = None
    cards: Callable[[Saga, Tribunal], list[LedgerCard]] | None = None


@dataclass(frozen=True)
class PackageText:
    """A section of words a package's tab opens with, before its lists:
    its id and title, its facts (label and value), what it says (markup)
    and its More commands (on the desktop, its own buttons)."""

    section_id: str
    title: str
    facts: Callable[[Saga, Tribunal], list[tuple[str, str]]]
    text: Callable[[Saga, Tribunal], str]
    more: tuple[PackageVerb, ...] = ()


@dataclass(frozen=True)
class PackageTab:
    """A tab (a chapter, on the desktop) a package adds to the sheet,
    holding its lists, after a section of words if it has one. With a
    `panel_id`, the tab docks a details panel under them that shows the
    chosen row of a list with `info` (`panel_empty` before one is
    chosen)."""

    title: str
    tab_id: str
    lists: tuple[PackageList, ...]
    text: PackageText | None = None
    panel_id: str = ""
    panel_empty: str = ""
    #: The desktop chapter's icon (an artwork concept).
    icon: str = "tribunal"


@dataclass(frozen=True)
class Envoy:
    """One who votes in the hall without a covenant (Hibernia's
    ambassadors): an id unlike any covenant's, a name, and what they
    speak for."""

    id: str
    name: str
    speaks_for: str = ""


@dataclass(frozen=True)
class TribunalPackage:
    """One Tribunal's customs."""

    key: str
    #: How the package is named: the region ("Rhine"), or "Core rules".
    name: str
    #: What its customs are, in a word or two ("Gilds"); "" for the core.
    customs: str = ""
    #: The sourcebook it needs in play (sourcebooks.SOURCEBOOKS); "" for
    #: the core rules.
    book: str = ""
    #: How many seasons before the meeting notice of a case is due.
    notice_seasons: int = 1
    #: That, in words, for the docket ("a season").
    notice_words: str = "a season"
    columns: tuple[RosterColumn, ...] = ()
    tabs: tuple[PackageTab, ...] = ()
    #: The troupe's votes, as its customs count them ("2 tokens"); None
    #: counts a vote for each magus and proxy.
    your_votes: Callable[[Saga, Tribunal], str] | None = None
    #: The steps it adds to holding a meeting ("elections"), by name.
    meeting_steps: tuple[str, ...] = ()
    #: How many days its meetings last (None: the core's
    #: meeting.DEFAULT_DAYS); Hibernia's seven (The Contested Isle p. 32).
    meeting_days: int | None = None
    #: A sentence on what the package adds, for the form and help.
    about: str = ""
    #: The fields it adds to a covenant's own forms (its gilds), for a
    #: covenant of this Tribunal or about to join it (None: a new one), and
    #: how to keep what they say for the covenant with that id.
    covenant_fields: (
        Callable[[Saga, Tribunal, Covenant | None], list[DialogField]] | None
    ) = None
    save_covenant: Callable[[Tribunal, str, dict[str, Any]], None] | None = None
    #: What its books call a covenant, the place where magi live
    #: ("oppidum"), and more than one; its screens say so.
    place: str = "covenant"
    places: str = "covenants"
    #: Lines a magus of one of its covenants shows on their sheet, each a
    #: label and its value (Transylvania's privilege).
    magus_facts: Callable[[Saga, Tribunal, Character], list[tuple[str, str]]] | None = (
        None
    )
    #: What a covenant must show at a meeting for its votes to count
    #: (Hibernia's "cathach"); "" when its customs ask nothing.
    credential: str = ""
    #: Why a covenant can't show it now ("" when it can), which the
    #: meeting's Attendance takes as its default.
    lacks_credential: Callable[[Saga, Tribunal, Covenant], str] | None = None
    #: Why its customs refuse one of its covenants swearing to another as
    #: vassal ("" allows it).
    no_vassals: str = ""
    #: Those who vote at the meeting beside the covenants, a vote each
    #: (Hibernia's confirmed ambassadors).
    envoys: Callable[[Saga, Tribunal, Meeting], list[Envoy]] | None = None
    #: A meeting that would fall in a Grand Tribunal's year is held a year
    #: earlier (the Rhine's of 1227, Guardians of the Forests p. 143).
    skips_grand_tribunal: bool = False
    #: Whether a quorum needs a Quaesitor present (Thebes has no
    #: Presiding Quaesitor, The Sundered Eagle p. 25).
    quorum_needs_quaesitor: bool = True
    #: Whether Redcaps present vote (in Thebes "by tradition" they don't,
    #: The Sundered Eagle p. 26), and whether the Praeco votes (the archon
    #: announces the result but votes as any magus present, p. 32).
    redcaps_vote: bool = True
    praeco_votes: bool = False
    #: Why its customs refuse a magus an office of the Tribunal (the
    #: office's name, "Praeco"), "" when they allow it (Transylvania's
    #: privileges).
    office_problem: Callable[[Saga, Tribunal, str, str], str] | None = None
    #: Whether a magus present casts no vote of his own (the Rhine's
    #: Tremere, whose sigils their exarchs cast).
    casts_no_vote: Callable[[Saga, Tribunal, Character], bool] | None = None
    #: A sum in Mythic pounds told in its region's own coins, which the
    #: treasury's balance shows beside the pounds (Thebes's hyperpyra).
    coins: Callable[[float], str] | None = None
    #: The kinds of treasury entry its customs add to the core's, which
    #: the treasury's Add offers (Transylvania's levies and promissory
    #: notes, treasury.LEVY and treasury.NOTE).
    treasury_kinds: tuple[str, ...] = ()

    @property
    def lists(self) -> tuple[PackageList, ...]:
        """Every list its tabs hold."""
        return tuple(entry for tab in self.tabs for entry in tab.lists)


CORE = TribunalPackage(
    CORE_PACKAGE,
    "Core rules",
    about="The Definitive Edition's Tribunal, with no regional customs.",
)

#: Every package, by key; the core first.
PACKAGES: dict[str, TribunalPackage] = {CORE.key: CORE}


def register(package: TribunalPackage) -> None:
    """Add `package` to the registry (each customs module calls this)."""
    PACKAGES[package.key] = package


def of(tribunal: Tribunal) -> TribunalPackage:
    """The Tribunal's package; the core rules for one no longer known."""
    return PACKAGES.get(tribunal.package, CORE)


def label(package: TribunalPackage) -> str:
    """ "Rhine: Gilds", or "Core rules"."""
    return f"{package.name}: {package.customs}" if package.customs else package.name


def offered(saga: Saga, current: str | None = None) -> list[TribunalPackage]:
    """The packages a Tribunal of `saga` may follow: the core, and each
    whose book is in play (and the one it follows now, whatever its
    book)."""
    books = sourcebooks.saga_books(saga)
    return [
        p
        for p in PACKAGES.values()
        if p.key == current or not p.book or sourcebooks.in_play(p.book, books)
    ]


def place_word(saga: Saga, covenant: Covenant | None, plural: bool = False) -> str:
    """What the covenant's Tribunal calls such a place ("covenant", or
    "oppidum" in Transylvania), in lower case."""
    tribunal = saga.tribunal(covenant.tribunal_id) if covenant is not None else None
    package = of(tribunal) if tribunal is not None else CORE
    return package.places if plural else package.place


def magus_facts(saga: Saga, character: Character) -> list[tuple[str, str]]:
    """What the magus's Tribunal's customs add to their sheet."""
    covenant = saga.covenant(character.covenant_id)
    tribunal = saga.tribunal(covenant.tribunal_id) if covenant is not None else None
    if tribunal is None or character.type != "magus":
        return []
    package = of(tribunal)
    if package.magus_facts is None:
        return []
    return package.magus_facts(saga, tribunal, character)


def office_problem(
    saga: Saga, tribunal: Tribunal, character_id: str, office: str
) -> str:
    """Why the Tribunal's customs refuse the magus `office` ("": they
    allow it, or say nothing)."""
    package = of(tribunal)
    if package.office_problem is None or not character_id:
        return ""
    return package.office_problem(saga, tribunal, character_id, office)


def envoys(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> list[Envoy]:
    """Who votes at `meeting` beside the covenants, as its customs say."""
    package = of(tribunal)
    return package.envoys(saga, tribunal, meeting) if package.envoys else []


def lacks_credential(saga: Saga, tribunal: Tribunal, covenant: Covenant) -> str:
    """Why `covenant` can't show what its Tribunal's customs ask of it
    ("its cathach is held by Vigil"); "" when it can, or nothing is
    asked."""
    package = of(tribunal)
    if not package.credential or package.lacks_credential is None:
        return ""
    return package.lacks_credential(saga, tribunal, covenant)


def package_verb(tribunal: Tribunal, action: str) -> PackageVerb | None:
    """The More command `action` of one of the Tribunal's package lists,
    or of a tab's section of words."""
    package = of(tribunal)
    texts = tuple(tab.text for tab in package.tabs if tab.text is not None)
    for entry in (*package.lists, *texts):
        for verb in entry.more:
            if verb.action == action:
                return verb
    return None


def data(tribunal: Tribunal, key: str) -> dict[str, Any]:
    """The package `key`'s own data on `tribunal`, made empty if it has
    none yet."""
    return tribunal.package_data.setdefault(key, {})


def entries(tribunal: Tribunal, key: str, name: str) -> list[dict[str, Any]]:
    """The list `name` in package `key`'s data, made empty if missing."""
    found = data(tribunal, key).setdefault(name, [])
    if not isinstance(found, list):
        raise ValueError(f"The Tribunal's {name} should be a list, not {found!r}.")
    return found


# The packages register themselves as they are imported.
from . import (  # noqa: F401
    hibernia,
    levant,
    normandy,
    provence,
    rhine,
    theban,
    transylvania,
)
