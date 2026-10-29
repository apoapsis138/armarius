"""The Normandy Tribunal's Library step (The Lion and the Lily pp. 22-23):
the books the Tribunal owns in common are kept at Confluensis and are
read only by those who win them at the Tourney, on a seven-year lease
under a Cow and Calf Oath, returned before the next meeting. A magus who
gives the Library an original book wins at the next Tourney, early in
its prize-giving, the lease of one worth up to as many Build Points (one
lease for each book given); when two contributors want the same book,
certamen settles it. A leased book stays the Tribunal's, kept at
Confluensis, and the lessee has seven years' exclusive access.

The Tourney's book prizes are bought with the prize pawns a team's rank
won (p. 33): a book costs a pawn per 5 Build Points, each team choosing
one tropaeum or lump of vis and one book or item a round, then again
while pawns remain. So the step takes as many books won as the Library
can lease, and refuses a team's books costing more than its pawns.

At the step the leases that are up are taken back, the books given to
the Library since the last meeting are recorded with their givers'
prizes, and the books won at the Tourney are leased to their winners
(tribunal_packages.normandy keeps the leases and gifts). A meeting.Step
(the Template Method the core's steps fill in), registered under the
name the Normandy package lists. What this meeting did is kept in its
record under "normandy_library": {"returned": [lease indexes],
"moved": {book id: [owner kind, owner id] before the gift}}, so holding
it again undoes it first."""

from __future__ import annotations

from typing import Any

from . import meeting as core
from . import tribunals, world
from .form_spec import DialogField
from .markup import escape
from .models import Book, Character, Covenant, Meeting, Saga, Tribunal
from .tribunal_packages import normandy as package

SOURCE = "The Lion and the Lily pp. 22-23, 33"


def _slots(values: dict[str, Any], prefix: str) -> list[int]:
    """The numbered fields `prefix`_N the form showed, in order."""
    return sorted(
        int(key.removeprefix(prefix))
        for key in values
        if key.startswith(prefix) and key.removeprefix(prefix).isdigit()
    )


def _record(meeting: Meeting) -> dict[str, Any]:
    return meeting.setdefault("normandy_library", {})


def _year(saga: Saga, meeting: Meeting) -> int:
    return int(meeting.get("year") or saga.current_year)


def _magi(saga: Saga, tribunal: Tribunal) -> list[Character]:
    return [
        m
        for c in tribunals.covenants_of(saga, tribunal)
        for m in world.covenant_magi(saga, c)
    ]


def wrote(book: Book, magus: Character) -> bool:
    """Whether `magus` is the book's author."""
    if book.author_id:
        return book.author_id == magus.id
    return bool(book.author.strip()) and book.author.strip() == magus.name


def giftable(saga: Saga, tribunal: Tribunal) -> list[tuple[Book, Character]]:
    """The books a magus of the Tribunal wrote that the Library doesn't
    hold yet, each with its author: an original work he may give it."""
    held = {b.id for b in package.library_books(saga, tribunal)}
    found = []
    for magus in _magi(saga, tribunal):
        for book in saga.books:
            if book.id not in held and wrote(book, magus):
                found.append((book, magus))
    return found


def _label(saga: Saga, book: Book) -> str:
    return f"{book.name} ({package.worth(saga, book)} BP)"


def _priced(saga: Saga, book: Book) -> str:
    """A book as the Tourney prices it: its Build Points and prize pawns."""
    pawns = package.book_pawns(saga, book)
    return f"{book.name} ({package.worth(saga, book)} BP, {pawns} pawn{'' if pawns == 1 else 's'})"


