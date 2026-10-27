"""The Rhine's Great Library tab: Durenmar's library, open to the Order
on its own terms (Guardians of the Forests pp. 55-57; the rules are
rules.great_library). It shows the rule of access, each magus's credit
there and the searches made, with Contribute (the credit's Add) and
Search the Great Library (the searches' Add, and More on the rule).

Its data is the Rhine package's ("rhine" in Tribunal.package_data):
"library_credit", a ledger for each magus {"magus_id", "given": [{"kind",
"what", "book_id", "seasons", "year", "season"}], "granted" (seasons the
librarian gave besides, or took back), "used", "note"}; and
"library_searches", each {"magus_id", "year", "season", "sought",
"subject", "level", "ease", "lore_used", "roll", "outcome", "quality",
"mastery", "lines", "book_id" (the book found, lent to the magus),
"credit_taken", "seasons_paid" (the seasons, from the search's on, the
loan covers: each a season of his credit unless he is exempt; missing: 1
if credit was taken, else 0)}.

A summa or tractatus found is added to the saga as a book lent to the
magus, so the planner's Study from a Book offers it; its description says
it is the library's. A Library book never leaves the library: the loan
covers only the seasons of credit paid for it (Book.loan_seasons), so a
plan may study it only in one of them, and it is never copied or given
for credit (GotF p. 55). Reading anything found but lab notes or the
records takes a season of his credit, unless he is exempt; Edit pays
for more seasons.

Pattern: the Rhine package (a Strategy in the package registry) gains a
second PackageTab of two PackageLists and a PackageText, so nothing else
in the app changes; the search's outcomes are the rules module's data."""

from __future__ import annotations

import random
from typing import Any

from .. import books as bk
from ..arts import ART_LOOKUP
from ..commands import Command, Confirm, Form, Refuse, SectionOps, notes
from ..form_spec import DialogField, pairs
from ..grids import Grid
from ..markup import escape
from ..models import Book, Character, Saga, Tribunal
from ..models.common import SEASONS
from ..models.seasons import season_order
from ..rules import great_library as gl
from ..rules.library import can_read, lent
from ..sections import (
    LIBRARY_CREDIT_SECTION,
    LIBRARY_RULES_SECTION,
    LIBRARY_SEARCHES_SECTION,
)
from ..world import when_text
from . import LedgerCard, PackageList, PackageTab, PackageText, PackageVerb, entries

#: The Rhine package's key: its data, the Great Library's among it, is
#: kept under it.
KEY = "rhine"

GOTF = "Guardians of the Forests"
#: The librarian the book names (GotF p. 58).
LIBRARIAN = "Andrus of Bonisagus"
#: How a book lent from the library opens its description.
BORROWED = "Read in the Great Library of Durenmar"


def ledgers(tribunal: Tribunal) -> list[dict[str, Any]]:
    """Each magus's credit at the library, in the order first recorded."""
    return entries(tribunal, KEY, "library_credit")


def searches(tribunal: Tribunal) -> list[dict[str, Any]]:
    """Each search of the library, in the order made."""
    return entries(tribunal, KEY, "library_searches")


def ledger_of(tribunal: Tribunal, magus_id: str) -> dict[str, Any] | None:
    return next((e for e in ledgers(tribunal) if e.get("magus_id") == magus_id), None)


def _ledger(tribunal: Tribunal, magus_id: str) -> dict[str, Any]:
    """The magus's ledger, opened if he has none yet."""
    found = ledger_of(tribunal, magus_id)
    if found is None:
        found = {"magus_id": magus_id, "given": [], "granted": 0, "used": 0, "note": ""}
        ledgers(tribunal).append(found)
    return found


def credit(ledger: dict[str, Any]) -> int:
    """The seasons of credit a ledger holds in all: its contributions'
    and any the librarian granted besides."""
    given = sum(int(g.get("seasons") or 0) for g in ledger.get("given", []))
    return given + int(ledger.get("granted") or 0)


def credit_left(ledger: dict[str, Any]) -> int:
    return credit(ledger) - int(ledger.get("used") or 0)


def magi(saga: Saga) -> list[Character]:
    """Every magus of the saga: any may travel to Durenmar to study."""
    return [c for c in saga.characters if c.type == "magus"]


def _name(saga: Saga, ident: str | None) -> str:
    found = saga.character(ident)
    return found.name if found is not None else "(gone)"


def _covenant(saga: Saga, magus: Character | None) -> str:
    if magus is None or not magus.covenant_id:
        return ""
    covenant = saga.covenant(magus.covenant_id)
    return covenant.name if covenant is not None else ""


