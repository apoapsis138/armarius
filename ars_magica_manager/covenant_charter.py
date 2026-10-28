"""A covenant's Charter of Covenant (Covenants pp. 31-36, its blank
charter in the Appendix pp. 125-128): what both front-ends show of it.

The charter is the written Oath of Covenant and its bylaws: what a member
is entitled to, what he owes, and what happens if he fails (p. 32). Its
usual sections run Oath of Covenant, Membership (the members' seals or
signatures are affixed to it; full, associate and probationary members),
Method of Governance (which also says how the charter may be altered),
Covenant Resources, Member Rights, Member Obligations, Censure, and the
Official Seal (pp. 33-36). Only breaking the charter is censured, by
withholding privileges the covenant holds in common, or by expulsion; to
withhold what is a magus's own deprives him of his magical power (pp.
35-36). Several Tribunals hold that a charter may not change a member's
obligation against his will, a High Crime (p. 35). A charter a Quaesitor
notarized is enforceable under the Tribunal's Peripheral Code, and
breaking it can then be charged as a Low Crime (pp. 32, 36); a Tribunal's
customs may say more (tribunal_packages.CharterCustom). The Definitive
Edition and its errata say nothing of covenant charters.

Clauses are list entries kept on the covenant, as diary lines are; a
clause's status, a seal's standing and a censure's penalty are plain
fields, since nothing but how they are drawn and offered depends on them
(the State pattern, reduced to a string).
"""

from __future__ import annotations

from dataclasses import dataclass

from . import charter_templates, world
from .markup import escape, fit
from .models import (
    CENSURE_EXPELLED,
    CENSURE_LOWERED,
    CHARTER_SECTIONS,
    CLAUSE_AMENDED,
    CLAUSE_BROKEN,
    CLAUSE_IN_FORCE,
    PERSONAL_PRIVILEGES,
    STANDING_EXPELLED,
    STANDING_FULL,
    STANDING_PROBATION,
    Censure,
    Character,
    CharterClause,
    CharterSeal,
    Covenant,
    CovenantCharter,
    Saga,
)
from .references import Fact
from .tribunal_packages import CharterCustom, charter_custom

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


# -- the law of it: the Official Seal and the Tribunal's customs --


def custom(saga: Saga, covenant: Covenant) -> CharterCustom | None:
    return charter_custom(saga, covenant)


def notarized(saga: Saga, covenant: Covenant) -> bool:
    """Whether a Quaesitor notarized the charter, or would at once: the
    Charter of Arae Flaviae used unaltered (Covenants p. 33)."""
    return charter_of(covenant).ratified or (
        charter_templates.ratified_at_once(saga, covenant) is not None
    )


def binding(saga: Saga, covenant: Covenant) -> bool:
    """Whether breaking the charter can be charged as a Low Crime: it is
    notarized (Covenants pp. 32, 36), or its Tribunal's customs make a
    sworn charter law (Provence)."""
    found = custom(saga, covenant)
    return notarized(saga, covenant) or (found is not None and found.sworn_binds)


def notarized_words(saga: Saga, covenant: Covenant) -> str:
    """ "Yes, by Quaesitor Arnulf, Spring 1220", "At once: the Charter of
    Arae Flaviae, unaltered", or "No"."""
    charter = charter_of(covenant)
    if charter.ratified:
        parts = ["Yes"]
        if charter.notarized_by.strip():
            parts.append(f"by {charter.notarized_by.strip()}")
        at = when(charter.notarized_year, charter.notarized_season)
        if at != "—":
            parts.append(at)
        return ", ".join(parts) if len(parts) > 1 else "Yes"
    if (template := charter_templates.ratified_at_once(saga, covenant)) is not None:
        return f"At once: {template.name}, unaltered"
    return "No"


def law_line(saga: Saga, covenant: Covenant) -> str:
    """What the law makes of the charter, in a sentence (plain text)."""
    found = custom(saga, covenant)
    if found is not None and found.sworn_binds:
        line = (
            "Sworn, the charter is a legal obligation of the Tribunal's "
            "Peripheral Code: breaking it can be charged as a Low Crime."
        )
        if not notarized(saga, covenant):
            line += " A Quaesitor should still notarize it."
        return line
    if notarized(saga, covenant):
        return (
            "Notarized by a Quaesitor, the charter is enforceable under the "
            f"Tribunal's Peripheral Code: breaking it can be charged as a Low "
            f"Crime ({COV} pp. 32, 36)."
        )
    return (
        "Not notarized: breaking it is the covenant's own affair. A charter "
        "a Quaesitor notarized is enforceable under the Peripheral Code "
        f"({COV} p. 32)."
    )


def review_words(saga: Saga, covenant: Covenant) -> str:
    """Whether the Tribunal's reviewers passed the charter ("" where its
    customs have none)."""
    found = custom(saga, covenant)
    if found is None or not found.reviewed_by:
        return ""
    return "Yes" if charter_of(covenant).reviewed else "Not yet"