def _undo(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> None:
    """Take back what this meeting's step did: the leases it ended and
    those it granted, the gifts it recorded and the books they moved."""
    year = _year(saga, meeting)
    record = _record(meeting)
    listed = package.leases(tribunal)
    for index in record.get("returned", []):
        if 0 <= index < len(listed) and listed[index].get("returned") == year:
            listed[index]["returned"] = None
    listed[:] = [e for e in listed if e.get("held_at") != year]
    gifts = package.gifts(tribunal)
    gifts[:] = [g for g in gifts if g.get("held_at") != year]
    for book_id, (kind, owner) in record.get("moved", {}).items():
        book = package.book(saga, book_id)
        if book is not None:
            book.owner_kind, book.owner_id = kind, owner
    record.update(returned=[], moved={})


def _return_fields(
    saga: Saga, tribunal: Tribunal, year: int, held: bool, kept: dict[str, Any]
) -> list[DialogField]:
    """A tick for each lease that fell due: its book is back."""
    found: list[DialogField] = []
    for index, lease in package.due(tribunal, year) + [
        (i, package.leases(tribunal)[i])
        for i in kept.get("returned", [])
        if held and 0 <= i < len(package.leases(tribunal))
    ]:
        book = package.book(saga, lease.get("book_id"))
        covenant = saga.covenant(lease.get("covenant_id"))
        if any(f.key == f"return_{index}" for f in found):
            continue
        found.append(
            DialogField(
                f"return_{index}",
                f"Returned: {escape(book.name if book else '(gone)')}",
                "check",
                index in kept.get("returned", []) if held else True,
                hint=f"Leased to {escape(covenant.name if covenant else '(gone)')} "
                f"in {lease.get('year')}: it must be back before this meeting.",
            )
        )
    return found


def _given_books(
    saga: Saga, tribunal: Tribunal, year: int
) -> list[tuple[Book, Character]]:
    """The books that can be given to the Library, with their writers: those
    still to give, and those given at this meeting."""
    return giftable(saga, tribunal) + [
        (b, m)
        for g in package.gifts(tribunal)
        if g.get("held_at") == year
        for b in [package.book(saga, g["book_id"])]
        for m in [saga.character(g.get("magus_id"))]
        if b is not None and m is not None
    ]


def _prize_books(saga: Saga, tribunal: Tribunal, year: int) -> list[Book]:
    """The Library books that can be taken as a prize: those available, and
    those already leased at this meeting."""
    return package.available(saga, tribunal) + [
        b
        for e in package.leases(tribunal)
        if e.get("held_at") == year
        for b in [package.book(saga, e.get("book_id"))]
        if b is not None
    ]


def _gift_fields(
    saga: Saga,
    tribunal: Tribunal,
    year: int,
    given: list[tuple[Book, Character]],
    prizes: list[Book],
) -> list[DialogField]:
    """A book given to the Library and its giver's prize, as many times as
    there are books to give."""
    found: list[DialogField] = []
    prize_options = [(escape(_label(saga, b)), b.id) for b in prizes]
    this_gifts = [g for g in package.gifts(tribunal) if g.get("held_at") == year]
    this_leases = [e for e in package.leases(tribunal) if e.get("held_at") == year]
    gift_leases = [e for e in this_leases if e.get("how") == package.BY_GIFT]
    # A lease for each book given: as many as there are to give.
    for slot in range(max(1, len(given))):
        gift = this_gifts[slot] if slot < len(this_gifts) else {}
        prize = gift_leases[slot] if slot < len(gift_leases) else {}
        shown = (
            (lambda v: True)
            if slot == 0
            else (lambda v, s=slot: bool(v.get(f"gift_{s - 1}")))
        )
        found += [
            DialogField(
                f"gift_{slot}",
                "Given to the Library" if slot == 0 else "And given",
                "select",
                gift.get("book_id"),
                options=[
                    (escape(f"{_label(saga, b)}, by {m.name}"), b.id) for b, m in given
                ],
                allow_blank=True,
                placeholder="(no book given)",
                hint="An original book a magus of the Tribunal wrote; it "
                "goes to Confluensis.",
                show_if=shown,
            ),
            DialogField(
                f"prize_{slot}",
                "Its giver's prize",
                "select",
                prize.get("book_id"),
                options=prize_options,
                allow_blank=True,
                placeholder="(none chosen)",
                hint="A Library book worth up to as many Build Points, "
                "leased for seven years.",
                show_if=lambda v, s=slot: bool(v.get(f"gift_{s}")),
            ),
        ]
    return found


def _won_fields(
    saga: Saga,
    tribunal: Tribunal,
    year: int,
    prizes: list[Book],
    covenants: list[Covenant],
    teams: dict[str, tuple[str, int | None]],
) -> list[DialogField]:
    """A book won at the Tourney and the covenant that won it, as many times
    as the Library can lease."""
    found: list[DialogField] = []
    won_options = [(escape(_priced(saga, b)), b.id) for b in prizes]
    this_leases = [e for e in package.leases(tribunal) if e.get("held_at") == year]
    won_leases = [e for e in this_leases if e.get("how") == package.BY_TOURNEY]
    # As many books won as the Library can lease; the teams' prize
    # pawns limit them (validate).
    for slot in range(max(1, len(prizes))):
        lease = won_leases[slot] if slot < len(won_leases) else {}
        shown = (
            (lambda v: True)
            if slot == 0
            else (lambda v, s=slot: bool(v.get(f"won_{s - 1}")))
        )
        found += [
            DialogField(
                f"won_{slot}",
                "Won at the Tourney" if slot == 0 else "And won",
                "select",
                lease.get("book_id"),
                options=won_options,
                allow_blank=True,
                placeholder="(no book won)",
                hint="Bought with the team's prize pawns: a pawn per 5 Build "
                "Points (The Lion and the Lily p. 33).",
                show_if=shown,
            ),
            DialogField(
                f"winner_{slot}",
                "Won by",
                "select",
                lease.get("covenant_id"),
                options=[
                    (escape(_team_label(c.name, teams[c.id][1])), c.id)
                    for c in covenants
                ],
                show_if=lambda v, s=slot: bool(v.get(f"won_{s}")),
            ),
        ]
    return found


class Library(core.Step):
    """The leases taken back, the gifts and their givers' prizes, and the
    books won at the Tourney."""

    def __init__(self, key: str, title: str, day: int) -> None:
        super().__init__(key, title, day)
        #: Each book's worth in Build Points, as the form last listed them.
        self.worths: dict[str, int] = {}
        #: Each book's cost in prize pawns, and each covenant's name and the
        #: prize pawns its team won at this year's Tourney (None: no result).
        self.costs: dict[str, int] = {}
        self.teams: dict[str, tuple[str, int | None]] = {}

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        year = _year(saga, meeting)
        held = self.key in meeting.get("done", [])
        found = _return_fields(saga, tribunal, year, held, _record(meeting))
        given = _given_books(saga, tribunal, year)
        prizes = _prize_books(saga, tribunal, year)
        covenants = tribunals.covenants_of(saga, tribunal)
        self.worths = {b.id: package.worth(saga, b) for b in prizes} | {
            b.id: package.worth(saga, b) for b, _m in given
        }
        self.costs = {b.id: package.book_pawns(saga, b) for b in prizes}
        self.teams = {
            c.id: (c.name, package.team_pawns(tribunal, year, c.name))
            for c in covenants
        }
        found += _gift_fields(saga, tribunal, year, given, prizes)
        found += _won_fields(saga, tribunal, year, prizes, covenants, self.teams)
        found.append(core._note_field(meeting, self.key))
        return found

    def validate(self, meeting: Meeting, values: dict[str, Any]) -> str | None:
        gift_slots, won_slots = _slots(values, "gift_"), _slots(values, "won_")
        chosen = [
            values.get(f"prize_{s}")
            for s in gift_slots
            if values.get(f"gift_{s}") and values.get(f"prize_{s}")
        ] + [values.get(f"won_{s}") for s in won_slots if values.get(f"won_{s}")]
        if len(chosen) != len(set(chosen)):
            return (
                "Two prizes name the same book: when two contributors want it, "
                "certamen settles who has it, and the other chooses again."
            )
        for slot in gift_slots:
            gift, prize = values.get(f"gift_{slot}"), values.get(f"prize_{slot}")
            if gift and prize and self.worths.get(prize, 0) > self.worths.get(gift, 0):
                return (
                    "A giver's prize may be worth no more Build Points than the "
                    "book given."
                )
        gifts = [values.get(f"gift_{s}") for s in gift_slots if values.get(f"gift_{s}")]
        if len(gifts) != len(set(gifts)):
            return "The same book can't be given twice."
        spent: dict[str, int] = {}
        for slot in won_slots:
            book_id = values.get(f"won_{slot}")
            if not book_id:
                continue
            winner = values.get(f"winner_{slot}")
            if not winner:
                return "Say which covenant won each book at the Tourney."
            spent[winner] = spent.get(winner, 0) + self.costs.get(book_id, 0)
        return self._overspent(spent)

    def _overspent(self, spent: dict[str, int]) -> str | None:
        """Why a team's books cost more prize pawns than its rank won (The
        Lion and the Lily p. 33), or None."""
        for winner, pawns in spent.items():
            name, won = self.teams.get(winner, ("(gone)", None))
            if won is None:
                return (
                    f"{name} has no result at this year's Tourney: record its "
                    "points on the Tourney tab first, as its rank's prize pawns "
                    "pay for the books it wins."
                )
            if pawns > won:
                return (
                    f"{name}'s books cost {pawns} prize pawns, more than the "
                    f"{won} its rank won: a book costs a pawn per 5 Build Points "
                    "(The Lion and the Lily p. 33)."
                )
        return None

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        core._keep_note(meeting, self.key, values)
        _undo(saga, tribunal, meeting)
        year = _year(saga, meeting)
        record = _record(meeting)
        listed = package.leases(tribunal)
        returned = []
        for index, lease in package.due(tribunal, year):
            if values.get(f"return_{index}", True):
                lease["returned"] = year
                returned.append(index)
        record["returned"] = returned
        keeper = package.keeper(saga, tribunal)
        moved: dict[str, list[str | None]] = {}
        for slot in _slots(values, "gift_"):
            book = package.book(saga, values.get(f"gift_{slot}"))
            if book is None:
                continue
            author = next((m for m in _magi(saga, tribunal) if wrote(book, m)), None)
            package.gifts(tribunal).append(
                {
                    "book_id": book.id,
                    "magus_id": author.id if author else None,
                    "year": year,
                    "held_at": year,
                }
            )
            if keeper is not None:
                moved[book.id] = [book.owner_kind, book.owner_id]
                book.owner_kind, book.owner_id = "covenant", keeper.id
            prize = package.book(saga, values.get(f"prize_{slot}"))
            if prize is not None:
                listed.append(
                    {
                        "book_id": prize.id,
                        "covenant_id": author.covenant_id if author else None,
                        "magus_id": author.id if author else None,
                        "year": year,
                        "until": year + package.LEASE_YEARS,
                        "how": package.BY_GIFT,
                        "returned": None,
                        "held_at": year,
                    }
                )
        record["moved"] = moved
        for slot in _slots(values, "won_"):
            book = package.book(saga, values.get(f"won_{slot}"))
            if book is None or not values.get(f"winner_{slot}"):
                continue
            listed.append(
                {
                    "book_id": book.id,
                    "covenant_id": values[f"winner_{slot}"],
                    "magus_id": None,
                    "year": year,
                    "until": year + package.LEASE_YEARS,
                    "how": package.BY_TOURNEY,
                    "returned": None,
                    "held_at": year,
                }
            )

    def _lines(self, saga: Saga, tribunal: Tribunal, meeting: Meeting) -> list[str]:
        year = _year(saga, meeting)
        listed = package.leases(tribunal)
        lines = []
        for index in _record(meeting).get("returned", []):
            if 0 <= index < len(listed):
                book = package.book(saga, listed[index].get("book_id"))
                if book is not None:
                    lines.append(f"Returned to Confluensis: {book.name}")
        for index, lease in package.due(tribunal, year):
            book = package.book(saga, lease.get("book_id"))
            covenant = saga.covenant(lease.get("covenant_id"))
            if book is not None and self.key in meeting.get("done", []):
                holder = covenant.name if covenant else "its leasee"
                lines.append(f"Not returned: {book.name}, still held by {holder}")
        for gift in package.gifts(tribunal):
            if gift.get("held_at") != year:
                continue
            book = package.book(saga, gift.get("book_id"))
            magus = saga.character(gift.get("magus_id"))
            if book is not None:
                by = f" by {magus.name}" if magus else ""
                lines.append(f"Given to the Library{by}: {_label(saga, book)}")
        for lease in listed:
            if lease.get("held_at") != year:
                continue
            book = package.book(saga, lease.get("book_id"))
            covenant = saga.covenant(lease.get("covenant_id"))
            if book is None:
                continue
            to = covenant.name if covenant else "its giver"
            how = "a giver's prize" if lease.get("how") == package.BY_GIFT else "won"
            lines.append(
                f"Leased to {to} ({how}) until {lease.get('until')}: {book.name}"
            )
        return lines

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        return core._join(
            *(escape(line) for line in self._lines(saga, tribunal, meeting)),
            core._note_text(meeting, self.key),
        )

    def save_label(self):
        return "Lease"

    def guide(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        year = _year(saga, meeting)
        count = len(package.due(tribunal, year))
        free = len(package.available(saga, tribunal))
        return (
            f"{count} lease{'' if count == 1 else 's'} of the Library's books "
            f"{'is' if count == 1 else 'are'} up and due back; {free} "
            f"book{'' if free == 1 else 's'} can be won. A book's worth is its "
            "Build Points.",
            "A book ticked returned is free to lease again; one left unticked "
            "is noted as still held. A book given goes to the Library, and its "
            "giver's prize (one for each book given) and each book won at the "
            "Tourney are leased for seven years, until the next meeting; the "
            "books stay the Tribunal's at Confluensis. A team buys the books it "
            "wins with its rank's prize pawns, a pawn per 5 Build Points, one "
            "book or item a round until its pawns are spent.",
        )

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        lines = self._lines(saga, tribunal, meeting)
        if not lines:
            return "", ""
        leased = sum(
            1
            for e in package.leases(tribunal)
            if e.get("held_at") == _year(saga, meeting)
        )
        return (
            "The Library of the Tribunal: " + "; ".join(lines) + ".",
            f"{leased} book{'' if leased == 1 else 's'} leased",
        )


def _team_label(name: str, pawns: int | None) -> str:
    """A covenant as the Won by list shows it: with its Tourney prize pawns."""
    if pawns is None:
        return f"{name} (no Tourney result this year)"
    return f"{name} ({pawns} prize pawn{'' if pawns == 1 else 's'})"


core.register_step("library", "The Library of the Tribunal", Library, "end")