def earlier_uses(tribunal: Tribunal, magus_id: str, subject: str) -> int:
    """How often the magus has added Durenmar Lore to a book's Quality in
    this subject before (each use costs the next -1, p. 57)."""
    wanted = subject.strip().lower()
    return sum(
        1
        for s in searches(tribunal)
        if s.get("magus_id") == magus_id
        and s.get("lore_used")
        and str(s.get("subject", "")).strip().lower() == wanted
    )


# -- the rule of access --


def facts(_saga: Saga, _tribunal: Tribunal) -> list[tuple[str, str]]:
    return [
        ("Librarian", LIBRARIAN),
        ("Readers a season", "about a dozen"),
        ("Exempt", "Bonisagus, Durenmar's members"),
    ]


def rules_text(_saga: Saga, _tribunal: Tribunal) -> str:
    return (
        "Those who study from the Great Library must contribute to it. A "
        "contribution the librarian accepts (a tractatus, a new spell; not a "
        "common one or a mediocre summa) gives [b]two seasons[/] of study, more "
        "for an exceptional one; a season copying gives one. Lab notes and the "
        "Tribunal records need no credit. Books never leave the tower.\n"
        '[dim]A vis "donation" is quietly taken instead, never acknowledged '
        f"({GOTF} p. 55).[/]"
    )


# -- Credit --


def credit_title(_saga: Saga, tribunal: Tribunal) -> str:
    count = len(ledgers(tribunal))
    return f"Credit ({count} {'magus' if count == 1 else 'magi'})"


def _given_text(ledger: dict[str, Any]) -> str:
    return "; ".join(
        g.get("what", "") for g in ledger.get("given", []) if g.get("what")
    )


def _left_words(saga: Saga, ledger: dict[str, Any]) -> tuple[str, str]:
    """The seasons left in words and their colour."""
    magus = saga.character(ledger.get("magus_id"))
    if magus is not None and gl.is_exempt(saga, magus):
        return "exempt", "$text-success"
    left = credit_left(ledger)
    if left > 1:
        return f"{left} seasons", "$text-success"
    if left == 1:
        return "1 season", "$text-warning"
    return "none", "$text-error"


def credit_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each magus's credit: his covenant, what he gave, the seasons left."""
    rows, styles = [], {}
    for index, ledger in enumerate(ledgers(tribunal)):
        magus = saga.character(ledger.get("magus_id"))
        words, colour = _left_words(saga, ledger)
        rows.append(
            [
                _name(saga, ledger.get("magus_id")),
                _covenant(saga, magus),
                _given_text(ledger) or "–",
                words,
            ]
        )
        styles[(index, 3)] = colour
    return Grid(
        ["Magus", "Covenant", "Given", "Left"],
        rows,
        list(range(len(rows))),
        "No credit yet: a magus who contributes a book, a season copying or "
        "vis earns seasons of study in the Great Library.",
        styles=styles,
        caps=[20, 12, 30, 0],
        stretch=2,
    )


def _seasons(count: int) -> str:
    return f"{count} season{'' if count == 1 else 's'}"


def credit_info(saga: Saga, tribunal: Tribunal, index: int) -> str:
    listed = ledgers(tribunal)
    if index >= len(listed):
        return ""
    ledger = listed[index]
    magus = saga.character(ledger.get("magus_id"))
    words, colour = _left_words(saga, ledger)
    head = escape(_name(saga, ledger.get("magus_id")))
    covenant = escape(_covenant(saga, magus))
    lines = [f"[b]{head}[/]" + (f"  ·  {covenant}" if covenant else "")]
    lines.append(
        f"[$label]Credit:[/] {_seasons(credit(ledger))}, {ledger.get('used', 0)} "
        f"used: [{colour}]{words}[/]"
    )
    lines.append(f"[$label]Given:[/] {escape(_given_text(ledger) or '–')}")
    if ledger.get("note"):
        lines.append(f"[i]{escape(ledger['note'])}[/]")
    lines.append("")
    if magus is not None and gl.is_exempt(saga, magus):
        lines.append(
            "[dim]House Bonisagus and Durenmar's members study there for as many "
            f"seasons as they wish ({GOTF} p. 55).[/]"
        )
    else:
        lines.append(
            "[dim]Each book found and read in the Great Library (Searches) takes "
            "a season of credit; lab notes and the records take none.[/]"
        )
    return "\n".join(lines)


def credit_cards(saga: Saga, tribunal: Tribunal) -> list[LedgerCard]:
    found = []
    for ledger in ledgers(tribunal):
        magus = saga.character(ledger.get("magus_id"))
        words, colour = _left_words(saga, ledger)
        badge = "Exempt" if words == "exempt" else f"{credit_left(ledger)} left"
        found.append(
            LedgerCard(
                _name(saga, ledger.get("magus_id")),
                meta=_covenant(saga, magus),
                badge=(badge, colour.removeprefix("$")),
                body=escape(_given_text(ledger) or "–"),
                note=f"[i]{escape(ledger['note'])}[/]" if ledger.get("note") else "",
            )
        )
    return found


