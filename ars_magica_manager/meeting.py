"""Holding a Tribunal: the meeting being held, kept on its Tribunal
(Tribunal.meeting) and saved after every step, so leaving it and holding
it again later resumes at the step in hand.

The steps run in a fixed order (Template Method: `Step` is the template,
each kind of step fills in its form, what it works out and its `guide`,
what the app works out at it and what each entry changes): the roll call
(who is present, and the proxies), the Opening, each case and motion on
the day it is heard (its hearing, then its vote, unless it was settled
at the private hearing), the package's own steps (the Theban elections),
Rulings and fines, Treasury and vis, and the Closing, which writes the
meeting into the Tribunal's Diary and ends it. A package can add a step,
never reorder the rest. Holding a step opens the next (commands.Then).

The rules are the Definitive Edition's (Tribunals: a quorum of twelve
magi in person from four covenants and a Quaesitor; the Praeco and the
Presiding Quaesitor do not vote, the Praeco breaking ties), with HoH:
True Lineages for the procedure (Tribunal Procedures: each case has a
prosecution and a defence, an absent accused is defended by a Guernicus
advocate, a case may be settled at the private hearing) and HoH:
Societates for the debate (a motion's proposer debates the Tribunal).

The record is a plain dict, so a save holds it as it is:
{"year", "season", "place", "days", "done": [step keys held],
"day_of": {case id: day}, "attendance": {covenant id: {"present": [magus
ids], "unnamed", "absent", "proxies", "ruling"}}, "notes": {step key:
words}}; an older save's attendance has only the count absent."""

from __future__ import annotations

import itertools
import random
from collections.abc import Callable, Iterator
from dataclasses import dataclass, replace
from typing import Any

from . import acta, ruling_templates, tribunal_packages, tribunals, world
from .arts import ARTS
from .commands import Command, Confirm, Form, Refuse, SectionOps, Then
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import (
    CASE_DECIDED,
    Attitude,
    Case,
    Character,
    Covenant,
    Meeting,
    Reason,
    Ruling,
    Saga,
    TreasuryEntry,
    Tribunal,
    TribunalDiaryEntry,
)
from .references import Fact
from .rules import debate
from .rules.apprentice_seasons import gifted
from .sections import ATTENDANCE_SECTION, BUSINESS_SECTION, VOTE_SECTION
from .sheets import tribunal as tribunal_sheet
from .tribunal_packages import Envoy

#: How many days a meeting lasts unless the storyguide says otherwise.
DEFAULT_DAYS = 3

#: What the Presiding Quaesitor rules on a covenant's proxies.
ALLOWED = "Allowed"
SET_ASIDE = "Set aside"
RULINGS = (ALLOWED, SET_ASIDE)

_ORDINALS = (
    "First",
    "Second",
    "Third",
    "Fourth",
    "Fifth",
    "Sixth",
    "Seventh",
    "Eighth",
    "Ninth",
    "Tenth",
)


def day_name(day: int) -> str:
    """ "The Second Day"."""
    if 1 <= day <= len(_ORDINALS):
        return f"The {_ORDINALS[day - 1]} Day"
    return f"Day {day}"


def _begin(saga: Saga, tribunal: Tribunal) -> Meeting:
    """A new meeting record: when the Tribunal is due to meet (or now),
    where, and its cases spread over the days but the last, as many as
    its customs give (meeting_days), else DEFAULT_DAYS."""
    length = tribunal_packages.of(tribunal).meeting_days or DEFAULT_DAYS
    meeting: Meeting = {
        "year": tribunal.next_year
        if tribunal.next_year is not None
        else saga.current_year,
        "season": tribunal.next_season or saga.current_season,
        "place": tribunal.meeting_place.strip(),
        "days": length,
        "done": [],
        "day_of": {},
        "attendance": {},
        "notes": {},
    }
    meeting["day_of"] = _spread(tribunal_sheet.open_cases(tribunal), length)
    return meeting