# -- the members' seals --


@dataclass(frozen=True)
class SealShown:
    """A magus as the charter's seals show him: his seal, or none yet."""

    character: Character
    seal: CharterSeal | None

    @property
    def when(self) -> str:
        return when(self.seal.year, self.seal.season) if self.seal else ""

    @property
    def standing(self) -> str:
        return self.seal.standing if self.seal else ""

    @property
    def expelled(self) -> bool:
        return self.standing == STANDING_EXPELLED


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


def standing_words(seal: CharterSeal) -> str:
    """ "", "associate member", "probationary until Summer 1222",
    "expelled Winter 1221"."""
    if seal.standing == STANDING_FULL:
        return ""
    until = when(seal.until_year, seal.until_season)
    if seal.standing == STANDING_PROBATION:
        return "probationary" + (f" until {until}" if until != "—" else "")
    if seal.standing == STANDING_EXPELLED:
        return "expelled" + (f" {until}" if until != "—" else "")
    return seal.standing.lower()


def probation_end(
    charter: CovenantCharter, year: int | None, season: str
) -> tuple[int | None, str]:
    """When a probation begun in (year, season) ends, by the charter's
    term ((None, "") with no term or no year)."""
    if charter.probation_seasons is None or year is None:
        return None, ""
    return world.seasons_after(year, season or "Spring", charter.probation_seasons)


def _sealed_name(shown: SealShown) -> str:
    name = escape(shown.character.name)
    notes = [s for s in (shown.when if shown.when != "—" else "",) if s]
    if shown.seal is not None and (words := standing_words(shown.seal)):
        notes.append(words)
    return name + (f" [dim]({escape(', '.join(notes))})[/]" if notes else "")


def sealed_line(saga: Saga, covenant: Covenant) -> str:
    """The terminal's line of seals: "Sealed by: Ilona (Spring 1115),
    Matthaios (1115, probationary until 1117)  ·  Not yet sworn:
    Benedek  ·  Expelled: Wolfram (1121)"."""
    found = seals(saga, covenant)
    if not found:
        return "[$label]Sealed by:[/] [dim]no magi in the covenant yet[/]"
    done = [s for s in found if s.seal is not None and not s.expelled]
    out = [s for s in found if s.expelled]
    waiting = [s for s in found if s.seal is None]
    parts = [
        f"[$label]Sealed by:[/] "
        f"{', '.join(_sealed_name(s) for s in done) or '[dim]no one yet[/]'}"
    ]
    if waiting:
        parts.append(
            "[$label]Not yet sworn:[/] "
            + ", ".join(escape(s.character.name) for s in waiting)
        )
    if out:
        parts.append(
            "[$label]Expelled:[/] [s dim]"
            + ", ".join(escape(s.character.name) for s in out)
            + "[/]"
        )
    return "  ·  ".join(parts)


def still_resident(saga: Saga, covenant: Covenant) -> list[Character]:
    """Expelled magi the saga still counts among the covenant's magi."""
    magi = {c.id for c in world.covenant_magi(saga, covenant)}
    return [
        s.character
        for s in seals(saga, covenant)
        if s.expelled and s.character.id in magi
    ]


def probations_ended(saga: Saga, covenant: Covenant) -> list[str]:
    """A line for each probationary member whose probation has run its
    term: "Ilona's probation ended Summer 1222" (the council then considers
    him for full membership)."""
    now = world.season_number(saga.current_year, saga.current_season)
    found = []
    for shown in seals(saga, covenant):
        seal = shown.seal
        if (
            seal is not None
            and seal.standing == STANDING_PROBATION
            and seal.until_year is not None
            and world.season_number(seal.until_year, seal.until_season) <= now
        ):
            found.append(
                f"{shown.character.name}'s probation ended "
                f"{when(seal.until_year, seal.until_season)}"
            )
    return found


# -- the charter --


def facts(saga: Saga, covenant: Covenant) -> list[Fact]:
    """Sworn, its clauses and how many are broken, its Official Seal,
    how many of the covenant's magi have sealed it, and, where the
    Tribunal reviews charters, whether it passed."""
    charter = charter_of(covenant)
    total = len(charter.clauses)
    clauses = f"{total}, {broken(charter)} broken" if total else "None yet"
    found = [s for s in seals(saga, covenant) if not s.expelled]
    sealed = sum(1 for s in found if s.seal is not None)
    shown = [
        Fact(
            "Sworn",
            when(charter.year, charter.season)
            if charter.year or charter.season
            else "",
        ),
        Fact("Clauses", clauses),
        Fact("Notarized", notarized_words(saga, covenant)),
        Fact("Sealed", f"{sealed} of {len(found)}" if found else ""),
    ]
    if reviewed := review_words(saga, covenant):
        shown.append(Fact("Reviewed", reviewed))
    if charter.probation_seasons is not None:
        shown.append(Fact("Probation", f"{charter.probation_seasons} seasons"))
    return shown


