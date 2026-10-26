"""What a Tribunal's sheet says, for either front-end: the facts under
its name, its roster of covenants and magi of note, its docket of cases,
its Peripheral Code, its treasury and its Diary. The roster is worked
out from the covenants and characters that belong to it (tribunals.py).

Each list is a grids.Grid of plain words: the desktop draws it as a
table, the terminal as padded lines, from the same cells. What a
Tribunal's package adds (tribunal_packages) is drawn the same way."""

from __future__ import annotations

import re

from .. import code_of_hermes, threats, tribunal_packages, tribunals, world
from ..grids import Grid
from ..markup import escape
from ..models import (
    CASE_OPEN,
    CASE_WITHDRAWN,
    SEASONS,
    Case,
    Character,
    Covenant,
    Ruling,
    Saga,
    TreasuryEntry,
    Tribunal,
    TribunalDiaryEntry,
)
from ..references import Fact
from ..treasury import LEVY, NOTE, amount_text, balance
from ..treasury import pawns as _pawns
from ..treasury import pounds as _pounds
from .character import house_name

# -- In the Saga --

#: Where the rest of a long In the Saga is shown.
MORE_UNDER_HISTORY = "More of In the Saga is on the History tab."


def summary_parts(tribunal: Tribunal) -> tuple[str, str]:
    """In the Saga split for the sheet: its first paragraph, shown under
    the Tribunal's name, and the rest, shown above its history, so a
    book-length summary doesn't push the roster off the page."""
    paragraphs = re.split(r"\n[ \t]*\n", tribunal.summary.strip(), maxsplit=1)
    lede = paragraphs[0].strip()
    rest = paragraphs[1].strip() if len(paragraphs) > 1 else ""
    return lede, rest


# -- the facts under its name --


def next_meeting(tribunal: Tribunal) -> str:
    """When and where the Tribunal next meets, or "(not set)"."""
    if tribunal.next_year is None:
        return "(not set)"
    when = f"{tribunal.next_season} {tribunal.next_year}"
    place = tribunal.meeting_place.strip()
    return f"{when}, at {place}" if place else when


def _officer(saga: Saga, character_id: str | None) -> str:
    character = saga.character(character_id)
    return character.name if character is not None else "(not chosen)"


def _praeco(saga: Saga, tribunal: Tribunal) -> str:
    """The Praeco; "Vacant" where the customs name the eldest magus at
    the next meeting."""
    if saga.character(tribunal.praeco_id) is None and (
        "succession" in tribunal_packages.of(tribunal).meeting_steps
    ):
        return "Vacant"
    return _officer(saga, tribunal.praeco_id)


def _of_total(recorded: int, total: int | None) -> str:
    return f"{recorded} recorded of {total}" if total is not None else str(recorded)


def proxies(tribunal: Tribunal, covenant: Covenant) -> int:
    """The proxies `covenant` holds for the Tribunal's next meeting."""
    return tribunal.proxies.get(covenant.id, 0)


def covenant_votes(saga: Saga, tribunal: Tribunal, covenant: Covenant) -> int:
    """A covenant's votes at the next meeting: one for each of its magi,
    and one for each proxy it carries."""
    return world.votes(saga, covenant) + proxies(tribunal, covenant)


def your_votes(saga: Saga, tribunal: Tribunal) -> int:
    """The player covenants' votes at `tribunal`, proxies included."""
    return sum(
        covenant_votes(saga, tribunal, c)
        for c in tribunals.covenants_of(saga, tribunal)
        if c.played
    )


def your_votes_text(saga: Saga, tribunal: Tribunal) -> str:
    """ "3 of 23": the troupe's votes of every vote in the hall, or as
    the Tribunal's customs count them."""
    counted = tribunal_packages.of(tribunal).your_votes
    if counted is not None:
        return counted(saga, tribunal)
    return f"{your_votes(saga, tribunal)} of {_all_votes(saga, tribunal)}"


def _all_votes(saga: Saga, tribunal: Tribunal) -> int:
    """Every vote in the hall: its magi in all, or those recorded."""
    if tribunal.magi_total is not None:
        return tribunal.magi_total
    return sum(world.votes(saga, c) for c in tribunals.covenants_of(saga, tribunal))


