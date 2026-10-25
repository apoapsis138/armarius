"""The Theban Tribunal's meeting, in the order and words of The Sundered
Eagle. Its first phase, the Hermetic Assembly, hears the decrees of
citizenship, contrition and defamation, then holds the ostrakismos; the
Law Council's changes to the Code and the People's Court's cases are the
meeting's own motions and cases; and its last phase, the Council of
Archai, thanks the outgoing magistrates with tokens, draws the new
archai by lot from each phyle (the sortition) and has them elect the
archon and the polemarch.

Each step is a meeting.Step (the Template Method the core's steps fill
in), registered under the name the Theban package lists. What a step
did is kept in the meeting record under "theban", so holding it again
undoes the first holding before doing it anew, and the minutes can say
what was done."""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from typing import Any

from . import meeting as core
from . import tribunals, world
from .arts import ARTS
from .form_spec import DialogField
from .markup import escape
from .models import Case, Character, Meeting, Saga, TreasuryEntry, Tribunal
from .sheets import tribunal as tribunal_sheet
from .tribunal_packages import data
from .tribunal_packages.theban import (
    KEY,
    PHYLAI,
    archai,
    is_metoikos,
    magi,
    phylai,
)

#: The tokens paid at the end of a term, by the office's first word. The
#: tamias is one of the Treasury Council's archai and is paid as one.
TERM_TOKENS = {"archon": 3, "polemarch": 5, "arche": 2}

#: How many archai each phyle sends to the Council.
ARCHAI_PER_PHYLE = 4

#: How many years an ostracised magus is kept out of the Tribunal.
OSTRACISM_YEARS = 7

#: The office the sortition fills, "Arche (Ionian)".
ARCHE = "Arche"

#: Why a drawn magus is set aside: refusing to stand costs a shard (The
#: Sundered Eagle p. 32).
REFUSED = "refused"

#: The three boards of magistrates, three archai each; the rest of the
#: archai form the Treasury Council (The Sundered Eagle pp. 27-28, 35).
BOARDS: tuple[str, ...] = ("Judicial Board", "Legislative Board", "Conciliatory Board")
BOARD_SEATS = 3
TREASURY_COUNCIL = "Treasury Council"
#: The Treasury Council's duties: one tamias by lot, four gathering vis
#: and Gifted children (one from each phyle where they can), the rest
#: tutors (p. 28).
TAMIAS_DUTY = "Treasury Council: tamias (treasurer)"
COLLECTOR_DUTY = "Treasury Council: gathers vis and Gifted children"
TUTOR_DUTY = "Treasury Council: tutor of the Gifted children"
COLLECTORS = 4


def _record(meeting: Meeting) -> dict[str, Any]:
    return meeting.setdefault("theban", {})


def _year(saga: Saga, meeting: Meeting) -> int:
    return int(meeting.get("year") or saga.current_year)


def entry_of(
    tribunal: Tribunal, character_id: str, create: bool = False
) -> dict[str, Any] | None:
    """The magus's entry in the Tribunal's tokens and shards, made (as a
    polites with none) when `create` and there is none."""
    for entry in magi(tribunal):
        if entry.get("character_id") == character_id:
            return entry
    if not create:
        return None
    entry = {
        "character_id": character_id,
        "status": "polites",
        "tokens": 0,
        "shards": 0,
    }
    magi(tribunal).append(entry)
    return entry


def _adjust(tribunal: Tribunal, character_id: str, key: str, by: int) -> None:
    entry = entry_of(tribunal, character_id, create=True)
    assert entry is not None
    entry[key] = max(0, int(entry.get(key) or 0) + by)


def _named(saga: Saga, ids: list[str]) -> list[Character]:
    return [c for c in (saga.character(i) for i in ids) if c is not None]


def _names(saga: Saga, ids: list[str]) -> str:
    found = [c.name for c in _named(saga, ids)]
    if len(found) > 1:
        return ", ".join(found[:-1]) + " and " + found[-1]
    return found[0] if found else ""


def tribunal_magi(saga: Saga, tribunal: Tribunal) -> list[Character]:
    """The named magi of the Tribunal's covenants."""
    return [
        m
        for c in tribunals.covenants_of(saga, tribunal)
        for m in world.covenant_magi(saga, c)
    ]


def _ostracised(entry: dict[str, Any] | None, year: int) -> bool:
    until = (entry or {}).get("ostracised_until")
    return until is not None and until >= year


def politai(saga: Saga, tribunal: Tribunal, year: int) -> list[Character]:
    """The Tribunal's magi who are citizens: not metoikoi, not ostracised.
    A magus with no entry is a polites with no tokens."""
    found = []
    for magus in tribunal_magi(saga, tribunal):
        entry = entry_of(tribunal, magus.id)
        if entry is not None and (is_metoikos(entry) or _ostracised(entry, year)):
            continue
        found.append(magus)
    return found


def _options(people: list[Character]) -> list[tuple[str, str]]:
    return [(escape(p.name), p.id) for p in people]


def next_principal(tribunal: Tribunal) -> str:
    """The phyle whose turn it is to govern the meeting: the one after
    the last meeting's, the Ionian first."""
    order = list(PHYLAI)
    last = data(tribunal, KEY).get("principal_phyle")
    if last not in order:
        return order[0]
    return order[(order.index(last) + 1) % len(order)]


# -- the Hermetic Assembly --


