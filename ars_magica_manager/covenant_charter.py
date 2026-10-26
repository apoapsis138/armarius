"""A covenant's Charter of Covenant (Covenants pp. 31-36, its blank
charter in the Appendix pp. 125-128): what both front-ends show of it.

The charter is the written Oath of Covenant and its bylaws: what a member
is entitled to, what he owes, and what happens if he fails (p. 32). Its
usual sections run Oath of Covenant, Membership (the members' seals or
signatures are affixed to it), Method of Governance (which also says how
the charter may be altered), Covenant Resources, Member Rights, Member
Obligations and Censure (pp. 33-35). Only breaking the charter is
censured, by withholding privileges or by expulsion, and a charter may
not change a member's obligation against his will (p. 35). A charter a
Quaesitor ratified may become part of the Tribunal's Peripheral Code,
and breaking it can then be charged as a Low Crime (pp. 32, 36). The
Definitive Edition and its errata say nothing of covenant charters.

Clauses are list entries kept on the covenant, as diary lines are; a
clause's status is a plain field, since nothing but how it is drawn
depends on it (the State pattern, reduced to a string).
"""

from __future__ import annotations

from dataclasses import dataclass

from . import world
from .markup import escape, fit
from .models import (
    CHARTER_SECTIONS,
    CLAUSE_AMENDED,
    CLAUSE_BROKEN,
    CLAUSE_IN_FORCE,
    Character,
    CharterClause,
    CharterSeal,
    Covenant,
    CovenantCharter,
    Saga,
)
from .references import Fact

#: The book, as the texts cite it.
COV = "Covenants"

#: Where clauses with no section (or one the book doesn't list) go, once
#: any clause has a section.
OTHER = "Other"

#: The terminal list's column widths (Clause, Text, Agreed); Status takes
#: what is left.
W_CLAUSE, W_TEXT, W_AGREED = 13, 44, 13
COLUMNS = ("Clause", "Text", "Agreed", "Status")


def charter_of(covenant: Covenant) -> CovenantCharter:
    return covenant.charter_of_covenant


def when(year: int | None, season: str) -> str:
    """ "Spring 1115", "1201", "Spring", or "—" with neither."""
    if year is None:
        return season or "—"
    return f"{season} {year}".strip()


def is_numbered(clause: CharterClause) -> bool:
    return clause.number.strip().isdigit()


def clause_mark(clause: CharterClause) -> str:
    """ "1." for a numbered clause, its title as written otherwise."""
    number = clause.number.strip()
    return f"{number}." if is_numbered(clause) else (number or "—")


def clause_name(clause: CharterClause) -> str:
    """ "Clause 1", or the clause's title."""
    number = clause.number.strip()
    return f"Clause {number}" if is_numbered(clause) else (number or "The clause")


def in_force(charter: CovenantCharter) -> int:
    """The clauses not broken (an amended one is in force)."""
    return sum(1 for c in charter.clauses if c.status != CLAUSE_BROKEN)


def broken(charter: CovenantCharter) -> int:
    return sum(1 for c in charter.clauses if c.status == CLAUSE_BROKEN)


def charter_title(charter: CovenantCharter) -> str:
    return charter.name.strip() or "Charter of Covenant"


def clauses_title(charter: CovenantCharter) -> str:
    """ "Clauses (4 in force of 7)", or "Clauses (0)"."""
    total = len(charter.clauses)
    if not total:
        return "Clauses (0)"
    return f"Clauses ({in_force(charter)} in force of {total})"


# -- the members' seals --


@dataclass(frozen=True)
class SealShown:
    """A magus as the charter's seals show him: his seal, or none yet."""

    character: Character
    seal: CharterSeal | None

    @property
    def when(self) -> str:
        return when(self.seal.year, self.seal.season) if self.seal else ""


def seal_of(charter: CovenantCharter, character_id: str) -> CharterSeal | None:
    return next((s for s in charter.seals if s.character_id == character_id), None)


def seals(saga: Saga, covenant: Covenant) -> list[SealShown]:
    """The magi who have sealed the charter, in the order they sealed it
    (those who left the covenant since too, since their seal stays on
    it), then the covenant's magi who haven't sealed it yet."""
    charter = charter_of(covenant)
    by_id = {c.id: c for c in saga.characters}
    shown = [
        SealShown(by_id[s.character_id], s)
        for s in sorted(
            charter.seals,
            key=lambda s: s.year if s.year is not None else 10_000,
        )
        if s.character_id in by_id
    ]
    sealed = {s.character.id for s in shown}
    shown += [
        SealShown(c, None)
        for c in world.covenant_magi(saga, covenant)
        if c.id not in sealed
    ]
    return shown