def open_cases(tribunal: Tribunal) -> list[Case]:
    """The cases still to be heard, in the order filed on the docket."""
    return [c for c in tribunal.cases if c.status == CASE_OPEN]


def closed_cases(tribunal: Tribunal) -> list[Case]:
    """The cases decided or withdrawn at past meetings."""
    return [c for c in tribunal.cases if c.status != CASE_OPEN]


def _yours(saga: Saga) -> list[str]:
    """The names a case against the troupe would name: its covenants and
    their magi."""
    names = []
    for covenant in world.player_covenants(saga):
        names.append(covenant.name)
        names += [m.name for m in world.covenant_magi(saga, covenant)]
    return [n.strip().casefold() for n in names if n.strip()]


def against_yours(saga: Saga, case: Case) -> bool:
    """Whether `case` is brought against one of the troupe's covenants or
    their magi (named in its Against)."""
    against = case.against.casefold()
    return bool(against) and any(name in against for name in _yours(saga))


def cases_fact(saga: Saga, tribunal: Tribunal) -> str:
    """ "2 pending", "2 (1 against you)", or "none pending"."""
    pending = open_cases(tribunal)
    if not pending:
        return "none pending"
    against = sum(against_yours(saga, c) for c in pending)
    if against:
        return f"{len(pending)} ({against} against you)"
    return f"{len(pending)} pending"


def facts(saga: Saga, tribunal: Tribunal) -> list[Fact]:
    """The Tribunal's facts under its name."""
    members = tribunals.covenants_of(saga, tribunal)
    magi = sum(world.votes(saga, c) for c in members)
    return [
        Fact("Customs", tribunal_packages.label(tribunal_packages.of(tribunal))),
        Fact("Meets every", f"{tribunal.meets_every} years"),
        Fact(
            "Next meeting",
            "(not set)"
            if tribunal.next_year is None
            else f"{tribunal.next_season} {tribunal.next_year}",
        ),
        Fact("Meeting place", tribunal.meeting_place.strip() or "(not set)"),
        Fact("Cases", cases_fact(saga, tribunal)),
        Fact("Praeco", _praeco(saga, tribunal)),
        Fact("Presiding Quaesitor", _officer(saga, tribunal.quaesitor_id)),
        Fact("Covenants", _of_total(len(members), tribunal.covenants_total)),
        Fact("Magi", _of_total(magi, tribunal.magi_total)),
        Fact("Your votes", your_votes_text(saga, tribunal)),
        # Only while a story waits to be begun.
        *(
            [Fact("Stories", threats.stories_text(saga))]
            if threats.counts(saga)[1]
            else []
        ),
    ]


# -- the roster --


def _unnamed(saga: Saga, tribunal: Tribunal) -> tuple[int, int | None]:
    """How many covenants and magi of the Tribunal are not recorded (the
    magi None when its size in magi isn't given)."""
    members = tribunals.covenants_of(saga, tribunal)
    covenants = max(0, (tribunal.covenants_total or 0) - len(members))
    magi = None
    if tribunal.magi_total is not None:
        magi = max(0, tribunal.magi_total - sum(world.votes(saga, c) for c in members))
    return covenants, magi


def roster_names(saga: Saga, tribunal: Tribunal) -> list[str]:
    """The Covenants list's rows by name: each covenant, then the
    unrecorded ones when there are any."""
    names = [c.name for c in tribunals.covenants_of(saga, tribunal)]
    covenants, magi = _unnamed(saga, tribunal)
    if covenants or magi:
        names.append("Unnamed covenants")
    return names


def attitude_target(saga: Saga) -> Covenant | None:
    """The player covenant the roster's Attitude column looks toward: the
    troupe's first."""
    played = world.player_covenants(saga)
    return played[0] if played else None