class Assembly(core.Step):
    """The Hermetic Assembly's decrees: a metoikos made polites, a shard
    removed for a reparation (contrition), and one decree of defamation,
    which gives a shard to the accused if upheld or to the accuser if
    not. The principal phyle governing the meeting is set here."""

    def _undo(self, tribunal: Tribunal, meeting: Meeting) -> None:
        held = _record(meeting).pop("assembly", None)
        if not held:
            return
        for ident in held.get("citizens", []):
            entry = entry_of(tribunal, ident)
            if entry is not None:
                entry["status"] = "metoikos"
        for ident in held.get("contrition", []):
            _adjust(tribunal, ident, "shards", 1)
        shard = held.get("shard_to")
        if shard:
            _adjust(tribunal, shard, "shards", -1)
        if "principal_before" in held:
            data(tribunal, KEY)["principal_phyle"] = held["principal_before"]

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = _record(meeting).get("assembly") or {}
        year = _year(saga, meeting)
        principal = held.get("principal") or next_principal(tribunal)
        found = [
            DialogField(
                "principal",
                "Principal phyle",
                "select",
                principal,
                options=[(name, name) for name in PHYLAI],
                hint="The phyle governing this meeting, in turn: Ionian, "
                "Aegean, Kretan, Propontian.",
            )
        ]
        made = set(held.get("citizens", []))
        for entry in magi(tribunal):
            magus = saga.character(entry.get("character_id"))
            if magus is None or _ostracised(entry, year):
                continue
            if not (is_metoikos(entry) or magus.id in made):
                continue
            found.append(
                DialogField(
                    f"citizen_{magus.id}",
                    f"Decree of citizenship: {escape(magus.name)}",
                    "check",
                    magus.id in made,
                    hint="A metoikos sponsored by an arche, resident at a "
                    "covenant, is made polites.",
                )
            )
        contrite = set(held.get("contrition", []))
        for entry in magi(tribunal):
            magus = saga.character(entry.get("character_id"))
            shards = int(entry.get("shards") or 0) + (
                magus.id in contrite if magus else 0
            )
            if magus is None or shards < 1 or is_metoikos(entry):
                continue
            if _ostracised(entry, year):
                continue
            found.append(
                DialogField(
                    f"contrition_{magus.id}",
                    f"Decree of contrition: {escape(magus.name)} ({shards} "
                    f"shard{'' if shards == 1 else 's'})",
                    "check",
                    magus.id in contrite,
                    hint="The reparation offered is accepted and a shard removed.",
                )
            )
            found += _reparation_fields(magus, held)
        citizens = _options(politai(saga, tribunal, year))
        # A decree against a magus who isn't present isn't voted on: the
        # Conciliatory Board takes it after the Tribunal (p. 32). With no
        # names taken at the roll, everyone is offered.
        here = {m.id for m, _ in core.magi_present(saga, tribunal, meeting)}
        accusable = (
            _options([m for m in politai(saga, tribunal, year) if m.id in here])
            if here
            else citizens
        )
        defamation = held.get("defamation") or {}
        found += [
            DialogField(
                "accused",
                "Defamation: the accused",
                "select",
                defamation.get("accused"),
                options=accusable,
                allow_blank=True,
                placeholder="(no decree of defamation)",
                hint="A polites present, said to have acted against the unity of "
                "the polity; against one who is absent, the Conciliatory Board "
                "decides after the Tribunal (The Sundered Eagle p. 32).",
            ),
            DialogField(
                "accuser",
                "Defamation: brought by",
                "select",
                defamation.get("accuser"),
                options=citizens,
                allow_blank=True,
                placeholder="(not recorded)",
                show_if=lambda values: bool(values.get("accused")),
            ),
            DialogField(
                "verdict",
                "Defamation: the Assembly",
                "select",
                defamation.get("verdict", "upheld"),
                options=[
                    ("Upheld: a shard to the accused", "upheld"),
                    ("Rejected: a shard to the accuser", "rejected"),
                ],
                show_if=lambda values: bool(values.get("accused")),
            ),
            core._note_field(meeting, self.key),
        ]
        return found

    def validate(self, meeting: Meeting, values: dict[str, Any]):
        if (
            values.get("accused")
            and values.get("verdict") == "rejected"
            and not values.get("accuser")
        ):
            return "A rejected decree gives the accuser a shard: say who brought it."
        if values.get("accused") and values.get("accused") == values.get("accuser"):
            return "A magus can't bring a decree of defamation against themselves."
        return None

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        _return_reparations(saga, tribunal, _record(meeting).get("assembly") or {})
        self._undo(tribunal, meeting)
        held: dict[str, Any] = {
            "principal": values.get("principal") or next_principal(tribunal),
            "principal_before": data(tribunal, KEY).get("principal_phyle"),
            "citizens": [],
            "contrition": [],
            "reparations": {},
        }
        data(tribunal, KEY)["principal_phyle"] = held["principal"]
        for key, ticked in values.items():
            if not ticked:
                continue
            if key.startswith("citizen_"):
                ident = key.removeprefix("citizen_")
                entry = entry_of(tribunal, ident)
                if entry is not None:
                    entry["status"] = "polites"
                    held["citizens"].append(ident)
            elif key.startswith("contrition_"):
                ident = key.removeprefix("contrition_")
                entry = entry_of(tribunal, ident)
                if entry is not None and int(entry.get("shards") or 0) > 0:
                    _adjust(tribunal, ident, "shards", -1)
                    held["contrition"].append(ident)
                    _take_reparation(saga, tribunal, meeting, ident, values, held)
        if values.get("accused"):
            verdict = values.get("verdict") or "upheld"
            shard_to = (
                values["accused"] if verdict == "upheld" else values.get("accuser")
            )
            held["defamation"] = {
                "accused": values["accused"],
                "accuser": values.get("accuser"),
                "verdict": verdict,
            }
            if shard_to:
                _adjust(tribunal, shard_to, "shards", 1)
                held["shard_to"] = shard_to
        _record(meeting)["assembly"] = held
        core._keep_note(meeting, self.key, values)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = _record(meeting).get("assembly") or {}
        shown = (
            f"[$label]Principal phyle:[/] {escape(held['principal'])}"
            if held.get("principal")
            else ""
        )
        return core._join(shown, core._note_text(meeting, self.key))

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = _record(meeting).get("assembly") or {}
        parts = []
        if held.get("principal"):
            parts.append(f"The {held['principal']} phyle governed the meeting.")
        if held.get("citizens"):
            parts.append(
                f"By decree of citizenship {_names(saga, held['citizens'])} became "
                + ("a polites." if len(held["citizens"]) == 1 else "politai.")
            )
        if held.get("contrition"):
            parts.append(
                f"By decree of contrition a shard was taken from "
                f"{_names(saga, held['contrition'])}."
            )
        for ident, paid in (held.get("reparations") or {}).items():
            magus = saga.character(ident)
            if magus is not None:
                parts.append(f"{magus.name}'s reparation: {reparation_text(paid)}.")
        defamation = held.get("defamation") or {}
        accused = saga.character(defamation.get("accused"))
        if accused is not None:
            if defamation.get("verdict") == "upheld":
                parts.append(
                    f"A decree of defamation against {accused.name} was upheld, "
                    "and a shard given."
                )
            else:
                accuser = saga.character(defamation.get("accuser"))
                by = f", and {accuser.name} given a shard" if accuser else ""
                parts.append(
                    f"A decree of defamation against {accused.name} was rejected{by}."
                )
        return " ".join(parts), ""


# -- a contrition's reparation (The Sundered Eagle p. 33) --


