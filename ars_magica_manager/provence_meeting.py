"""The Provençal Tribunal's residency step (Faith & Flame p. 22): the
magi present are written down as attending, which keeps them residents
for the next three meetings; a newcomer present may be granted residency
by a vote at his first meeting; and a resident who has left may be
written down as departed, registered or (having voted at another
Tribunal's meeting first) in breach of the Peripheral Code.

A meeting.Step (the Template Method the core's steps fill in),
registered under the name the Provence package lists. What this meeting
recorded is kept under "provence_residency": {"newcomers" and
"granted": [magus ids], "departed": id, "breach": id}, so holding it
again undoes it first."""

from __future__ import annotations

from typing import Any

from . import meeting as core
from .form_spec import DialogField
from .markup import escape
from .models import Character, Meeting, Saga, Tribunal
from .tribunal_packages import provence as package
from .tribunal_packages.rhine import tribunal_magi

SOURCE = "Faith & Flame p. 22"


def _record(meeting: Meeting) -> dict[str, Any]:
    return meeting.setdefault("provence_residency", {})


def _year(saga: Saga, meeting: Meeting) -> int:
    return int(meeting.get("year") or saga.current_year)


def _present(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> list[Character]:
    return [m for m, _c in core.magi_present(saga, tribunal, meeting)]


def _undo(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> None:
    """Take back what this meeting's step recorded."""
    year = _year(saga, meeting)
    record = _record(meeting)
    held = package.meetings(tribunal)
    if year in held:
        held.remove(year)
    for ident, years in list(package.attended(tribunal).items()):
        if year in years:
            years.remove(year)
        if not years:
            package.attended(tribunal).pop(ident)
    granted = package.registered(tribunal)
    for ident in record.get("granted", []):
        if granted.get(ident) == year:
            granted.pop(ident)
    gone = package.departed(tribunal)
    for key in ("departed", "breach"):
        ident = record.get(key)
        if ident and (gone.get(ident) or {}).get("year") == year:
            gone.pop(ident)
    record.clear()


class Residency(core.Step):
    """The magi present recorded as attending, newcomers granted
    residency, and departures."""

    def _newcomers(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting
    ) -> list[Character]:
        """The magi present who are not residents (as things stood before
        this meeting's step was held)."""
        kept = _record(meeting)
        if "newcomers" in kept:
            return [
                m
                for ident in kept["newcomers"]
                for m in [saga.character(ident)]
                if m is not None
            ]
        found = []
        for magus in _present(saga, tribunal, meeting):
            resident, _why = package.residency(tribunal, magus)
            if not resident:
                found.append(magus)
        return found

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        kept = _record(meeting)
        found: list[DialogField] = []
        for magus in self._newcomers(saga, tribunal, meeting):
            found.append(
                DialogField(
                    f"grant_{magus.id}",
                    f"Grant residency: {escape(magus.name)}",
                    "check",
                    magus.id in kept.get("granted", []),
                    hint="Not a resident when the meeting opened: the Tribunal "
                    "may grant it by vote at his first meeting.",
                )
            )
        residents = [
            (escape(m.name), m.id)
            for m in tribunal_magi(saga, tribunal)
            if m.id not in package.departed(tribunal) or m.id in kept.values()
        ]
        found += [
            DialogField(
                "departed",
                "Departure registered",
                "select",
                kept.get("departed"),
                options=residents,
                allow_blank=True,
                placeholder="(none)",
                hint="A resident who registered with the Redcaps or the Praeco "
                "that he is leaving for another Tribunal.",
            ),
            DialogField(
                "breach",
                "Voted elsewhere unregistered",
                "select",
                kept.get("breach"),
                options=residents,
                allow_blank=True,
                placeholder="(none)",
                hint="A resident who voted at another Tribunal's meeting without "
                "registering his departure first: he has broken the Peripheral "
                "Code, and is no longer a resident.",
            ),
            core._note_field(meeting, self.key),
        ]
        return found

    def validate(self, meeting: Meeting, values: dict[str, Any]) -> str | None:
        if values.get("departed") and values.get("departed") == values.get("breach"):
            return "One magus can't both register his departure and leave unregistered."
        return None

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        core._keep_note(meeting, self.key, values)
        newcomers = self._newcomers(saga, tribunal, meeting)
        _undo(saga, tribunal, meeting)
        year = _year(saga, meeting)
        record = _record(meeting)
        held = package.meetings(tribunal)
        held.append(year)
        held.sort()
        for magus in _present(saga, tribunal, meeting):
            package.attended(tribunal).setdefault(magus.id, []).append(year)
        granted = [m.id for m in newcomers if values.get(f"grant_{m.id}")]
        for ident in granted:
            package.registered(tribunal)[ident] = year
        record["granted"] = granted
        record["newcomers"] = [m.id for m in newcomers]
        for key, breach in (("departed", False), ("breach", True)):
            ident = values.get(key)
            if ident:
                package.departed(tribunal)[ident] = {"year": year, "breach": breach}
                record[key] = ident

    def _lines(self, saga: Saga, tribunal: Tribunal, meeting: Meeting) -> list[str]:
        record = _record(meeting)
        lines = []
        names = [
            m.name
            for ident in record.get("granted", [])
            for m in [saga.character(ident)]
            if m is not None
        ]
        if names:
            lines.append(f"Granted residency by vote: {', '.join(names)}")
        for key, words in (
            ("departed", "Registered his departure"),
            ("breach", "Voted at another Tribunal without registering his departure"),
        ):
            magus = saga.character(record.get(key))
            if magus is not None:
                lines.append(f"{words}: {magus.name}")
        return lines

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return core._join(
            *(escape(line) for line in self._lines(saga, tribunal, meeting)),
            core._note_text(meeting, self.key),
        )

    def save_label(self):
        return "Record"

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        count = len(self._newcomers(saga, tribunal, meeting))
        return (
            f"The magi present are recorded as attending, which keeps them "
            f"residents for the next three meetings; {count} present "
            f"{'is' if count == 1 else 'are'} not resident. A magus Gauntleted "
            "in the Tribunal is a resident until three meetings pass without "
            "him.",
            "Each newcomer you tick is granted residency by vote and stays a "
            "resident until he leaves; a departure ends a magus's residency, "
            "and one unregistered is a breach of the Peripheral Code.",
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        lines = self._lines(saga, tribunal, meeting)
        present = len(_present(saga, tribunal, meeting))
        words = f"The roll of residents was kept: {present} magi attended."
        if lines:
            words += " " + "; ".join(lines) + "."
        return words, f"{present} attending"


core.register_step("residency", "The roll of residents", Residency, "opening")