def roster_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Every covenant of the Tribunal, the troupe's first: its detail,
    magi, votes, the proxies it holds and its attitude toward the
    troupe's covenant; then the covenants not recorded, counted."""
    target = attitude_target(saga)
    package = tribunal_packages.of(tribunal)
    columns = package.columns
    attitude_column = 5 + len(columns)
    rows: list[list[str]] = []
    keys: list[int | None] = []
    styles: dict[tuple[int, int], str] = {}
    spans: set[int] = set()
    members = tribunals.covenants_of(saga, tribunal)
    for index, covenant in enumerate(members):
        if index and members[index - 1].played and not covenant.played:
            # The troupe's covenants stand above a divider.
            styles[(len(rows), 0)] = "$label"
            spans.add(len(rows))
            rows.append(["Other covenants", *("" for _ in range(5 + len(columns)))])
            keys.append(None)
        row = len(rows)
        held = proxies(tribunal, covenant)
        attitude = ""
        if target is not None and covenant is not target:
            score = world.attitude_score(world.attitude_toward(covenant, target.id))
            attitude = (
                f"{world.SEAL_GLYPH} {world.signed(score)} {world.attitude_word(score)}"
            )
            styles[(row, attitude_column)] = f"${world.attitude_colour(score)}"
        if covenant.played:
            styles[(row, 0)] = "b"
        keys.append(index)
        rows.append(
            [
                world.marked_name(covenant),
                covenant.detail,
                str(world.votes(saga, covenant)),
                str(covenant_votes(saga, tribunal, covenant)),
                f"{held} held" if held else "",
                *(c.value(saga, tribunal, covenant) for c in columns),
                attitude,
            ]
        )
    covenants, magi = _unnamed(saga, tribunal)
    if covenants or magi:
        keys.append(len(members))
        rows.append(
            [
                f"{covenants} unnamed" if covenants else "Unnamed covenants",
                "",
                "" if magi is None else str(magi),
                "" if magi is None else str(magi),
                "",
                *("" for _ in columns),
                "",
            ]
        )
    return Grid(
        [
            package.place.title(),
            "Detail",
            "Magi",
            "Votes",
            "Proxies",
            *(c.title for c in columns),
            "Attitude",
        ],
        rows,
        keys,
        f"No {package.place} belongs to it yet: choose it as a covenant's "
        "Tribunal in Edit Covenant.",
        styles,
        caps=[22, 6, 4, 5, 8, *(c.cap for c in columns), 0],
        spans=frozenset(spans),
    )


def roster_title(saga: Saga, tribunal: Tribunal) -> str:
    places = tribunal_packages.of(tribunal).places.title()
    return f"{places} ({len(tribunals.covenants_of(saga, tribunal))})"


def _offices(saga: Saga, tribunal: Tribunal, magus: Character) -> list[str]:
    offices = []
    if magus.id == tribunal.praeco_id:
        offices.append("Praeco")
    if magus.id == tribunal.quaesitor_id:
        offices.append("Presiding Quaesitor")
    name = magus.name.strip().casefold()
    for case in open_cases(tribunal):
        whom = case.against or case.title
        if case.prosecutor.strip().casefold() == name:
            offices.append(f"Prosecutes {whom}")
        if case.defender.strip().casefold() == name:
            offices.append(f"Defends {whom}")
    return offices


def magi_of_note(saga: Saga, tribunal: Tribunal) -> list[Character]:
    """The magi a Tribunal's storyguide keeps an eye on: its officers,
    the magi of its covenants the troupe doesn't play, and anyone
    prosecuting or defending a case on its docket."""
    pleading = {
        name.strip().casefold()
        for case in open_cases(tribunal)
        for name in (case.prosecutor, case.defender)
        if name.strip()
    }
    members = {c.id for c in tribunals.covenants_of(saga, tribunal) if not c.played}
    return [
        c
        for c in saga.characters
        if c.type == "magus"
        and (
            c.id in (tribunal.praeco_id, tribunal.quaesitor_id)
            or c.covenant_id in members
            or c.name.strip().casefold() in pleading
        )
    ]


