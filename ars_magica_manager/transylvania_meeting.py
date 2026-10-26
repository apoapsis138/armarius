"""The Transylvanian Tribunal's meeting steps (Against the Dark pp. 19,
97).

The Praeco's purse (p. 19): at each meeting the Tribunal gives the
Praeco the projects she is to fund, and with them the levies she may
raise; the legal covenants of the cives, socii and coloniae, and some
foederati, owe them reasonable aid (by their status, not each magus). A
large vis source is set aside for her use. She collects the Redcaps'
and Quaesitores' stipends and Redcaps deliver them, so they pass through
the treasury. She may also borrow against
the treasury's income, issuing promissory notes that are redeemed when
presented to her; old notes still change hands as a currency.

The Curantis (p. 97): appointed at every meeting for a term to the
next, usually as the single candidate the elders agreed beforehand; he
may not serve two terms running. He tours the zenodochia, the
Tribunal's safehouses, about a season a year, and is expected to build
at least one new one in his term. He draws a generous vis salary from
the Tribunal, which the troupe sets, and the outgoing Curantis selects
his Notary.

Both are meeting.Steps (the Template Method the core's steps fill in),
registered under the names the Transylvanian package lists. What each
did is kept in the meeting record under "transylvania", by step key:
the levies {"projects", "art", "levies" {covenant id: pawns}, "paid",
"source", "source_art", "stipends", "note_holder", "note_pawns",
"note_art", "rows" [treasury entry ids made], "redeemed" [note ids]},
and the Curantis {"curantis", "notary", "salary", "art", "built",
"rows"}."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from types import MappingProxyType
from typing import Any

from . import meeting as core
from . import tribunals
from .arts import ARTS
from .form_spec import DialogField, pairs
from .markup import escape
from .models import Meeting, Saga, TreasuryEntry, Tribunal
from .treasury import LEVY, NOTE, amount_text, pawns, pounds
from .tribunal_packages import transylvania as tr

SOURCE = "Against the Dark pp. 19, 97"


def _record(meeting: Meeting, key: str) -> dict[str, Any]:
    return meeting.setdefault("transylvania", {}).setdefault(key, {})


def _year(saga: Saga, meeting: Meeting) -> int:
    return int(meeting.get("year") or saga.current_year)


def _held(meeting: Meeting, key: str) -> bool:
    return key in meeting.get("done", [])


def _amount(amount: float, art: str) -> str:
    return pawns(amount, art) if art else pounds(amount)


def _drop_rows(tribunal: Tribunal, ids: list[str]) -> None:
    """Take out the treasury entries an earlier holding of a step made."""
    gone = set(ids)
    tribunal.treasury = [e for e in tribunal.treasury if e.id not in gone]


def _art_field(
    key: str,
    label: str,
    value: str | None,
    silver: bool,
    show_if: Callable[[dict[str, Any]], bool] | None = None,
) -> DialogField:
    return DialogField(
        key,
        label,
        "select",
        value or (None if silver else "Vim"),
        options=pairs(ARTS),
        allow_blank=silver,
        placeholder="(silver)",
        hint="Leave blank for pounds of silver." if silver else "",
        show_if=show_if,
    )


def outstanding_notes(tribunal: Tribunal, meeting: Meeting) -> list[TreasuryEntry]:
    """The promissory notes not yet redeemed, and those this meeting
    redeemed (so holding it again shows them still)."""
    redeemed = set(_record(meeting, "praeco_purse").get("redeemed", []))
    return [
        e
        for e in tribunal.treasury
        if e.kind == NOTE and (not e.paid or e.id in redeemed)
    ]


class PraecoPurse(core.Step):
    """The projects given the Praeco, the levies raised for them on each
    oppidum, her reserved vis source, the stipends she passes on, and
    the promissory notes she redeems and issues."""

    _no_aid: frozenset[str] = frozenset()

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        kept = _record(meeting, "praeco_purse")
        levies = kept.get("levies", {})
        oppida = tribunals.covenants_of(saga, tribunal)
        self._no_aid = frozenset(
            c.id for c in oppida if tr.owes_no_aid(saga, tribunal, c)
        )
        found = [
            DialogField(
                "projects",
                "The Praeco's projects",
                "area",
                kept.get("projects", tr.projects(tribunal)),
                hint="What the Tribunal charges the Praeco to fund until the "
                "next meeting; they, and the levies she may raise, change at "
                "every meeting (Against the Dark p. 19).",
            ),
            _art_field("art", "Levies in", kept.get("art"), silver=True),
        ]
        for oppidum in oppida:
            found.append(
                DialogField(
                    f"levy_{oppidum.id}",
                    f"Levy on {escape(oppidum.name)}",
                    "optint",
                    levies.get(oppidum.id),
                    hint=escape(tr.aid_text(saga, tribunal, oppidum)),
                )
            )
        found += [
            DialogField(
                "paid",
                "Levies paid at the meeting",
                "check",
                bool(kept.get("paid", False)),
                hint="Unpaid, they stay owed on the treasury until marked paid.",
            ),
            DialogField(
                "source",
                "From her vis source",
                "optint",
                kept.get("source"),
                hint="Pawns from the large vis source set aside for the "
                "Praeco's use, into the treasury.",
            ),
            _art_field("source_art", "Its Art", kept.get("source_art"), silver=False),
            DialogField(
                "stipends",
                "Stipends passed on",
                "text",
                kept.get("stipends", ""),
                placeholder="e.g. 4 pawns of Vim to each Quaesitor",
                hint="The Redcaps' and Quaesitores' stipends, as the Peripheral "
                "Code sets them: she collects them and Redcaps deliver them, "
                "so the treasury doesn't change.",
            ),
        ]
        for note in outstanding_notes(tribunal, meeting):
            redeemed = note.id in kept.get("redeemed", [])
            found.append(
                DialogField(
                    f"redeem_{note.id}",
                    f"Redeem {escape(note.who or 'a holder')}'s note",
                    "check",
                    redeemed if _held(meeting, self.key) else False,
                    hint=escape(
                        f"{amount_text(note)}; redeemed, it leaves the treasury."
                    ),
                )
            )
        found += [
            DialogField(
                "note_holder",
                "New note to",
                "text",
                kept.get("note_holder", ""),
                placeholder="who lends against the treasury's income",
                hint="A promissory note: what is lent comes into the treasury "
                "now, and leaves it when the note is presented and redeemed.",
            ),
            DialogField(
                "note_pawns",
                "Its face value",
                "optint",
                kept.get("note_pawns"),
                show_if=lambda v: bool(v.get("note_holder")),
            ),
            _art_field(
                "note_art",
                "Its Art",
                kept.get("note_art"),
                silver=True,
                show_if=lambda v: bool(v.get("note_holder")),
            ),
            core._note_field(meeting, self.key),
        ]
        return found

    def validate(self, meeting: Meeting, values: dict[str, Any]):
        for key, value in values.items():
            if value is None or not isinstance(value, int) or value >= 0:
                continue
            if key.startswith("levy_") or key in ("source", "note_pawns"):
                return "An amount can't be fewer than none."
        for ident in self._no_aid:
            if values.get(f"levy_{ident}"):
                return (
                    "That oppidum's magi are all hospites, whom the Praeco's "
                    "levies don't reach (Against the Dark p. 19)."
                )
        return None

    def _undo(self, tribunal: Tribunal, meeting: Meeting) -> None:
        kept = _record(meeting, "praeco_purse")
        _drop_rows(tribunal, kept.get("rows", []))
        undone = set(kept.get("redeemed", []))
        for entry in tribunal.treasury:
            if entry.id in undone:
                entry.paid = False
        kept["rows"], kept["redeemed"] = [], []

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        core._keep_note(meeting, self.key, values)
        notes = outstanding_notes(tribunal, meeting)
        self._undo(tribunal, meeting)
        kept = _record(meeting, "praeco_purse")
        year = _year(saga, meeting)
        rows: list[str] = []

        def add(entry: TreasuryEntry) -> None:
            tribunal.treasury.append(entry)
            rows.append(entry.id)

        words = (values.get("projects") or "").strip()
        kept["projects"] = words
        tr.data(tribunal, tr.KEY)["projects"] = words
        art = values.get("art") or ""
        paid = bool(values.get("paid"))
        levies: dict[str, int] = {}
        for oppidum in tribunals.covenants_of(saga, tribunal):
            amount = int(values.get(f"levy_{oppidum.id}") or 0)
            if amount > 0:
                levies[oppidum.id] = amount
                add(
                    TreasuryEntry(
                        LEVY,
                        amount,
                        art=art,
                        who=oppidum.name,
                        paid=paid,
                        note=f"For the Praeco's projects, {year}",
                    )
                )
        kept.update(art=art, levies=levies, paid=paid)
        source = int(values.get("source") or 0)
        source_art = values.get("source_art") or "Vim"
        kept.update(source=source or None, source_art=source_art)
        if source > 0:
            add(
                TreasuryEntry(
                    "vis",
                    source,
                    art=source_art,
                    note=f"From the Praeco's vis source, {year}",
                )
            )
        kept["stipends"] = (values.get("stipends") or "").strip()
        kept["redeemed"] = [n.id for n in notes if values.get(f"redeem_{n.id}")]
        for note in notes:
            if note.id in kept["redeemed"]:
                note.paid = True
        holder = (values.get("note_holder") or "").strip()
        face = int(values.get("note_pawns") or 0)
        note_art = values.get("note_art") or ""
        kept.update(note_holder=holder, note_pawns=face or None, note_art=note_art)
        if holder and face > 0:
            add(
                TreasuryEntry(
                    NOTE, face, art=note_art, who=holder, note=f"Issued {year}"
                )
            )
            add(
                TreasuryEntry(
                    "vis" if note_art else "silver",
                    face,
                    art=note_art,
                    who=holder,
                    note=f"Lent against a promissory note, {year}",
                )
            )
        kept["rows"] = rows

    def _lines(self, saga: Saga, tribunal: Tribunal, meeting: Meeting) -> list[str]:
        kept = _record(meeting, "praeco_purse")
        lines = []
        if kept.get("projects"):
            lines.append(f"The Praeco's projects: {kept['projects']}")
        levies = kept.get("levies", {})
        if levies:
            art = kept.get("art") or ""
            each = []
            for ident, amount in levies.items():
                oppidum = saga.covenant(ident)
                name = oppidum.name if oppidum is not None else "(gone)"
                each.append(f"{name} {_amount(amount, art)}")
            paid = "paid" if kept.get("paid") else "owed"
            lines.append(f"Levies ({paid}): " + ", ".join(each))
        if kept.get("source"):
            lines.append(
                "From the Praeco's vis source: "
                + pawns(kept["source"], kept.get("source_art") or "Vim")
            )
        if kept.get("stipends"):
            lines.append(f"Stipends passed on: {kept['stipends']}")
        listed = {e.id: e for e in tribunal.treasury}
        for ident in kept.get("redeemed", []):
            note = listed.get(ident)
            if note is not None:
                lines.append(f"Redeemed: {note.who}'s note of {amount_text(note)}")
        if kept.get("note_holder") and kept.get("note_pawns"):
            lines.append(
                f"A promissory note issued to {kept['note_holder']}, for "
                + _amount(kept["note_pawns"], kept.get("note_art") or "")
            )
        return lines

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return core._join(
            *(escape(line) for line in self._lines(saga, tribunal, meeting)),
            core._note_text(meeting, self.key),
        )

    def save_label(self):
        return "Levy"

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        oppida = len(tribunals.covenants_of(saga, tribunal))
        notes = len(outstanding_notes(tribunal, meeting))
        return (
            f"{oppida} oppid{'um' if oppida == 1 else 'a'} the Praeco may levy, "
            f"and {notes} promissory note{'' if notes == 1 else 's'} outstanding.",
            "Each levy is owed to the treasury until paid; her vis source and "
            "what a new note borrows come in, and a redeemed note's pawns go out.",
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        lines = self._lines(saga, tribunal, meeting)
        if not lines:
            return "", ""
        count = len(_record(meeting, "praeco_purse").get("levies", {}))
        return (
            "; ".join(lines) + ".",
            f"{count} lev{'y' if count == 1 else 'ies'}",
        )


class Curantis(core.Step):
    """The outgoing Curantis's term reckoned, and the next appointed with
    his Notary and salary."""

    _outgoing: dict[str, Any] | None = None
    _refused: Mapping[str, str] = MappingProxyType({})

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        kept = _record(meeting, "curantis")
        year = _year(saga, meeting)
        self._outgoing = outgoing = tr.curantis_entry(tribunal, before=year)
        magi = core.eldest_magi(saga, tribunal)
        self._refused = {
            m.id: problem
            for m in magi
            if (problem := tr.curantis_problem(saga, tribunal, m.id, outgoing))
        }
        options = [(escape(m.name), m.id) for m in magi]
        found: list[DialogField] = []
        if outgoing is not None:
            name = escape(tr._name(saga, outgoing.get("character_id")))
            found += [
                DialogField(
                    "outgoing",
                    "",
                    "info",
                    f"{name} has been Curantis since {outgoing.get('year')}.",
                ),
                DialogField(
                    "built",
                    "Zenodochium built",
                    "check",
                    bool(kept.get("built", outgoing.get("built", False))),
                    hint=f"Whether {name} built a new zenodochium in his term, "
                    "as he is expected to (Against the Dark p. 97).",
                ),
            ]
        else:
            found.append(
                DialogField(
                    "outgoing", "", "info", "No Curantis is recorded before this one."
                )
            )
        chooser = (
            f"Selected by the outgoing Curantis, {escape(tr._name(saga, outgoing.get('character_id')))}"
            if outgoing is not None
            else "Selected by the outgoing Curantis"
        )
        found += [
            DialogField(
                "curantis",
                "Curantis",
                "select",
                kept.get("curantis"),
                options=options,
                allow_blank=True,
                placeholder="(none appointed)",
                hint="Voted in until the next meeting, usually unopposed: the "
                "elders agree the single candidate beforehand. No one serves "
                "two terms running.",
            ),
            DialogField(
                "notary",
                "His Notary",
                "select",
                kept.get("notary"),
                options=options,
                allow_blank=True,
                placeholder="(none)",
                hint=f"{chooser}; often a Redcap, or a magus fresh from his "
                "Gauntlet. He acts as the Curantis's aedile.",
                show_if=lambda v: bool(v.get("curantis")),
            ),
            DialogField(
                "salary",
                "Salary for the term",
                "optint",
                kept.get("salary"),
                hint="A generous vis salary from the treasury, set to the vis "
                "of your saga: he must be powerful to do the work.",
                show_if=lambda v: bool(v.get("curantis")),
            ),
            _art_field(
                "salary_art",
                "Its Art",
                kept.get("art"),
                silver=False,
                show_if=lambda v: bool(v.get("curantis")),
            ),
            core._note_field(meeting, self.key),
        ]
        return found

    def validate(self, meeting: Meeting, values: dict[str, Any]):
        chosen = values.get("curantis")
        if not chosen:
            return None
        if chosen in self._refused:
            return self._refused[chosen]
        if values.get("notary") == chosen:
            return "The Curantis can't be his own Notary."
        if (values.get("salary") or 0) < 0:
            return "A salary can't be fewer than none."
        return None

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        core._keep_note(meeting, self.key, values)
        kept = _record(meeting, "curantis")
        year = _year(saga, meeting)
        _drop_rows(tribunal, kept.get("rows", []))
        listed = tr.curantes(tribunal)
        listed[:] = [e for e in listed if int(e.get("year") or 0) != year]
        outgoing = tr.curantis_entry(tribunal, before=year)
        if outgoing is not None and "built" in values:
            outgoing["built"] = bool(values["built"])
            kept["built"] = outgoing["built"]
        chosen = values.get("curantis") or None
        salary = int(values.get("salary") or 0) if chosen else 0
        art = values.get("salary_art") or "Vim"
        kept.update(
            curantis=chosen,
            notary=(values.get("notary") or None) if chosen else None,
            salary=salary or None,
            art=art,
            rows=[],
        )
        if chosen is None:
            return
        listed.append(
            {
                "character_id": chosen,
                "year": year,
                "notary_id": kept["notary"],
                "salary": salary,
                "art": art,
            }
        )
        if salary > 0:
            paid = TreasuryEntry(
                "vis",
                -salary,
                art=art,
                who=tr._name(saga, chosen),
                note=f"The Curantis's salary, {year} to the next meeting",
            )
            tribunal.treasury.append(paid)
            kept["rows"] = [paid.id]

    def _lines(self, saga: Saga, tribunal: Tribunal, meeting: Meeting) -> list[str]:
        kept = _record(meeting, "curantis")
        year = _year(saga, meeting)
        lines = []
        outgoing = tr.curantis_entry(tribunal, before=year)
        if outgoing is not None and "built" in kept:
            name = tr._name(saga, outgoing.get("character_id"))
            lines.append(
                f"{name} built a new zenodochium in his term"
                if kept["built"]
                else f"{name} built no new zenodochium in his term"
            )
        if kept.get("curantis"):
            line = f"{tr._name(saga, kept['curantis'])} was appointed Curantis"
            if kept.get("notary"):
                line += f", with {tr._name(saga, kept['notary'])} as his Notary"
            if kept.get("salary"):
                line += (
                    f"; his salary {pawns(kept['salary'], kept.get('art') or 'Vim')}"
                )
            lines.append(line)
        return lines

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return core._join(
            *(escape(line) for line in self._lines(saga, tribunal, meeting)),
            core._note_text(meeting, self.key),
        )

    def save_label(self):
        return "Appoint"

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        outgoing = tr.curantis_entry(tribunal, before=_year(saga, meeting))
        who = (
            f"{tr._name(saga, outgoing.get('character_id'))} may not be appointed again"
            if outgoing is not None
            else "No Curantis is recorded before this meeting"
        )
        return (
            f"The officer of the zenodochia, for a term to the next meeting: {who}.",
            "His salary leaves the treasury now; he and his Notary show on the "
            "Five Covenants list.",
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        lines = self._lines(saga, tribunal, meeting)
        if not lines:
            return "", ""
        return "; ".join(lines) + ".", ""


core.register_step("praeco_purse", "The Praeco's purse", PraecoPurse, "end")
core.register_step("curantis", "The Curantis and his Notary", Curantis, "end")
