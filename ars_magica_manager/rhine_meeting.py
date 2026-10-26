"""The Rhine Tribunal's meeting step (Guardians of the Forests p. 27):
the first business after the opening is the introduction of every magus
who has passed his Gauntlet since the last meeting, and straight after
it the rite that confers the retired magi's sigils by proxy on the new
masters and archmagi (pp. 24, 26). The magi made master or archmage
since (the Gilds list's Mark of Approval and Archmage's Challenge,
tribunal_packages.rhine.promotions) are each entrusted a sigil here: it
is named for the retired magus it belonged to, typically his master's,
and adds a proxy to his covenant's votes from this meeting on.

A meeting.Step (the Template Method the core's steps fill in),
registered under the name the Rhine package lists. What it did is kept
in the meeting record under "rhine_rite": {"introduced": [character
ids], "others": words, "conferred": [indexes into the promotions]}."""

from __future__ import annotations

from typing import Any

from . import meeting as core
from .form_spec import DialogField
from .markup import escape
from .models import Character, Meeting, Saga, Tribunal
from .rules import rhine_ranks as ranks
from .tribunal_packages.rhine import entrusted, promotions, tribunal_magi

SOURCE = "Guardians of the Forests pp. 24, 26-27"


def _record(meeting: Meeting) -> dict[str, Any]:
    return meeting.setdefault("rhine_rite", {})


def _year(saga: Saga, meeting: Meeting) -> int:
    return int(meeting.get("year") or saga.current_year)