def magi_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """The magi of note: House, covenant, office or part in a case, and
    how much of them is written down."""
    magi = magi_of_note(saga, tribunal)
    rows = []
    for magus in magi:
        covenant = saga.covenant(magus.covenant_id)
        rows.append(
            [
                magus.name,
                house_name(magus) or "",
                covenant.name if covenant is not None else "",
                ", ".join(_offices(saga, tribunal, magus)),
                magus.detail,
            ]
        )
    return Grid(
        [
            "Magus",
            "House",
            tribunal_packages.of(tribunal).place.title(),
            "Office",
            "Detail",
        ],
        rows,
        list(range(len(rows))),
        "No magi of note: its officers and the magi of its other covenants show here.",
        caps=[24, 11, 12, 24, 6],
    )


def magi_title(saga: Saga, tribunal: Tribunal) -> str:
    return f"Magi of Note ({len(magi_of_note(saga, tribunal))})"


# -- the docket --


def season_before(year: int, season: str, seasons: int) -> tuple[int, str]:
    """The season `seasons` before `season` of `year` (Winter closes its
    year)."""
    index = SEASONS.index(season) if season in SEASONS else 0
    index -= seasons
    year += index // len(SEASONS)
    return year, SEASONS[index % len(SEASONS)]


def notice_due(tribunal: Tribunal) -> str:
    """When notice of a case for the next meeting is due, or "" with no
    meeting set."""
    if tribunal.next_year is None:
        return ""
    year, season = season_before(
        tribunal.next_year,
        tribunal.next_season,
        tribunal_packages.of(tribunal).notice_seasons,
    )
    return f"{season} {year}"


def cases_title(tribunal: Tribunal) -> str:
    pending = len(open_cases(tribunal))
    if tribunal.next_year is None:
        return f"Cases ({pending})"
    return f"Cases for {tribunal.next_year} ({pending})"


def _filed(case: Case) -> str:
    return world.when_text(case.filed_year, case.filed_season)


def cases_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """The cases for the next meeting: kind, when filed, when notice is
    due (or, flagged, that it hasn't been given) and what is sought."""
    due = notice_due(tribunal)
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, case in enumerate(open_cases(tribunal)):
        notice = due
        if not case.notice_given:
            notice = "not given"
            styles[(index, 3)] = "$text-warning"
        if against_yours(saga, case):
            styles[(index, 0)] = "$text-error"
        rows.append([case.title, case.kind.title(), _filed(case), notice, case.penalty])
    return Grid(
        ["Case", "Kind", "Filed", "Notice due", "Sought"],
        rows,
        list(range(len(rows))),
        "No cases on the docket.",
        styles,
        caps=[20, 6, 11, 11, 0],
    )


def past_title(tribunal: Tribunal) -> str:
    return f"Rulings of Past Tribunals ({len(closed_cases(tribunal))})"


def outcome(case: Case) -> str:
    """How a closed case ended: its outcome, or that it was withdrawn."""
    if case.status == CASE_WITHDRAWN:
        return f"withdrawn: {case.outcome}" if case.outcome else "withdrawn"
    return case.outcome or "decided"