def sealed_line(saga: Saga, covenant: Covenant) -> str:
    """The terminal's line of seals: "Sealed by: Ilona (Spring 1115),
    Matthaios (1115)  ·  Not yet sworn: Benedek"."""
    found = seals(saga, covenant)
    if not found:
        return "[$label]Sealed by:[/] [dim]no magi in the covenant yet[/]"
    done = [s for s in found if s.seal is not None]
    waiting = [s for s in found if s.seal is None]
    parts = []
    names = ", ".join(
        escape(s.character.name)
        + (f" [dim]({escape(s.when)})[/]" if s.when != "—" else "")
        for s in done
    )
    parts.append(f"[$label]Sealed by:[/] {names or '[dim]no one yet[/]'}")
    if waiting:
        parts.append(
            "[$label]Not yet sworn:[/] "
            + ", ".join(escape(s.character.name) for s in waiting)
        )
    return "  ·  ".join(parts)


# -- the charter --


def facts(saga: Saga, covenant: Covenant) -> list[Fact]:
    """Sworn, its clauses and how many are broken, whether a Quaesitor
    ratified it, and how many of the covenant's magi have sealed it."""
    charter = charter_of(covenant)
    total = len(charter.clauses)
    clauses = f"{total}, {broken(charter)} broken" if total else "None yet"
    found = seals(saga, covenant)
    sealed = sum(1 for s in found if s.seal is not None)
    return [
        Fact(
            "Sworn",
            when(charter.year, charter.season)
            if charter.year or charter.season
            else "",
        ),
        Fact("Clauses", clauses),
        Fact("Ratified", "Yes, by a Quaesitor" if charter.ratified else "No"),
        Fact("Sealed", f"{sealed} of {len(found)}" if found else ""),
    ]


def facts_line(saga: Saga, covenant: Covenant) -> str:
    return "  ·  ".join(
        f"[$label]{escape(f.label)}:[/] {escape(f.value) if f.value else '—'}"
        for f in facts(saga, covenant)
    )


def preamble_text(charter: CovenantCharter) -> str:
    if not charter.preamble.strip():
        return "[dim]No preamble yet: edit the charter to write its oath.[/]"
    return f"[i]{escape(charter.preamble.strip())}[/]"


def charter_text(saga: Saga, covenant: Covenant) -> str:
    """The terminal's charter section: its facts, who sealed it, and its
    preamble."""
    charter = charter_of(covenant)
    lines = [facts_line(saga, covenant), sealed_line(saga, covenant), ""]
    lines.append(preamble_text(charter))
    if charter.ratified:
        lines.append("")
        lines.append(
            f"[dim]Ratified by a Quaesitor: breaking it can be charged as a "
            f"Low Crime ({COV} p. 36).[/]"
        )
    return "\n".join(lines)


# -- the clauses --


def grouped(charter: CovenantCharter) -> list[tuple[str, list[int]]]:
    """The clauses' indexes under their charter section, in the book's
    order, those with none (or one the book doesn't list) last under
    OTHER; with no section used at all, one group with no heading, as
    entered."""
    clauses = charter.clauses
    if not any(c.section in CHARTER_SECTIONS for c in clauses):
        return [("", list(range(len(clauses))))] if clauses else []
    groups: list[tuple[str, list[int]]] = []
    for name in CHARTER_SECTIONS:
        found = [i for i, c in enumerate(clauses) if c.section == name]
        if found:
            groups.append((name, found))
    rest = [i for i, c in enumerate(clauses) if c.section not in CHARTER_SECTIONS]
    if rest:
        groups.append((OTHER, rest))
    return groups


def order(charter: CovenantCharter) -> list[int]:
    """The clauses' indexes in the order the list shows them."""
    return [i for _name, found in grouped(charter) for i in found]


def status_words(clause: CharterClause) -> str:
    """ "In force", "Amended Summer 1180", "Broken 1201"."""
    if clause.status == CLAUSE_IN_FORCE:
        return CLAUSE_IN_FORCE
    since = when(clause.since_year, clause.since_season)
    return clause.status if since == "—" else f"{clause.status} {since}"


#: The theme colour of each status.
STATUS_COLOURS = {
    CLAUSE_IN_FORCE: "text-success",
    CLAUSE_AMENDED: "text-warning",
    CLAUSE_BROKEN: "text-error",
}


def status_markup(clause: CharterClause) -> str:
    colour = STATUS_COLOURS.get(clause.status, "text-success")
    return f"[${colour}]{escape(status_words(clause))}[/]"