def _magus_options(saga: Saga) -> list[tuple[str, str]]:
    found = []
    for magus in magi(saga):
        covenant = _covenant(saga, magus)
        label = f"{magus.name} ({covenant})" if covenant else magus.name
        found.append((escape(label), magus.id))
    return found


def _book_options(saga: Saga, magus: Character | None) -> list[tuple[str, str]]:
    """The books the magus could give a copy of: those he may read (his
    covenant's library, his own and his laboratory's)."""
    if magus is None:
        return []
    return [
        (escape(f"{b.name} ({b.type})"), b.id)
        for b in saga.books
        if b.type != "Other" and can_read(saga, magus, b) and not lent(b)
    ]


def contribute_fields(saga: Saga, magus_id: str | None) -> list[DialogField]:
    """Magus, what he gives, which book, the seasons of credit."""
    every = magi(saga)
    chosen = saga.character(magus_id) or (every[0] if every else None)
    books = []
    for magus in every:
        books += [o for o in _book_options(saga, magus) if o not in books]
    return [
        DialogField(
            "magus",
            "Magus",
            "select",
            chosen.id if chosen is not None else None,
            options=_magus_options(saga),
            required=True,
        ),
        DialogField(
            "kind",
            "Gives",
            "select",
            gl.BOOK,
            options=list(gl.CONTRIBUTIONS),
            required=True,
            fills=lambda v: {"seasons": gl.CREDIT.get(v.get("kind") or gl.BOOK, 2)},
        ),
        DialogField(
            "book",
            "Which",
            "select",
            None,
            options=books,
            allow_blank=True,
            placeholder="(not one of the saga's books)",
            hint="A copy will do; it need not be his own work. The original "
            "stays where it is.",
            show_if=lambda v: v.get("kind") in (gl.BOOK, gl.GREAT),
        ),
        DialogField(
            "what",
            "What",
            "text",
            "",
            placeholder='e.g. 4 pawns of Vim, a "donation"',
            hint="What he gave, in a few words (blank: the book's name).",
        ),
        DialogField("seasons", "Seasons of credit", "int", gl.CREDIT[gl.BOOK]),
    ]


def contribute_live(saga: Saga, values: dict[str, Any]) -> str:
    kind = values.get("kind") or gl.BOOK
    line = {
        gl.BOOK: "Two seasons of free study. A common spell or a low-level, "
        "mediocre summa may be refused: the library has a glut of them.",
        gl.GREAT: "The librarian may grant more seasons for a weighty summa.",
        gl.COPYING: "One season, and thought fit only for apprentices.",
        gl.VIS: "Taken, never acknowledged: the seasons are what the librarian says.",
    }[kind]
    magus = saga.character(values.get("magus"))
    extra = ""
    if magus is not None and gl.is_exempt(saga, magus):
        extra = (
            f"\n[$text-warning]{escape(magus.name)} is exempt: Bonisagus and "
            "Durenmar's members need no credit.[/]"
        )
    return f"{line}{extra}\n[dim]{GOTF} p. 55.[/]"


def _book(saga: Saga, book_id: str | None) -> Book | None:
    return next((b for b in saga.books if book_id and b.id == book_id), None)


def contribute_form(
    saga: Saga, tribunal: Tribunal, magus_id: str | None = None
) -> Form:
    """Contribute: a magus gives the library a book, a season copying or
    vis, and earns seasons of credit (GotF p. 55)."""

    def validate(values: dict[str, Any]) -> str | None:
        if values.get("seasons") is not None and values["seasons"] < 0:
            return "Seasons of credit can't be fewer than none."
        kind = values.get("kind")
        if (
            kind in (gl.BOOK, gl.GREAT)
            and not values.get("book")
            and not (values.get("what") or "").strip()
        ):
            return "Choose the book he gives, or say what it is."
        if kind == gl.VIS and not (values.get("what") or "").strip():
            return "Say how much vis he gives."
        return None

    def apply(values: dict[str, Any]) -> None:
        book = _book(saga, values.get("book"))
        kind = values["kind"]
        what = (values.get("what") or "").strip()
        if not what:
            what = (
                book.name
                if book is not None
                else "a season copying"
                if kind == gl.COPYING
                else gl.CONTRIBUTION_NAMES[kind]
            )
        _ledger(tribunal, values["magus"]).setdefault("given", []).append(
            {
                "kind": kind,
                "what": what,
                "book_id": book.id if book is not None else None,
                "seasons": int(values.get("seasons") or 0),
                "year": saga.current_year,
                "season": saga.current_season,
            }
        )

    return Form(
        "Contribute to the Great Library",
        lambda: contribute_fields(saga, magus_id),
        apply,
        validate=validate,
        live=lambda values: contribute_live(saga, values),
        inspector="The Librarian's Ledger",
        save_label="Contribute",
        help_id="great-library-contribute",
    )