def _reparation_fields(magus: Character, held: dict[str, Any]) -> list[DialogField]:
    """What a contrite magus offers the Tribunal, shown once his decree is
    ticked: its words, and the vis it takes from him."""
    paid = (held.get("reparations") or {}).get(magus.id) or {}
    ticked = f"contrition_{magus.id}"
    pawns_key = f"reparation_pawns_{magus.id}"
    return [
        DialogField(
            f"reparation_{magus.id}",
            "  The reparation",
            "text",
            paid.get("what", ""),
            placeholder="e.g. a summa on Corpus, an invested item",
            hint="The magus sets it himself (The Sundered Eagle p. 33): seven "
            "or more pawns, a summa or an invested item from one with many "
            "enemies or who defied the Tribunal.",
            show_if=lambda values: bool(values.get(ticked)),
        ),
        DialogField(
            pawns_key,
            "  Its vis, in pawns",
            "optint",
            paid.get("wanted", paid.get("pawns")),
            hint="Taken from the magus's own vis into the Tribunal's treasury.",
            show_if=lambda values: bool(values.get(ticked)),
        ),
        DialogField(
            f"reparation_art_{magus.id}",
            "  Of the Art",
            "select",
            paid.get("art", "Vim"),
            options=[(art, art) for art in ARTS],
            show_if=lambda values: bool(values.get(ticked) and values.get(pawns_key)),
        ),
    ]


def _take_reparation(
    saga: Saga,
    tribunal: Tribunal,
    meeting: Meeting,
    ident: str,
    values: dict[str, Any],
    held: dict[str, Any],
) -> None:
    """Record the reparation; its pawns leave the magus's vis (as many as
    he has) for the Tribunal's treasury."""
    what = str(values.get(f"reparation_{ident}") or "").strip()
    wanted = max(0, int(values.get(f"reparation_pawns_{ident}") or 0))
    art = str(values.get(f"reparation_art_{ident}") or "Vim")
    if not what and not wanted:
        return
    paid: dict[str, Any] = {"what": what}
    magus = saga.character(ident)
    if wanted and magus is not None:
        key = art.lower()
        pawns = min(wanted, int(magus.raw_vis.get(key, 0)))
        if pawns:
            magus.raw_vis[key] = magus.raw_vis.get(key, 0) - pawns
            if not magus.raw_vis[key]:
                del magus.raw_vis[key]
            entry = TreasuryEntry(
                "vis",
                pawns,
                art=art,
                who=magus.name,
                note=f"Reparation for a shard, {_year(saga, meeting)}",
            )
            tribunal.treasury.append(entry)
            paid["treasury_id"] = entry.id
        paid.update(pawns=pawns, art=art, wanted=wanted)
    held["reparations"][ident] = paid


def _return_reparations(saga: Saga, tribunal: Tribunal, held: dict[str, Any]) -> None:
    """Undo the reparations an earlier holding took: the pawns back to each
    magus, their treasury lines removed."""
    for ident, paid in (held.get("reparations") or {}).items():
        pawns = int(paid.get("pawns") or 0)
        magus = saga.character(ident)
        if pawns and magus is not None:
            key = str(paid.get("art") or "Vim").lower()
            magus.raw_vis[key] = magus.raw_vis.get(key, 0) + pawns
        if paid.get("treasury_id"):
            tribunal.treasury = [
                t for t in tribunal.treasury if t.id != paid["treasury_id"]
            ]


def reparation_text(paid: Mapping[str, Any]) -> str:
    """A reparation as the minutes give it: "a summa on Corpus and 7 pawns
    of Vim", and how many pawns offered he lacked."""
    parts = [str(paid["what"])] if paid.get("what") else []
    pawns = int(paid.get("pawns") or 0)
    if pawns:
        parts.append(f"{pawns} pawns of {paid.get('art', 'Vim')}")
    short = int(paid.get("wanted") or 0) - pawns
    words = " and ".join(parts) or "nothing recorded"
    if short > 0:
        words += f" ({short} of the pawns offered he hadn't)"
    return words


def ostracism_candidates(
    saga: Saga, tribunal: Tribunal, meeting: Meeting
) -> list[tuple[Character, int]]:
    """Every polites with a shard, and how many, but those made politai
    at this meeting."""
    made = set((_record(meeting).get("assembly") or {}).get("citizens", []))
    held = _record(meeting).get("ostrakismos") or {}
    found = []
    for magus in politai(saga, tribunal, _year(saga, meeting)) + _named(
        saga, [held["ostracised"]] if held.get("ostracised") else []
    ):
        entry = entry_of(tribunal, magus.id)
        shards = int((entry or {}).get("shards") or 0)
        if held.get("ostracised") == magus.id:
            shards = int(held.get("before", {}).get("shards") or 0)
        if shards and magus.id not in made and all(m.id != magus.id for m, _ in found):
            found.append((magus, shards))
    return found


