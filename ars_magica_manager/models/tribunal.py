"""A Tribunal: the record of a region's magi in council, its cases, its
Peripheral Code, its treasury and its diary, and the meeting being held.
Most of its sheet is worked out from the covenants that belong to it
(tribunals.py); only what belongs to the Tribunal itself is kept here."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypedDict

from .common import Change, known_fields, move_secrets
from .traits import new_instance_id

#: The Tribunal package every saga has: the Definitive Edition's rules,
#: with no regional customs.
CORE_PACKAGE = "core"

#: How often a Tribunal meets, in years, unless its package says otherwise.
MEETS_EVERY = 7

#: A case's kinds.
CASE_KINDS: tuple[str, ...] = ("charge", "motion", "appeal")

#: A case's status: still to be heard, decided at a meeting, or withdrawn.
CASE_OPEN = "open"
CASE_DECIDED = "decided"
CASE_WITHDRAWN = "withdrawn"
CASE_STATUSES: tuple[str, ...] = (CASE_OPEN, CASE_DECIDED, CASE_WITHDRAWN)

#: What a treasury entry is.
TREASURY_KINDS: tuple[str, ...] = ("vis", "silver", "loan", "fine")


@dataclass
class Case:
    """A charge, motion or appeal on the Tribunal's docket. Who brings it
    and who it is against are names (or covenant and character names as
    typed); the evidence is one short entry a line."""

    title: str
    kind: str = "charge"
    brought_by: str = ""
    against: str = ""
    charge: str = ""
    filed_year: int | None = None
    filed_season: str = ""
    #: Whether notice of it has been given (by the package's rule it is
    #: due a while before the meeting).
    notice_given: bool = False
    penalty: str = ""
    evidence: str = ""
    prosecutor: str = ""
    defender: str = ""
    status: str = CASE_OPEN
    outcome: str = ""
    #: When what the ruling settled for a term ends, to be debated again
    #: (None: no term); `term_docketed` once that new case is on the
    #: docket.
    term_ends_year: int | None = None
    term_ends_season: str = ""
    term_docketed: bool = False
    id: str = field(default_factory=new_instance_id, compare=False)


@dataclass
class Ruling:
    """A ruling of the Peripheral Code: the year it was made and what it
    says; one made at a meeting names its case."""

    title: str
    year: int | None = None
    says: str = ""
    case_id: str = ""
    id: str = field(default_factory=new_instance_id, compare=False)


@dataclass
class TreasuryEntry:
    """One line of the Tribunal's treasury: vis (pawns of an Art), silver
    (pounds), a loan out of it (to whom, how much, when due) or a fine owed
    to it (by whom, from which case, paid or not). Loans and unpaid fines
    are not yet in hand."""

    kind: str
    amount: float = 0
    art: str = ""
    who: str = ""
    due_year: int | None = None
    case_id: str = ""
    paid: bool = False
    note: str = ""
    id: str = field(default_factory=new_instance_id, compare=False)


class Meeting(TypedDict, total=False):
    """The meeting a Tribunal is holding (meeting.py), kept as a plain
    dict so a save holds it as it is. A step keeps what it decided under
    its own key; a package's steps keep theirs too (Hibernia's council
    and tithe, the Theban elections)."""

    year: int
    season: str
    place: str
    days: int
    #: The keys of the steps held.
    done: list[str]
    #: Each case's day, by case id.
    day_of: dict[str, int]
    #: Each covenant's roll call, by covenant id: "present" (magus ids),
    #: "unnamed", "absent", "proxies", "ruling".
    attendance: dict[str, dict[str, Any]]
    #: What the storyguide noted at each step, by step key.
    notes: dict[str, str]
    #: The Diary entry each step's minutes went into, by step key.
    minutes: dict[str, str]
    #: Each case's vote, debate and ruling, by case id.
    votes: dict[str, dict[str, Any]]
    debates: dict[str, dict[str, Any]]
    rulings: dict[str, dict[str, Any]]
    succession: dict[str, Any]
    lot: list[str]
    host: dict[str, Any]
    council: dict[str, Any]
    tithe: dict[str, Any]
    theban: dict[str, Any]
    #: The Rhine's introduction of new magi and conferral of sigils
    #: (rhine_meeting.py).
    rhine_rite: dict[str, Any]


@dataclass
class TribunalDiaryEntry:
    """A line of the Tribunal's Diary: the minutes of a meeting, a change
    the yearly step made, or a note typed in."""

    year: int
    season: str = ""
    title: str = ""
    details: str = ""
    #: What the entry changed, so deleting it can undo it (see the
    #: yearly step); empty for an entry typed in.
    changes: list[Change] = field(default_factory=list)
    #: The numbers a meeting's minutes set in the margin ("23 votes, 3
    #: by proxy").
    margin: str = ""
    id: str = field(default_factory=new_instance_id, compare=False)


@dataclass
class Tribunal:
    id: str
    name: str
    summary: str = ""
    #: Its history, era by era: a chapter of its own, apart from the
    #: summary of what it is like now.
    history: str = ""
    #: Its package (tribunal_packages.PACKAGES): the core rules, or a
    #: region's customs. Never mixed.
    package: str = CORE_PACKAGE
    meets_every: int = MEETS_EVERY
    next_year: int | None = None
    next_season: str = "Summer"
    meeting_place: str = ""
    #: The Praeco and the Presiding Quaesitor (characters, any detail).
    praeco_id: str | None = None
    quaesitor_id: str | None = None
    #: How many covenants and magi it really has: most are never written
    #: down (None: only those recorded).
    covenants_total: int | None = None
    magi_total: int | None = None
    #: Proxies each covenant holds for the next meeting, by covenant id:
    #: they change at every meeting, so they are kept here.
    proxies: dict[str, int] = field(default_factory=dict)
    cases: list[Case] = field(default_factory=list)
    #: The Peripheral Code in force.
    rulings: list[Ruling] = field(default_factory=list)
    treasury: list[TreasuryEntry] = field(default_factory=list)
    diary: list[TribunalDiaryEntry] = field(default_factory=list)
    #: Each package's own data, by package key: kept when the package is
    #: switched, so switching back finds it again.
    package_data: dict[str, dict[str, Any]] = field(default_factory=dict)
    #: The meeting being held (a dict the meeting module reads), or None.
    meeting: Meeting | None = None
    #: What only the storyguide should read: the record's Secrets
    #: chapter, hidden from players signed in to a hosted copy.
    secrets: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Tribunal:
        # Older saves kept secrets under a heading in the summary or history.
        d = move_secrets(known_fields(cls, data), "summary", "history")
        d["cases"] = [Case(**known_fields(Case, c)) for c in d.get("cases", [])]
        d["rulings"] = [Ruling(**known_fields(Ruling, r)) for r in d.get("rulings", [])]
        d["treasury"] = [
            TreasuryEntry(**known_fields(TreasuryEntry, t))
            for t in d.get("treasury", [])
        ]
        d["diary"] = [
            TribunalDiaryEntry(**known_fields(TribunalDiaryEntry, e))
            for e in d.get("diary", [])
        ]
        return cls(**d)