def past_grid(tribunal: Tribunal) -> Grid:
    """The cases past meetings decided, and those withdrawn."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, case in enumerate(closed_cases(tribunal)):
        if case.status == CASE_WITHDRAWN:
            styles[(index, 3)] = "$label"
        rows.append([case.title, case.kind.title(), _filed(case), outcome(case)])
    return Grid(
        ["Case", "Kind", "Filed", "Outcome"],
        rows,
        list(range(len(rows))),
        "None decided yet.",
        styles,
        caps=[24, 7, 11, 0],
    )


def case_text(saga: Saga, tribunal: Tribunal, case: Case | None) -> str:
    """Everything about one case, as markup for a details panel."""
    if case is None:
        return "[$label]Choose a case to read it.[/]"
    heading = f"[b]{escape(case.title)}[/]  {case.kind.title()}"
    if case.status == CASE_OPEN:
        if tribunal.next_year is not None:
            heading += f" · to be heard {tribunal.next_season} {tribunal.next_year}"
    else:
        heading += f" · {escape(outcome(case))}"
    lines = [heading]

    def line(label: str, words: str) -> None:
        if words.strip():
            lines.append(f"[$label]{label}:[/] {escape(words.strip())}")

    line("Charge", case.charge)
    if case.kind == "charge":
        line("Under the Code", code_of_hermes.crime_note(case.charge))
    line("Brought by", case.brought_by)
    line("Against", case.against)
    line("Prosecutor", case.prosecutor)
    line("Defender", case.defender)
    line("Filed", _filed(case))
    if case.status == CASE_OPEN:
        due = notice_due(tribunal)
        given = "given" if case.notice_given else "not yet given"
        ahead = tribunal_packages.of(tribunal).notice_words
        line(
            "Notice",
            f"{given}; due {due}, {ahead} before the meeting" if due else given,
        )
    line("Sought", case.penalty)
    if case.term_ends_year is not None:
        season = case.term_ends_season or "Summer"
        line(
            "Term",
            f"ended {season} {case.term_ends_year}: back on the docket"
            if case.term_docketed
            else f"ends {season} {case.term_ends_year}, to be debated again",
        )
    evidence = [e.strip() for e in case.evidence.splitlines() if e.strip()]
    if evidence:
        lines.append(
            f"[$label]Evidence ({len(evidence)}):[/] "
            + " · ".join(escape(e) for e in evidence)
        )
    return "\n".join(lines)


# -- the Peripheral Code --


def _case_title(tribunal: Tribunal, case_id: str) -> str:
    case = next((c for c in tribunal.cases if c.id == case_id), None)
    return case.title if case is not None else ""


def code_title(tribunal: Tribunal) -> str:
    return f"Peripheral Code ({len(tribunal.rulings)})"


def customs_note(tribunal: Tribunal) -> str:
    """What the Tribunal's customs add, for its Peripheral Code; "" under
    the core rules."""
    package = tribunal_packages.of(tribunal)
    if package is tribunal_packages.CORE:
        return ""
    return f"{tribunal_packages.label(package)}. {package.about}"


def code_grid(tribunal: Tribunal) -> Grid:
    """The rulings in force: the year made, what each says, and its case."""
    rows = [
        [
            ruling.title,
            "" if ruling.year is None else str(ruling.year),
            ruling.says.strip().splitlines()[0] if ruling.says.strip() else "",
            _case_title(tribunal, ruling.case_id),
        ]
        for ruling in tribunal.rulings
    ]
    return Grid(
        ["Ruling", "Year", "Says", "Case"],
        rows,
        list(range(len(rows))),
        "No rulings recorded: the Peripheral Code's rulings go here.",
        caps=[24, 4, 44, 0],
        stretch=2,
    )


def ruling_text(tribunal: Tribunal, ruling: Ruling | None) -> str:
    """One ruling of the Peripheral Code, as markup for a details panel:
    the year it was made, all it says, and the case it came from."""
    if ruling is None:
        return "[$label]Choose a ruling to read it.[/]"
    lines = []
    if ruling.year is not None:
        lines.append(f"[$label]Made in:[/] {ruling.year}")
    case = _case_title(tribunal, ruling.case_id)
    if case:
        lines.append(f"[$label]Case:[/] {escape(case)}")
    if lines:
        lines.append("")
    lines.append(escape(ruling.says.strip()) or "[$label]Nothing written yet.[/]")
    return "\n".join(lines)


# -- the treasury --


def treasury_title(tribunal: Tribunal) -> str:
    return f"Treasury ({len(tribunal.treasury)})"


def _when_or_case(tribunal: Tribunal, entry: TreasuryEntry) -> str:
    if entry.kind == "loan":
        due = f"due {entry.due_year}" if entry.due_year is not None else ""
        return "repaid" if entry.paid else due
    if entry.kind == "fine":
        case = _case_title(tribunal, entry.case_id)
        paid = "paid" if entry.paid else "unpaid"
        return f"{case}, {paid}" if case else paid
    if entry.kind == LEVY:
        return "paid" if entry.paid else "unpaid"
    if entry.kind == NOTE:
        return "redeemed" if entry.paid else "outstanding"
    return ""


def treasury_grid(tribunal: Tribunal) -> Grid:
    """Each entry: what it is, how much, who owes it and when."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, entry in enumerate(tribunal.treasury):
        if entry.kind in ("loan", "fine", LEVY, NOTE) and not entry.paid:
            styles[(index, 3)] = "$text-warning"
        rows.append(
            [
                entry.kind.title(),
                amount_text(entry),
                entry.who,
                _when_or_case(tribunal, entry),
                entry.note,
            ]
        )
    return Grid(
        ["Entry", "Amount", "Who", "Due or case", "Note"],
        rows,
        list(range(len(rows))),
        "Nothing in the treasury yet.",
        styles,
        caps=[6, 18, 16, 22, 0],
        stretch=4,
    )