def facts_line(saga: Saga, covenant: Covenant) -> str:
    return "  ·  ".join(
        f"[$label]{escape(f.label)}:[/] {escape(f.value) if f.value else '—'}"
        for f in facts(saga, covenant)
    )


def preamble_text(charter: CovenantCharter) -> str:
    if not charter.preamble.strip():
        return "[dim]No preamble yet: edit the charter to write its oath.[/]"
    return f"[i]{escape(charter.preamble.strip())}[/]"


def custom_note(saga: Saga, covenant: Covenant) -> str:
    """What the covenant's Tribunal's customs say of charters ("")."""
    found = custom(saga, covenant)
    return found.note if found is not None else ""


def charter_text(saga: Saga, covenant: Covenant) -> str:
    """The terminal's charter section: its facts, who sealed it, its
    preamble, and what the law makes of it."""
    charter = charter_of(covenant)
    lines = [facts_line(saga, covenant), sealed_line(saga, covenant), ""]
    lines.append(preamble_text(charter))
    lines.append("")
    lines.append(f"[dim]{escape(law_line(saga, covenant))}[/]")
    if note := custom_note(saga, covenant):
        lines.append(f"[dim]{escape(note)}[/]")
    for line in probations_ended(saga, covenant):
        lines.append(
            f"[$text-warning]{escape(line)}: Seal the Charter to make him a "
            "full member, or extend it.[/]"
        )
    if out := still_resident(saga, covenant):
        names = ", ".join(escape(c.name) for c in out)
        lines.append(
            f"[$text-warning]Expelled but still of the covenant: {names}. "
            "More's End Membership removes them.[/]"
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


def censure_words(saga: Saga, censure: Censure) -> str:
    """ "Ilona: privileges withheld (Library, Vis share) from Spring 1221
    until Winter 1221", plain text."""
    who = saga.character(censure.character_id)
    name = who.name if who is not None else "A magus no longer in the saga"
    words = censure.penalty.lower()
    if censure.penalty not in (CENSURE_EXPELLED, CENSURE_LOWERED) and censure.withheld:
        words += f" ({', '.join(censure.withheld)})"
    at = when(censure.year, censure.season)
    if at != "—":
        words += f" from {at}" if censure.until_year is not None else f", {at}"
    until = when(censure.until_year, censure.until_season)
    if until != "—":
        words += f" until {until}"
    return f"{name}: {words}"


def personal_warning(withheld: list[str]) -> str:
    """The warning for withholding what Tribunals take for a magus's own
    ("" when nothing such is withheld)."""
    own = [w for w in withheld if w in PERSONAL_PRIVILEGES]
    if not own:
        return ""
    return (
        f"{' and '.join(own)}: most Tribunals take a magus's laboratory for "
        "his own, and to withhold what is his deprives him of his magical "
        f"power, against the Oath of Hermes ({COV} p. 36). Unless the "
        "charter makes it a privilege, this is on shaky legal ground."
    )


def censure_line(saga: Saga, clause: CharterClause) -> str:
    """Under a censured clause, who was censured and how ("" for none)."""
    if clause.censure is None:
        return ""
    line = f"[$label]Censured:[/] {escape(censure_words(saga, clause.censure))}"
    if clause.censure.case_id:
        line += " [dim](charged at Tribunal)[/]"
    if clause.censure.note.strip():
        line += f" [i]{escape(clause.censure.note.strip())}[/]"
    return line


def gloss(clause: CharterClause, binds: bool) -> str:
    """What the books say of a broken or amended clause ("" for one in
    force); `binds`, whether a breach can be charged as a Low Crime."""
    if clause.status == CLAUSE_BROKEN:
        crime = (
            " This charter binds under the Peripheral Code, so the breach can "
            f"be charged as a Low Crime ({COV} pp. 32, 36)."
            if binds
            else " A charter a Quaesitor notarized makes it a Low Crime "
            f"({COV} pp. 32, 36)."
        )
        return (
            f"[dim]Breaking the charter is what a covenant may censure: "
            f"privileges withheld, or expulsion ({COV} p. 35).{crime}[/]"
        )
    if clause.status == CLAUSE_AMENDED:
        return (
            f"[dim]The charter says how it may be altered ({COV} p. 33). "
            "Several Tribunals hold that it may not change a member's "
            "obligation without his agreement; doing so is a High Crime "
            f"({COV} p. 35).[/]"
        )
    return ""


def info(saga: Saga, covenant: Covenant, index: int | None, *, wide: bool) -> str:
    """The chosen clause in full: the inspector (desktop) or details panel
    (terminal, `wide`)."""
    charter = charter_of(covenant)
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
    if censured := censure_line(saga, c):
        lines.append(censured)
    if glossed := gloss(c, binding(saga, covenant)):
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
    status = status_markup(clause)
    if clause.censure is not None:
        status += " [dim]· censured[/]"
    return (
        escape(fit(clause_mark(clause), W_CLAUSE))
        + words
        + escape(fit(when(clause.year, clause.season), W_AGREED))
        + status
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