def clause_text(clause: CharterClause) -> str:
    """The clause's words, struck through and dimmed when broken."""
    words = escape(clause.text.strip())
    return f"[s dim]{words}[/]" if clause.status == CLAUSE_BROKEN else words


def note_line(clause: CharterClause) -> str:
    """Under a broken clause, when and how it was broken; under an amended
    one, what changed; "" for one in force or with no note."""
    if clause.status == CLAUSE_IN_FORCE or not clause.note.strip():
        return ""
    since = when(clause.since_year, clause.since_season)
    colour = STATUS_COLOURS[clause.status]
    head = clause.status if since == "—" else f"{clause.status}, {since}"
    return f"[${colour}]{escape(head)}:[/] [i]{escape(clause.note.strip())}[/]"


def gloss(charter: CovenantCharter, clause: CharterClause) -> str:
    """What the books say of a broken or amended clause ("" for one in
    force)."""
    if clause.status == CLAUSE_BROKEN:
        crime = (
            f" This charter was ratified by a Quaesitor, so the breach can be "
            f"charged as a Low Crime ({COV} p. 36)."
            if charter.ratified
            else f" A charter a Quaesitor ratified makes it a Low Crime ({COV} p. 36)."
        )
        return (
            f"[dim]Breaking the charter is what a covenant may censure: "
            f"privileges withheld, or expulsion ({COV} p. 35).{crime}[/]"
        )
    if clause.status == CLAUSE_AMENDED:
        return (
            f"[dim]The charter says how it may be altered ({COV} p. 33); an "
            f"obligation may not be changed against a member's will "
            f"({COV} p. 35).[/]"
        )
    return ""


def info(charter: CovenantCharter, index: int | None, *, wide: bool) -> str:
    """The chosen clause in full: the inspector (desktop) or details panel
    (terminal, `wide`)."""
    if index is None or not 0 <= index < len(charter.clauses):
        return (
            "[dim]Choose a clause to see when it was agreed, and how it was "
            "broken or amended.[/]"
        )
    c = charter.clauses[index]
    agreed = when(c.year, c.season)
    lines: list[str] = []
    if wide:
        lines.append(
            f"[b]{escape(clause_name(c))}[/]  [dim]of "
            f"{escape(charter_title(charter))}"
            + (f" · {escape(c.section)}" if c.section else "")
            + f"[/]  ·  agreed {escape(agreed)}  ·  {status_markup(c)}"
        )
    lines.append(clause_text(c))
    if not wide:
        lines.append("")
        if c.section:
            lines.append(f"[$label]Section:[/] {escape(c.section)}")
        lines.append(f"[$label]Agreed:[/] {escape(agreed)}")
        lines.append(f"[$label]Status:[/] {status_markup(c)}")
    if extra := note_line(c):
        lines.append(extra)
    if glossed := gloss(charter, c):
        if not wide:
            lines.append("")
        lines.append(glossed)
    return "\n".join(lines)


def inspector_title(charter: CovenantCharter, index: int) -> tuple[str, str]:
    """The inspector's heading and the line under it."""
    c = charter.clauses[index]
    return clause_name(c), f"{charter_title(charter)}  ·  {status_words(c)}"


def table_header() -> str:
    """The terminal list's column titles (after its two-character marker)."""
    clause, text, agreed, status = COLUMNS
    return (
        "  "
        + fit(clause, W_CLAUSE)
        + fit(text, W_TEXT)
        + fit(agreed, W_AGREED)
        + status
    )


def _short(words: str, width: int) -> str:
    return words if len(words) <= width else words[: width - 1].rstrip() + "…"


def row(clause: CharterClause) -> str:
    """One clause as the terminal lists it."""
    words = escape(fit(_short(clause.text.strip(), W_TEXT - 2), W_TEXT))
    if clause.status == CLAUSE_BROKEN:
        plain = words.rstrip()
        words = f"[s dim]{plain}[/]" + " " * (len(words) - len(plain))
    return (
        escape(fit(clause_mark(clause), W_CLAUSE))
        + words
        + escape(fit(when(clause.year, clause.season), W_AGREED))
        + status_markup(clause)
    )


def rows(charter: CovenantCharter) -> list[tuple[int | None, str]]:
    """The terminal list's rows: each clause (by its index), under a
    heading for its section once any clause has one."""
    if not charter.clauses:
        return [(None, "[dim]No clauses yet: a to add the first.[/]")]
    found: list[tuple[int | None, str]] = []
    for name, indexes in grouped(charter):
        if name:
            found.append((None, f"[b $heading]{escape(name)}[/]"))
        found += [(i, row(charter.clauses[i])) for i in indexes]
    return found