class Ostrakismos(core.Step):
    """The last business of the Assembly: the logothete reads every
    polites with a shard, the candidates are chosen, and each magus
    writes a name, or "no one", on a sherd. The one ostracised loses
    citizenship, and the tokens and shards with it, and is kept out of the
    Tribunal for seven years; if he returns, it is as a metoikos."""

    def _undo(self, tribunal: Tribunal, meeting: Meeting) -> None:
        held = _record(meeting).pop("ostrakismos", None)
        if not held or not held.get("ostracised"):
            return
        entry = entry_of(tribunal, held["ostracised"])
        if entry is not None:
            for key, value in held.get("before", {}).items():
                if value is None:
                    entry.pop(key, None)
                else:
                    entry[key] = value

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = _record(meeting).get("ostrakismos") or {}
        candidates = ostracism_candidates(saga, tribunal, meeting)
        if not candidates:
            return [
                DialogField(
                    "none",
                    "",
                    "info",
                    "No polites holds a shard: there is no ostrakismos.",
                ),
                core._note_field(meeting, self.key),
            ]
        listed = "; ".join(
            f"{escape(m.name)} ({n} shard{'' if n == 1 else 's'})"
            for m, n in candidates
        )
        return [
            DialogField("read", "", "info", f"The logothete reads: {listed}."),
            DialogField(
                "ostracised",
                "Ostracised",
                "select",
                held.get("ostracised"),
                options=[(escape(m.name), m.id) for m, _ in candidates],
                allow_blank=True,
                placeholder="(no one)",
                hint='The name on most sherds, or no one if "no one" has the '
                "most. A tie is voted again between those tied.",
            ),
            core._note_field(meeting, self.key),
        ]

    def live(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        magus = saga.character(values.get("ostracised"))
        if magus is None:
            return ""
        until = _year(saga, meeting) + OSTRACISM_YEARS
        return f"{escape(magus.name)} leaves the Tribunal until {until}."

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        self._undo(tribunal, meeting)
        held: dict[str, Any] = {}
        chosen = values.get("ostracised")
        if chosen:
            entry = entry_of(tribunal, chosen, create=True)
            assert entry is not None
            keys = ("status", "tokens", "shards", "ostracised_until", "why")
            held = {"ostracised": chosen, "before": {k: entry.get(k) for k in keys}}
            year = _year(saga, meeting)
            entry.update(
                status="metoikos",
                tokens=0,
                shards=0,
                ostracised_until=year + OSTRACISM_YEARS,
                why=f"Ostracised at the Tribunal of {year}",
            )
        _record(meeting)["ostrakismos"] = held
        core._keep_note(meeting, self.key, values)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = _record(meeting).get("ostrakismos") or {}
        magus = saga.character(held.get("ostracised"))
        shown = (
            f"[$label]Ostracised:[/] {escape(magus.name)}" if magus is not None else ""
        )
        return core._join(shown, core._note_text(meeting, self.key))

    def save_label(self):
        return "Count"

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        if "ostrakismos" not in _record(meeting):
            return "", ""
        held = _record(meeting)["ostrakismos"]
        magus = saga.character(held.get("ostracised"))
        if magus is None:
            return "At the ostrakismos no one was ostracised.", ""
        until = _year(saga, meeting) + OSTRACISM_YEARS
        return (
            f"At the ostrakismos {magus.name} was ostracised, losing "
            f"citizenship, and may not return before {until}.",
            "Ostracised",
        )


# -- the Council of Archai --


def term_tokens(office: str) -> int:
    """The tokens an office's holder is paid at the end of the term."""
    first = office.strip().split(" ")[0].casefold() if office.strip() else ""
    return TERM_TOKENS.get(first, 0)


class EndOfTerm(core.Step):
    """The outgoing magistrates thanked and paid: two tokens for each
    arche, three for the archon and five for the polemarch (the
    logothete is paid none). Who is outgoing is read once, as the step
    is first shown, so holding it again after the sortition pays the
    same magi."""

    def _outgoing(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting
    ) -> list[dict[str, Any]]:
        record = _record(meeting)
        if "outgoing" not in record:
            record["outgoing"] = [
                {
                    "holder_id": office["holder_id"],
                    "office": office.get("office", ""),
                    "tokens": term_tokens(office.get("office", "")),
                }
                for office in archai(tribunal)
                if office.get("holder_id")
                and term_tokens(office.get("office", ""))
                and saga.character(office["holder_id"]) is not None
            ]
        return record["outgoing"]

    def _undo(self, tribunal: Tribunal, meeting: Meeting) -> None:
        for paid in _record(meeting).pop("paid", []):
            _adjust(tribunal, paid["holder_id"], "tokens", -paid["tokens"])

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        outgoing = self._outgoing(saga, tribunal, meeting)
        if not outgoing:
            return [
                DialogField(
                    "none",
                    "",
                    "info",
                    "No outgoing magistrates are recorded to thank.",
                ),
                core._note_field(meeting, self.key),
            ]
        paid = {(p["holder_id"], p["office"]) for p in _record(meeting).get("paid", [])}
        held = "paid" in _record(meeting)
        found = []
        for index, out in enumerate(outgoing):
            magus = saga.character(out["holder_id"])
            name = magus.name if magus is not None else "(gone)"
            found.append(
                DialogField(
                    f"pay_{index}",
                    f"{escape(name)}, {escape(out['office'])}: {out['tokens']} tokens",
                    "check",
                    (out["holder_id"], out["office"]) in paid if held else True,
                )
            )
        found.append(core._note_field(meeting, self.key))
        return found

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        self._undo(tribunal, meeting)
        paid = []
        for index, out in enumerate(self._outgoing(saga, tribunal, meeting)):
            if not values.get(f"pay_{index}"):
                continue
            entry = entry_of(tribunal, out["holder_id"], create=True)
            if entry is None or is_metoikos(entry):
                continue
            _adjust(tribunal, out["holder_id"], "tokens", out["tokens"])
            paid.append(out)
        _record(meeting)["paid"] = paid
        core._keep_note(meeting, self.key, values)

    def save_label(self):
        return "Pay"

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        paid = _record(meeting).get("paid", [])
        if not paid:
            return "", ""
        parts = []
        for out in paid:
            magus = saga.character(out["holder_id"])
            if magus is not None:
                parts.append(f"{magus.name} ({out['office']}, {out['tokens']})")
        return (
            "The outgoing magistrates were thanked and paid in tokens: "
            + ", ".join(parts)
            + ".",
            f"{sum(p['tokens'] for p in paid)} tokens",
        )


def is_arche(office: dict[str, Any]) -> bool:
    return office.get("office", "").startswith(ARCHE + " ")


def sortition_pool(
    saga: Saga,
    tribunal: Tribunal,
    year: int,
    phyle: str,
    made: set[str] | frozenset[str] = frozenset(),
) -> list[str]:
    """The phyle's candidate list: its politai, but those serving as
    archai now (no one serves two terms running), the Redcaps, who are not
    drawn, and those `made` politai at this meeting (The Sundered Eagle
    p. 32)."""
    serving = {o.get("holder_id") for o in archai(tribunal) if is_arche(o)}
    covenants = {c.id for c in tribunals.covenants_of(saga, tribunal)}
    return [
        m.id
        for m in politai(saga, tribunal, year)
        if m.covenant_id in covenants
        and phylai(tribunal).get(m.covenant_id or "") == phyle
        and m.id not in serving
        and m.id not in made
        and m.hermetic.house != "house_mercere"
    ]


def boards_served(tribunal: Tribunal) -> dict[str, list[str]]:
    """The boards each magus has sat on, by character id: no arche sits
    on the same board twice (The Sundered Eagle p. 27)."""
    found = data(tribunal, KEY).setdefault("boards_served", {})
    if not isinstance(found, dict):
        raise ValueError(f"The boards served should be a mapping, not {found!r}.")
    return found


def assign_boards(
    archai_ids: list[str],
    served: Mapping[str, Sequence[str]],
    phyle_of: Mapping[str, str],
    dice: random.Random,
) -> tuple[dict[str, str], dict[str, int]]:
    """Each new arche's duty, and the board seats left for Redcaps.

    Those who have been archai before are placed first, each on a board
    he has not sat on, by lot where there is a choice; then the rest by
    lot until each board has three; the remaining archai form the
    Treasury Council, where one is drawn as tamias, four gather vis and
    Gifted children (one from each phyle where possible) and the rest
    are tutors (The Sundered Eagle pp. 27-28, 35)."""
    seats = dict.fromkeys(BOARDS, BOARD_SEATS)
    duties: dict[str, str] = {}
    veterans = [i for i in archai_ids if served.get(i)]
    newcomers = [i for i in archai_ids if not served.get(i)]
    dice.shuffle(veterans)
    dice.shuffle(newcomers)
    for ident in veterans + newcomers:
        open_boards = [b for b in BOARDS if seats[b] and b not in served.get(ident, ())]
        if open_boards:
            board = dice.choice(open_boards)
            seats[board] -= 1
            duties[ident] = board
    treasury = [i for i in archai_ids if i not in duties]
    dice.shuffle(treasury)
    if treasury:
        duties[treasury.pop(0)] = TAMIAS_DUTY
    phylai_seen: set[str] = set()
    collectors: list[str] = []
    for ident in list(treasury):
        phyle = phyle_of.get(ident, "")
        if len(collectors) < COLLECTORS and phyle not in phylai_seen:
            phylai_seen.add(phyle)
            collectors.append(ident)
    for ident in treasury:
        if len(collectors) < COLLECTORS and ident not in collectors:
            collectors.append(ident)
    for ident in treasury:
        duties[ident] = COLLECTOR_DUTY if ident in collectors else TUTOR_DUTY
    return duties, {b: n for b, n in seats.items() if n}


def board_members(tribunal: Tribunal) -> dict[str, list[str]]:
    """The archai on each board and the Treasury Council, as the
    sortition assigned them."""
    found: dict[str, list[str]] = {b: [] for b in (*BOARDS, TREASURY_COUNCIL)}
    for office in archai(tribunal):
        duty = office.get("duties", "")
        holder = office.get("holder_id")
        if not is_arche(office) or not holder:
            continue
        if duty in BOARDS:
            found[duty].append(holder)
        elif duty.startswith(TREASURY_COUNCIL):
            found[TREASURY_COUNCIL].append(holder)
    return found


class Sortition(core.Step):
    """The new archai drawn by lot, four from each phyle, the principal
    phyle first, each serving until the next meeting. The draw is made
    once and kept, with one name more from each phyle, so the
    storyguide may set one drawn magus aside and the next drawn takes
    the seat; one who refused to stand is given a shard. A phyle with too
    few politai leaves seats for the logothete to fill with Redcaps. The
    archai are then assigned to the boards and the Treasury Council, and
    the tamias drawn (assign_boards)."""

    def _order(self, tribunal: Tribunal, meeting: Meeting) -> list[str]:
        principal = (_record(meeting).get("assembly") or {}).get(
            "principal"
        ) or next_principal(tribunal)
        order = list(PHYLAI)
        start = order.index(principal) if principal in order else 0
        return order[start:] + order[:start]

    def _draw(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting
    ) -> dict[str, list[str]]:
        record = _record(meeting)
        if "draw" not in record:
            year = _year(saga, meeting)
            record["draw"] = {}
            made = set((record.get("assembly") or {}).get("citizens", []))
            for phyle in self._order(tribunal, meeting):
                pool = sortition_pool(saga, tribunal, year, phyle, made)
                count = min(len(pool), ARCHAI_PER_PHYLE + 1)
                record["draw"][phyle] = core.rng().sample(pool, count)
        return record["draw"]

    def _seated(
        self, draw: dict[str, list[str]], set_aside: str | None
    ) -> dict[str, list[str]]:
        seated = {}
        for phyle, drawn in draw.items():
            names = [i for i in drawn if i != set_aside]
            seated[phyle] = names[:ARCHAI_PER_PHYLE]
        return seated

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        draw = self._draw(saga, tribunal, meeting)
        if not any(draw.values()):
            return [
                DialogField(
                    "none",
                    "",
                    "info",
                    "No polites is recorded in a phyle to draw: enter each "
                    "covenant's phyle on the roster.",
                ),
                core._note_field(meeting, self.key),
            ]
        seated = self._seated(draw, None)
        found = []
        for phyle in self._order(tribunal, meeting):
            names = _names(saga, seated.get(phyle, [])) or "no one"
            short = ARCHAI_PER_PHYLE - len(seated.get(phyle, []))
            vacant = (
                f" ({short} seat{'s' if short != 1 else ''} for Redcaps)"
                if short
                else ""
            )
            found.append(
                DialogField(
                    f"drawn_{phyle}", "", "info", f"{phyle}: {escape(names)}{vacant}"
                )
            )
        drawn_ids = [i for phyle in draw for i in seated.get(phyle, [])]
        found += [
            DialogField(
                "set_aside",
                "Set aside",
                "select",
                (_record(meeting).get("sortition") or {}).get("set_aside"),
                options=_options(_named(saga, drawn_ids)),
                allow_blank=True,
                placeholder="(no one)",
                hint="One magus drawn may be set aside; the next name drawn "
                "from the same phyle takes the seat.",
            ),
            DialogField(
                "why",
                "Why set aside",
                "select",
                (_record(meeting).get("sortition") or {}).get("why", REFUSED),
                options=[
                    ("Refused to stand: a shard", REFUSED),
                    ("Some other cause: no shard", "other"),
                ],
                show_if=lambda values: bool(values.get("set_aside")),
                hint="A polites eligible for the list who refuses consent is "
                "given a shard (The Sundered Eagle p. 32); one unable to "
                "attend stays on the list.",
            ),
            core._note_field(meeting, self.key),
        ]
        return found

    def live(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        set_aside = values.get("set_aside")
        if not set_aside:
            return ""
        draw = self._draw(saga, tribunal, meeting)
        for phyle, drawn in draw.items():
            if set_aside in drawn:
                seated = self._seated({phyle: drawn}, set_aside)[phyle]
                taken = [i for i in seated if i not in drawn[:ARCHAI_PER_PHYLE]]
                if taken:
                    return f"{escape(_names(saga, taken))} takes the seat."
                return "No one is left in the phyle to take the seat."
        return ""

    def _undo(self, tribunal: Tribunal, meeting: Meeting) -> None:
        held = _record(meeting).get("sortition") or {}
        if held.get("shard_to"):
            _adjust(tribunal, held["shard_to"], "shards", -1)
        served = boards_served(tribunal)
        for ident, board in (held.get("boards_added") or {}).items():
            past = served.get(ident, [])
            if board in past:
                past.remove(board)
            if not past:
                served.pop(ident, None)

    def _duties(
        self,
        tribunal: Tribunal,
        meeting: Meeting,
        seated: dict[str, list[str]],
    ) -> dict[str, Any]:
        """The boards drawn for the seated archai, drawn once for a set
        of archai and kept, so holding the step again gives the same."""
        record = _record(meeting)
        ids = sorted(i for names in seated.values() for i in names)
        kept = record.get("boards_draw") or {}
        if kept.get("for") != ids:
            phyle_of = {i: phyle for phyle, names in seated.items() for i in names}
            duties, redcaps = assign_boards(
                [i for phyle in seated for i in seated[phyle]],
                boards_served(tribunal),
                phyle_of,
                core.rng(),
            )
            kept = {"for": ids, "duties": duties, "redcap_seats": redcaps}
            record["boards_draw"] = kept
        return kept

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        self._undo(tribunal, meeting)
        draw = self._draw(saga, tribunal, meeting)
        set_aside = values.get("set_aside")
        seated = self._seated(draw, set_aside)
        ends = core._next(tribunal, meeting)
        drawn = self._duties(tribunal, meeting, seated)
        duties: dict[str, str] = drawn["duties"]
        archai(tribunal)[:] = [o for o in archai(tribunal) if not is_arche(o)]
        tamias = None
        for phyle in self._order(tribunal, meeting):
            for ident in seated.get(phyle, []):
                duty = duties.get(ident, "")
                if duty == TAMIAS_DUTY:
                    tamias = ident
                archai(tribunal).append(
                    {
                        "office": f"{ARCHE} ({phyle})",
                        "holder_id": ident,
                        "term_ends": ends,
                        "duties": duty,
                    }
                )
        if any(o.get("office", "").casefold() == "tamias" for o in archai(tribunal)):
            _office(tribunal, "Tamias").update(holder_id=tamias, term_ends=ends)
        served = boards_served(tribunal)
        added: dict[str, str] = {}
        for ident, duty in duties.items():
            if duty in BOARDS:
                served.setdefault(ident, []).append(duty)
                added[ident] = duty
        held: dict[str, Any] = {
            "set_aside": set_aside,
            "why": values.get("why") or REFUSED,
            "seated": seated,
            "boards_added": added,
            "redcap_seats": drawn.get("redcap_seats", {}),
        }
        if set_aside and held["why"] == REFUSED:
            entry = entry_of(tribunal, set_aside, create=True)
            if entry is not None and not is_metoikos(entry):
                _adjust(tribunal, set_aside, "shards", 1)
                held["shard_to"] = set_aside
        _record(meeting)["sortition"] = held
        core._keep_note(meeting, self.key, values)

    def save_label(self):
        return "Draw"

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = _record(meeting).get("sortition")
        if not held:
            return "", ""
        parts = [
            f"for the {phyle} phyle {_names(saga, ids)}"
            for phyle, ids in held["seated"].items()
            if ids
        ]
        if not parts:
            return "", ""
        words = "By sortition the new archai were drawn: " + "; ".join(parts) + "."
        aside = saga.character(held.get("set_aside"))
        if aside is not None:
            refused = held.get("why", REFUSED) == REFUSED
            words += (
                f" {aside.name} refused to stand and was given a shard."
                if refused
                else f" {aside.name} was set aside."
            )
        boards = [
            f"{board}: {_names(saga, ids)}"
            for board, ids in board_members(tribunal).items()
            if ids
        ]
        if boards:
            words += " The archai were assigned: " + "; ".join(boards) + "."
        redcaps = {b: n for b, n in (held.get("redcap_seats") or {}).items() if n}
        if redcaps:
            words += (
                " The logothete fills with Redcaps "
                + ", ".join(
                    f"{n} seat{'' if n == 1 else 's'} on the {b}"
                    for b, n in redcaps.items()
                )
                + "."
            )
        count = sum(len(ids) for ids in held["seated"].values())
        return words, f"{count} archai"


def _office(tribunal: Tribunal, name: str) -> dict[str, Any]:
    for office in archai(tribunal):
        if office.get("office", "").casefold() == name.casefold():
            return office
    office = {"office": name, "holder_id": None, "term_ends": None, "duties": ""}
    archai(tribunal).insert(0 if name == "Archon" else 1, office)
    return office


class ArchonAndPolemarch(core.Step):
    """The new archai elect the archon from among themselves, by tradition
    the eldest unless they prefer another, and then the polemarch from
    every polites (the same magus is often chosen again). The archon is
    the Tribunal's Praeco."""

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        new = _named(saga, [o["holder_id"] for o in archai(tribunal) if is_arche(o)])
        year = _year(saga, meeting)
        if not new:
            return [
                DialogField(
                    "none",
                    "",
                    "info",
                    "No archai are seated: hold the sortition first.",
                ),
                core._note_field(meeting, self.key),
            ]
        eldest = core.eldest_magi(saga, tribunal)
        by_age = sorted(new, key=lambda m: eldest.index(m) if m in eldest else 999)
        held = _record(meeting).get("election") or {}
        polemarch = _office(tribunal, "Polemarch").get("holder_id")
        return [
            DialogField(
                "archon",
                "Archon",
                "select",
                held.get("archon") or by_age[0].id,
                options=_options(by_age),
                required=True,
                hint="Chosen by the archai from among themselves; an arche "
                "with no preference votes for the eldest.",
            ),
            DialogField(
                "polemarch",
                "Polemarch",
                "select",
                held.get("polemarch") or polemarch,
                options=_options(politai(saga, tribunal, year)),
                allow_blank=True,
                placeholder="(vacant)",
                hint="Chosen by the archai from every polites; only a past "
                "polemarch may refuse.",
            ),
            core._note_field(meeting, self.key),
        ]

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        ends = core._next(tribunal, meeting)
        if values.get("archon"):
            archon = _office(tribunal, "Archon")
            archon.update(holder_id=values["archon"], term_ends=ends)
            tribunal.praeco_id = values["archon"]
        polemarch = _office(tribunal, "Polemarch")
        polemarch.update(holder_id=values.get("polemarch") or None, term_ends=ends)
        _record(meeting)["election"] = {
            "archon": values.get("archon"),
            "polemarch": values.get("polemarch"),
        }
        core._keep_note(meeting, self.key, values)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = _record(meeting).get("election") or {}
        archon = saga.character(held.get("archon"))
        polemarch = saga.character(held.get("polemarch"))
        return core._join(
            f"[$label]Archon:[/] {escape(archon.name)}" if archon else "",
            f"[$label]Polemarch:[/] {escape(polemarch.name)}" if polemarch else "",
            core._note_text(meeting, self.key),
        )

    def save_label(self):
        return "Elect"

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = _record(meeting).get("election") or {}
        archon = saga.character(held.get("archon"))
        polemarch = saga.character(held.get("polemarch"))
        ends = core._next(tribunal, meeting)
        parts = []
        if archon is not None:
            parts.append(f"The archai elected {archon.name} archon")
        if polemarch is not None:
            parts.append(f"{polemarch.name} polemarch")
        if not parts:
            return "", ""
        return " and ".join(parts) + f", until {ends}.", "Archon"


# -- the execution of sentences --

#: The shards a conviction carries, by the kind of crime, and the tokens
#: the magus who brought the case earns: one, or three if the guilty is
#: Marched; a case the People's Court defeats costs its bringer a shard
#: (The Sundered Eagle pp. 28, 35).
CRIME_SHARDS = {"high": 3, "low": 1}
CONVICTION_TOKENS, MARCH_TOKENS = 1, 3
DEFEATED_SHARDS = 1

CONVICTED, EXONERATED, NO_VERDICT = "convicted", "exonerated", "none"


def verdict_of(meeting: Meeting, case: Case) -> str:
    """How the People's Court found: a charge carried is a conviction, one
    that failed an exoneration; one settled or not voted, no verdict."""
    kept = meeting.get("votes", {}).get(case.id)
    if core.settled(meeting, case) or kept is None:
        return NO_VERDICT
    carried = core.passes(core.kept_votes(kept), kept.get("tie", ""))
    if carried is None:
        return NO_VERDICT
    return CONVICTED if carried else EXONERATED


def _crime_of(case: Case) -> str:
    words = f"{case.charge} {case.penalty}".casefold()
    return "high" if "high crime" in words or "march" in words else "low"


def sentence_changes(
    verdict: str, crime: str, marched: bool, guilty: str | None, accuser: str | None
) -> list[tuple[str, str, int]]:
    """What a case's outcome gives, as (character id, "tokens" or
    "shards", how many)."""
    found: list[tuple[str, str, int]] = []
    if verdict == CONVICTED:
        if guilty:
            found.append((guilty, "shards", CRIME_SHARDS.get(crime, 1)))
        if accuser:
            tokens = MARCH_TOKENS if marched else CONVICTION_TOKENS
            found.append((accuser, "tokens", tokens))
    elif verdict == EXONERATED and accuser:
        found.append((accuser, "shards", DEFEATED_SHARDS))
    return found


class Sentences(core.Step):
    """The first business of the Council of Archai: each charge the
    People's Court heard. A conviction carries three shards for a High
    Crime or one for a Low Crime, beside its punishment, and the magus
    who brought the case earns a token, three if the guilty is Marched;
    one whose case was defeated is given a shard. A metoikos holds no
    tokens or shards, so is given none. No March is held on Delos."""

    def _cases(self, tribunal: Tribunal) -> list[Case]:
        return [c for c in tribunal_sheet.open_cases(tribunal) if c.kind == "charge"]

    def _undo(self, tribunal: Tribunal, meeting: Meeting) -> None:
        for ident, key, by in _record(meeting).pop("sentences", []):
            _adjust(tribunal, ident, key, -by)

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        cases = self._cases(tribunal)
        if not cases:
            return [
                DialogField("none", "", "info", "No charge was heard at this meeting."),
                core._note_field(meeting, self.key),
            ]
        kept = _record(meeting).get("sentence_choices") or {}
        people = _options(tribunal_magi(saga, tribunal))
        found: list[DialogField] = []
        for case in cases:
            mine = kept.get(case.id) or {}
            short = escape(
                case.title if len(case.title) <= 30 else case.title[:29] + "…"
            )
            guilty = core._magus_named(saga, case.against)
            accuser = core._magus_named(saga, case.brought_by)
            found += [
                DialogField(
                    f"verdict_{case.id}",
                    f"{short}: the verdict",
                    "select",
                    mine.get("verdict") or verdict_of(meeting, case),
                    options=[
                        ("Convicted", CONVICTED),
                        ("Exonerated: a shard to the accuser", EXONERATED),
                        ("No verdict (settled or withdrawn)", NO_VERDICT),
                    ],
                ),
                DialogField(
                    f"crime_{case.id}",
                    f"{short}: the crime",
                    "select",
                    mine.get("crime") or _crime_of(case),
                    options=[
                        ("A High Crime: three shards", "high"),
                        ("A Low Crime: one shard", "low"),
                    ],
                    show_if=lambda v, cid=case.id: v.get(f"verdict_{cid}") == CONVICTED,
                ),
                DialogField(
                    f"marched_{case.id}",
                    f"{short}: Wizard's March",
                    "check",
                    bool(mine.get("marched")),
                    hint="Held off Delos, where no death may happen (p. 35).",
                    show_if=lambda v, cid=case.id: v.get(f"verdict_{cid}") == CONVICTED,
                ),
                DialogField(
                    f"guilty_{case.id}",
                    f"{short}: the accused",
                    "select",
                    mine.get("guilty") or (guilty.id if guilty else None),
                    options=people,
                    allow_blank=True,
                    placeholder="(not a Theban magus)",
                ),
                DialogField(
                    f"accuser_{case.id}",
                    f"{short}: brought by",
                    "select",
                    mine.get("accuser") or (accuser.id if accuser else None),
                    options=people,
                    allow_blank=True,
                    placeholder="(not a Theban magus)",
                ),
            ]
        found.append(core._note_field(meeting, self.key))
        return found

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        self._undo(tribunal, meeting)
        done: list[tuple[str, str, int]] = []
        choices: dict[str, dict[str, Any]] = {}
        for case in self._cases(tribunal):
            mine = {
                "verdict": values.get(f"verdict_{case.id}") or NO_VERDICT,
                "crime": values.get(f"crime_{case.id}") or "low",
                "marched": bool(values.get(f"marched_{case.id}")),
                "guilty": values.get(f"guilty_{case.id}") or None,
                "accuser": values.get(f"accuser_{case.id}") or None,
            }
            choices[case.id] = mine
            for ident, key, by in sentence_changes(
                mine["verdict"],
                mine["crime"],
                mine["marched"],
                mine["guilty"],
                mine["accuser"],
            ):
                entry = entry_of(tribunal, ident, create=True)
                if entry is None or is_metoikos(entry):
                    continue
                _adjust(tribunal, ident, key, by)
                done.append((ident, key, by))
        _record(meeting)["sentences"] = done
        _record(meeting)["sentence_choices"] = choices
        core._keep_note(meeting, self.key, values)

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return (
            "Each charge's verdict, from how its vote went.",
            "A conviction gives the guilty three shards for a High Crime or one "
            "for a Low, and the accuser a token (three if the guilty is "
            "Marched); a defeated case gives the accuser a shard.",
        )

    def save_label(self):
        return "Sentence"

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        done = _record(meeting).get("sentences", [])
        if not done:
            return "", ""
        parts = []
        for ident, key, by in done:
            magus = saga.character(ident)
            if magus is not None:
                noun = key[:-1] if by == 1 else key
                parts.append(f"{magus.name} {by} {noun}")
        return (
            "With the sentences, the tokens and shards were given: "
            + ", ".join(parts)
            + ".",
            "",
        )


# -- the Ceremony of Propitiation --

#: The archon's Ritual at the lake costs eight pawns of Creo or Vim from
#: the Tribunal's coffers; a propitiated patron gains 25 xp, less its
#: Might, but each pawn offered takes two from that penalty (The Sundered
#: Eagle p. 31).
CEREMONY_PAWNS = 8
PATRON_XP = 25
PAWN_OFFSET = 2


def patron_xp(might: int, pawns: int) -> int:
    """The xp a patron of `might` gains from `pawns` offered: 25 less its
    Might, the Might's penalty cut by two a pawn (a Might 25 patron
    offered 10 pawns gains 20)."""
    if pawns <= 0:
        return 0
    return max(0, PATRON_XP - max(0, might - PAWN_OFFSET * pawns))


def patrons(tribunal: Tribunal) -> dict[str, dict[str, Any]]:
    """Each covenant's patron, by covenant id: {"name", "might"}."""
    found = data(tribunal, KEY).setdefault("patrons", {})
    if not isinstance(found, dict):
        raise ValueError(f"The patrons should be a mapping, not {found!r}.")
    return found


class Propitiation(core.Step):
    """The closing rite at the sacred lake on Delos: the archon casts the
    ancient Ritual from its Casting Tablet, at eight pawns of Creo or
    Vim from the Tribunal's coffers, and each covenant offers to its
    patron, most often vis. Each patron gains 25 xp less its Might, its
    Might's penalty cut by two for each pawn offered. The League Against
    Idolatry boycotts the rite."""

    def _undo(self, tribunal: Tribunal, meeting: Meeting) -> None:
        held = _record(meeting).pop("propitiation", None)
        if not held:
            return
        ident = held.get("treasury_id")
        tribunal.treasury[:] = [e for e in tribunal.treasury if e.id != ident]

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = _record(meeting).get("propitiation") or {}
        offered = held.get("offerings") or {}
        found = [
            DialogField(
                "art",
                "The archon's Ritual: 8 pawns of",
                "select",
                held.get("art", "Vim"),
                options=[("Creo", "Creo"), ("Vim", "Vim"), ("Not cast", "")],
                hint="From the Tribunal's coffers (The Sundered Eagle p. 31).",
            )
        ]
        for covenant in tribunals.covenants_of(saga, tribunal):
            patron = patrons(tribunal).get(covenant.id) or {}
            mine = offered.get(covenant.id) or {}
            name = escape(covenant.name)
            found += [
                DialogField(
                    f"pawns_{covenant.id}",
                    f"{name}: pawns offered",
                    "int",
                    int(mine.get("pawns", 0)),
                    hint=f"To {escape(patron['name'])}." if patron.get("name") else "",
                ),
                DialogField(
                    f"might_{covenant.id}",
                    f"{name}: the patron's Might",
                    "optint",
                    mine.get("might", patron.get("might")),
                    show_if=lambda v, cid=covenant.id: bool(v.get(f"pawns_{cid}")),
                ),
            ]
        found.append(core._note_field(meeting, self.key))
        return found

    def validate(self, meeting: Meeting, values: dict[str, Any]):
        for key, value in values.items():
            if key.startswith(("pawns_", "might_")) and (value or 0) < 0:
                return "Pawns and Might can't be fewer than none."
        return None

    def live(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        total = sum(v or 0 for k, v in values.items() if k.startswith("pawns_"))
        return f"{total} pawns offered at the lake." if total else ""

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        self._undo(tribunal, meeting)
        held: dict[str, Any] = {"art": values.get("art") or "", "offerings": {}}
        if held["art"]:
            entry = TreasuryEntry(
                "vis",
                -CEREMONY_PAWNS,
                art=held["art"],
                who="the archon",
                note=f"The Ceremony of Propitiation, {_year(saga, meeting)}",
            )
            tribunal.treasury.append(entry)
            held["treasury_id"] = entry.id
        for covenant in tribunals.covenants_of(saga, tribunal):
            pawns = int(values.get(f"pawns_{covenant.id}") or 0)
            might = values.get(f"might_{covenant.id}")
            if not pawns:
                continue
            offering: dict[str, Any] = {"pawns": pawns, "might": might}
            if might is not None:
                patrons(tribunal).setdefault(covenant.id, {})["might"] = might
                offering["xp"] = patron_xp(int(might), pawns)
            held["offerings"][covenant.id] = offering
        _record(meeting)["propitiation"] = held
        core._keep_note(meeting, self.key, values)

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return (
            "The archon's Ritual, and each covenant's offering to its patron.",
            "The Ritual's 8 pawns come out of the treasury; each patron's xp "
            "is 25 less its Might, the Might cut by two a pawn offered.",
        )

    def save_label(self):
        return "Offer"

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        held = _record(meeting).get("propitiation")
        if not held:
            return "", ""
        parts = []
        for ident, offering in held.get("offerings", {}).items():
            covenant = saga.covenant(ident)
            if covenant is None:
                continue
            xp = offering.get("xp")
            gain = f", its patron gaining {xp} xp" if xp is not None else ""
            parts.append(f"{covenant.name} {offering['pawns']} pawns{gain}")
        words = "At the lake on Delos the Ceremony of Propitiation was held"
        if held.get("art"):
            words += (
                f", the archon's Ritual costing {CEREMONY_PAWNS} pawns of {held['art']}"
            )
        words += "." + (" Offered: " + "; ".join(parts) + "." if parts else "")
        total = sum(o["pawns"] for o in held.get("offerings", {}).values())
        return words, f"{total} pawns offered"


core.register_step("assembly", "The Assembly's decrees", Assembly, "opening")
core.register_step("ostrakismos", "The ostrakismos", Ostrakismos, "opening")
core.register_step("sentences", "The execution of sentences", Sentences, "end")
core.register_step("end_of_term", "The outgoing magistrates' tokens", EndOfTerm, "end")
core.register_step("sortition", "The sortition", Sortition, "end")
core.register_step(
    "archon_polemarch", "Archon and polemarch", ArchonAndPolemarch, "end"
)
core.register_step(
    "propitiation", "The Ceremony of Propitiation", Propitiation, "closing"
)