def ledger_fields(saga: Saga, ledger: dict[str, Any]) -> list[DialogField]:
    return [
        DialogField(
            "given",
            "Given",
            "info",
            escape(_given_text(ledger) or "nothing yet"),
        ),
        DialogField(
            "granted",
            "Seasons granted besides",
            "int",
            int(ledger.get("granted") or 0),
            hint="The librarian's own grant beyond what was given (less than "
            "none for a contribution he refused).",
        ),
        DialogField(
            "used",
            "Seasons used",
            "int",
            int(ledger.get("used") or 0),
            hint="Each book found and read there takes one; a search keeps this "
            "up to date.",
        ),
        DialogField(
            "note",
            "Note",
            "text",
            ledger.get("note", ""),
            placeholder="e.g. Spring 1219 studied Andrus's summa on Animal.",
        ),
    ]


def ledger_form(saga: Saga, ledger: dict[str, Any]) -> Form:
    def validate(values: dict[str, Any]) -> str | None:
        if values.get("used") is not None and values["used"] < 0:
            return "Seasons used can't be fewer than none."
        return None

    def apply(values: dict[str, Any]) -> None:
        ledger["granted"] = int(values.get("granted") or 0)
        ledger["used"] = int(values.get("used") or 0)
        ledger["note"] = values.get("note", "")

    return Form(
        f"Credit: {escape(_name(saga, ledger.get('magus_id')))}",
        lambda: ledger_fields(saga, ledger),
        apply,
        validate=validate,
        help_id="great-library-contribute",
    )


def credit_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def remove(index: int) -> Command:
        ledger = ledgers(tribunal)[index]

        def apply() -> None:
            ledgers(tribunal).remove(ledger)

        return Confirm(
            f"Delete {escape(_name(saga, ledger.get('magus_id')))}'s credit at "
            "the Great Library? His searches stay listed.",
            apply,
        )

    def add() -> Command:
        if not magi(saga):
            return Refuse(
                "Contribute to the Great Library", "The saga has no magi yet."
            )
        return contribute_form(saga, tribunal)

    return SectionOps(
        add=add,
        edit=lambda index: ledger_form(saga, ledgers(tribunal)[index]),
        remove=remove,
        rows=lambda: [_name(saga, e.get("magus_id")) for e in ledgers(tribunal)],
    )


# -- Searches --


def searches_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"Searches ({len(searches(tribunal))})"


def sought_text(entry: dict[str, Any]) -> str:
    """What a search was for, in a few words ("Summa on Animal, level 16")."""
    sought = entry.get("sought", "")
    subject = str(entry.get("subject", "")).strip() or "?"
    level = entry.get("level")
    if sought == gl.ART_SUMMA or sought == gl.ABILITY_SUMMA:
        return f"{subject} summa, level {level}"
    if sought == gl.TRACTATUS:
        return f"{subject} tractatus"
    if sought in (gl.STANDARD, gl.GENERAL, gl.OTHER_SPELL):
        return f"Lab Text: {subject}"
    if sought == gl.DEVICE:
        return f"Device's Lab Text: {subject}"
    if sought == gl.NOTES:
        return f"Lab notes: {subject}"
    return f"Records: {subject}"


def headline(entry: dict[str, Any]) -> str:
    outcome = entry.get("outcome", gl.NONE)
    result = gl.Result(outcome, "", quality=entry.get("quality"))
    return result.headline()


def _tone(entry: dict[str, Any]) -> str:
    return gl.TONES.get(entry.get("outcome", gl.NONE), "bad")


_COLOURS = {"ok": "$text-success", "warn": "$text-warning", "bad": "$text-error"}