def _spread(cases: list[Case], days: int) -> dict[str, int]:
    """Each case's day: spread in docket order over every day but the
    last, which is kept for the rulings and the closing."""
    open_days = max(1, days - 1)
    count = max(1, len(cases))
    return {c.id: 1 + i * open_days // count for i, c in enumerate(cases)}


def days(meeting: Meeting) -> int:
    return max(1, int(meeting.get("days") or DEFAULT_DAYS))


def day_of(meeting: Meeting, case: Case) -> int:
    """The day `case` is heard: as the Opening set it, else the first."""
    day = meeting.get("day_of", {}).get(case.id, 1)
    return max(1, min(days(meeting), int(day)))


# -- attendance --


def _attendance(meeting: Meeting, covenant: Covenant) -> dict[str, Any]:
    return meeting.get("attendance", {}).get(covenant.id, {})


def named_present(saga: Saga, meeting: Meeting, covenant: Covenant) -> list[Character]:
    """`covenant`'s named magi answering the roll: those ticked present,
    or (before the roll call, or in an older save that kept only a count)
    all of them."""
    magi = world.covenant_magi(saga, covenant)
    entry = _attendance(meeting, covenant)
    if "present" not in entry:
        return magi
    ticked = set(entry["present"])
    return [m for m in magi if m.id in ticked]


def in_person(saga: Saga, meeting: Meeting, covenant: Covenant) -> int:
    """How many of `covenant`'s magi, named or not, are in the hall."""
    entry = _attendance(meeting, covenant)
    if "present" in entry:
        unnamed = min(int(entry.get("unnamed") or 0), covenant.unnamed_magi)
        return len(named_present(saga, meeting, covenant)) + unnamed
    return max(0, world.votes(saga, covenant) - int(entry.get("absent") or 0))


def absent(saga: Saga, meeting: Meeting, covenant: Covenant) -> int:
    return world.votes(saga, covenant) - in_person(saga, meeting, covenant)


def officers(tribunal: Tribunal) -> set[str]:
    """The Praeco and the Presiding Quaesitor: in the hall, neither votes
    (the Praeco only breaks a tie), unless the Tribunal's customs let the
    Praeco vote."""
    praeco = None if tribunal_packages.of(tribunal).praeco_votes else tribunal.praeco_id
    return {i for i in (praeco, tribunal.quaesitor_id) if i}


def _silent(saga: Saga, tribunal: Tribunal, magus: Character) -> bool:
    """Whether a magus present casts no vote: an officer; an unGifted
    Redcap, at every Tribunal (DE p. 15), where a Gifted one votes; or any
    Redcap where the customs say Redcaps don't vote. A Redcap carrying a
    magus's sigil still casts that vote, as his covenant's proxy."""
    if magus.id in officers(tribunal):
        return True
    package = tribunal_packages.of(tribunal)
    if package.casts_no_vote is not None and package.casts_no_vote(
        saga, tribunal, magus
    ):
        return True
    if magus.hermetic.house != REDCAP_HOUSE:
        return False
    return not tribunal_packages.of(tribunal).redcaps_vote or not gifted(magus)


def magi_present(
    saga: Saga, tribunal: Tribunal, meeting: Meeting
) -> list[tuple[Character, Covenant]]:
    """Every named magus in the hall, with their covenant, in the order of
    the roll."""
    return [
        (m, c)
        for c in tribunals.covenants_of(saga, tribunal)
        for m in named_present(saga, meeting, c)
    ]


#: The quorum: magi in person, from covenants, and a Quaesitor (DE,
#: Tribunals).
QUORUM_MAGI, QUORUM_COVENANTS = 12, 4
REDCAP_HOUSE = "house_mercere"


def quorum(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> str:
    """ "13 magi from 5 covenants, and a Quaesitor: quorate", or what it
    lacks."""
    counts = [
        in_person(saga, meeting, c) for c in tribunals.covenants_of(saga, tribunal)
    ]
    magi, covenants = sum(counts), sum(1 for n in counts if n)
    quaesitor = saga.character(tribunal.quaesitor_id)
    if quaesitor is not None and quaesitor.covenant_id:
        home = saga.covenant(quaesitor.covenant_id)
        if (
            home is not None
            and home in tribunals.covenants_of(saga, tribunal)
            and quaesitor not in named_present(saga, meeting, home)
        ):
            quaesitor = None
    words = (
        f"{magi} {'magus' if magi == 1 else 'magi'} from {covenants} "
        f"covenant{'' if covenants == 1 else 's'}"
    )
    if quaesitor is not None:
        words += ", and a Quaesitor"
    elif tribunal_packages.of(tribunal).quorum_needs_quaesitor:
        words += ", and no Quaesitor"
    lacking = []
    if magi < QUORUM_MAGI:
        lacking.append(f"{QUORUM_MAGI} magi")
    if covenants < QUORUM_COVENANTS:
        lacking.append(f"{QUORUM_COVENANTS} covenants")
    needs_quaesitor = tribunal_packages.of(tribunal).quorum_needs_quaesitor
    if quaesitor is None and needs_quaesitor:
        lacking.append("a Quaesitor")
    if lacking:
        return f"{words}: not quorate (it needs {' and '.join(lacking)})"
    return f"{words}: quorate"


def carried(tribunal: Tribunal, meeting: Meeting, covenant: Covenant) -> int:
    """The proxies `covenant` carries into the hall: as attendance
    recorded them, else as the Tribunal's roster holds them."""
    entry = _attendance(meeting, covenant)
    if "proxies" in entry:
        return int(entry.get("proxies") or 0)
    return tribunal_sheet.proxies(tribunal, covenant)


def ruling(meeting: Meeting, covenant: Covenant) -> str:
    return _attendance(meeting, covenant).get("ruling") or ALLOWED


def shows(saga: Saga, tribunal: Tribunal, meeting: Meeting, covenant: Covenant) -> bool:
    """Whether `covenant` shows what its Tribunal's customs ask of it to
    be represented (Hibernia's cathach): as attendance recorded it, else
    unless the customs say it can't."""
    if not tribunal_packages.of(tribunal).credential:
        return True
    entry = _attendance(meeting, covenant)
    if "shows" in entry:
        return bool(entry["shows"])
    return not tribunal_packages.lacks_credential(saga, tribunal, covenant)


def present(
    saga: Saga, tribunal: Tribunal, meeting: Meeting, covenant: Covenant
) -> tuple[int, int]:
    """`covenant`'s votes in the hall: its magi present (but the Praeco
    and the Presiding Quaesitor, who don't vote), and the proxies it
    carries that the Quaesitor allowed; none for a covenant that doesn't
    show what its Tribunal's customs ask (its cathach)."""
    if not shows(saga, tribunal, meeting, covenant):
        return 0, 0
    magi = in_person(saga, meeting, covenant) - sum(
        _silent(saga, tribunal, m) for m in named_present(saga, meeting, covenant)
    )
    proxies = carried(tribunal, meeting, covenant)
    allowed = proxies if ruling(meeting, covenant) == ALLOWED else 0
    return magi, allowed


def voters(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> list[Covenant | Envoy]:
    """Who the Praeco calls, in order: the covenants of the roll, then
    those its customs let vote beside them (Hibernia's ambassadors)."""
    return [
        *tribunals.covenants_of(saga, tribunal),
        *tribunal_packages.envoys(saga, tribunal, meeting),
    ]


def votes_of(
    saga: Saga, tribunal: Tribunal, meeting: Meeting, voter: Covenant | Envoy
) -> int:
    """A voter's votes in the hall: a covenant's magi present and allowed
    proxies, an envoy's one."""
    if isinstance(voter, Envoy):
        return 1
    return sum(present(saga, tribunal, meeting, voter))


def hall(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> tuple[int, int]:
    """Every vote in the hall, and how many of them are proxies."""
    magi = proxies = 0
    for covenant in tribunals.covenants_of(saga, tribunal):
        m, p = present(saga, tribunal, meeting, covenant)
        magi += m
        proxies += p
    magi += len(tribunal_packages.envoys(saga, tribunal, meeting))
    return magi + proxies, proxies


def present_text(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> str:
    """ "23 votes, 3 by proxy"."""
    votes, proxies = hall(saga, tribunal, meeting)
    words = f"{votes} vote{'' if votes == 1 else 's'}"
    return f"{words}, {proxies} by proxy" if proxies else words


# -- the debate and the vote --

FOR = "For"
AGAINST = "Against"
UNDECIDED = "Undecided"
LEANINGS = (FOR, AGAINST, UNDECIDED)


def rng() -> random.Random:
    """The dice a debate is rolled with (tests replace it)."""
    return random.Random()


def _party(covenant: Covenant | Envoy, words: str) -> bool:
    name = covenant.name.strip().casefold()
    return bool(name) and name in words.casefold()


def leaning_why(saga: Saga, case: Case, covenant: Covenant | Envoy) -> tuple[str, str]:
    """How a covenant leans on `case` before the debate, and why: a party
    votes its own side; any other leans by its attitude toward a troupe
    covenant that is a party (Warm or better with it, Wary or worse
    against it), and is otherwise undecided. An envoy has no attitudes:
    undecided unless a party."""
    if _party(covenant, case.brought_by):
        return FOR, "it brings the case"
    if _party(covenant, case.against):
        return AGAINST, "the case is against it"
    if isinstance(covenant, Envoy):
        return UNDECIDED, "an ambassador sides with no one unless a party"
    for player in world.player_covenants(saga):
        if player is covenant:
            continue
        side = FOR if _party(player, case.brought_by) else None
        if side is None and _party(player, case.against):
            side = AGAINST
        if side is None:
            continue
        score = world.attitude_score(world.attitude_toward(covenant, player.id))
        role = "brings it" if side == FOR else "defends"
        feeling = f"{world.attitude_word(score)} ({world.signed(score)})"
        if score > 0:
            return side, f"{feeling} toward {player.name}, which {role}"
        if score < 0:
            other = AGAINST if side == FOR else FOR
            return other, f"{feeling} toward {player.name}, which {role}"
    return UNDECIDED, "no settled view of either party"


def default_leaning(saga: Saga, case: Case, covenant: Covenant | Envoy) -> str:
    return leaning_why(saga, case, covenant)[0]


def leanings(
    saga: Saga, tribunal: Tribunal, meeting: Meeting, case: Case
) -> dict[str, str]:
    """Each voter's leaning on `case`, by id: as the vote was held, else
    the defaults."""
    kept = meeting.get("votes", {}).get(case.id, {}).get("leanings", {})
    return {
        c.id: kept.get(c.id) or default_leaning(saga, case, c)
        for c in voters(saga, tribunal, meeting)
    }


def debate_of(meeting: Meeting, case: Case) -> dict[str, Any] | None:
    return meeting.get("debates", {}).get(case.id)


def settled(meeting: Meeting, case: Case) -> bool:
    """Whether `case` was settled at the private hearing: it is neither
    debated nor voted on."""
    return bool((debate_of(meeting, case) or {}).get("settled"))


def strength(meeting: Meeting, case: Case) -> tuple[str | None, int]:
    """Who won the debate (FOR the prosecution or proposer, AGAINST the
    defence, None for none yet or a tie) and its Argument Strength,
    after a proposal's penalty."""
    held_debate = debate_of(meeting, case)
    if held_debate is None or held_debate.get("settled"):
        return None, 0
    lost = held_debate.get("lost", [0, 0])
    if lost[0] == lost[1]:
        return None, 0
    side = FOR if lost[0] < lost[1] else AGAINST
    margin = abs(lost[0] - lost[1])
    if case.kind == "motion" and side == FOR:
        margin += debate.PROPOSALS.get(held_debate.get("proposal", ""), 0)
    return (side, margin) if margin > 0 else (None, 0)


@dataclass(frozen=True)
class Called:
    """One covenant's (or envoy's) votes as the Praeco calls it: how many
    for, against and abstaining, how many of them the debate swayed, and
    the tally of the hall so far."""

    covenant: Covenant | Envoy
    votes: int
    yes: int
    no: int
    abstain: int
    swayed: int
    tally: tuple[int, int, int]


def call_the_vote(
    saga: Saga,
    tribunal: Tribunal,
    meeting: Meeting,
    case: Case,
    leaning: dict[str, str] | None = None,
) -> Iterator[Called]:
    """The vote on `case`, covenant by covenant in the order of the roll
    (Iterator): each votes as it leans, with the votes the debate's victor
    won from the undecided and (from a Triumphant Victory) from its
    opponents taken from the first covenants called."""
    lean = leaning if leaning is not None else leanings(saga, tribunal, meeting, case)
    members = voters(saga, tribunal, meeting)
    hall_votes = {c.id: votes_of(saga, tribunal, meeting, c) for c in members}
    side, margin = strength(meeting, case)
    hostile_side = AGAINST if side == FOR else FOR
    neutral = sum(
        v for cid, v in hall_votes.items() if lean.get(cid, UNDECIDED) == UNDECIDED
    )
    hostile = sum(
        v for cid, v in hall_votes.items() if lean.get(cid, UNDECIDED) == hostile_side
    )
    from_neutral, from_hostile = (
        debate.swayed(margin, neutral, hostile) if side else (0, 0)
    )
    tally = [0, 0, 0]
    for covenant in members:
        votes = hall_votes[covenant.id]
        leans = lean.get(covenant.id, UNDECIDED)
        counts = {FOR: 0, AGAINST: 0, UNDECIDED: 0}
        counts[leans] = votes
        moved = 0
        if side is not None and leans == UNDECIDED and from_neutral:
            moved = min(votes, from_neutral)
            from_neutral -= moved
        elif side is not None and leans == hostile_side and from_hostile:
            moved = min(votes, from_hostile)
            from_hostile -= moved
        if moved and side is not None:
            counts[leans] -= moved
            counts[side] += moved
        tally[0] += counts[FOR]
        tally[1] += counts[AGAINST]
        tally[2] += counts[UNDECIDED]
        yield Called(
            covenant,
            votes,
            counts[FOR],
            counts[AGAINST],
            counts[UNDECIDED],
            moved,
            (tally[0], tally[1], tally[2]),
        )


def tally(
    saga: Saga,
    tribunal: Tribunal,
    meeting: Meeting,
    case: Case,
    leaning: dict[str, str] | None = None,
) -> tuple[int, int, int]:
    """For, against and abstaining, once every covenant is called."""
    final = (0, 0, 0)
    for called in call_the_vote(saga, tribunal, meeting, case, leaning):
        final = called.tally
    return final


def passes(votes: tuple[int, int, int], tie: str = "") -> bool | None:
    """Whether a vote carries: more for than against, or on a tie as the
    Praeco breaks it (None: a tie he hasn't broken yet)."""
    yes, no, _abstain = votes
    if yes != no:
        return yes > no
    if tie in (FOR, AGAINST):
        return tie == FOR
    return None


def kept_votes(kept: dict[str, Any]) -> tuple[int, int, int]:
    return kept["for"], kept["against"], kept.get("abstain", 0)


def vote_outcome(meeting: Meeting, case: Case) -> str:
    """ "Carried, 9 to 7" or "Failed, 4 to 10", as the vote went ("" with
    no vote held); a tie says the Praeco broke it."""
    kept = meeting.get("votes", {}).get(case.id)
    if kept is None:
        return ""
    word = "Carried" if passes(kept_votes(kept), kept.get("tie", "")) else "Failed"
    tied = " on the Praeco's casting vote" if kept["for"] == kept["against"] else ""
    return f"{word}, {kept['for']} to {kept['against']}{tied}"


def tally_text(votes: tuple[int, int, int], tie: str = "") -> str:
    """ "For 9, against 10, 4 abstaining: it fails"; on a tie, as the
    Praeco breaks it."""
    yes, no, abstain = votes
    outcome = passes(votes, tie)
    if yes == no and outcome is None:
        verdict = "a tie, for the Praeco to break"
    elif yes == no:
        verdict = f"a tie: the Praeco casts {'for' if outcome else 'against'} it, and {'it is carried' if outcome else 'it fails'}"
    else:
        verdict = "it is carried" if outcome else "it fails"
    rest = f", {abstain} abstaining" if abstain else ""
    return f"For {yes}, against {no}{rest}: {verdict}"


def tally_bar(votes: tuple[int, int, int], width: int = 30) -> str:
    """The tally as a bar: for, abstaining, against."""
    total = sum(votes) or 1
    yes = round(votes[0] * width / total)
    no = round(votes[1] * width / total)
    middle = max(0, width - yes - no)
    return "█" * yes + "░" * middle + "▓" * no


# -- the steps (Template Method) --


@dataclass
class Step:
    """One step of the order of business: its key in the record, what the
    list calls it and the day it is held. `fields`, `apply`, `text` and
    `guide` are the parts each kind fills in; holding a step (`hold`) is
    the same for all: its form, then the step marked held, the record
    saved with the saga, and the next step's form."""

    key: str
    title: str
    day: int

    def fields(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting
    ) -> list[DialogField]:
        return [_note_field(meeting, self.key)]

    def validate(self, meeting: Meeting, values: dict[str, Any]) -> str | None:
        return None

    def apply(
        self,
        saga: Saga,
        tribunal: Tribunal,
        meeting: Meeting,
        values: dict[str, Any],
    ) -> None:
        _keep_note(meeting, self.key, values)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting) -> str:
        return _note_text(meeting, self.key)

    def save_label(self) -> str:
        return "Hold"

    def guide(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting
    ) -> tuple[str, str]:
        """What the app works out at this step, and what each thing
        entered changes (plain words; "" for nothing to say)."""
        return "", "Anything noted goes into the minutes."

    def minutes(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting
    ) -> tuple[str, str]:
        """What the minutes say of the step, and the numbers set in their
        margin (the step's Note is added to them)."""
        return "", ""

    def live(
        self,
        saga: Saga,
        tribunal: Tribunal,
        meeting: Meeting,
        values: dict[str, Any],
    ) -> str:
        """A line kept up to date under the form as it is filled in ("":
        none)."""
        return ""


def _note_field(meeting: Meeting, key: str) -> DialogField:
    return DialogField(
        "note",
        "Note",
        "area",
        meeting.get("notes", {}).get(key, ""),
        hint="Anything said or decided at this step, in your own words.",
    )


def _keep_note(meeting: Meeting, key: str, values: dict[str, Any]) -> None:
    note = (values.get("note") or "").strip()
    notes = meeting.setdefault("notes", {})
    if note:
        notes[key] = note
    else:
        notes.pop(key, None)


def _note_text(meeting: Meeting, key: str) -> str:
    note = meeting.get("notes", {}).get(key, "")
    return f"[$label]Note:[/] {escape(note)}" if note else ""


def _join(*parts: str) -> str:
    return "\n".join(p for p in parts if p)


class Opening(Step):
    """The day count, where it is held, and the day each case is heard."""

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        cases = tribunal_sheet.open_cases(tribunal)
        found = [
            DialogField(
                "place",
                "Held at",
                "text",
                meeting.get("place", ""),
                placeholder=tribunal.meeting_place.strip() or "a covenant",
            ),
            DialogField(
                "days",
                "Days",
                "int",
                days(meeting),
                required=True,
                hint="How long the meeting lasts; the last day is kept for "
                "the rulings and the closing.",
            ),
        ]
        if cases:
            found.append(DialogField("days_note", "", "info", "The day each is heard:"))
        found += [
            DialogField(
                f"day_{c.id}", c.title, "int", day_of(meeting, c), required=True
            )
            for c in cases
        ]
        return found

    def validate(self, meeting: Meeting, values: dict[str, Any]):
        count = values.get("days") or 0
        if count < 1:
            return "A meeting lasts at least a day."
        for key, value in values.items():
            if key.startswith("day_") and not 1 <= (value or 0) <= count:
                return f"Each case is heard on a day from 1 to {count}."
        return None

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        meeting["place"] = values.get("place", "")
        meeting["days"] = values["days"]
        meeting["day_of"] = {
            key.removeprefix("day_"): value
            for key, value in values.items()
            if key.startswith("day_")
        }

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        roll = ", ".join(c.name for c in tribunals.covenants_of(saga, tribunal))
        return _join(
            f"[$label]Held at:[/] {escape(meeting.get('place') or '(not set)')}",
            f"[$label]Days:[/] {days(meeting)}",
            f"[$label]The roll of covenants:[/] {escape(roll or '(none recorded)')}",
        )

    def save_label(self):
        return "Open"

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return (
            "Each case and motion is spread over the days but the last, in "
            "the order of the docket; the last day is kept for the rulings "
            "and the closing.",
            "Held at names the place in the Acta. Days sets how long the "
            "meeting lasts, and the day you give a case is the day its "
            "hearing and vote come in the order of business.",
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        roll = ", ".join(c.name for c in tribunals.covenants_of(saga, tribunal))
        place = meeting.get("place") or ""
        at = f" at {place}" if place else ""
        count = days(meeting)
        words = f"The Tribunal opened{at} and the oaths were sworn."
        if roll:
            words += f" The roll of covenants was read: {roll}."
        return words, f"{count} day{'' if count == 1 else 's'}"


class Attendance(Step):
    """The roll call: each covenant's magi ticked present (or the whole
    covenant at once), how many of a sketch covenant's unnamed magi came,
    and the proxies each carries with the Presiding Quaesitor's ruling on
    them."""

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        found: list[DialogField] = []
        credential = tribunal_packages.of(tribunal).credential
        for covenant in tribunals.covenants_of(saga, tribunal):
            cid = covenant.id
            name = covenant.name
            magi = world.covenant_magi(saga, covenant)
            here = named_present(saga, meeting, covenant)
            if credential:
                lacks = tribunal_packages.lacks_credential(saga, tribunal, covenant)
                found.append(
                    DialogField(
                        f"shows_{cid}",
                        f"{name}: shows its {credential}",
                        "check",
                        shows(saga, tribunal, meeting, covenant),
                        hint=f"{lacks}."
                        if lacks
                        else "Without it, its magi and "
                        "the proxies it carries have no vote.",
                    )
                )
            whole = len(here) == len(magi) and in_person(
                saga, meeting, covenant
            ) == world.votes(saga, covenant)
            if magi:
                found.append(
                    DialogField(
                        f"all_{cid}",
                        f"{name}: all present",
                        "check",
                        whole,
                        hint="Untick to tick its magi one by one.",
                    )
                )
            for magus in magi:
                role = ""
                if magus.id == tribunal.praeco_id:
                    role = " (Praeco: votes only to break a tie)"
                elif magus.id == tribunal.quaesitor_id:
                    role = " (Presiding Quaesitor: no vote)"
                found.append(
                    DialogField(
                        f"present_{cid}_{magus.id}",
                        f"{escape(magus.name)}{role}",
                        "check",
                        magus in here,
                        show_if=lambda v, cid=cid: not v.get(f"all_{cid}"),
                    )
                )
            if covenant.unnamed_magi:
                kept = _attendance(meeting, covenant)
                unnamed = (
                    int(kept.get("unnamed") or 0)
                    if "present" in kept
                    else covenant.unnamed_magi
                )
                found.append(
                    DialogField(
                        f"unnamed_{cid}",
                        f"{name}: unnamed magi present",
                        "int",
                        unnamed,
                        hint=f"Of its {covenant.unnamed_magi} magi not named.",
                        show_if=lambda v, cid=cid, named=bool(magi): (
                            not named or not v.get(f"all_{cid}")
                        ),
                    )
                )
            found += [
                DialogField(
                    f"proxies_{cid}",
                    f"{name}: proxies",
                    "int",
                    carried(tribunal, meeting, covenant),
                    hint="The sigils it carries for magi not in the hall.",
                ),
                DialogField(
                    f"ruling_{cid}",
                    f"{name}: Quaesitor",
                    "select",
                    ruling(meeting, covenant),
                    options=pairs(RULINGS),
                    required=True,
                    hint="Whether the Presiding Quaesitor allows its proxies.",
                    show_if=lambda v, cid=cid: (v.get(f"proxies_{cid}") or 0) > 0,
                ),
            ]
        if not found:
            found.append(
                DialogField(
                    "none", "", "info", "No covenant belongs to this Tribunal yet."
                )
            )
        return found

    def validate(self, meeting: Meeting, values: dict[str, Any]):
        if any(
            (v or 0) < 0
            for k, v in values.items()
            if k.startswith(("unnamed_", "proxies_"))
        ):
            return "Magi present and proxies can't be fewer than none."
        return None

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        attendance = meeting.setdefault("attendance", {})
        for covenant in tribunals.covenants_of(saga, tribunal):
            cid = covenant.id
            proxies = values.get(f"proxies_{cid}") or 0
            everyone = bool(values.get(f"all_{cid}"))
            magi = world.covenant_magi(saga, covenant)
            here = [
                m.id for m in magi if everyone or values.get(f"present_{cid}_{m.id}")
            ]
            unnamed = (
                covenant.unnamed_magi
                if everyone or f"unnamed_{cid}" not in values
                else min(values[f"unnamed_{cid}"] or 0, covenant.unnamed_magi)
            )
            attendance[cid] = {
                "present": here,
                "unnamed": unnamed,
                "absent": world.votes(saga, covenant) - len(here) - unnamed,
                "proxies": proxies,
                "ruling": values.get(f"ruling_{cid}") or ALLOWED,
            }
            if f"shows_{cid}" in values:
                attendance[cid]["shows"] = bool(values[f"shows_{cid}"])
            if proxies:
                tribunal.proxies[cid] = proxies
            else:
                tribunal.proxies.pop(cid, None)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return _join(
            f"[$label]Present:[/] {escape(present_text(saga, tribunal, meeting))}",
            f"[$label]Quorum:[/] {escape(quorum(saga, tribunal, meeting))}",
        )

    def save_label(self):
        return "Call the roll"

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return (
            "The votes in the hall: one for each magus present and each "
            "proxy the Presiding Quaesitor allows. The Praeco and the "
            "Presiding Quaesitor don't vote (the Praeco breaks a tie). The "
            "quorum: twelve magi in person from four covenants, and a "
            "Quaesitor.",
            "Who you tick present can speak at the hearings and votes; "
            "proxies add votes but never a voice. The proxies are kept on "
            "the roster for the next meeting.",
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        lines = []
        credential = tribunal_packages.of(tribunal).credential
        for covenant in tribunals.covenants_of(saga, tribunal):
            if not shows(saga, tribunal, meeting, covenant):
                lines.append(
                    f"{covenant.name} did not show its {credential}, and was "
                    "not represented."
                )
                continue
            gone = absent(saga, meeting, covenant)
            if gone:
                missing = [
                    m.name
                    for m in world.covenant_magi(saga, covenant)
                    if m not in named_present(saga, meeting, covenant)
                ]
                who = f" ({', '.join(missing)})" if missing else ""
                lines.append(f"{covenant.name}: {gone} absent{who}.")
            proxies = carried(tribunal, meeting, covenant)
            if proxies:
                ruled = (
                    "allowed"
                    if ruling(meeting, covenant) == ALLOWED
                    else "set aside by the Presiding Quaesitor"
                )
                lines.append(
                    f"{covenant.name} carried {proxies} "
                    f"prox{'y' if proxies == 1 else 'ies'}, {ruled}."
                )
        return (
            " ".join(lines) or "Every magus answered the roll.",
            present_text(saga, tribunal, meeting),
        )


#: Who can speak at a hearing besides the magi present: a Guernicus
#: advocate defends an absent accused, the Presiding Quaesitor prosecutes
#: a high crime no one else will, and a motion's proposer debates the
#: whole Tribunal (HoH: True Lineages, Tribunal Procedures; HoH:
#: Societates, Proposal Cases). A name entered before speakers were
#: chosen is kept as entered.
ADVOCATE, QUAESITOR, THE_TRIBUNAL, AS_ENTERED = (
    "@advocate",
    "@quaesitor",
    "@tribunal",
    "@as:",
)
_SPEAKERS = {
    ADVOCATE: "A Guernicus advocate",
    QUAESITOR: "The Presiding Quaesitor",
    THE_TRIBUNAL: "The Tribunal",
}


def speaker_name(saga: Saga, value: str) -> str:
    """Who `value` (a speaker choice) names."""
    if value in _SPEAKERS:
        return _SPEAKERS[value]
    if value.startswith(AS_ENTERED):
        return value.removeprefix(AS_ENTERED)
    found = saga.character(value)
    return found.name if found is not None else value


def speaker_options(
    saga: Saga, tribunal: Tribunal, meeting: Meeting, case: Case, side: str
) -> list[tuple[str, str]]:
    """Who can speak for (FOR) or against (AGAINST) `case`: the magi
    present, then the Presiding Quaesitor (prosecuting a charge), a
    Guernicus advocate (defending one) or the Tribunal (opposing a
    motion), and a name the case had before."""
    found = [
        (f"{escape(m.name)} ({escape(c.name)})", m.id)
        for m, c in magi_present(saga, tribunal, meeting)
    ]
    motion = case.kind == "motion"
    if side == FOR and not motion:
        quaesitor = saga.character(tribunal.quaesitor_id)
        if quaesitor is None:
            found.append((_SPEAKERS[QUAESITOR], QUAESITOR))
        elif quaesitor.id not in [v for _l, v in found]:
            found.append(
                (f"{escape(quaesitor.name)}, Presiding Quaesitor", quaesitor.id)
            )
    if side == AGAINST:
        special = THE_TRIBUNAL if motion else ADVOCATE
        found.append((_SPEAKERS[special], special))
    before = (case.prosecutor if side == FOR else case.defender).strip()
    if before and not any(speaker_name(saga, v) == before for _l, v in found):
        found.append((f"{escape(before)} (as entered)", AS_ENTERED + before))
    return found


def _magus_named(saga: Saga, words: str) -> Character | None:
    found = _character(saga, words)
    return found if found is not None and found.type == "magus" else None


def default_speaker(
    saga: Saga, tribunal: Tribunal, meeting: Meeting, case: Case, side: str
) -> str:
    """Who speaks unless the storyguide says otherwise: as the hearing was
    held, else the case's speaker, else the magus (or a magus of the
    covenant) the case names, else the Quaesitor prosecuting, a Guernicus
    advocate defending an absent accused, and the Tribunal opposing a
    motion."""
    options = [v for _l, v in speaker_options(saga, tribunal, meeting, case, side)]
    index = 0 if side == FOR else 1
    kept = (debate_of(meeting, case) or {}).get("speakers")
    if kept and kept[index] in options:
        return kept[index]
    before = (case.prosecutor if side == FOR else case.defender).strip()
    named = _character(saga, before) if before else None
    if named is not None and named.id in options:
        return named.id
    if before and AS_ENTERED + before in options:
        return AS_ENTERED + before
    words = case.brought_by if side == FOR else case.against
    here = magi_present(saga, tribunal, meeting)
    magus = _magus_named(saga, words) if words.strip() else None
    if magus is not None and magus.id in options:
        return magus.id
    if magus is None and words.strip():
        for m, c in here:
            if _party(c, words):
                return m.id
    if side == AGAINST:
        return THE_TRIBUNAL if case.kind == "motion" else ADVOCATE
    return QUAESITOR if QUAESITOR in options else options[0]


def unscored(saga: Saga, options: list[tuple[str, str]]) -> set[str]:
    """The speakers among `options` with no scores written down: they
    debate at a skill."""
    found = set()
    for _label, value in options:
        character = saga.character(value)
        if character is None or not debate.has_scores(character):
            found.add(value)
    return found


def _skill(value: str) -> str:
    return debate.ABLE if value in (ADVOCATE, QUAESITOR) else debate.MIDDLING


class Hearing(Step):
    """A charge or appeal debated between its prosecutor and defender, or
    a motion between one who speaks for it and one against: the speakers
    (chosen from the magi present, a Guernicus advocate, the Presiding
    Quaesitor or the Tribunal), the rounds the praeco allows, and each
    side's debate Fatigue levels lost, entered or (left blank) rolled by
    the Societates rules with the case's evidence as the prosecution's
    testimony. A charge may instead be settled at the private hearing."""

    def __init__(self, case: Case, day: int) -> None:
        motion = case.kind == "motion"
        title = f"Motion: {case.title}" if motion else case.title
        super().__init__(f"case:{case.id}", title, day)
        self.case = case

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        case = self.case
        motion = case.kind == "motion"
        kept = debate_of(meeting, case) or {}
        skills = kept.get("skills") or ["", ""]
        found: list[DialogField] = []
        if not motion:
            found.append(
                DialogField(
                    "settled",
                    "Settled in private",
                    "check",
                    bool(kept.get("settled")),
                    hint="Both sides accept the Presiding Quaesitor's ruling: "
                    "it is neither debated nor voted on.",
                )
            )

        def debated(values: dict[str, Any]) -> bool:
            return not values.get("settled")

        for index, (side, key, label) in enumerate(
            (
                (FOR, "prosecutor", "Speaks for it" if motion else "Prosecutor"),
                (AGAINST, "defender", "Speaks against it" if motion else "Defender"),
            )
        ):
            options = speaker_options(saga, tribunal, meeting, case, side)
            chosen = default_speaker(saga, tribunal, meeting, case, side)
            lacking = unscored(saga, options)
            found += [
                DialogField(
                    key,
                    label,
                    "select",
                    chosen,
                    options=options,
                    required=True,
                    hint="The magi present, or "
                    + (
                        "the Presiding Quaesitor."
                        if side == FOR
                        else "the Tribunal itself."
                        if motion
                        else "a Guernicus advocate for an accused who is absent."
                    ),
                ),
                DialogField(
                    f"skill_{key}",
                    f"{label}: debates as",
                    "select",
                    skills[index] or _skill(chosen),
                    options=pairs(tuple(debate.SKILLS)),
                    required=True,
                    hint="No scores are written down for them: how well they debate.",
                    show_if=lambda v, key=key, lacking=lacking: (
                        debated(v) and v.get(key) in lacking
                    ),
                ),
            ]
        if motion:
            found.append(
                DialogField(
                    "proposal",
                    "Proposal",
                    "select",
                    kept.get("proposal") or "Clarification",
                    options=pairs(debate.PROPOSALS),
                    required=True,
                    hint="An Addition costs it 1 Argument Strength, an "
                    "Alteration of the Code 3.",
                )
            )
        entered = kept.get("entered") and not kept.get("settled")
        found += [
            DialogField(
                "rounds",
                "Rounds",
                "int",
                kept.get("rounds") or debate.DEFAULT_ROUNDS,
                required=True,
                hint=f"The praeco allows 1 to {debate.MAX_ROUNDS}; a side "
                f"that loses {debate.KNOCKED_OUT} levels ends it.",
                show_if=debated,
            ),
            DialogField(
                "defence_testimony",
                "Defence testimony",
                "area",
                kept.get("defence_testimony", ""),
                hint="One a line, as the case's Evidence is for the "
                "prosecution: a peer's +3, an apprentice's +2, any other "
                "+1, and +3 more if a Quaesitor examined it.",
                show_if=debated,
            ),
            DialogField(
                "lost_for",
                "Levels lost (for)",
                "optint",
                kept.get("lost", [None, None])[0] if entered else None,
                hint="Leave both blank to roll the debate.",
                show_if=debated,
            ),
            DialogField(
                "lost_against",
                "Levels lost (against)",
                "optint",
                kept.get("lost", [None, None])[1] if entered else None,
                show_if=debated,
            ),
        ]
        return [*found, _note_field(meeting, self.key)]

    def validate(self, meeting: Meeting, values: dict[str, Any]):
        if values.get("settled"):
            return None
        if not 1 <= (values.get("rounds") or 0) <= debate.MAX_ROUNDS:
            return f"A debate runs 1 to {debate.MAX_ROUNDS} rounds."
        entered = [values.get("lost_for"), values.get("lost_against")]
        if (entered[0] is None) != (entered[1] is None):
            return "Enter both sides' levels lost, or neither to roll."
        if any(v is not None and not 0 <= v <= debate.KNOCKED_OUT for v in entered):
            return f"A side loses 0 to {debate.KNOCKED_OUT} levels."
        if values.get("prosecutor") and values.get("prosecutor") == values.get(
            "defender"
        ):
            return "One magus can't speak for both sides."
        return None

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        case = self.case
        speakers = [values.get("prosecutor") or "", values.get("defender") or ""]
        skills = [
            values.get("skill_prosecutor") or _skill(speakers[0]),
            values.get("skill_defender") or _skill(speakers[1]),
        ]
        case.prosecutor = speaker_name(saga, speakers[0]) if speakers[0] else ""
        case.defender = speaker_name(saga, speakers[1]) if speakers[1] else ""
        defence = values.get("defence_testimony", "")
        record: dict[str, Any] = {
            "speakers": speakers,
            "skills": skills,
            "rounds": values.get("rounds") or debate.DEFAULT_ROUNDS,
            "defence_testimony": defence,
            "proposal": values.get("proposal", ""),
        }
        if values.get("settled"):
            record |= {"settled": True, "lost": [0, 0], "entered": False, "lines": []}
            meeting.get("votes", {}).pop(case.id, None)
        elif values.get("lost_for") is not None:
            record |= {
                "lost": [values["lost_for"], values["lost_against"]],
                "entered": True,
                "lines": [],
            }
        else:
            sides = tuple(
                debate.debater(speaker_name(saga, value), saga.character(value), skill)
                for value, skill in zip(speakers, skills, strict=True)
            )
            testimony = (
                [debate.testimony_bonus(e) for e in _lines(case.evidence)],
                [debate.testimony_bonus(e) for e in _lines(defence)],
            )
            held = debate.run((sides[0], sides[1]), testimony, record["rounds"], rng())
            record |= {"lost": held.lost, "entered": False, "lines": held.lines}
        meeting.setdefault("debates", {})[case.id] = record
        _keep_note(meeting, self.key, values)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        # The details panel names the step: the case's own heading goes.
        lines = tribunal_sheet.case_text(saga, tribunal, self.case).split("\n")
        return _join(
            debate_text(meeting, self.case),
            *lines[1:],
            _note_text(meeting, self.key),
        )

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        motion = self.case.kind == "motion"
        cost = (
            " A motion's proposer loses 1 of it for an Addition to the Code, "
            "3 for an Alteration."
            if motion
            else ""
        )
        settle = (
            ""
            if motion
            else " Settled at the private hearing: no debate and no vote; "
            "the ruling says how it was settled."
        )
        return (
            "Left blank, the levels lost are rolled round by round "
            "(HoH: Societates): each speaker attacks with Communication + the "
            "best of Folk Ken, Intrigue or Artes Liberales, and defends with "
            "Intelligence + the best of Charm, Guile or Leadership. The case's "
            "Evidence backs the prosecution and the Defence testimony the "
            "defence, each used once. The side that loses fewer levels wins, "
            "and the difference is its Argument Strength, which sways the "
            "undecided votes at the vote." + cost,
            "The speakers' own scores are rolled; one with none written down "
            "debates at the skill you give (Middling, Able or Formidable). "
            "More rounds give the better speaker more chances. Entering both "
            "levels lost replaces the roll." + settle,
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        case = self.case
        if settled(meeting, case):
            return (
                f"{case.title} was settled before the Presiding Quaesitor at "
                "the private hearing, and not heard in the hall.",
                "settled",
            )
        side, margin = strength(meeting, case)
        words = (
            f"{case.prosecutor or 'Its speaker'} spoke for {case.title}; "
            f"{case.defender or 'none'} against."
        )
        if side is not None:
            winner = case.prosecutor if side == FOR else case.defender
            winner = winner or ("Its side" if side == FOR else "The other side")
            words += f" {winner} carried the hall ({debate.sway(margin)[0]})."
        else:
            words += " Neither carried the hall."
        lost = (debate_of(meeting, case) or {}).get("lost", [0, 0])
        return words, f"levels {lost[0]}–{lost[1]}"


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _character(saga: Saga, name: str) -> Character | None:
    wanted = name.strip().casefold()
    if not wanted:
        return None
    return next((c for c in saga.characters if c.name.casefold() == wanted), None)


def debate_text(meeting: Meeting, case: Case) -> str:
    """The debate's outcome, and each round as it went."""
    held_debate = debate_of(meeting, case)
    if held_debate is None:
        return ""
    if held_debate.get("settled"):
        return (
            "[$label]Settled at the private hearing:[/] neither debated nor voted on."
        )
    lost = held_debate.get("lost", [0, 0])
    sides = f"{case.prosecutor or 'For'} lost {lost[0]}, {case.defender or 'against'} {lost[1]}"
    side, margin = strength(meeting, case)
    if side is None:
        outcome = "neither carries the hall"
    else:
        name, neutral, hostile = debate.sway(margin)
        winner = case.prosecutor if side == FOR else case.defender
        won = f"{neutral}% of the undecided votes"
        if hostile:
            won += f" and {hostile}% of the other side's"
        outcome = (
            f"{winner or side} wins with an Argument Strength of {margin} "
            f"({name}): {won}"
        )
    rounds = [escape(line) for line in held_debate.get("lines", [])]
    return _join(
        f"[$label]The debate:[/] {escape(sides)} levels; {escape(outcome)}.",
        *rounds,
    )


class Vote(Step):
    """The vote on a case: each covenant's leaning (from its attitude to
    the parties, which the storyguide can change), the votes the debate
    swayed, the tally as each covenant is called, and on a tie the
    Praeco's casting vote."""

    def __init__(self, case: Case, day: int) -> None:
        super().__init__(f"vote:{case.id}", f"The vote: {case.title}", day)
        self.case = case

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        lean = leanings(saga, tribunal, meeting, self.case)
        kept = meeting.get("votes", {}).get(self.case.id, {})

        def tied(values: dict[str, Any]) -> bool:
            yes, no, _abstain = tally(
                saga,
                tribunal,
                meeting,
                self.case,
                self._leaning(saga, tribunal, meeting, values),
            )
            return yes == no

        return [
            *(
                DialogField(
                    f"lean_{c.id}",
                    f"{c.name}: leans",
                    "select",
                    lean[c.id],
                    options=pairs(LEANINGS),
                    required=True,
                    hint=f"Of itself: {why}.",
                )
                for c in voters(saga, tribunal, meeting)
                for _lean, why in [leaning_why(saga, self.case, c)]
            ),
            DialogField(
                "tie",
                "The Praeco casts",
                "select",
                kept.get("tie") or AGAINST,
                options=pairs((FOR, AGAINST)),
                required=True,
                hint="The votes are tied: the Praeco breaks the tie. On a "
                "call for a Wizard's March a tie defeats it.",
                show_if=tied,
            ),
            _note_field(meeting, self.key),
        ]

    def _leaning(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ) -> dict[str, str]:
        return {
            c.id: values.get(f"lean_{c.id}") or UNDECIDED
            for c in voters(saga, tribunal, meeting)
        }

    def live(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ) -> str:
        votes = tally(
            saga,
            tribunal,
            meeting,
            self.case,
            self._leaning(saga, tribunal, meeting, values),
        )
        return escape(tally_text(votes, values.get("tie") or ""))

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        lean = self._leaning(saga, tribunal, meeting, values)
        yes, no, abstain = tally(saga, tribunal, meeting, self.case, lean)
        meeting.setdefault("votes", {})[self.case.id] = {
            "leanings": lean,
            "for": yes,
            "against": no,
            "abstain": abstain,
            "tie": (values.get("tie") or AGAINST) if yes == no else "",
        }
        _keep_note(meeting, self.key, values)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        kept = meeting.get("votes", {}).get(self.case.id)
        if kept is None:
            return ""
        return _join(
            f"[$label]The vote:[/] "
            f"{escape(tally_text(kept_votes(kept), kept.get('tie', '')))}.",
            _note_text(meeting, self.key),
        )

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return (
            "Each covenant starts leaning by its attitude to the parties (said "
            "under it). The debate's victor wins a share of the undecided votes "
            "(10% from an Edge up to 60% from a Landslide) and, from a "
            "Triumphant Victory, some of the other side's. The covenants are "
            "called in the order of the roll; the undecided abstain.",
            "Change a leaning and the tally under the form follows it. On a "
            "tie, choose how the Praeco casts. The vote is the ruling's "
            "starting point.",
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        kept = meeting.get("votes", {}).get(self.case.id)
        if kept is None:
            return "", ""
        votes = kept_votes(kept)
        margin = f"{votes[0]}–{votes[1]}"
        if votes[2]:
            margin += f", {votes[2]} abst."
        return (
            f"The vote on {self.case.title}: {tally_text(votes, kept.get('tie', ''))}.",
            margin,
        )


class Elections(Step):
    """The Tribunal's offices, each given a holder and a term (only when
    its customs have offices: the Theban archai)."""

    def _offices(self, tribunal: Tribunal) -> list[dict[str, Any]]:
        return tribunal_packages.entries(tribunal, tribunal.package, "archai")

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        offices = self._offices(tribunal)
        magi = [
            (m.name, m.id)
            for c in tribunals.covenants_of(saga, tribunal)
            for m in world.covenant_magi(saga, c)
        ]
        found: list[DialogField] = []
        for index, office in enumerate(offices):
            found += [
                DialogField(
                    f"holder_{index}",
                    office.get("office") or "(an office)",
                    "select",
                    office.get("holder_id"),
                    options=magi,
                    allow_blank=True,
                ),
                DialogField(
                    f"term_{index}", "Term ends", "optint", office.get("term_ends")
                ),
            ]
        if not offices:
            found.append(
                DialogField(
                    "none", "", "info", "No offices recorded: add them on its tab."
                )
            )
        return [*found, _note_field(meeting, self.key)]

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return (
            "Nothing is worked out: the offices are as recorded on the Tribunal's tab.",
            "Each holder you choose takes the office now, until the term's "
            "end you give; the Acta lists them.",
        )

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        for index, office in enumerate(self._offices(tribunal)):
            if f"holder_{index}" in values:
                office["holder_id"] = values[f"holder_{index}"]
                office["term_ends"] = values.get(f"term_{index}")
        _keep_note(meeting, self.key, values)

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        lines = []
        for office in self._offices(tribunal):
            holder = saga.character(office.get("holder_id"))
            if holder is not None:
                term = office.get("term_ends")
                until = f", until {term}" if term else ""
                lines.append(f"{holder.name} was chosen {office.get('office')}{until}.")
        return " ".join(lines), ""


def eldest_magi(saga: Saga, tribunal: Tribunal) -> list[Character]:
    """The Tribunal's named magi, eldest first (those whose birth year
    isn't known last)."""
    magi = [
        m
        for c in tribunals.covenants_of(saga, tribunal)
        for m in world.covenant_magi(saga, c)
    ]
    return sorted(
        magi,
        key=lambda m: (m.background.year_born is None, m.background.year_born or 0),
    )


class Succession(Step):
    """A Tribunal whose customs name its eldest magus Praeco: with none,
    the eldest is offered; set them aside and the next eldest is."""

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        praeco = saga.character(tribunal.praeco_id)
        if praeco is not None:
            return [
                DialogField(
                    "none",
                    "",
                    "info",
                    f"{escape(praeco.name)} is Praeco: there is no succession.",
                ),
                _note_field(meeting, self.key),
            ]
        magi = eldest_magi(saga, tribunal)
        if not magi:
            return [
                DialogField(
                    "none",
                    "",
                    "info",
                    "No magus of the Tribunal is recorded to name.",
                ),
                _note_field(meeting, self.key),
            ]
        return [
            DialogField(
                "praeco",
                "Praeco",
                "select",
                magi[0].id,
                options=[(escape(_aged(saga, m)), m.id) for m in magi],
                required=True,
                hint="The eldest magus is named Praeco; if they decline or are "
                "set aside, choose the next eldest.",
            ),
            _note_field(meeting, self.key),
        ]

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        if values.get("praeco"):
            meeting["succession"] = {
                "named": values["praeco"],
                "set_aside": [
                    m.id
                    for m in itertools.takewhile(
                        lambda m: m.id != values["praeco"], eldest_magi(saga, tribunal)
                    )
                ],
            }
            tribunal.praeco_id = values["praeco"]
        _keep_note(meeting, self.key, values)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        praeco = saga.character(tribunal.praeco_id)
        if praeco is None:
            return _join("[$label]Praeco:[/] vacant", _note_text(meeting, self.key))
        return _join(
            f"[$label]Praeco:[/] {escape(praeco.name)}", _note_text(meeting, self.key)
        )

    def save_label(self):
        return "Name"

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return (
            "With no Praeco, the eldest magus of the Tribunal (by Year Born) "
            "is offered.",
            "The magus you name becomes Praeco; any older magi are written in "
            "the minutes as set aside.",
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = meeting.get("succession") or {}
        named = saga.character(held.get("named"))
        if named is None:
            return "", ""
        aside = [saga.character(i) for i in held.get("set_aside", [])]
        passed = ", ".join(m.name for m in aside if m is not None)
        words = f"The Praeco's seat being vacant, {named.name} was named Praeco"
        words += f", {passed} being set aside." if passed else ", as the eldest."
        return words, "Praeco"


def _aged(saga: Saga, magus: Character) -> str:
    born = magus.background.year_born
    return f"{magus.name} (age {saga.current_year - born})" if born else magus.name


def lot_choices(saga: Saga, tribunal: Tribunal) -> list[Covenant]:
    """The covenants the next host is drawn from: the Tribunal's own."""
    return tribunals.covenants_of(saga, tribunal)


class HostByLot(Step):
    """The next meeting's host covenant drawn by lot, with one redraw;
    it becomes the Tribunal's meeting place."""

    def _lot(self, saga: Saga, tribunal: Tribunal, meeting: Meeting) -> list[str]:
        """The two draws (the lot and its one redraw), made once and kept
        with the meeting so the form shows the same each time."""
        ids = [c.id for c in lot_choices(saga, tribunal)]
        drawn = [i for i in meeting.get("lot", []) if i in ids]
        if len(drawn) < 2 and ids:
            drawn = [random.choice(ids), random.choice(ids)]
            meeting["lot"] = drawn
        return drawn

    def _host(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, redraw: bool
    ) -> Covenant | None:
        drawn = self._lot(saga, tribunal, meeting)
        if not drawn:
            return None
        return saga.covenant(drawn[1] if redraw else drawn[0])

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        host = self._host(saga, tribunal, meeting, False)
        if host is None:
            return [
                DialogField("none", "", "info", "No covenant is recorded to draw."),
                _note_field(meeting, self.key),
            ]
        return [
            DialogField(
                "drawn",
                "",
                "info",
                f"The lot falls on {escape(host.name)}.",
            ),
            DialogField(
                "redraw",
                "Redraw",
                "check",
                False,
                hint="The lot may be drawn again once; the second draw stands.",
            ),
            _note_field(meeting, self.key),
        ]

    def live(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        host = self._host(saga, tribunal, meeting, bool(values.get("redraw")))
        return f"Next host: {escape(host.name)}." if host is not None else ""

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        host = self._host(saga, tribunal, meeting, bool(values.get("redraw")))
        if host is not None:
            meeting["host"] = {"id": host.id, "redrawn": bool(values.get("redraw"))}
            tribunal.meeting_place = host.name
        _keep_note(meeting, self.key, values)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = meeting.get("host") or {}
        host = saga.covenant(held.get("id"))
        shown = f"[$label]Next host:[/] {escape(host.name)}" if host else ""
        return _join(shown, _note_text(meeting, self.key))

    def save_label(self):
        return "Draw"

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return (
            "The lot is drawn from the Tribunal's covenants, with one redraw, "
            "and kept, so holding the step again draws the same.",
            "Tick Redraw and the second draw stands. The covenant drawn "
            "becomes the next meeting's place.",
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = meeting.get("host") or {}
        host = saga.covenant(held.get("id"))
        if host is None:
            return "", ""
        again = " on the second draw" if held.get("redrawn") else ""
        return (
            f"The lot for the next host fell{again} on {host.name}, where the "
            "Tribunal meets next.",
            "By lot",
        )


class Rulings(Step):
    """The ruling on each case heard (starting from how its vote went),
    written out or from a template whose blanks are asked next; any fine
    and who pays it; whether the ruling goes into the Peripheral Code; a
    term after which it is debated again; and how a party covenant's
    attitude toward a troupe covenant on the other side moves. All of it
    is written when the meeting closes."""

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        cases = tribunal_sheet.open_cases(tribunal)
        found: list[DialogField] = []
        offered = ruling_templates.templates(saga)
        termed = {
            t["name"]
            for t in offered
            if ruling_templates.YEARS in ruling_templates.blanks(t["text"])
        }
        for c in cases:
            kept = ruling_of(meeting, c)
            short = _short(c.title)
            start = (
                "Settled at the private hearing."
                if settled(meeting, c)
                else vote_outcome(meeting, c)
            )
            found += [
                DialogField(
                    f"template_{c.id}",
                    f"{short}: written from",
                    "select",
                    kept.get("template", ""),
                    options=[
                        ("Written out", ""),
                        *((t["name"], t["name"]) for t in offered),
                    ],
                    hint="A template's blanks are asked next (Edit Saga keeps "
                    "the templates).",
                ),
                DialogField(
                    f"outcome_{c.id}",
                    f"{short}: the ruling",
                    "text",
                    kept.get("outcome") or c.outcome or start,
                    show_if=lambda v, cid=c.id: not v.get(f"template_{cid}"),
                ),
                DialogField(
                    f"fine_{c.id}",
                    f"{short}: fine",
                    "optfloat",
                    kept.get("fine"),
                    hint="Pawns of vis, or pounds of silver with no Art.",
                ),
                DialogField(
                    f"art_{c.id}",
                    f"{short}: fine in",
                    "select",
                    kept.get("art") or "",
                    options=pairs(ARTS),
                    allow_blank=True,
                    show_if=lambda v, cid=c.id: v.get(f"fine_{cid}") is not None,
                ),
                DialogField(
                    f"who_{c.id}",
                    f"{short}: fined",
                    "text",
                    kept.get("who", c.against),
                    show_if=lambda v, cid=c.id: v.get(f"fine_{cid}") is not None,
                ),
                DialogField(
                    f"code_{c.id}",
                    f"{short}: into the Code",
                    "check",
                    kept.get("code", c.kind == "motion"),
                ),
                DialogField(
                    f"term_{c.id}",
                    f"{short}: term",
                    "optint",
                    kept.get("term"),
                    hint="Years until it comes back to be debated again (blank: "
                    "never). A notice comes the season before and when it "
                    "ends, and it goes back on the docket.",
                    show_if=lambda v, cid=c.id: v.get(f"template_{cid}") not in termed,
                ),
            ]
            pair = parties(saga, c)
            if pair is not None:
                other, player = pair
                found.append(
                    DialogField(
                        f"attitude_{c.id}",
                        f"{short}: {other.name}",
                        "select",
                        kept.get("attitude", default_attitude(meeting, c, other)),
                        options=[(a, a) for a in ATTITUDE_CHANGES],
                        required=True,
                        hint=f"How {other.name}'s attitude toward {player.name} moves.",
                    )
                )
        if not cases:
            found.append(DialogField("none", "", "info", "No case was heard."))
        return [*found, _note_field(meeting, self.key)]

    def validate(self, meeting: Meeting, values: dict[str, Any]):
        for key, value in values.items():
            if key.startswith("fine_") and value is not None and value <= 0:
                return "A fine is more than nothing; leave it blank for none."
            if key.startswith("term_") and value is not None and value < 1:
                return "A term is a year or more; leave it blank for none."
        return None

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        kept = meeting.setdefault("rulings", {})
        asked: list[Case] = []
        for case in tribunal_sheet.open_cases(tribunal):
            if f"template_{case.id}" not in values:
                continue
            before = kept.get(case.id, {})
            name = values.get(f"template_{case.id}") or ""
            template = ruling_templates.named(saga, name) if name else None
            record = {
                "template": name if template is not None else "",
                "fine": values.get(f"fine_{case.id}"),
                "art": values.get(f"art_{case.id}") or "",
                "who": values.get(f"who_{case.id}", ""),
                "code": bool(values.get(f"code_{case.id}")),
                "attitude": values.get(f"attitude_{case.id}", "0"),
                "term": values.get(f"term_{case.id}"),
            }
            if template is None:
                case.outcome = values.get(f"outcome_{case.id}", "")
            else:
                blanks = _blanks(case, template, before, record["term"])
                record["blanks"] = blanks
                record["term"] = _years(blanks) or record["term"]
                case.outcome = ruling_templates.fill(template["text"], blanks)
                asked.append(case)
            record["outcome"] = case.outcome
            kept[case.id] = record
        _keep_note(meeting, self.key, values)
        return _ask_blanks(saga, tribunal, meeting, self, asked)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        lines = []
        for c in tribunal_sheet.open_cases(tribunal):
            kept = ruling_of(meeting, c)
            line = f"[b]{escape(c.title)}:[/] {escape(c.outcome or '(no ruling yet)')}"
            if kept.get("fine"):
                line += f" · fine {escape(fine_text(kept))}"
            if kept.get("term"):
                line += f" · debated again in {kept['term']} years"
            lines.append(line)
        return _join(*lines, _note_text(meeting, self.key))

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return (
            "Each ruling starts from how its vote went. Closing the meeting "
            "writes them: each case decided, a fine owed to the treasury, the "
            "ruling into the Peripheral Code if ticked, the party's attitude "
            "moved, and a term's end set to come due.",
            "Choose a template and its blanks are asked next, making the "
            "ruling's words. A {years} blank, or the term given a written-out "
            "ruling, sets a term in years: a notice comes the season before it ends and when it does, "
            "and the matter goes back on the docket. Written out, the words "
            "are yours.",
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        lines = []
        fines = []
        for c in tribunal_sheet.open_cases(tribunal):
            if not c.outcome.strip():
                continue
            lines.append(f"{c.title}: {c.outcome.rstrip('.')}.")
            kept = ruling_of(meeting, c)
            if kept.get("fine"):
                fines.append(f"fine {fine_text(kept)}")
        return " ".join(lines), "; ".join(fines)


def _years(blanks: dict[str, str]) -> int | None:
    years = str(blanks.get(ruling_templates.YEARS) or "").strip()
    return int(years) if years.isdigit() and int(years) > 0 else None


def _blanks(
    case: Case, template: dict[str, str], before: dict[str, Any], term: int | None
) -> dict[str, str]:
    """A template's blanks as they stand: as last filled for this template,
    else suggested from the case."""
    same = before.get("template") == template["name"]
    kept = before.get("blanks", {}) if same else {}
    return {
        blank: kept.get(blank) or ruling_templates.suggested(case, blank, term)
        for blank in ruling_templates.blanks(template["text"])
    }


def _ask_blanks(
    saga: Saga,
    tribunal: Tribunal,
    meeting: Meeting,
    step: Step,
    cases: list[Case],
) -> Form | None:
    """The blanks of each case's template, a form a case: each makes its
    ruling's words (and a {years} blank its term), and the minutes are
    written again."""
    if not cases:
        return None
    case, rest = cases[0], cases[1:]
    kept = ruling_of(meeting, case)
    template = ruling_templates.named(saga, kept.get("template", ""))
    if template is None:
        return _ask_blanks(saga, tribunal, meeting, step, rest)

    def fields() -> list[DialogField]:
        found = [
            DialogField("_says", "", "info", escape(template["text"])),
        ]
        for blank in ruling_templates.blanks(template["text"]):
            value = kept.get("blanks", {}).get(blank, "")
            if blank == ruling_templates.YEARS:
                found.append(
                    DialogField(
                        f"blank_{blank}",
                        "Years",
                        "optint",
                        int(value) if str(value).isdigit() else None,
                        hint="Until it is debated again.",
                    )
                )
            else:
                found.append(
                    DialogField(f"blank_{blank}", blank.capitalize(), "text", value)
                )
        return found

    def filled(values: dict[str, Any]) -> dict[str, str]:
        return {
            k.removeprefix("blank_"): "" if v is None else str(v)
            for k, v in values.items()
            if k.startswith("blank_")
        }

    def live(values: dict[str, Any]) -> str:
        return escape(ruling_templates.fill(template["text"], filled(values)))

    def apply(values: dict[str, Any]) -> Form | None:
        blanks = filled(values)
        kept["blanks"] = blanks
        kept["term"] = _years(blanks) or kept.get("term")
        case.outcome = kept["outcome"] = ruling_templates.fill(template["text"], blanks)
        write_minutes(saga, tribunal, meeting, step)
        return _ask_blanks(saga, tribunal, meeting, step, rest)

    return Form(
        f"Ruling: {escape(case.title)} ({escape(template['name'])})",
        fields,
        apply,
        live=live,
        save_label="Rule",
        help_id="hold-tribunal",
    )


#: The attitude moves a ruling can make, as the yearly step offers them.
ATTITUDE_CHANGES = ("0", "+1", "+2", "-1", "-2", "-3")


def _short(title: str) -> str:
    """A case's title cut to fit beside a field's own words."""
    return title if len(title) <= 18 else title[:17] + "…"


def ruling_of(meeting: Meeting, case: Case) -> dict[str, Any]:
    return meeting.get("rulings", {}).get(case.id, {})


def fine_text(kept: dict[str, Any]) -> str:
    """ "3 pawns of Corpus" or "10 pounds of silver"."""
    entry = TreasuryEntry("fine", kept.get("fine") or 0, art=kept.get("art") or "")
    if not entry.art:
        entry.kind = "silver"
    return tribunal_sheet.amount_text(entry)


def parties(saga: Saga, case: Case) -> tuple[Covenant, Covenant] | None:
    """A case between a troupe covenant and another recorded covenant:
    (the other, the troupe's); None otherwise."""
    played = world.player_covenants(saga)
    for player in played:
        for words, other_words in (
            (case.brought_by, case.against),
            (case.against, case.brought_by),
        ):
            if not _party(player, words):
                continue
            other = next(
                (
                    c
                    for c in saga.covenants
                    if c is not player and not c.played and _party(c, other_words)
                ),
                None,
            )
            if other is not None:
                return other, player
    return None


def default_attitude(meeting: Meeting, case: Case, other: Covenant) -> str:
    """A party that lost its case takes it ill (-1); otherwise no move."""
    kept = meeting.get("votes", {}).get(case.id)
    if kept is None:
        return "0"
    carried = bool(passes(kept_votes(kept), kept.get("tie", "")))
    brought = _party(other, case.brought_by)
    return "0" if carried == brought else "-1"


class Treasury(Step):
    """The treasury as it stands, and the loans that fall due this year."""

    def _due(self, tribunal: Tribunal, meeting: Meeting) -> list[str]:
        year = meeting.get("year")
        return [
            f"{e.who or 'a loan'}: {tribunal_sheet.amount_text(e)}"
            for e in tribunal.treasury
            if e.kind == "loan" and not e.paid and e.due_year == year
        ]

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        found = [
            DialogField(f"balance_{n}", "", "info", f"{label}: {words}")
            for n, (label, words) in enumerate(tribunal_sheet.balance_lines(tribunal))
        ]
        due = self._due(tribunal, meeting)
        if due:
            found.append(DialogField("due", "", "info", "Loans due: " + "; ".join(due)))
        return [*found, _note_field(meeting, self.key)]

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return (
            "The treasury's balance, and the loans that fall due this year.",
            "Nothing changes here: note anything paid or lent, and record it "
            "on the Treasury tab.",
        )

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        balance = [
            f"[$label]{escape(label)}:[/] {escape(words)}"
            for label, words in tribunal_sheet.balance_lines(tribunal)
        ]
        due = self._due(tribunal, meeting)
        return _join(
            *balance,
            f"[$label]Loans due:[/] {escape('; '.join(due))}" if due else "",
            _note_text(meeting, self.key),
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        due = self._due(tribunal, meeting)
        words = "The treasury was reckoned."
        if due:
            words += f" Loans due: {'; '.join(due)}."
        lines = tribunal_sheet.balance_lines(tribunal)
        return words, lines[0][1] if lines else ""


class Closing(Step):
    """Ends the meeting: each case with a ruling is decided, the meeting
    goes into the Diary, and the next one is set."""

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return [
            DialogField("what", "", "info", closing_text(saga, tribunal, meeting)),
            _note_field(meeting, self.key),
        ]

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return escape(closing_text(saga, tribunal, meeting))

    def save_label(self):
        return "Close"

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return (
            closing_text(saga, tribunal, meeting),
            "Closing ends the meeting; its steps can't be held again afterwards.",
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return (
            f"The Tribunal closed; it meets again in "
            f"{meeting.get('season', 'Summer')} {_next(tribunal, meeting)}.",
            "",
        )


#: The Grand Tribunal meets every 33 years, in 1228 and 1261 (Guardians of
#: the Forests p. 140).
GRAND_TRIBUNAL_EVERY, GRAND_TRIBUNAL_YEAR = 33, 1228


def grand_tribunal_year(year: int) -> bool:
    return (year - GRAND_TRIBUNAL_YEAR) % GRAND_TRIBUNAL_EVERY == 0


def _next(tribunal: Tribunal, meeting: Meeting) -> int:
    """The next meeting's year: its interval on, a year earlier if that is
    a Grand Tribunal's year and the Tribunal's customs say so."""
    year = int(meeting.get("year") or 0) + max(1, tribunal.meets_every)
    if tribunal_packages.of(tribunal).skips_grand_tribunal and grand_tribunal_year(
        year
    ):
        return year - 1
    return year


def closing_text(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> str:
    """What closing the meeting does."""
    decided = sum(bool(c.outcome.strip()) for c in tribunal_sheet.open_cases(tribunal))
    words = f"{decided} case{'' if decided == 1 else 's'}"
    return (
        f"Closing ends the meeting: {words} with a ruling are decided (their "
        f"fines owed to the treasury, and into the Code as the rulings say), "
        f"the Acta goes into the Diary, and the next meeting is set for "
        f"{meeting.get('season', 'Summer')} {_next(tribunal, meeting)}."
    )


#: The package steps the core knows how to hold, by name: what the list
#: calls each, its kind, and when it is held: on the first day after the
#: attendance ("opening"), or on the last day before the rulings ("end")
#: or just before the closing ("closing").
_PACKAGE_STEPS: dict[str, tuple[str, type[Step], str]] = {
    "elections": ("Elections", Elections, "end"),
    "succession": ("The Praeco's succession", Succession, "opening"),
    "host_by_lot": ("The next host, by lot", HostByLot, "closing"),
}


#: The steps that fill the Tribunal's offices, so the Acta lists them.
OFFICE_STEPS = {"elections", "sortition", "archon_polemarch"}


def register_step(name: str, title: str, kind: type[Step], when: str) -> None:
    """Makes a package's own step one the meeting can hold, under the name
    its package lists in meeting_steps."""
    _PACKAGE_STEPS[name] = (title, kind, when)


def steps(tribunal: Tribunal, meeting: Meeting) -> list[Step]:
    """The order of business, in the order it is held."""
    last = days(meeting)
    added: dict[str, list[Step]] = {"opening": [], "end": [], "closing": []}
    for name in tribunal_packages.of(tribunal).meeting_steps:
        title, kind, when = _PACKAGE_STEPS.get(name, (name.title(), Step, "end"))
        added[when].append(kind(name, title, 1 if when == "opening" else last))
    found: list[Step] = [
        Attendance("attendance", "The roll call and proxies", 1),
        Opening("opening", "Opening and the oaths", 1),
        *added["opening"],
    ]
    cases = sorted(
        tribunal_sheet.open_cases(tribunal), key=lambda c: day_of(meeting, c)
    )
    for case in cases:
        found.append(Hearing(case, day_of(meeting, case)))
        if not settled(meeting, case):
            found.append(Vote(case, day_of(meeting, case)))
    found += [
        *added["end"],
        Rulings("rulings", "Rulings and fines", last),
        Treasury("treasury", "Treasury and vis", last),
        *added["closing"],
        Closing("closing", "Closing", last),
    ]
    return found


def held(meeting: Meeting, step: Step) -> bool:
    return step.key in meeting.get("done", [])


def current(tribunal: Tribunal, meeting: Meeting) -> Step:
    """The step in hand: the first not yet held."""
    found = steps(tribunal, meeting)
    return next((s for s in found if not held(meeting, s)), found[-1])


def now_text(tribunal: Tribunal, meeting: Meeting) -> str:
    """ "The Second Day › Fengheld v. Arnhaven"."""
    step = current(tribunal, meeting)
    return f"{day_name(step.day)} › {step.title}"


# -- holding a step --


def _when(saga: Saga, meeting: Meeting) -> tuple[int, str]:
    return int(meeting.get("year") or saga.current_year), meeting.get("season", "")


def write_minutes(saga: Saga, tribunal: Tribunal, meeting: Meeting, step: Step) -> None:
    """The step's minutes, one Diary entry a step with its numbers in the
    margin; holding a step again rewrites its entry."""
    words, margin = step.minutes(saga, tribunal, meeting)
    note = meeting.get("notes", {}).get(step.key, "")
    words = " ".join(w for w in (words, note) if w)
    if not words:
        return
    year, season = _when(saga, meeting)
    title = f"¶ {day_name(step.day)}: {step.title}"
    written = meeting.setdefault("minutes", {})
    entry = next((e for e in tribunal.diary if e.id == written.get(step.key)), None)
    if entry is None:
        entry = TribunalDiaryEntry(year, season)
        tribunal.diary.append(entry)
        written[step.key] = entry.id
    entry.title, entry.details, entry.margin = title, words, margin


#: What is told when a step is held (Observer): each gets the step just
#: held, after it is marked held. The minutes are the first.
LISTENERS: list[Callable[[Saga, Tribunal, Meeting, Step], None]] = [write_minutes]


def _decide(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> None:
    """Each case with a ruling is decided, and what its ruling says is
    written: the Peripheral Code, the fine owed to the treasury, and the
    party's attitude."""
    year, season = _when(saga, meeting)
    for case in tribunal_sheet.open_cases(tribunal):
        if not case.outcome.strip():
            continue
        case.status = CASE_DECIDED
        kept = ruling_of(meeting, case)
        if kept.get("term"):
            case.term_ends_year = year + int(kept["term"])
            case.term_ends_season = season or "Summer"
            case.term_docketed = False
        if kept.get("code"):
            tribunal.rulings.append(Ruling(case.title, year, case.outcome, case.id))
        if kept.get("fine"):
            art = kept.get("art") or ""
            tribunal.treasury.append(
                TreasuryEntry(
                    "fine" if art else "silver",
                    kept["fine"],
                    art=art,
                    who=kept.get("who", ""),
                    case_id=case.id,
                    note="" if art else "a fine, owed",
                )
            )
        change = int(kept.get("attitude") or 0)
        pair = parties(saga, case)
        if change and pair is not None:
            other, player = pair
            attitude = world.attitude_toward(other, player.id)
            if attitude is None:
                attitude = Attitude(player.id, 0)
                other.attitudes.append(attitude)
            attitude.reasons.append(
                Reason(f"Ruled on at Tribunal: {case.title}", change, year, season)
            )


def acta_text(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> str:
    """The Acta, built from the meeting (acta.ActaBuilder)."""
    year, season = _when(saga, meeting)
    builder = acta.ActaBuilder().heading(
        tribunals.title(tribunal), meeting.get("place", ""), season, year
    )
    attending = [
        c.name
        for c in tribunals.covenants_of(saga, tribunal)
        if sum(present(saga, tribunal, meeting, c)) > 0
    ]
    builder.attendance(attending, present_text(saga, tribunal, meeting))
    for case in tribunal_sheet.open_cases(tribunal):
        if case.outcome.strip():
            kept = ruling_of(meeting, case)
            fine = fine_text(kept) if kept.get("fine") else ""
            builder.ruling(case.title, case.outcome, fine, kept.get("who", ""))
    if OFFICE_STEPS & set(meeting.get("done", [])):
        for office in tribunal_packages.entries(tribunal, tribunal.package, "archai"):
            holder = saga.character(office.get("holder_id"))
            if holder is not None:
                term = office.get("term_ends")
                builder.office(
                    office.get("office") or "to an office",
                    holder.name,
                    str(term) if term else "",
                )
    witnesses = [
        c.name
        for c in (
            saga.character(tribunal.praeco_id),
            saga.character(tribunal.quaesitor_id),
        )
        if c is not None
    ]
    return builder.witnesses(witnesses).text()


def _close(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> None:
    """The meeting ends: its rulings are written, the Acta goes into the
    Diary, and the next meeting is set."""
    year, season = _when(saga, meeting)
    text = acta_text(saga, tribunal, meeting)
    _decide(saga, tribunal, meeting)
    tribunal.diary.append(
        TribunalDiaryEntry(
            year, season, acta.title(tribunals.title(tribunal), season, year), text
        )
    )
    tribunal.next_year = _next(tribunal, meeting)
    tribunal.next_season = meeting.get("season") or tribunal.next_season
    tribunal.meeting = None


def position(
    tribunal: Tribunal, meeting: Meeting, step: Step
) -> tuple[int, int, Step | None]:
    """Where `step` stands in the order of business: its number, how many
    steps there are, and the next one (None after the last)."""
    found = steps(tribunal, meeting)
    keys = [s.key for s in found]
    index = keys.index(step.key) if step.key in keys else len(found) - 1
    following = found[index + 1] if index + 1 < len(found) else None
    return index + 1, len(found), following


def next_step(tribunal: Tribunal, meeting: Meeting, step: Step) -> Step | None:
    """The step holding `step` leads to: the one after it, or (when that
    was held already) the step in hand; None after the Closing."""
    if isinstance(step, Closing):
        return None
    _number, _count, following = position(tribunal, meeting, step)
    if following is not None and not held(meeting, following):
        return following
    in_hand = current(tribunal, meeting)
    if held(meeting, in_hand) or in_hand.key == step.key:
        return None
    return in_hand


def guide_lines(
    saga: Saga,
    tribunal: Tribunal,
    meeting: Meeting,
    step: Step,
    markup: bool = True,
) -> list[str]:
    """What the app works out at `step` and what your entries change: the
    details panel's markup lines, or (`markup` False) the form head's
    plain ones."""
    worked, entered = step.guide(saga, tribunal, meeting)

    def line(head: str, words: str) -> str:
        if not words:
            return ""
        return f"[b]{head}[/] {escape(words)}" if markup else f"{head} {words}"

    return [
        found
        for found in (
            line("Worked out for you:", worked),
            line("What you enter changes:", entered),
        )
        if found
    ]


def _intro(
    saga: Saga, tribunal: Tribunal, meeting: Meeting, step: Step
) -> list[DialogField]:
    """The head of a step's form: where it stands and what follows, then
    its guide."""
    number, count, _following = position(tribunal, meeting, step)
    following = next_step(tribunal, meeting, step)
    if isinstance(step, Closing):
        then = "Closing ends the meeting."
    elif following is None:
        then = "Saving holds it."
    else:
        then = (
            f"Saving holds it and opens the next: {following.title}. "
            "Cancel to stop; the meeting waits at the step in hand."
        )
    lines = guide_lines(saga, tribunal, meeting, step, markup=False)
    return [
        DialogField("_where", "", "info", f"Step {number} of {count}. {then}"),
        *(DialogField(f"_guide_{i}", "", "info", line) for i, line in enumerate(lines)),
    ]


def _then(step: Any, after: Callable[[], Any]) -> Any:
    """`step`, with `after()` run once it and every form it leads to are
    saved (None: at once)."""
    if step is None:
        return after()
    if isinstance(step, Form):
        inner = step.apply
        return replace(step, apply=lambda values: _then(inner(values), after))
    return step


def step_form(
    saga: Saga,
    tribunal: Tribunal,
    step: Step,
    meeting: Meeting | None = None,
) -> Form:
    """Hold `step` of the meeting being held (or of `meeting`, a new one
    its roll call begins): its form; on saving it (and any form it asks
    next, such as a ruling's blanks) the step is marked held and the next
    step's form opens (commands.Then); the Closing ends the meeting."""
    record = meeting if meeting is not None else tribunal.meeting
    assert record is not None

    def go_on() -> Any:
        if tribunal.meeting is None:
            return None
        following = next_step(tribunal, record, step)
        return Then(step_form(saga, tribunal, following)) if following else None

    def apply(values: dict[str, Any]) -> Any:
        tribunal.meeting = record
        asked = step.apply(saga, tribunal, record, values)
        done = record.setdefault("done", [])
        if step.key not in done:
            done.append(step.key)
        for listener in LISTENERS:
            listener(saga, tribunal, record, step)
        if isinstance(step, Closing):
            _close(saga, tribunal, record)
        return _then(asked, go_on)

    number, count, _following = position(tribunal, record, step)
    heading = (
        f"Hold Tribunal: {tribunals.title(tribunal)}"
        if meeting is not None
        else f"Step {number} of {count}: {day_name(step.day)}, {step.title}"
    )
    return Form(
        heading,
        lambda: [
            *_intro(saga, tribunal, record, step),
            *step.fields(saga, tribunal, record),
        ],
        apply,
        validate=lambda values: step.validate(record, values),
        live=lambda values: step.live(saga, tribunal, record, values),
        save_label=step.save_label(),
        help_id="hold-tribunal",
    )


def hold(saga: Saga, tribunal: Tribunal) -> Command:
    """Hold Tribunal: the step in hand, or (with no meeting being held)
    a new meeting's Opening; cancelling that holds none."""
    if tribunal.meeting is not None:
        return step_form(saga, tribunal, current(tribunal, tribunal.meeting))
    meeting = _begin(saga, tribunal)
    return step_form(saga, tribunal, steps(tribunal, meeting)[0], meeting)


# -- what the hall shows --


def record(saga: Saga, tribunal: Tribunal) -> Meeting:
    """The meeting being held, or the one Hold Tribunal would open (not
    kept): what the hall shows before it opens."""
    return tribunal.meeting if tribunal.meeting is not None else _begin(saga, tribunal)


def title(saga: Saga, tribunal: Tribunal) -> str:
    """ "The Meeting: Summer 1228", or "The Next Meeting: Summer 1228"."""
    meeting = record(saga, tribunal)
    words = "The Meeting" if tribunal.meeting is not None else "The Next Meeting"
    return f"{words}: {meeting.get('season', '')} {meeting.get('year', '')}"


def facts(saga: Saga, tribunal: Tribunal) -> list[Fact]:
    """Where it is held, the step in hand and the one after it, how to go
    on, the votes in the hall and the quorum."""
    meeting = record(saga, tribunal)
    held_at = meeting.get("place") or "(not set)"
    if tribunal.meeting is None:
        return [
            Fact("Held at", held_at),
            Fact("Now", "Not yet opened: Edit (e) calls the roll and opens it"),
        ]
    step = current(tribunal, meeting)
    number, count, _following = position(tribunal, meeting, step)
    following = next_step(tribunal, meeting, step)
    return [
        Fact("Held at", held_at),
        Fact("Now", f"Step {number} of {count}: {now_text(tribunal, meeting)}"),
        Fact(
            "Then",
            following.title if following is not None else "the meeting closes",
        ),
        Fact("To go on", "Edit (e) holds the step in hand; each opens the next"),
        Fact("Present", present_text(saga, tribunal, meeting)),
        Fact("Quorum", quorum(saga, tribunal, meeting)),
    ]


def business_title(saga: Saga, tribunal: Tribunal) -> str:
    count = days(record(saga, tribunal))
    return f"Order of Business ({count} day{'' if count == 1 else 's'})"


def business_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each step and its day (named on the day's first step): held ✓,
    the one in hand ▶, the rest to come."""
    meeting = record(saga, tribunal)
    found = steps(tribunal, meeting)
    now = current(tribunal, meeting).key if tribunal.meeting is not None else None
    rows: list[list[str]] = []
    styles: dict[tuple[int, int], str] = {}
    shown_day = 0
    for index, step in enumerate(found):
        if held(meeting, step):
            mark = "✓ held"
        elif step.key == now:
            mark = "▶ in hand"
            for column in range(3):
                styles[(index, column)] = "b"
        else:
            mark = ""
        day = day_name(step.day) if step.day != shown_day else ""
        rows.append([step.title, day, mark])
        shown_day = step.day
    return Grid(
        ["Step", "Day", ""],
        rows,
        list(range(len(rows))),
        "",
        styles,
        caps=[44, 17, 9],
    )


def attendance_title(saga: Saga, tribunal: Tribunal) -> str:
    votes, _ = hall(saga, tribunal, record(saga, tribunal))
    return f"Attendance ({votes} vote{'' if votes == 1 else 's'} in the hall)"


def attendance_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each covenant's magi, those absent, the proxies it carries and the
    votes it has in the hall."""
    meeting = record(saga, tribunal)
    credential = tribunal_packages.of(tribunal).credential
    rows = []
    for covenant in tribunals.covenants_of(saga, tribunal):
        proxies = carried(tribunal, meeting, covenant)
        magi, allowed = present(saga, tribunal, meeting, covenant)
        set_aside = proxies and ruling(meeting, covenant) == SET_ASIDE
        votes = str(magi + allowed)
        if not shows(saga, tribunal, meeting, covenant):
            votes = f"0, no {credential}"
        rows.append(
            [
                covenant.name,
                str(world.votes(saga, covenant)),
                str(absent(saga, meeting, covenant) or ""),
                f"{proxies} (set aside)" if set_aside else str(proxies or ""),
                votes,
            ]
        )
    return Grid(
        ["Covenant", "Magi", "Absent", "Proxies", "Votes"],
        rows,
        list(range(len(rows))),
        "No covenant belongs to this Tribunal yet.",
        caps=[22, 4, 6, 13, 0],
    )


def vote_case(saga: Saga, tribunal: Tribunal) -> Case | None:
    """The case the Vote section shows: the one in hand (its debate or
    its vote), else the last voted on, else the first to be heard."""
    meeting = record(saga, tribunal)
    cases = tribunal_sheet.open_cases(tribunal)
    if not cases:
        return None
    if tribunal.meeting is not None:
        now = current(tribunal, meeting)
        if isinstance(now, (Hearing, Vote)):
            return now.case
        voted = [c for c in cases if c.id in meeting.get("votes", {})]
        if voted:
            return voted[-1]
    return min(cases, key=lambda c: day_of(meeting, c))


def vote_title(saga: Saga, tribunal: Tribunal) -> str:
    case = vote_case(saga, tribunal)
    if case is None:
        return "The Vote"
    votes, _ = hall(saga, tribunal, record(saga, tribunal))
    return f"The Vote: {case.title} ({votes})"


def vote_grid(saga: Saga, tribunal: Tribunal, *, tally_row: bool = False) -> Grid:
    """Each covenant as the Praeco calls it: its votes for, against and
    undecided, and those the debate swayed; then (`tally_row`) the
    tally, for a front-end that draws no bar under it."""
    case = vote_case(saga, tribunal)
    meeting = record(saga, tribunal)
    rows: list[list[str]] = []
    styles: dict[tuple[int, int], str] = {}
    called = list(call_the_vote(saga, tribunal, meeting, case)) if case else []
    for index, c in enumerate(called):
        note = ""
        if case is not None and _party(c.covenant, case.brought_by):
            note = "brings it"
        elif case is not None and _party(c.covenant, case.against):
            note = "defends"
        if c.swayed:
            note = _join_words(note, f"{c.swayed} swayed")
            styles[(index, 5)] = "$warning"
        rows.append(
            [
                c.covenant.name,
                str(c.votes),
                str(c.yes or "·"),
                str(c.no or "·"),
                str(c.abstain or "·"),
                note,
            ]
        )
    keys: list[int | None] = list(range(len(rows)))
    if called and tally_row:
        yes, no, abstain = called[-1].tally
        rows.append(
            ["Tally", str(yes + no + abstain), str(yes), str(no), str(abstain), ""]
        )
        keys.append(None)
        for column in range(6):
            styles[(len(rows) - 1, column)] = "b"
    return Grid(
        ["Covenant", "Votes", "For", "Against", "Undecided", "Note"],
        rows,
        keys,
        "No case to vote on.",
        styles,
        caps=[22, 5, 3, 7, 9, 24],
    )


def _join_words(first: str, second: str) -> str:
    return f"{first}; {second}" if first else second


def vote_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    """Edit holds the vote on the case the section shows (opening the
    meeting first if it isn't open)."""

    def edit(_row: int) -> Command:
        case = vote_case(saga, tribunal)
        if tribunal.meeting is None or case is None:
            return hold(saga, tribunal)
        step = next(
            s for s in steps(tribunal, tribunal.meeting) if s.key == f"vote:{case.id}"
        )
        return step_form(saga, tribunal, step)

    return SectionOps(
        edit=edit,
        rows=lambda: [c.name for c in voters(saga, tribunal, record(saga, tribunal))],
    )


def step_text(saga: Saga, tribunal: Tribunal, index: int | None) -> str:
    """The details panel: the chosen step, what was entered at it and
    what it worked out."""
    meeting = record(saga, tribunal)
    found = steps(tribunal, meeting)
    if index is None or index >= len(found):
        return "[$label]Choose a step to read what was entered at it.[/]"
    step = found[index]
    if tribunal.meeting is None:
        state = "the meeting is not yet open"
    else:
        state = "held" if held(meeting, step) else "to come"
    heading = f"[b]{escape(step.title)}[/]  {day_name(step.day)}, {state}"
    body = step.text(saga, tribunal, meeting) if tribunal.meeting is not None else ""
    return _join(
        heading,
        body or "[$label]Hold it with Edit (e).[/]",
        *guide_lines(saga, tribunal, meeting, step),
    )


def business_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    """Edit holds the chosen step (again, if it was held; with no meeting
    open, the Opening); Delete abandons the meeting, keeping what its
    steps changed."""

    def edit(row: int) -> Command:
        if tribunal.meeting is None:
            return hold(saga, tribunal)
        found = steps(tribunal, tribunal.meeting)
        return step_form(saga, tribunal, found[min(row, len(found) - 1)])

    def remove(_row: int) -> Command:
        if tribunal.meeting is None:
            return Refuse("Abandon", "No meeting is being held.")

        def apply() -> None:
            tribunal.meeting = None

        return Confirm(
            "Abandon this meeting? What its steps changed stays as it is.",
            apply,
            yes_label="Abandon",
        )

    return SectionOps(
        edit=edit,
        remove=remove,
        rows=lambda: [s.title for s in steps(tribunal, record(saga, tribunal))],
    )


def attendance_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    """Edit holds the roll call (which opens the meeting if it isn't
    open)."""

    def edit(_row: int) -> Command:
        if tribunal.meeting is None:
            return hold(saga, tribunal)
        roll = next(
            s for s in steps(tribunal, tribunal.meeting) if s.key == "attendance"
        )
        return step_form(saga, tribunal, roll)

    return SectionOps(
        edit=edit,
        rows=lambda: [c.name for c in tribunals.covenants_of(saga, tribunal)],
    )


def ops(saga: Saga, tribunal: Tribunal) -> dict[str, SectionOps]:
    """The hall's sections the core edits, by id."""
    return {
        BUSINESS_SECTION: business_ops(saga, tribunal),
        ATTENDANCE_SECTION: attendance_ops(saga, tribunal),
        VOTE_SECTION: vote_ops(saga, tribunal),
    }


# The packages' own steps register themselves with the meeting.
from . import (  # noqa: F401
    hibernia_meeting,
    rhine_meeting,
    theban_meeting,
    transylvania_meeting,
)