def new_magi(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> list[Character]:
    """The Tribunal's magi who passed their Gauntlet since its last
    meeting (its interval before this one) and by this one's year."""
    year = _year(saga, meeting)
    since = year - max(1, tribunal.meets_every)
    found = []
    for magus in tribunal_magi(saga, tribunal):
        passed = ranks.gauntlet_year(magus)
        if passed is not None and since < passed <= year:
            found.append(magus)
    return found


def _parens(saga: Saga, magus: Character) -> Character | None:
    name = magus.hermetic.parens
    return next((c for c in saga.characters if name and c.name == name), None)


def journeyman_trained(saga: Saga, magus: Character) -> bool:
    """Whether the magus's parens is a journeyman magus: he is introduced
    as a recruited hedge wizard, never that magus's filius (p. 24)."""
    parens = _parens(saga, magus)
    return parens is not None and parens.type == "magus" and not ranks.is_master(parens)


def introduction(saga: Saga, magus: Character) -> str:
    """ "Felicia, trained by Dorana"; for one a journeyman trained, that he
    comes as a recruited hedge wizard."""
    if journeyman_trained(saga, magus):
        return (
            f"{magus.name}, trained by {magus.hermetic.parens}, a journeyman: "
            "as a recruited hedge wizard"
        )
    parens = magus.hermetic.parens
    return f"{magus.name}, trained by {parens}" if parens else magus.name


def candidates(
    saga: Saga, tribunal: Tribunal, meeting: Meeting
) -> list[tuple[int, dict[str, Any], Character]]:
    """The promotions whose sigils the rite confers: those not yet
    conferred, and those this meeting conferred, with their index."""
    kept = set(_record(meeting).get("conferred", []))
    members = {m.id for m in tribunal_magi(saga, tribunal)}
    found = []
    for index, entry in enumerate(promotions(tribunal)):
        magus = saga.character(entry.get("character_id"))
        if magus is None or magus.id not in members:
            continue
        if entry.get("conferred") is None or index in kept:
            found.append((index, entry, magus))
    return found


def default_sigil(saga: Saga, magus: Character, entry: dict[str, Any]) -> str:
    """The sigil a new master is typically entrusted: his parens's (if
    retired, which the storyguide judges); "" for an archmage's second."""
    if entry.get("names"):
        return entry["names"][0]
    return magus.hermetic.parens if entry.get("rank") == ranks.MASTER else ""


def _undo(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> None:
    """Take back what this meeting's rite conferred, so holding it again
    confers afresh."""
    listed = promotions(tribunal)
    held = entrusted(tribunal)
    for index in _record(meeting).get("conferred", []):
        if not 0 <= index < len(listed):
            continue
        entry = listed[index]
        magus = saga.character(entry.get("character_id"))
        if magus is not None:
            names = held.get(magus.id, [])
            for name in entry.get("names", []):
                if name in names:
                    names.remove(name)
            if not names:
                held.pop(magus.id, None)
            _add_proxies(tribunal, meeting, magus, -int(entry.get("sigils") or 0))
        entry["conferred"], entry["names"] = None, []
    _record(meeting)["conferred"] = []


def _add_proxies(
    tribunal: Tribunal, meeting: Meeting, magus: Character, count: int
) -> None:
    """The magus's covenant carries `count` more proxies (fewer, when
    negative): from the next meeting on, and at this one when its roll
    call counted them."""
    ident = magus.covenant_id
    if not ident or not count:
        return
    total = max(0, tribunal.proxies.get(ident, 0) + count)
    if total:
        tribunal.proxies[ident] = total
    else:
        tribunal.proxies.pop(ident, None)
    entry = meeting.get("attendance", {}).get(ident)
    if entry is not None and "proxies" in entry:
        entry["proxies"] = max(0, int(entry.get("proxies") or 0) + count)


class Rite(core.Step):
    """The new magi introduced, then the sigils by proxy conferred on the
    new masters and archmagi."""

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        kept = _record(meeting)
        held = self.key in meeting.get("done", [])
        found: list[DialogField] = []
        for magus in new_magi(saga, tribunal, meeting):
            on = magus.id in kept.get("introduced", []) if held else True
            found.append(
                DialogField(
                    f"intro_{magus.id}",
                    f"Introduce {escape(magus.name)}",
                    "check",
                    on,
                    hint=escape(introduction(saga, magus)),
                )
            )
        found.append(
            DialogField(
                "others",
                "Others introduced",
                "area",
                kept.get("others", ""),
                hint="Magi Gauntleted since the last meeting who aren't in the saga.",
            )
        )
        conferring = candidates(saga, tribunal, meeting)
        for index, entry, magus in conferring:
            label = f"{escape(magus.name)} ({ranks.RANK_NAMES[entry['rank']]})"
            on = index in kept.get("conferred", []) if held else True
            found.append(
                DialogField(f"confer_{index}", f"Confer: {label}", "check", on)
            )
            found.append(
                DialogField(
                    f"sigil_{index}",
                    "Sigil of",
                    "text",
                    default_sigil(saga, magus, entry),
                    placeholder="the retired magus whose sigil",
                    hint="Typically his master's, if retired; else a respected "
                    "retired magus of like House, gild or outlook.",
                    show_if=lambda v, i=index: bool(v.get(f"confer_{i}")),
                )
            )
        if not conferring:
            found.append(
                DialogField(
                    "none",
                    "",
                    "info",
                    "No master or archmage has been made since: the Gilds "
                    "list's Mark of Approval and Archmage's Challenge record them.",
                )
            )
        found.append(core._note_field(meeting, self.key))
        return found

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        core._keep_note(meeting, self.key, values)
        record = _record(meeting)
        record["introduced"] = [
            m.id
            for m in new_magi(saga, tribunal, meeting)
            if values.get(f"intro_{m.id}")
        ]
        record["others"] = (values.get("others") or "").strip()
        conferring = candidates(saga, tribunal, meeting)
        _undo(saga, tribunal, meeting)
        year = _year(saga, meeting)
        held = entrusted(tribunal)
        conferred = []
        for index, entry, magus in conferring:
            if not values.get(f"confer_{index}"):
                continue
            name = (values.get(f"sigil_{index}") or "").strip() or "a retired magus"
            entry["conferred"], entry["names"] = year, [name]
            held.setdefault(magus.id, []).append(name)
            _add_proxies(tribunal, meeting, magus, int(entry.get("sigils") or 0))
            conferred.append(index)
        record["conferred"] = conferred

    def _lines(self, saga: Saga, tribunal: Tribunal, meeting: Meeting) -> list[str]:
        record = _record(meeting)
        lines = []
        for ident in record.get("introduced", []):
            magus = saga.character(ident)
            if magus is not None:
                lines.append(f"Introduced: {introduction(saga, magus)}")
        if record.get("others"):
            lines.append(f"Also introduced: {record['others']}")
        listed = promotions(tribunal)
        for index in record.get("conferred", []):
            if 0 <= index < len(listed):
                entry = listed[index]
                magus = saga.character(entry.get("character_id"))
                if magus is not None:
                    rank = ranks.RANK_NAMES[entry["rank"]].lower()
                    lines.append(
                        f"Entrusted to {magus.name}, new {rank}: the sigil of "
                        f"{', '.join(entry.get('names', []))}"
                    )
        return lines

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return core._join(
            *(escape(line) for line in self._lines(saga, tribunal, meeting)),
            core._note_text(meeting, self.key),
        )

    def save_label(self):
        return "Confer"

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        count = len(candidates(saga, tribunal, meeting))
        return (
            f"The magi Gauntleted since the last meeting, and {count} new "
            f"master{'' if count == 1 else 's'} or archmag"
            f"{'us' if count == 1 else 'i'} owed a sigil.",
            "Each sigil conferred adds a proxy to its holder's covenant, at "
            "this meeting and the next.",
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        lines = self._lines(saga, tribunal, meeting)
        if not lines:
            return "", ""
        record = _record(meeting)
        count = len(record.get("conferred", []))
        return (
            "The new magi were introduced and the sigils conferred: "
            + "; ".join(lines)
            + ".",
            f"{count} sigil{'' if count == 1 else 's'} conferred",
        )


core.register_step(
    "rhine_rite", "The new magi and the sigils by proxy", Rite, "opening"
)