def searches_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each search: when, who, what was sought, the roll and the result."""
    rows, styles = [], {}
    for index, entry in enumerate(searches(tribunal)):
        rows.append(
            [
                when_text(entry.get("year"), entry.get("season", "")),
                _name(saga, entry.get("magus_id")),
                sought_text(entry),
                entry.get("roll", ""),
                headline(entry),
            ]
        )
        styles[(index, 4)] = _COLOURS[_tone(entry)]
    return Grid(
        ["Season", "Magus", "Sought", "Roll", "Result"],
        rows,
        list(range(len(rows))),
        "No searches yet: Search the Great Library for a summa, a tractatus, a "
        "Lab Text, lab notes or the Tribunal's records.",
        styles=styles,
        caps=[11, 10, 24, 13, 0],
        stretch=2,
    )


def seasons_paid(entry: dict[str, Any]) -> int:
    """The seasons the loan of the book found covers, from the search's on:
    each a season of credit, unless the magus is exempt."""
    paid = entry.get("seasons_paid")
    if paid is None:
        return 1 if entry.get("credit_taken") else 0
    return int(paid)


def loan_seasons(entry: dict[str, Any]) -> list[int]:
    """The seasons (models.seasons.season_order) the loan covers."""
    start = season_order(season=entry.get("season"), year=int(entry.get("year") or 0))
    return [start + n for n in range(seasons_paid(entry))]


def _season_words(order: int) -> str:
    return when_text(order // len(SEASONS), SEASONS[order % len(SEASONS)])


def loan_words(entry: dict[str, Any]) -> str:
    """The seasons the loan covers in words ("Spring 1220 to Summer
    1220"), or "no season yet"."""
    covered = loan_seasons(entry)
    if not covered:
        return "no season yet"
    if len(covered) == 1:
        return _season_words(covered[0])
    return f"{_season_words(covered[0])} to {_season_words(covered[-1])}"


def _extra_lines(saga: Saga, entry: dict[str, Any]) -> list[str]:
    lines = []
    book = _book(saga, entry.get("book_id"))
    if book is not None:
        lines.append(
            f"[$label]Lent:[/] {escape(book.name)}, to "
            f"{escape(_name(saga, entry.get('magus_id')))} for "
            f"{loan_words(entry)}, the seasons paid for: the planner's Study "
            "from a Book offers it only in those, and it is never copied or "
            f"given away ({GOTF} p. 55)."
        )
    if entry.get("credit_taken"):
        paid = seasons_paid(entry)
        lines.append(
            "[$label]Credit:[/] a season of his credit."
            if paid == 1
            else f"[$label]Credit:[/] {_seasons(paid)} of his credit."
        )
    if entry.get("lore_used"):
        lines.append(
            "[dim]He added his Durenmar Lore: its next use in this subject is at "
            "-1 more.[/]"
        )
    if entry.get("note"):
        lines.append(f"[i]{escape(entry['note'])}[/]")
    return lines


def search_info(saga: Saga, tribunal: Tribunal, index: int) -> str:
    listed = searches(tribunal)
    if index >= len(listed):
        return ""
    entry = listed[index]
    when = when_text(entry.get("year"), entry.get("season", ""))
    head = (
        f"[b]{escape(sought_text(entry))}[/]  ·  "
        f"{escape(_name(saga, entry.get('magus_id')))}  ·  {when}"
    )
    lines = [escape(line) for line in entry.get("lines", [])]
    return "\n".join([head, *lines, *_extra_lines(saga, entry)])


def search_cards(saga: Saga, tribunal: Tribunal) -> list[LedgerCard]:
    found = []
    for entry in searches(tribunal):
        when = when_text(entry.get("year"), entry.get("season", ""))
        found.append(
            LedgerCard(
                sought_text(entry),
                meta=f"{_name(saga, entry.get('magus_id'))}, {when}",
                badge=(headline(entry), _COLOURS[_tone(entry)].removeprefix("$")),
                body=escape(entry.get("roll", "")),
                rubric="?",
            )
        )
    return found


def _wanted(tribunal: Tribunal, magus: Character, values: dict[str, Any]) -> gl.Search:
    sought = values.get("sought") or gl.ART_SUMMA
    subject = (values.get("subject") or "").strip()
    return gl.Search(
        sought,
        subject,
        int(values.get("level") or 0),
        values.get("ease"),
        gl.durenmar_lore(magus),
        earlier_uses(tribunal, magus.id, subject),
        bool(values.get("lore")) and sought in gl.BOOKS,
    )


def _shows_level(values: dict[str, Any]) -> bool:
    return values.get("sought") in (gl.ART_SUMMA, gl.ABILITY_SUMMA)


def _shows_lore(values: dict[str, Any]) -> bool:
    return values.get("sought") in gl.BOOKS


def _shows_ease(values: dict[str, Any]) -> bool:
    return values.get("sought") in gl.SET_BY_TROUPE


def _shows_read(values: dict[str, Any]) -> bool:
    return gl.needs_credit(values.get("sought") or gl.ART_SUMMA)


def search_fields(saga: Saga, magus_id: str | None) -> list[DialogField]:
    every = magi(saga)
    chosen = saga.character(magus_id) or (every[0] if every else None)
    return [
        DialogField(
            "magus",
            "Magus",
            "select",
            chosen.id if chosen is not None else None,
            options=_magus_options(saga),
            required=True,
        ),
        DialogField(
            "sought",
            "Looking for",
            "select",
            gl.ART_SUMMA,
            options=list(gl.SOUGHT),
            required=True,
        ),
        DialogField(
            "subject",
            "Art, Ability or spell",
            "text",
            "",
            required=True,
            placeholder="e.g. Vim",
            hint="For lab notes or the records, the subject, covenant or magus.",
        ),
        DialogField("level", "Level wanted", "int", 15, show_if=_shows_level),
        DialogField(
            "lore",
            "Add his Durenmar Lore to the Quality",
            "check",
            False,
            hint="-1 for each earlier use of it in the same Art or Ability.",
            show_if=_shows_lore,
        ),
        DialogField(
            "ease",
            "Ease Factor",
            "optint",
            None,
            hint="6 to 21 for a spell or device not in the core book. Lab notes: "
            "blank for a named author's. Records: blank for a season's search.",
            show_if=_shows_ease,
        ),
        DialogField(
            "read",
            "He reads what is found this season",
            "check",
            True,
            hint="A season of his credit, unless he is exempt.",
            show_if=_shows_read,
        ),
        DialogField(
            "season",
            "Season",
            "select",
            saga.current_season,
            options=pairs(SEASONS),
            required=True,
        ),
        DialogField("year", "Year", "int", saga.current_year),
    ]


def _takes_credit(saga: Saga, magus: Character, values: dict[str, Any]) -> bool:
    """Whether reading what is found would take a season of credit."""
    return (
        bool(values.get("read"))
        and gl.needs_credit(values.get("sought") or gl.ART_SUMMA)
        and not gl.is_exempt(saga, magus)
    )


def search_live(saga: Saga, tribunal: Tribunal, values: dict[str, Any]) -> str:
    magus = saga.character(values.get("magus"))
    if magus is None:
        return ""
    wanted = _wanted(tribunal, magus, values)
    lines = [escape(line) for line in gl.odds(saga, magus, wanted)]
    if wanted.sought in gl.BOOKS and not gl.durenmar_lore(magus) and values.get("lore"):
        lines.append(f"[$text-warning]{escape(magus.name)} has no Durenmar Lore.[/]")
    if gl.is_exempt(saga, magus):
        lines.append(f"{escape(magus.name)} is exempt: he needs no credit.")
    elif _takes_credit(saga, magus, values):
        ledger = ledger_of(tribunal, magus.id)
        left = credit_left(ledger) if ledger is not None else 0
        colour = "$text-error" if left <= 0 else "$label"
        lines.append(
            f"[{colour}]Reading it takes a season of his credit: {left} left.[/]"
        )
    lines.append(
        f"[dim]{GOTF} pp. 56-57. Lab notes and records need no credit; books take "
        "a season of credit when studied.[/]"
    )
    return "\n".join(lines)


def _borrowed_book(
    saga: Saga, magus: Character, entry: dict[str, Any], result: gl.Result
) -> Book:
    """The summa or tractatus found, lent to the magus for the season."""
    sought, subject = entry["sought"], entry["subject"]
    art = ART_LOOKUP.get(subject.strip().lower())
    if sought == gl.TRACTATUS:
        kind, label = "Tractatus", f"Tractatus on {subject}"
    elif sought == gl.ART_SUMMA or art is not None:
        kind, label = "Art Summa", f"Summa on {subject}"
    else:
        kind, label = "Ability Summa", f"Summa on {subject}"
    book = bk.add_book(saga, f"{label} (the Great Library)", kind)
    if kind == "Tractatus":
        book.subject_kind = "Art" if art is not None else "Ability"
    if art is not None:
        book.art = art
    else:
        book.ability = bk.canonical_ability(subject) or subject
    if kind != "Tractatus":
        book.level = entry.get("level")
    book.quality = result.quality
    book.owner_kind, book.owner_id = "character", magus.id
    book.loan_seasons = loan_seasons(entry)
    book.description = (
        f"{BORROWED}, {when_text(entry['year'], entry['season'])}: its books never "
        "leave the tower, so it is studied only in the seasons of credit paid "
        f"for it, and never copied ({GOTF} p. 55)."
    )
    return book


def search_form(
    saga: Saga,
    tribunal: Tribunal,
    magus_id: str | None = None,
    rng: random.Random | None = None,
) -> Form:
    """Search the Great Library: the roll the book gives for what is
    sought, kept in Searches (GotF pp. 56-57)."""

    def validate(values: dict[str, Any]) -> str | None:
        magus = saga.character(values.get("magus"))
        if magus is None:
            return None
        sought = values.get("sought")
        ease = values.get("ease")
        if (
            sought in (gl.ART_SUMMA, gl.ABILITY_SUMMA)
            and (values.get("level") or 0) < 1
        ):
            return "Give the level of summa wanted."
        if sought in (gl.OTHER_SPELL, gl.DEVICE) and ease is None:
            return (
                "Give the Ease Factor the troupe sets: 6 to 21 for a spell or "
                f"device not in the core book ({GOTF} pp. 56-57)."
            )
        if (
            sought in (gl.OTHER_SPELL, gl.DEVICE)
            and ease is not None
            and not gl.LEAST_EASE <= ease <= gl.MOST_EASE
        ):
            return "The Ease Factor for such a text is 6 to 21."
        if ease is not None and ease < 0:
            return "An Ease Factor can't be below 0."
        if _takes_credit(saga, magus, values):
            ledger = ledger_of(tribunal, magus.id)
            if ledger is None or credit_left(ledger) <= 0:
                return (
                    f"{escape(magus.name)} has no credit left: those who study from "
                    "the Great Library must contribute to it. Contribute first, "
                    f"or untick reading it ({GOTF} p. 55)."
                )
        return None

    def apply(values: dict[str, Any]) -> list[str]:
        magus = saga.character(values["magus"])
        assert magus is not None
        wanted = _wanted(tribunal, magus, values)
        result = gl.search(rng or random.Random(), saga, magus, wanted)
        entry: dict[str, Any] = {
            "magus_id": magus.id,
            "year": values.get("year") or saga.current_year,
            "season": values.get("season") or saga.current_season,
            "sought": wanted.sought,
            "subject": wanted.subject,
            "level": wanted.level if _shows_level(values) else None,
            "ease": gl.ease_of(wanted.sought, wanted.ease),
            "lore_used": result.lore_used,
            "roll": result.roll,
            "outcome": result.outcome,
            "quality": result.quality,
            "mastery": result.mastery,
            "lines": result.lines,
            "book_id": None,
            "credit_taken": False,
            "seasons_paid": 1 if values.get("read") and result.found else 0,
        }
        if result.found and wanted.sought in gl.BOOKS:
            entry["book_id"] = _borrowed_book(saga, magus, entry, result).id
        if result.found and _takes_credit(saga, magus, values):
            ledger = _ledger(tribunal, magus.id)
            ledger["used"] = int(ledger.get("used") or 0) + 1
            entry["credit_taken"] = True
        elif gl.is_exempt(saga, magus):
            _ledger(tribunal, magus.id)
        searches(tribunal).append(entry)
        return notes(
            f"{escape(sought_text(entry))}: {escape(headline(entry))}.",
            *(escape(line) for line in result.lines),
        )

    return Form(
        "Search the Great Library",
        lambda: search_fields(saga, magus_id),
        apply,
        validate=validate,
        live=lambda values: search_live(saga, tribunal, values),
        inspector="The Stacks",
        save_label="Roll",
        help_id="great-library-search",
    )


def search_step(saga: Saga, tribunal: Tribunal, _row: int) -> Command:
    """More's Search the Great Library (and the Searches' Add)."""
    if not magi(saga):
        return Refuse("Search the Great Library", "The saga has no magi yet.")
    return search_form(saga, tribunal)


#: The outcomes as the search's Edit offers them.
OUTCOMES: list[tuple[str, str]] = [
    ("Found", gl.FOUND),
    ("A similar one (a device)", gl.SIMILAR),
    ("Certamen for it", gl.CERTAMEN),
    ("In use this season", gl.IN_USE),
    ("Not there", gl.NONE),
    ("Flawed", gl.FLAWED),
]


def quality_hint(entry: dict[str, Any]) -> str:
    """The Quality field's hint: the suggested cap, and the absolute limit
    the storyguide may raise it to (GotF p. 57)."""
    sought = entry.get("sought") or ""
    if sought not in gl.BOOKS:
        return ""
    cap = gl.suggested_quality_cap(sought, int(entry.get("level") or 0))
    limit = gl.absolute_quality_limit(sought)
    return (
        f"At most {cap} is suggested; the storyguide may raise it to {limit}, "
        f"the absolute limit ({GOTF} p. 57)."
    )


def edit_search_form(
    saga: Saga, entry: dict[str, Any], tribunal: Tribunal | None = None
) -> Form:
    """Correct a search as recorded (one rolled at the table), raise a
    book's Quality up to the absolute limit, and pay for more seasons of
    its loan."""
    magus = saga.character(entry.get("magus_id"))
    exempt = magus is not None and gl.is_exempt(saga, magus)

    def loan_fields() -> list[DialogField]:
        if _book(saga, entry.get("book_id")) is None:
            return []
        return [
            DialogField(
                "seasons_paid",
                "Seasons of credit paid",
                "int",
                seasons_paid(entry),
                hint="The loan covers these seasons, from the search's on: a "
                "Library book is studied only in a season of credit paid for it"
                + (" (he is exempt: no credit is taken)" if exempt else "")
                + f" ({GOTF} p. 55).",
            )
        ]

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "subject",
                "Art, Ability or spell",
                "text",
                entry.get("subject", ""),
                required=True,
            ),
            DialogField("roll", "Roll", "text", entry.get("roll", "")),
            DialogField(
                "outcome",
                "Result",
                "select",
                entry.get("outcome", gl.NONE),
                options=OUTCOMES,
                required=True,
            ),
            DialogField(
                "quality",
                "Quality",
                "optint",
                entry.get("quality"),
                hint=quality_hint(entry),
            ),
            *loan_fields(),
            DialogField(
                "season",
                "Season",
                "select",
                entry.get("season", saga.current_season),
                options=pairs(SEASONS),
                required=True,
            ),
            DialogField("year", "Year", "int", entry.get("year", saga.current_year)),
            DialogField("note", "Note", "text", entry.get("note", "")),
        ]

    def extra_credit(values: dict[str, Any]) -> int:
        """The seasons of credit more (or fewer) the edit takes."""
        if exempt or "seasons_paid" not in values:
            return 0
        taken = seasons_paid(entry) if entry.get("credit_taken") else 0
        return int(values.get("seasons_paid") or 0) - taken

    def validate(values: dict[str, Any]) -> str | None:
        quality = values.get("quality")
        sought = entry.get("sought") or ""
        if quality is not None and sought in gl.BOOKS:
            limit = gl.absolute_quality_limit(sought)
            if quality > limit:
                return (
                    f"The Quality can be raised to {limit} at most, the absolute "
                    f"limit ({GOTF} p. 57)."
                )
        if (values.get("seasons_paid") or 0) < 0:
            return "Seasons of credit can't be fewer than none."
        extra = extra_credit(values)
        if extra > 0 and tribunal is not None:
            ledger = ledger_of(tribunal, entry.get("magus_id", ""))
            left = credit_left(ledger) if ledger is not None else 0
            if extra > left:
                return (
                    f"{escape(_name(saga, entry.get('magus_id')))} has {left} "
                    f"season{'' if left == 1 else 's'} of credit left: contribute "
                    f"to the library for more ({GOTF} p. 55)."
                )
        return None

    def apply(values: dict[str, Any]) -> None:
        extra = extra_credit(values)
        for key in ("subject", "roll", "outcome", "quality", "season", "year", "note"):
            entry[key] = values.get(key)
        book = _book(saga, entry.get("book_id"))
        if book is not None and values.get("quality") is not None:
            book.quality = values["quality"]
        if "seasons_paid" in values:
            paid = int(values.get("seasons_paid") or 0)
            if extra and tribunal is not None:
                ledger = _ledger(tribunal, entry.get("magus_id", ""))
                ledger["used"] = max(0, int(ledger.get("used") or 0) + extra)
            entry["seasons_paid"] = paid
            entry["credit_taken"] = paid > 0 and not exempt
        if book is not None:
            book.loan_seasons = loan_seasons(entry)

    return Form(
        "Edit a Search",
        fields,
        apply,
        validate=validate,
        help_id="great-library-search",
    )


