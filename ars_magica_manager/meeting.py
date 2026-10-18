"""Holding a Tribunal: the meeting being held, kept on its Tribunal
(Tribunal.meeting) and saved after every step, so leaving it and holding
it again later resumes at the step in hand.

The steps run in a fixed order (Template Method: `Step` is the template,
each kind of step fills in its form and what it works out): the
Opening, Attendance and proxies, each case and motion on the day it is
heard, the package's own steps (the Theban elections), Rulings and
fines, Treasury and vis, and the Closing, which writes the meeting into
the Tribunal's Diary and ends it. A package can add a step, never
reorder the rest.

The record is a plain dict, so a save holds it as it is:
{"year", "season", "place", "days", "done": [step keys held],
"day_of": {case id: day}, "attendance": {covenant id: {"absent",
"proxies", "ruling"}}, "notes": {step key: words}}."""

from __future__ import annotations

import itertools
import random
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any

from . import acta, tribunal_packages, tribunal_sheet, tribunals, world
from .arts import ARTS
from .character_sheet import Fact
from .commands import Command, Confirm, Form, Refuse, SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import (
    CASE_DECIDED,
    CASE_OPEN,
    Attitude,
    Case,
    Character,
    Covenant,
    Reason,
    Ruling,
    Saga,
    TreasuryEntry,
    Tribunal,
    TribunalDiaryEntry,
)
from .rules import debate
from .sections import ATTENDANCE_SECTION, BUSINESS_SECTION, VOTE_SECTION

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


def _begin(saga: Saga, tribunal: Tribunal) -> dict[str, Any]:
    """A new meeting record: when the Tribunal is due to meet (or now),
    where, and its cases spread over the days but the last."""
    meeting: dict[str, Any] = {
        "year": tribunal.next_year
        if tribunal.next_year is not None
        else saga.current_year,
        "season": tribunal.next_season or saga.current_season,
        "place": tribunal.meeting_place.strip(),
        "days": DEFAULT_DAYS,
        "done": [],
        "day_of": {},
        "attendance": {},
        "notes": {},
    }
    meeting["day_of"] = _spread(business(tribunal), DEFAULT_DAYS)
    return meeting