def _owed(tribunal: Tribunal, kind: str) -> list[str]:
    owed: dict[str, float] = {}
    for entry in tribunal.treasury:
        if entry.kind == kind and not entry.paid:
            key = entry.art or "silver"
            owed[key] = owed.get(key, 0) + entry.amount
    return [
        _pounds(n) if key == "silver" else _pawns(n, key) for key, n in owed.items()
    ]


def balance_lines(tribunal: Tribunal) -> list[tuple[str, str]]:
    """The balance as (label, words): silver and vis in hand, loans out
    and fines unpaid, and levies unpaid and promissory notes outstanding
    where there are any."""
    held = balance(tribunal)
    silver = held.pop("silver", 0)
    vis = ", ".join(
        f"{int(n) if float(n).is_integer() else n} {art}"
        for art, n in sorted(held.items())
        if n
    )
    coins = tribunal_packages.of(tribunal).coins
    in_hand = _pounds(silver)
    if coins is not None and silver:
        in_hand += f" ({coins(silver)})"
    return [
        ("Silver in hand", in_hand),
        ("Vis in hand", f"{vis} (pawns)" if vis else "none"),
        ("Loans out", ", ".join(_owed(tribunal, "loan")) or "none"),
        ("Fines unpaid", ", ".join(_owed(tribunal, "fine")) or "none"),
        # The kinds a Tribunal's customs add, shown once it has any.
        *(
            (label, ", ".join(_owed(tribunal, kind)) or "none")
            for kind, label in ((LEVY, "Levies unpaid"), (NOTE, "Notes outstanding"))
            if any(e.kind == kind for e in tribunal.treasury)
        ),
    ]


# -- the Diary --


def _date_key(entry: TribunalDiaryEntry) -> tuple[int, int]:
    season = SEASONS.index(entry.season) if entry.season in SEASONS else -1
    return entry.year, season


def diary_order(tribunal: Tribunal) -> list[int]:
    """The Diary's entries by index, newest first."""
    return sorted(
        range(len(tribunal.diary)),
        key=lambda i: _date_key(tribunal.diary[i]),
        reverse=True,
    )


def diary_title(tribunal: Tribunal) -> str:
    return f"Diary ({len(tribunal.diary)})"


def diary_text(entry: TribunalDiaryEntry | None) -> str:
    """One Diary entry, as markup for a details panel: its numbers and
    all its details."""
    if entry is None:
        return "[$label]Choose an entry to read it.[/]"
    lines = [f"[$label]Numbers:[/] {escape(entry.margin)}", ""] if entry.margin else []
    lines.append(escape(entry.details.strip()) or "[$label]No details written.[/]")
    return "\n".join(lines)


def diary_grid(tribunal: Tribunal) -> Grid:
    """The Diary, newest first: when, what and its details' first line."""
    order = diary_order(tribunal)
    rows = []
    for index in order:
        entry = tribunal.diary[index]
        details = entry.details.strip()
        rows.append(
            [
                world.when_text(entry.year, entry.season),
                entry.title,
                entry.margin,
                details.splitlines()[0] if details else "",
            ]
        )
    return Grid(
        ["When", "Entry", "Numbers", "Details"],
        rows,
        list(order),
        "Nothing written yet: each meeting's minutes go here.",
        caps=[11, 30, 18, 0],
        stretch=3,
    )