def search_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def remove(index: int) -> Command:
        entry = searches(tribunal)[index]
        book = _book(saga, entry.get("book_id"))
        also = []
        if book is not None:
            also.append(f"the book lent, {escape(book.name)}, goes back to the library")
        if entry.get("credit_taken"):
            paid = seasons_paid(entry)
            also.append(
                "the season of credit it took is given back"
                if paid == 1
                else f"the {paid} seasons of credit it took are given back"
            )
        said = f" ({'; '.join(also)})" if also else ""

        def apply() -> None:
            searches(tribunal).remove(entry)
            if book is not None and book in saga.books:
                saga.books.remove(book)
            ledger = ledger_of(tribunal, entry.get("magus_id", ""))
            if entry.get("credit_taken") and ledger is not None:
                ledger["used"] = max(
                    0, int(ledger.get("used") or 0) - seasons_paid(entry)
                )

        return Confirm(
            f"Delete the search for {escape(sought_text(entry))}{said}?", apply
        )

    return SectionOps(
        add=lambda: search_step(saga, tribunal, 0),
        edit=lambda index: edit_search_form(saga, searches(tribunal)[index], tribunal),
        remove=remove,
        rows=lambda: [sought_text(e) for e in searches(tribunal)],
    )


#: The Great Library's tab, after the Gilds.
LIBRARY_TAB = PackageTab(
    "Great Library",
    "tab-trib-library",
    (
        PackageList(
            LIBRARY_CREDIT_SECTION,
            credit_title,
            credit_grid,
            credit_ops,
            info=credit_info,
            cards=credit_cards,
        ),
        PackageList(
            LIBRARY_SEARCHES_SECTION,
            searches_title,
            searches_grid,
            search_ops,
            info=search_info,
            cards=search_cards,
        ),
    ),
    text=PackageText(
        LIBRARY_RULES_SECTION,
        "The Great Library of Durenmar",
        facts,
        rules_text,
        more=(PackageVerb("library_search", "Search the Great Library", search_step),),
    ),
    panel_id="trib-library-info",
    panel_empty="[dim]Choose a magus or a search.[/]",
    icon="library",
)
