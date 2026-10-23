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

from typing import Any

from . import meeting as core
from . import tribunals, world
from .form_spec import DialogField
from .markup import escape
from .models import Character, Meeting, Saga, Tribunal
from .tribunal_packages import data
from .tribunal_packages.theban import (
    KEY,
    PHYLAI,
    archai,
    is_metoikos,
    magi,
    phylai,
)

#: The tokens paid at the end of a term, by the office's first word.
TERM_TOKENS = {"archon": 3, "polemarch": 5, "arche": 2, "tamias": 2}

#: How many archai each phyle sends to the Council.
ARCHAI_PER_PHYLE = 4

#: How many years an ostracised magus is kept out of the Tribunal.
OSTRACISM_YEARS = 7

#: The office the sortition fills, "Arche (Ionian)".
ARCHE = "Arche"


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
        citizens = _options(politai(saga, tribunal, year))
        defamation = held.get("defamation") or {}
        found += [
            DialogField(
                "accused",
                "Defamation: the accused",
                "select",
                defamation.get("accused"),
                options=citizens,
                allow_blank=True,
                placeholder="(no decree of defamation)",
                hint="A polites said to have acted against the unity of the polity.",
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
        self._undo(tribunal, meeting)
        held: dict[str, Any] = {
            "principal": values.get("principal") or next_principal(tribunal),
            "principal_before": data(tribunal, KEY).get("principal_phyle"),
            "citizens": [],
            "contrition": [],
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


def sortition_pool(saga: Saga, tribunal: Tribunal, year: int, phyle: str) -> list[str]:
    """The phyle's candidate list: its politai, but those serving as
    archai now (no one serves two terms running) and the Redcaps, who
    are not drawn."""
    serving = {o.get("holder_id") for o in archai(tribunal) if is_arche(o)}
    covenants = {c.id for c in tribunals.covenants_of(saga, tribunal)}
    return [
        m.id
        for m in politai(saga, tribunal, year)
        if m.covenant_id in covenants
        and phylai(tribunal).get(m.covenant_id or "") == phyle
        and m.id not in serving
        and m.hermetic.house != "house_mercere"
    ]


class Sortition(core.Step):
    """The new archai drawn by lot, four from each phyle, the principal
    phyle first, each serving until the next meeting. The draw is made
    once and kept, with one name more from each phyle, so the
    storyguide may set one drawn magus aside and the next drawn takes
    the seat. A phyle with too few politai leaves seats for the
    logothete to fill with Redcaps."""

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
            for phyle in self._order(tribunal, meeting):
                pool = sortition_pool(saga, tribunal, year, phyle)
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

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        draw = self._draw(saga, tribunal, meeting)
        seated = self._seated(draw, values.get("set_aside"))
        ends = core._next(tribunal, meeting)
        archai(tribunal)[:] = [o for o in archai(tribunal) if not is_arche(o)]
        for phyle in self._order(tribunal, meeting):
            for ident in seated.get(phyle, []):
                archai(tribunal).append(
                    {
                        "office": f"{ARCHE} ({phyle})",
                        "holder_id": ident,
                        "term_ends": ends,
                        "duties": "",
                    }
                )
        _record(meeting)["sortition"] = {
            "set_aside": values.get("set_aside"),
            "seated": seated,
        }
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
            words += f" {aside.name} was set aside."
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


core.register_step("assembly", "The Assembly's decrees", Assembly, "opening")
core.register_step("ostrakismos", "The ostrakismos", Ostrakismos, "opening")
core.register_step("end_of_term", "The outgoing magistrates' tokens", EndOfTerm, "end")
core.register_step("sortition", "The sortition", Sortition, "end")
core.register_step(
    "archon_polemarch", "Archon and polemarch", ArchonAndPolemarch, "end"
)