def _spread(cases: list[Case], days: int) -> dict[str, int]:
    """Each case's day: spread in docket order over every day but the
    last, which is kept for the rulings and the closing."""
    open_days = max(1, days - 1)
    count = max(1, len(cases))
    return {c.id: 1 + i * open_days // count for i, c in enumerate(cases)}


def business(tribunal: Tribunal) -> list[Case]:
    """The cases and motions the meeting hears: those still open."""
    return [c for c in tribunal.cases if c.status == CASE_OPEN]


def days(meeting: dict[str, Any]) -> int:
    return max(1, int(meeting.get("days") or DEFAULT_DAYS))


def day_of(meeting: dict[str, Any], case: Case) -> int:
    """The day `case` is heard: as the Opening set it, else the first."""
    day = meeting.get("day_of", {}).get(case.id, 1)
    return max(1, min(days(meeting), int(day)))


# -- attendance --


def _attendance(meeting: dict[str, Any], covenant: Covenant) -> dict[str, Any]:
    return meeting.get("attendance", {}).get(covenant.id, {})


def absent(meeting: dict[str, Any], covenant: Covenant) -> int:
    return int(_attendance(meeting, covenant).get("absent") or 0)


def carried(tribunal: Tribunal, meeting: dict[str, Any], covenant: Covenant) -> int:
    """The proxies `covenant` carries into the hall: as attendance
    recorded them, else as the Tribunal's roster holds them."""
    entry = _attendance(meeting, covenant)
    if "proxies" in entry:
        return int(entry.get("proxies") or 0)
    return tribunal_sheet.proxies(tribunal, covenant)


def ruling(meeting: dict[str, Any], covenant: Covenant) -> str:
    return _attendance(meeting, covenant).get("ruling") or ALLOWED


def present(
    saga: Saga, tribunal: Tribunal, meeting: dict[str, Any], covenant: Covenant
) -> tuple[int, int]:
    """`covenant`'s votes in the hall: its magi present, and the proxies
    it carries that the Quaesitor allowed."""
    magi = max(0, world.votes(saga, covenant) - absent(meeting, covenant))
    proxies = carried(tribunal, meeting, covenant)
    allowed = proxies if ruling(meeting, covenant) == ALLOWED else 0
    return magi, allowed


def hall(saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> tuple[int, int]:
    """Every vote in the hall, and how many of them are proxies."""
    magi = proxies = 0
    for covenant in tribunals.covenants_of(saga, tribunal):
        m, p = present(saga, tribunal, meeting, covenant)
        magi += m
        proxies += p
    return magi + proxies, proxies


def present_text(saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> str:
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


def _party(covenant: Covenant, words: str) -> bool:
    name = covenant.name.strip().casefold()
    return bool(name) and name in words.casefold()


def default_leaning(saga: Saga, case: Case, covenant: Covenant) -> str:
    """How a covenant leans on `case` before the debate: a party votes its
    own side; any other leans by its attitude toward a troupe covenant
    that is a party (Warm or better with it, Wary or worse against it),
    and is otherwise undecided."""
    if _party(covenant, case.brought_by):
        return FOR
    if _party(covenant, case.against):
        return AGAINST
    for player in world.player_covenants(saga):
        if player is covenant:
            continue
        side = FOR if _party(player, case.brought_by) else None
        if side is None and _party(player, case.against):
            side = AGAINST
        if side is None:
            continue
        score = world.attitude_score(world.attitude_toward(covenant, player.id))
        if score > 0:
            return side
        if score < 0:
            return AGAINST if side == FOR else FOR
    return UNDECIDED


def leanings(
    saga: Saga, tribunal: Tribunal, meeting: dict[str, Any], case: Case
) -> dict[str, str]:
    """Each covenant's leaning on `case`, by id: as the vote was held, else
    the defaults."""
    kept = meeting.get("votes", {}).get(case.id, {}).get("leanings", {})
    return {
        c.id: kept.get(c.id) or default_leaning(saga, case, c)
        for c in tribunals.covenants_of(saga, tribunal)
    }


def debate_of(meeting: dict[str, Any], case: Case) -> dict[str, Any] | None:
    return meeting.get("debates", {}).get(case.id)


def strength(meeting: dict[str, Any], case: Case) -> tuple[str | None, int]:
    """Who won the debate (FOR the prosecution or proposer, AGAINST the
    defence, None for none yet or a tie) and its Argument Strength,
    after a proposal's penalty."""
    held_debate = debate_of(meeting, case)
    if held_debate is None:
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
    """One covenant's votes as the Praeco calls it: how many for, against
    and abstaining, how many of them the debate swayed, and the tally of
    the hall so far."""

    covenant: Covenant
    votes: int
    yes: int
    no: int
    abstain: int
    swayed: int
    tally: tuple[int, int, int]


def call_the_vote(
    saga: Saga,
    tribunal: Tribunal,
    meeting: dict[str, Any],
    case: Case,
    leaning: dict[str, str] | None = None,
) -> Iterator[Called]:
    """The vote on `case`, covenant by covenant in the order of the roll
    (Iterator): each votes as it leans, with the votes the debate's victor
    won from the undecided and (from a Triumphant Victory) from its
    opponents taken from the first covenants called."""
    lean = leaning if leaning is not None else leanings(saga, tribunal, meeting, case)
    members = tribunals.covenants_of(saga, tribunal)
    hall_votes = {c.id: sum(present(saga, tribunal, meeting, c)) for c in members}
    side, margin = strength(meeting, case)
    hostile_side = AGAINST if side == FOR else FOR
    neutral = sum(v for cid, v in hall_votes.items() if lean[cid] == UNDECIDED)
    hostile = sum(v for cid, v in hall_votes.items() if lean[cid] == hostile_side)
    from_neutral, from_hostile = (
        debate.swayed(margin, neutral, hostile) if side else (0, 0)
    )
    tally = [0, 0, 0]
    for covenant in members:
        votes = hall_votes[covenant.id]
        leans = lean[covenant.id]
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
    meeting: dict[str, Any],
    case: Case,
    leaning: dict[str, str] | None = None,
) -> tuple[int, int, int]:
    """For, against and abstaining, once every covenant is called."""
    final = (0, 0, 0)
    for called in call_the_vote(saga, tribunal, meeting, case, leaning):
        final = called.tally
    return final


def vote_outcome(meeting: dict[str, Any], case: Case) -> str:
    """ "Carried, 9 to 7" or "Failed, 4 to 10", as the vote went ("" with
    no vote held)."""
    kept = meeting.get("votes", {}).get(case.id)
    if kept is None:
        return ""
    word = "Carried" if kept["for"] > kept["against"] else "Failed"
    return f"{word}, {kept['for']} to {kept['against']}"


def tally_text(votes: tuple[int, int, int]) -> str:
    """ "For 9, against 10, 4 abstaining: it fails"."""
    yes, no, abstain = votes
    verdict = "it is carried" if yes > no else "it fails"
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
    list calls it and the day it is held. `fields`, `apply` and `text`
    are the parts each kind fills in; holding a step (`hold`) is the
    same for all: its form, then the step marked held and the record
    saved with the saga."""

    key: str
    title: str
    day: int

    def fields(
        self, saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]
    ) -> list[DialogField]:
        return [_note_field(meeting, self.key)]

    def validate(self, meeting: dict[str, Any], values: dict[str, Any]) -> str | None:
        return None

    def apply(
        self,
        saga: Saga,
        tribunal: Tribunal,
        meeting: dict[str, Any],
        values: dict[str, Any],
    ) -> None:
        _keep_note(meeting, self.key, values)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> str:
        return _note_text(meeting, self.key)

    def save_label(self) -> str:
        return "Hold"

    def minutes(
        self, saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]
    ) -> tuple[str, str]:
        """What the minutes say of the step, and the numbers set in their
        margin (the step's Note is added to them)."""
        return "", ""

    def live(
        self,
        saga: Saga,
        tribunal: Tribunal,
        meeting: dict[str, Any],
        values: dict[str, Any],
    ) -> str:
        """A line kept up to date under the form as it is filled in ("":
        none)."""
        return ""


def _note_field(meeting: dict[str, Any], key: str) -> DialogField:
    return DialogField(
        "note",
        "Note",
        "area",
        meeting.get("notes", {}).get(key, ""),
        hint="Anything said or decided at this step, in your own words.",
    )


def _keep_note(meeting: dict[str, Any], key: str, values: dict[str, Any]) -> None:
    note = (values.get("note") or "").strip()
    notes = meeting.setdefault("notes", {})
    if note:
        notes[key] = note
    else:
        notes.pop(key, None)


def _note_text(meeting: dict[str, Any], key: str) -> str:
    note = meeting.get("notes", {}).get(key, "")
    return f"[$label]Note:[/] {escape(note)}" if note else ""


def _join(*parts: str) -> str:
    return "\n".join(p for p in parts if p)


class Opening(Step):
    """The day count, where it is held, and the day each case is heard."""

    def fields(self, saga, tribunal, meeting):
        cases = business(tribunal)
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

    def validate(self, meeting, values):
        count = values.get("days") or 0
        if count < 1:
            return "A meeting lasts at least a day."
        for key, value in values.items():
            if key.startswith("day_") and not 1 <= (value or 0) <= count:
                return f"Each case is heard on a day from 1 to {count}."
        return None

    def apply(self, saga, tribunal, meeting, values):
        meeting["place"] = values.get("place", "")
        meeting["days"] = values["days"]
        meeting["day_of"] = {
            key.removeprefix("day_"): value
            for key, value in values.items()
            if key.startswith("day_")
        }

    def text(self, saga, tribunal, meeting):
        roll = ", ".join(c.name for c in tribunals.covenants_of(saga, tribunal))
        return _join(
            f"[$label]Held at:[/] {escape(meeting.get('place') or '(not set)')}",
            f"[$label]Days:[/] {days(meeting)}",
            f"[$label]The roll of covenants:[/] {escape(roll or '(none recorded)')}",
        )

    def save_label(self):
        return "Open"

    def minutes(self, saga, tribunal, meeting):
        roll = ", ".join(c.name for c in tribunals.covenants_of(saga, tribunal))
        place = meeting.get("place") or ""
        at = f" at {place}" if place else ""
        count = days(meeting)
        words = f"The Tribunal opened{at} and the oaths were sworn."
        if roll:
            words += f" The roll of covenants was read: {roll}."
        return words, f"{count} day{'' if count == 1 else 's'}"


class Attendance(Step):
    """Who is absent and the proxies each covenant carries, with the
    Presiding Quaesitor's ruling on them."""

    def fields(self, saga, tribunal, meeting):
        found: list[DialogField] = []
        for covenant in tribunals.covenants_of(saga, tribunal):
            cid = covenant.id
            magi = world.votes(saga, covenant)
            name = covenant.name
            found += [
                DialogField(
                    f"absent_{cid}",
                    f"{name}: absent",
                    "int",
                    absent(meeting, covenant),
                    hint=f"Of its {magi} {'magus' if magi == 1 else 'magi'}.",
                ),
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

    def validate(self, meeting, values):
        if any(
            (v or 0) < 0
            for k, v in values.items()
            if k.startswith(("absent_", "proxies_"))
        ):
            return "Absent magi and proxies can't be fewer than none."
        return None

    def apply(self, saga, tribunal, meeting, values):
        attendance = meeting.setdefault("attendance", {})
        for covenant in tribunals.covenants_of(saga, tribunal):
            cid = covenant.id
            proxies = values.get(f"proxies_{cid}") or 0
            attendance[cid] = {
                "absent": min(
                    values.get(f"absent_{cid}") or 0, world.votes(saga, covenant)
                ),
                "proxies": proxies,
                "ruling": values.get(f"ruling_{cid}") or ALLOWED,
            }
            if proxies:
                tribunal.proxies[cid] = proxies
            else:
                tribunal.proxies.pop(cid, None)

    def text(self, saga, tribunal, meeting):
        return f"[$label]Present:[/] {escape(present_text(saga, tribunal, meeting))}"

    def minutes(self, saga, tribunal, meeting):
        lines = []
        for covenant in tribunals.covenants_of(saga, tribunal):
            gone = absent(meeting, covenant)
            if gone:
                lines.append(f"{covenant.name}: {gone} absent.")
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


class Hearing(Step):
    """A charge or appeal debated between its prosecutor and defender, or
    a motion between one who speaks for it and one against: their names
    (taken from the case), the rounds the praeco allows, and each side's
    debate Fatigue levels lost, entered or (left blank) rolled by the
    Societates rules with the case's evidence as the prosecution's
    testimony."""

    def __init__(self, case: Case, day: int) -> None:
        motion = case.kind == "motion"
        title = f"Motion: {case.title}" if motion else case.title
        super().__init__(f"case:{case.id}", title, day)
        self.case = case

    def fields(self, saga, tribunal, meeting):
        case = self.case
        motion = case.kind == "motion"
        kept = debate_of(meeting, case) or {}
        found = [
            DialogField(
                "prosecutor",
                "Speaks for it" if motion else "Prosecutor",
                "text",
                case.prosecutor or case.brought_by,
                required=True,
            ),
            DialogField(
                "defender",
                "Speaks against it" if motion else "Defender",
                "text",
                case.defender or ("" if motion else case.against),
                required=True,
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
        found += [
            DialogField(
                "rounds",
                "Rounds",
                "int",
                kept.get("rounds") or debate.DEFAULT_ROUNDS,
                required=True,
                hint=f"The praeco allows 1 to {debate.MAX_ROUNDS}; a side "
                f"that loses {debate.KNOCKED_OUT} levels ends it.",
            ),
            DialogField(
                "defence_testimony",
                "Defence testimony",
                "area",
                kept.get("defence_testimony", ""),
                hint="One a line, as the case's Evidence is for the "
                "prosecution: a peer's +3, an apprentice's +2, any other "
                "+1, and +3 more if a Quaesitor examined it.",
            ),
            DialogField(
                "lost_for",
                "Levels lost (for)",
                "optint",
                kept.get("lost", [None, None])[0] if kept.get("entered") else None,
                hint="Leave both blank to roll the debate.",
            ),
            DialogField(
                "lost_against",
                "Levels lost (against)",
                "optint",
                kept.get("lost", [None, None])[1] if kept.get("entered") else None,
            ),
        ]
        return [*found, _note_field(meeting, self.key)]

    def validate(self, meeting, values):
        if not 1 <= (values.get("rounds") or 0) <= debate.MAX_ROUNDS:
            return f"A debate runs 1 to {debate.MAX_ROUNDS} rounds."
        entered = [values.get("lost_for"), values.get("lost_against")]
        if (entered[0] is None) != (entered[1] is None):
            return "Enter both sides' levels lost, or neither to roll."
        if any(v is not None and not 0 <= v <= debate.KNOCKED_OUT for v in entered):
            return f"A side loses 0 to {debate.KNOCKED_OUT} levels."
        return None

    def apply(self, saga, tribunal, meeting, values):
        case = self.case
        case.prosecutor = values.get("prosecutor", "")
        case.defender = values.get("defender", "")
        defence = values.get("defence_testimony", "")
        record = {
            "rounds": values["rounds"],
            "defence_testimony": defence,
            "proposal": values.get("proposal", ""),
        }
        if values.get("lost_for") is not None:
            record |= {
                "lost": [values["lost_for"], values["lost_against"]],
                "entered": True,
                "lines": [],
            }
        else:
            sides = (
                debate.debater(case.prosecutor, _character(saga, case.prosecutor)),
                debate.debater(case.defender, _character(saga, case.defender)),
            )
            testimony = (
                [debate.testimony_bonus(e) for e in _lines(case.evidence)],
                [debate.testimony_bonus(e) for e in _lines(defence)],
            )
            held = debate.run(sides, testimony, values["rounds"], rng())
            record |= {"lost": held.lost, "entered": False, "lines": held.lines}
        meeting.setdefault("debates", {})[case.id] = record
        _keep_note(meeting, self.key, values)

    def text(self, saga, tribunal, meeting):
        # The details panel names the step: the case's own heading goes.
        lines = tribunal_sheet.case_text(saga, tribunal, self.case).split("\n")
        return _join(
            debate_text(meeting, self.case),
            *lines[1:],
            _note_text(meeting, self.key),
        )

    def minutes(self, saga, tribunal, meeting):
        case = self.case
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


def debate_text(meeting: dict[str, Any], case: Case) -> str:
    """The debate's outcome, and each round as it went."""
    held_debate = debate_of(meeting, case)
    if held_debate is None:
        return ""
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
    swayed, and the tally as each covenant is called."""

    def __init__(self, case: Case, day: int) -> None:
        super().__init__(f"vote:{case.id}", f"The vote: {case.title}", day)
        self.case = case

    def fields(self, saga, tribunal, meeting):
        lean = leanings(saga, tribunal, meeting, self.case)
        return [
            *(
                DialogField(
                    f"lean_{c.id}",
                    f"{c.name}: leans",
                    "select",
                    lean[c.id],
                    options=pairs(LEANINGS),
                    required=True,
                )
                for c in tribunals.covenants_of(saga, tribunal)
            ),
            _note_field(meeting, self.key),
        ]

    def _leaning(self, saga, tribunal, values) -> dict[str, str]:
        return {
            c.id: values.get(f"lean_{c.id}") or UNDECIDED
            for c in tribunals.covenants_of(saga, tribunal)
        }

    def live(self, saga, tribunal, meeting, values) -> str:
        votes = tally(
            saga, tribunal, meeting, self.case, self._leaning(saga, tribunal, values)
        )
        return escape(tally_text(votes))

    def apply(self, saga, tribunal, meeting, values):
        lean = self._leaning(saga, tribunal, values)
        yes, no, abstain = tally(saga, tribunal, meeting, self.case, lean)
        meeting.setdefault("votes", {})[self.case.id] = {
            "leanings": lean,
            "for": yes,
            "against": no,
            "abstain": abstain,
        }
        _keep_note(meeting, self.key, values)

    def text(self, saga, tribunal, meeting):
        kept = meeting.get("votes", {}).get(self.case.id)
        if kept is None:
            return ""
        votes = (kept["for"], kept["against"], kept["abstain"])
        return _join(
            f"[$label]The vote:[/] {escape(tally_text(votes))}.",
            _note_text(meeting, self.key),
        )

    def minutes(self, saga, tribunal, meeting):
        kept = meeting.get("votes", {}).get(self.case.id)
        if kept is None:
            return "", ""
        votes = (kept["for"], kept["against"], kept["abstain"])
        margin = f"{votes[0]}–{votes[1]}"
        if votes[2]:
            margin += f", {votes[2]} abst."
        return f"The vote on {self.case.title}: {tally_text(votes)}.", margin


class Elections(Step):
    """The Tribunal's offices, each given a holder and a term (only when
    its customs have offices: the Theban archai)."""

    def _offices(self, tribunal: Tribunal) -> list[dict[str, Any]]:
        return tribunal_packages.entries(tribunal, tribunal.package, "archai")

    def fields(self, saga, tribunal, meeting):
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

    def apply(self, saga, tribunal, meeting, values):
        for index, office in enumerate(self._offices(tribunal)):
            if f"holder_{index}" in values:
                office["holder_id"] = values[f"holder_{index}"]
                office["term_ends"] = values.get(f"term_{index}")
        _keep_note(meeting, self.key, values)

    def minutes(self, saga, tribunal, meeting):
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

    def fields(self, saga, tribunal, meeting):
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

    def apply(self, saga, tribunal, meeting, values):
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

    def text(self, saga, tribunal, meeting):
        praeco = saga.character(tribunal.praeco_id)
        if praeco is None:
            return _join("[$label]Praeco:[/] vacant", _note_text(meeting, self.key))
        return _join(
            f"[$label]Praeco:[/] {escape(praeco.name)}", _note_text(meeting, self.key)
        )

    def save_label(self):
        return "Name"

    def minutes(self, saga, tribunal, meeting):
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

    def _lot(
        self, saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]
    ) -> list[str]:
        """The two draws (the lot and its one redraw), made once and kept
        with the meeting so the form shows the same each time."""
        ids = [c.id for c in lot_choices(saga, tribunal)]
        drawn = [i for i in meeting.get("lot", []) if i in ids]
        if len(drawn) < 2 and ids:
            drawn = [random.choice(ids), random.choice(ids)]
            meeting["lot"] = drawn
        return drawn

    def _host(self, saga, tribunal, meeting, redraw: bool) -> Covenant | None:
        drawn = self._lot(saga, tribunal, meeting)
        if not drawn:
            return None
        return saga.covenant(drawn[1] if redraw else drawn[0])

    def fields(self, saga, tribunal, meeting):
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

    def live(self, saga, tribunal, meeting, values):
        host = self._host(saga, tribunal, meeting, bool(values.get("redraw")))
        return f"Next host: {escape(host.name)}." if host is not None else ""

    def apply(self, saga, tribunal, meeting, values):
        host = self._host(saga, tribunal, meeting, bool(values.get("redraw")))
        if host is not None:
            meeting["host"] = {"id": host.id, "redrawn": bool(values.get("redraw"))}
            tribunal.meeting_place = host.name
        _keep_note(meeting, self.key, values)

    def text(self, saga, tribunal, meeting):
        held = meeting.get("host") or {}
        host = saga.covenant(held.get("id"))
        shown = f"[$label]Next host:[/] {escape(host.name)}" if host else ""
        return _join(shown, _note_text(meeting, self.key))

    def save_label(self):
        return "Draw"

    def minutes(self, saga, tribunal, meeting):
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
    any fine and who pays it, whether the ruling goes into the Peripheral
    Code, and how a party covenant's attitude toward a troupe covenant on
    the other side moves. All of it is written when the meeting closes."""

    def fields(self, saga, tribunal, meeting):
        cases = business(tribunal)
        found: list[DialogField] = []
        for c in cases:
            kept = ruling_of(meeting, c)
            short = _short(c.title)
            found += [
                DialogField(
                    f"outcome_{c.id}",
                    c.title,
                    "text",
                    kept.get("outcome") or c.outcome or vote_outcome(meeting, c),
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

    def validate(self, meeting, values):
        for key, value in values.items():
            if key.startswith("fine_") and value is not None and value <= 0:
                return "A fine is more than nothing; leave it blank for none."
        return None

    def apply(self, saga, tribunal, meeting, values):
        kept = meeting.setdefault("rulings", {})
        for case in business(tribunal):
            if f"outcome_{case.id}" not in values:
                continue
            case.outcome = values[f"outcome_{case.id}"]
            kept[case.id] = {
                "outcome": case.outcome,
                "fine": values.get(f"fine_{case.id}"),
                "art": values.get(f"art_{case.id}") or "",
                "who": values.get(f"who_{case.id}", ""),
                "code": bool(values.get(f"code_{case.id}")),
                "attitude": values.get(f"attitude_{case.id}", "0"),
            }
        _keep_note(meeting, self.key, values)

    def text(self, saga, tribunal, meeting):
        lines = [
            f"[b]{escape(c.title)}:[/] {escape(c.outcome or '(no ruling yet)')}"
            + (
                f" · fine {escape(fine_text(ruling_of(meeting, c)))}"
                if ruling_of(meeting, c).get("fine")
                else ""
            )
            for c in business(tribunal)
        ]
        return _join(*lines, _note_text(meeting, self.key))

    def minutes(self, saga, tribunal, meeting):
        lines = []
        fines = []
        for c in business(tribunal):
            if not c.outcome.strip():
                continue
            lines.append(f"{c.title}: {c.outcome}.")
            kept = ruling_of(meeting, c)
            if kept.get("fine"):
                fines.append(f"fine {fine_text(kept)}")
        return " ".join(lines), "; ".join(fines)


#: The attitude moves a ruling can make, as the yearly step offers them.
ATTITUDE_CHANGES = ("0", "+1", "+2", "-1", "-2", "-3")


def _short(title: str) -> str:
    """A case's title cut to fit beside a field's own words."""
    return title if len(title) <= 18 else title[:17] + "…"


def ruling_of(meeting: dict[str, Any], case: Case) -> dict[str, Any]:
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


def default_attitude(meeting: dict[str, Any], case: Case, other: Covenant) -> str:
    """A party that lost its case takes it ill (-1); otherwise no move."""
    kept = meeting.get("votes", {}).get(case.id)
    if kept is None:
        return "0"
    carried = kept["for"] > kept["against"]
    brought = _party(other, case.brought_by)
    return "0" if carried == brought else "-1"


class Treasury(Step):
    """The treasury as it stands, and the loans that fall due this year."""

    def _due(self, tribunal: Tribunal, meeting: dict[str, Any]) -> list[str]:
        year = meeting.get("year")
        return [
            f"{e.who or 'a loan'}: {tribunal_sheet.amount_text(e)}"
            for e in tribunal.treasury
            if e.kind == "loan" and not e.paid and e.due_year == year
        ]

    def fields(self, saga, tribunal, meeting):
        found = [
            DialogField("balance", "", "info", f"{label}: {words}")
            for label, words in tribunal_sheet.balance_lines(tribunal)
        ]
        due = self._due(tribunal, meeting)
        if due:
            found.append(DialogField("due", "", "info", "Loans due: " + "; ".join(due)))
        return [*found, _note_field(meeting, self.key)]

    def text(self, saga, tribunal, meeting):
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

    def minutes(self, saga, tribunal, meeting):
        due = self._due(tribunal, meeting)
        words = "The treasury was reckoned."
        if due:
            words += f" Loans due: {'; '.join(due)}."
        lines = tribunal_sheet.balance_lines(tribunal)
        return words, lines[0][1] if lines else ""


class Closing(Step):
    """Ends the meeting: each case with a ruling is decided, the meeting
    goes into the Diary, and the next one is set."""

    def fields(self, saga, tribunal, meeting):
        return [
            DialogField("what", "", "info", closing_text(saga, tribunal, meeting)),
            _note_field(meeting, self.key),
        ]

    def text(self, saga, tribunal, meeting):
        return escape(closing_text(saga, tribunal, meeting))

    def save_label(self):
        return "Close"

    def minutes(self, saga, tribunal, meeting):
        return (
            f"The Tribunal closed; it meets again in "
            f"{meeting.get('season', 'Summer')} {_next(tribunal, meeting)}.",
            "",
        )


def _next(tribunal: Tribunal, meeting: dict[str, Any]) -> int:
    return int(meeting.get("year") or 0) + max(1, tribunal.meets_every)


def closing_text(saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> str:
    """What closing the meeting does."""
    decided = sum(bool(c.outcome.strip()) for c in business(tribunal))
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


def steps(tribunal: Tribunal, meeting: dict[str, Any]) -> list[Step]:
    """The order of business, in the order it is held."""
    last = days(meeting)
    added: dict[str, list[Step]] = {"opening": [], "end": [], "closing": []}
    for name in tribunal_packages.of(tribunal).meeting_steps:
        title, kind, when = _PACKAGE_STEPS.get(name, (name.title(), Step, "end"))
        added[when].append(kind(name, title, 1 if when == "opening" else last))
    found: list[Step] = [
        Opening("opening", "Opening and the oaths", 1),
        Attendance("attendance", "Attendance and proxies", 1),
        *added["opening"],
    ]
    cases = sorted(business(tribunal), key=lambda c: day_of(meeting, c))
    for case in cases:
        found += [
            Hearing(case, day_of(meeting, case)),
            Vote(case, day_of(meeting, case)),
        ]
    found += [
        *added["end"],
        Rulings("rulings", "Rulings and fines", last),
        Treasury("treasury", "Treasury and vis", last),
        *added["closing"],
        Closing("closing", "Closing", last),
    ]
    return found


def held(meeting: dict[str, Any], step: Step) -> bool:
    return step.key in meeting.get("done", [])


def current(tribunal: Tribunal, meeting: dict[str, Any]) -> Step:
    """The step in hand: the first not yet held."""
    found = steps(tribunal, meeting)
    return next((s for s in found if not held(meeting, s)), found[-1])


def now_text(tribunal: Tribunal, meeting: dict[str, Any]) -> str:
    """ "The Second Day › Fengheld v. Arnhaven"."""
    step = current(tribunal, meeting)
    return f"{day_name(step.day)} › {step.title}"


# -- holding a step --


def _when(saga: Saga, meeting: dict[str, Any]) -> tuple[int, str]:
    return int(meeting.get("year") or saga.current_year), meeting.get("season", "")


def write_minutes(
    saga: Saga, tribunal: Tribunal, meeting: dict[str, Any], step: Step
) -> None:
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
LISTENERS: list[Callable[[Saga, Tribunal, dict[str, Any], Step], None]] = [
    write_minutes
]


def _decide(saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> None:
    """Each case with a ruling is decided, and what its ruling says is
    written: the Peripheral Code, the fine owed to the treasury, and the
    party's attitude."""
    year, season = _when(saga, meeting)
    for case in business(tribunal):
        if not case.outcome.strip():
            continue
        case.status = CASE_DECIDED
        kept = ruling_of(meeting, case)
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


def acta_text(saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> str:
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
    for case in business(tribunal):
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


def _close(saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> None:
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


def step_form(
    saga: Saga,
    tribunal: Tribunal,
    step: Step,
    meeting: dict[str, Any] | None = None,
) -> Form:
    """Hold `step` of the meeting being held (or of `meeting`, a new one
    its Opening begins): its form; on saving it the step is marked held
    and the Closing ends the meeting."""
    record = meeting if meeting is not None else tribunal.meeting
    assert record is not None

    def apply(values: dict[str, Any]) -> None:
        tribunal.meeting = record
        step.apply(saga, tribunal, record, values)
        done = record.setdefault("done", [])
        if step.key not in done:
            done.append(step.key)
        for listener in LISTENERS:
            listener(saga, tribunal, record, step)
        if isinstance(step, Closing):
            _close(saga, tribunal, record)

    heading = (
        f"Hold Tribunal: {tribunals.title(tribunal)}"
        if meeting is not None
        else f"{day_name(step.day)}: {step.title}"
    )
    return Form(
        heading,
        lambda: step.fields(saga, tribunal, record),
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


def record(saga: Saga, tribunal: Tribunal) -> dict[str, Any]:
    """The meeting being held, or the one Hold Tribunal would open (not
    kept): what the hall shows before it opens."""
    return tribunal.meeting if tribunal.meeting is not None else _begin(saga, tribunal)


def title(saga: Saga, tribunal: Tribunal) -> str:
    """ "The Meeting: Summer 1228", or "The Next Meeting: Summer 1228"."""
    meeting = record(saga, tribunal)
    words = "The Meeting" if tribunal.meeting is not None else "The Next Meeting"
    return f"{words}: {meeting.get('season', '')} {meeting.get('year', '')}"


def facts(saga: Saga, tribunal: Tribunal) -> list[Fact]:
    """Where it is held, the step in hand and the votes in the hall."""
    meeting = record(saga, tribunal)
    held_at = meeting.get("place") or "(not set)"
    if tribunal.meeting is None:
        return [
            Fact("Held at", held_at),
            Fact("Now", "Not yet opened: hold any step (e) to open it"),
        ]
    return [
        Fact("Held at", held_at),
        Fact("Now", now_text(tribunal, meeting)),
        Fact("Present", present_text(saga, tribunal, meeting)),
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
    rows = []
    for covenant in tribunals.covenants_of(saga, tribunal):
        proxies = carried(tribunal, meeting, covenant)
        magi, allowed = present(saga, tribunal, meeting, covenant)
        set_aside = proxies and ruling(meeting, covenant) == SET_ASIDE
        rows.append(
            [
                covenant.name,
                str(world.votes(saga, covenant)),
                str(absent(meeting, covenant) or ""),
                f"{proxies} (set aside)" if set_aside else str(proxies or ""),
                str(magi + allowed),
            ]
        )
    return Grid(
        ["Covenant", "Magi", "Absent", "Proxies", "Votes"],
        rows,
        list(range(len(rows))),
        "No covenant belongs to this Tribunal yet.",
        caps=[22, 4, 6, 13, 5],
    )


def vote_case(saga: Saga, tribunal: Tribunal) -> Case | None:
    """The case the Vote section shows: the one in hand (its debate or
    its vote), else the last voted on, else the first to be heard."""
    meeting = record(saga, tribunal)
    cases = business(tribunal)
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
        rows=lambda: [c.name for c in tribunals.covenants_of(saga, tribunal)],
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
    return _join(heading, body or "[$label]Hold it with Edit (e).[/]")


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
    """Edit holds Attendance and proxies (opening the meeting first if
    it isn't open)."""

    def edit(_row: int) -> Command:
        if tribunal.meeting is None:
            return hold(saga, tribunal)
        return step_form(saga, tribunal, steps(tribunal, tribunal.meeting)[1])

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
from . import theban_meeting  # noqa: F401
