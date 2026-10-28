"""A covenant's History tab (a chapter on the desktop): everything dated
that is written about it, in one timeline, oldest first, told in eras.

It gathers, without copying: the covenant's own Diary, the diaries of its
place, of the places inside it and of the records placed there (a
faction of its founders), and the saga's calendar entries for it that
come once. Rows with the same date and words are one row naming each
record that keeps it. Edit changes a row where it is written; Delete
leaves it out of the history only (the key, its date and words, is kept
on the covenant, so an entry whose words change comes back). What is
left out is hidden until the tab's Left Out block shows it, at the
history's foot, where Delete on a row puts it back.

The eras are the covenant's own list (a name and the year each begins);
with none, the history is told before and after its founding. The rows
from the current season on are always "Now and ahead".

Pattern: Adapter + Iterator, as open_stories gathers Story Events: each
source's entries are turned into one Row, and one function gathers and
sorts them; the tab is a KindTab (the kind tabs' Strategy), drawn by
each front-end's kind-tab code, as the covenant's Manors and Projects
are."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, cast

from ..commands import Command, Confirm, Form, Refuse, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..manors import holder_covenant, manors_of
from ..markup import escape
from ..models import (
    ONCE,
    SEASONS,
    STORY_EVENT,
    Covenant,
    HistoryEra,
    Neighbour,
    Saga,
)
from ..neighbour_lists import (
    KindBlock,
    KindList,
    KindTab,
    Toggle,
    list_ops,
    tab_ops,
)
from ..place_events import diary as place_diary
from ..place_events import diary_ops as place_diary_ops
from ..places import within
from ..rules.sites import is_place, place
from ..sections import ERAS_SECTION, HISTORY_SECTION, HISTORY_VIEW_SECTION
from .ahead import calendar_form
from .diary import covenant_diary_ops

TAB_ID = "tab-cov-history"

#: The eras told when the covenant has none of its own, split at its
#: founding; and the one every history ends with.
BEFORE = "Before the covenant"
SINCE = "The covenant's years"
NOW = "Now and ahead"
UNDATED = "Undated"
LEFT_OUT = "Left out of the history"

#: Where a row is written.
DIARY, PLACE, CALENDAR = "diary", "place", "calendar"


@dataclass(frozen=True)
class Source:
    """A record that keeps a row: which list (DIARY, the covenant's
    Diary; PLACE, a neighbour's diary; CALENDAR, the saga's calendar),
    the record's id, and the entry's index in that list."""

    kind: str
    record_id: str
    index: int
    label: str

    @property
    def record(self) -> str:
        """The record it is written in, as the source filter knows it."""
        return f"{self.kind}:{self.record_id}"


@dataclass(frozen=True)
class Row:
    """A dated entry of the history, and every record that keeps it."""

    year: int | None
    season: str
    text: str
    sources: tuple[Source, ...]

    @property
    def key(self) -> str:
        """What a left-out row is known by: its date and words."""
        return f"{self.year or ''}|{self.season}|{self.text}"

    @property
    def when(self) -> str:
        if self.year is None:
            return self.season
        return f"{self.season} {self.year}".strip()

    def order(self) -> int:
        """The row's place in time; a year with no season comes before
        its Spring."""
        season = SEASONS.index(self.season) + 1 if self.season in SEASONS else 0
        return (self.year or 0) * (len(SEASONS) + 1) + season


# -- gathering --


def _diary_rows(covenant: Covenant) -> Iterator[tuple[int | None, str, str, Source]]:
    label = f"{covenant.name}'s Diary"
    for index, entry in enumerate(covenant.diary):
        text = entry.name or entry.details.strip() or "(unnamed)"
        yield entry.year, entry.season, text, Source(DIARY, covenant.id, index, label)


def kept_by(saga: Saga, covenant: Covenant) -> list[Neighbour]:
    """The records whose diaries the history reads: the covenant's place,
    the places inside it, and the records placed in any of them."""
    home = place(saga, covenant.place_id)
    if home is None:
        return []
    ids = {home.id, *within(saga, home)}
    found = [home]
    found += [n for n in saga.neighbours if n.id != home.id and n.id in ids]
    found += [
        n
        for n in saga.neighbours
        if not is_place(n) and n.place_id in ids and n.id not in ids
    ]
    return found


def _place_rows(
    saga: Saga, covenant: Covenant
) -> Iterator[tuple[int | None, str, str, Source]]:
    for record in kept_by(saga, covenant):
        for index, entry in enumerate(place_diary(record)):
            text = str(entry.get("text") or "").strip()
            if not text:
                continue
            year = entry.get("year")
            yield (
                year if isinstance(year, int) else None,
                str(entry.get("season") or ""),
                text,
                Source(PLACE, record.id, index, record.name),
            )


def _calendar_rows(
    saga: Saga, covenant: Covenant
) -> Iterator[tuple[int | None, str, str, Source]]:
    for index, entry in enumerate(saga.calendar):
        if entry.covenant_id != covenant.id or entry.repeats != ONCE:
            continue
        text = entry.title + (f": {entry.note}" if entry.note.strip() else "")
        yield entry.year, entry.season, text, Source(CALENDAR, "", index, "Ahead")


def rows(saga: Saga, covenant: Covenant) -> list[Row]:
    """Every dated entry about the covenant, oldest first (ties in the
    order gathered), those with the same date and words merged."""
    merged: dict[tuple[int | None, str, str], list[Source]] = {}
    for year, season, text, source in (
        *_diary_rows(covenant),
        *_place_rows(saga, covenant),
        *_calendar_rows(saga, covenant),
    ):
        merged.setdefault((year, season, text), []).append(source)
    found = [
        Row(year, season, text, tuple(sources))
        for (year, season, text), sources in merged.items()
    ]
    return sorted(found, key=Row.order)


# -- eras --


def eras(covenant: Covenant) -> list[HistoryEra]:
    """The covenant's own eras, as kept (in the order entered)."""
    return cast(list[HistoryEra], covenant.history.setdefault("eras", []))


def told_eras(covenant: Covenant) -> list[HistoryEra]:
    """The eras the history is told in, by the year each begins: the
    covenant's own, or before and after its founding."""
    own = sorted(eras(covenant), key=lambda era: era["year"])
    if own:
        return own
    if covenant.year_founded is None:
        return []
    return [
        HistoryEra(name=BEFORE, year=-10_000),
        HistoryEra(name=SINCE, year=covenant.year_founded),
    ]


def era_of(told: list[HistoryEra], year: int) -> str:
    """The era `year` falls in ("" before the first)."""
    name = ""
    for era in told:
        if year >= era["year"]:
            name = era["name"]
    return name


def era_span(told: list[HistoryEra], index: int) -> str:
    """ "1115-1199": the years era `index` runs, to the next one's."""
    era = told[index]
    start = "" if era["year"] <= -10_000 else str(era["year"])
    end = str(told[index + 1]["year"] - 1) if index + 1 < len(told) else ""
    if start and end:
        return f"{start}-{end}"
    if end:
        return f"to {end}"
    return f"from {start}" if start else ""


# -- leaving out --


def left_out(covenant: Covenant) -> list[str]:
    return cast(list[str], covenant.history.setdefault("left_out", []))


def hidden_records(covenant: Covenant) -> list[str]:
    """The records (Source.record) whose entries the history hides."""
    return cast(list[str], covenant.history.setdefault("hidden_sources", []))


def records(saga: Saga, covenant: Covenant) -> list[tuple[str, str]]:
    """Each record the history reads from, as (Source.record, its name):
    the covenant's Diary, then the others in the order first met, then
    Ahead."""
    found: dict[str, str] = {}
    for row in rows(saga, covenant):
        for source in row.sources:
            found.setdefault(source.record, source.label)
    order = {DIARY: 0, PLACE: 1, CALENDAR: 2}
    return sorted(found.items(), key=lambda item: order[item[0].split(":")[0]])


def filtered(covenant: Covenant, row: Row) -> bool:
    """Whether the source filter hides the row: every record keeping it
    is hidden."""
    hidden = set(hidden_records(covenant))
    return all(s.record in hidden for s in row.sources)


def _hidden_names(saga: Saga, covenant: Covenant) -> list[str]:
    hidden = hidden_records(covenant)
    return [name for key, name in records(saga, covenant) if key in hidden]


def shows_left_out(covenant: Covenant) -> bool:
    """Whether the history lists what is left out (at its foot), so one
    can be put back; it is hidden otherwise."""
    return bool(covenant.history.get("show_left_out"))


def is_now(saga: Saga, row: Row) -> bool:
    """Whether the row is in the current season or after it."""
    if row.year is None:
        return False
    current = Row(saga.current_year, saga.current_season, "", ())
    return row.order() >= current.order()


@dataclass(frozen=True)
class Shown:
    """What the History list shows: its heading rows (an era's name and
    years) and its entries, in order; `rows` are the entries, each
    listed once (`None` is a heading)."""

    lines: list[tuple[str, str, Row | None]]
    rows: list[Row]


def shown(saga: Saga, covenant: Covenant) -> Shown:
    """The history as listed: each era's heading and its rows, "Now and
    ahead", the undated, and what is left out."""
    every = [r for r in rows(saga, covenant) if not filtered(covenant, r)]
    out = set(left_out(covenant))
    told = told_eras(covenant)
    lines: list[tuple[str, str, Row | None]] = []
    listed: list[Row] = []

    def group(name: str, years: str, members: list[Row]) -> None:
        if not members:
            return
        lines.append((name, years, None))
        for row in members:
            lines.append(("", "", row))
            listed.append(row)

    kept = [r for r in every if r.key not in out]
    dated = [r for r in kept if r.year is not None and not is_now(saga, r)]
    first = told[0]["year"] if told else None
    if first is not None:
        group("Earlier", "", [r for r in dated if (r.year or 0) < first])
    for index, era in enumerate(told):
        group(
            era["name"],
            era_span(told, index),
            [r for r in dated if era_of(told, r.year or 0) == era["name"]],
        )
    if not told:
        group("", "", dated)
    group(
        NOW,
        f"from {saga.current_season} {saga.current_year}",
        [r for r in kept if is_now(saga, r)],
    )
    group(UNDATED, "", [r for r in kept if r.year is None])
    if shows_left_out(covenant):
        group(LEFT_OUT, "Delete puts one back", [r for r in every if r.key in out])
    return Shown(lines, listed)


# -- the History list --


def _from(row: Row) -> str:
    return ", ".join(dict.fromkeys(s.label for s in row.sources))


def history_title(saga: Saga, holder: Neighbour) -> str:
    covenant = holder_covenant(saga, holder)
    count = len(rows(saga, covenant)) if covenant is not None else 0
    return f"History ({count})"


def history_grid(saga: Saga, holder: Neighbour) -> Grid:
    covenant = holder_covenant(saga, holder)
    found = shown(saga, covenant) if covenant is not None else Shown([], [])
    grid_rows: list[list[str]] = []
    keys: list[int | None] = []
    spans: set[int] = set()
    styles: dict[tuple[int, int], str] = {}
    out = set(left_out(covenant)) if covenant is not None else set()
    for name, years, row in found.lines:
        if row is None:
            spans.add(len(grid_rows))
            styles[(len(grid_rows), 0)] = "b"
            grid_rows.append([f"{name}  {years}".strip() if years else name, "", ""])
            keys.append(None)
            continue
        if row.key in out:
            styles[(len(grid_rows), 1)] = "dim"
        grid_rows.append([row.when, row.text, _from(row)])
        keys.append(found.rows.index(row))
    return Grid(
        ["When", "What happened", "Written in"],
        grid_rows,
        keys,
        "Nothing dated is written about the covenant yet: its Diary, its "
        "place's and their diaries, and Ahead's entries for it show here.",
        styles,
        caps=[12, 50, 20],
        stretch=1,
        spans=frozenset(spans),
    )


def history_header(saga: Saga, holder: Neighbour) -> str:
    covenant = holder_covenant(saga, holder)
    if covenant is None:
        return ""
    every = rows(saga, covenant)
    records = {(s.kind, s.record_id) for r in every for s in r.sources}
    out = len({*left_out(covenant)} & {r.key for r in every})
    line = (
        f"{len(every)} entr{'y' if len(every) == 1 else 'ies'} from "
        f"{len(records)} record{'' if len(records) == 1 else 's'}"
    )
    if out:
        line += f"; {out} left out"
    if hidden := _hidden_names(saga, covenant):
        line += f"; not showing {', '.join(hidden)}"
    return f"[$label]{escape(line)}[/]"


def history_info(saga: Saga, holder: Neighbour, key: int) -> str:
    covenant = holder_covenant(saga, holder)
    if covenant is None:
        return ""
    listed = shown(saga, covenant).rows
    if not 0 <= key < len(listed):
        return ""
    row = listed[key]
    lines = [
        f"[b]{escape(row.text)}[/]",
        f"[$label]When:[/] {escape(row.when) or '(undated)'}",
        f"[$label]Written in:[/] {escape(_from(row))}",
    ]
    if row.year is not None and not is_now(saga, row):
        era = era_of(told_eras(covenant), row.year)
        if era:
            lines.append(f"[$label]Era:[/] {escape(era)}")
    for source in row.sources:
        if source.kind == DIARY:
            entry = covenant.diary[source.index]
            if entry.category == STORY_EVENT:
                lines.append(f"[$label]Status:[/] {escape(entry.status or 'Open')}")
            if entry.details.strip() and entry.details.strip() != row.text:
                lines.append(escape(entry.details.strip()))
    if row.key in left_out(covenant):
        lines.append("[$label]Left out of the history:[/] Delete puts it back.")
    if len(row.sources) > 1:
        lines.append(
            "[$label]Edit changes it in the first record named; it shows "
            "as one row while their words match.[/]"
        )
    return "\n".join(lines)


def _edit(saga: Saga, covenant: Covenant, source: Source) -> Command:
    """The form that changes a row where it is written."""
    if source.kind == DIARY:
        ops = covenant_diary_ops(saga, covenant)
        assert ops.edit is not None
        return ops.edit(source.index)
    if source.kind == CALENDAR:
        return calendar_form(saga, saga.calendar[source.index])
    record = saga.neighbour(source.record_id)
    if record is None:
        return Refuse("Gone", "The record that kept it is gone.")
    ops = place_diary_ops(saga, record)
    assert ops.edit is not None
    return ops.edit(source.index)


def history_ops(saga: Saga, holder: Neighbour) -> SectionOps:
    """Add writes in the covenant's Diary; Edit changes a row where it is
    written; Delete leaves it out of the history, or puts it back."""
    covenant = holder_covenant(saga, holder)
    if covenant is None:
        return SectionOps()
    found = covenant

    def chosen(key: int) -> Row:
        return shown(saga, found).rows[key]

    def remove(key: int) -> Command:
        row = chosen(key)
        out = left_out(found)
        short = row.text if len(row.text) <= 60 else row.text[:57] + "..."
        if row.key in out:
            return Confirm(
                f"Put {escape(short)} back into the history?",
                lambda: out.remove(row.key),
            )
        return Confirm(
            f"Leave {escape(short)} out of the history? It stays where it is written.",
            lambda: out.append(row.key),
        )

    diary_ops = covenant_diary_ops(saga, covenant)
    return SectionOps(
        add=diary_ops.add,
        edit=lambda key: _edit(saga, found, chosen(key).sources[0]),
        remove=remove,
        rows=lambda: [r.text for r in shown(saga, found).rows],
    )


def history_toggles(saga: Saga, holder: Neighbour) -> list[Toggle]:
    """A chip per record the history reads from, lit while its entries
    show."""
    covenant = holder_covenant(saga, holder)
    if covenant is None:
        return []
    hidden = hidden_records(covenant)

    def flip(key: str) -> None:
        if key in hidden:
            hidden.remove(key)
        else:
            hidden.append(key)

    return [
        Toggle(name, key not in hidden, lambda key=key: flip(key))
        for key, name in records(saga, covenant)
    ]


HISTORY_LIST = KindList(
    HISTORY_SECTION,
    history_title,
    history_grid,
    history_ops,
    history_info,
    header=history_header,
    toggles=history_toggles,
)


# -- the Eras list --


def _history_holder(covenant: Covenant) -> Neighbour:
    """The covenant's History settings as a neighbour's details (an
    Adapter), so its Eras list is edited as any kind's list is."""
    return Neighbour(
        id=covenant.id, name=covenant.name, kind="covenant", details=covenant.history
    )


def eras_title(saga: Saga, holder: Neighbour) -> str:
    covenant = holder_covenant(saga, holder)
    return f"Eras ({len(eras(covenant)) if covenant is not None else 0})"


def eras_grid(saga: Saga, holder: Neighbour) -> Grid:
    covenant = holder_covenant(saga, holder)
    own = eras(covenant) if covenant is not None else []
    told = sorted(own, key=lambda era: era["year"])
    order = sorted(range(len(own)), key=lambda i: own[i]["year"])
    return Grid(
        ["Era", "Years"],
        [[told[i]["name"], era_span(told, i)] for i in range(len(told))],
        [*order],
        "No eras of its own: the history is told before and after the "
        "founding. Add one to name a stretch of years.",
        caps=[34, 0],
    )


def era_fields(
    _saga: Saga, _holder: Neighbour, era: HistoryEra | None
) -> list[DialogField]:
    return [
        DialogField(
            "name",
            "Era",
            "text",
            era["name"] if era else "",
            required=True,
            placeholder="e.g. The Founders' years",
        ),
        DialogField(
            "year",
            "Begins in",
            "int",
            era["year"] if era else None,
            required=True,
            hint="It runs to the year before the next era begins.",
        ),
    ]


def eras_ops(saga: Saga, holder: Neighbour) -> SectionOps:
    """Add, Edit and Delete on the Eras list: no two eras begin in the
    same year."""
    covenant = holder_covenant(saga, holder)
    if covenant is None:
        return SectionOps()
    found = covenant

    def ops(editing: int | None) -> SectionOps:
        def problem(values: dict[str, Any]) -> str | None:
            year = values.get("year")
            if any(
                e["year"] == year for i, e in enumerate(eras(found)) if i != editing
            ):
                return f"An era already begins in {year}."
            return None

        return list_ops(
            saga,
            _history_holder(found),
            "eras",
            "Era",
            era_fields,
            lambda era: era["name"] or "this era",
            validate=problem,
        )

    every = ops(None)

    def edit(index: int) -> Command:
        step = ops(index).edit
        assert step is not None
        return step(index)

    return SectionOps(add=every.add, edit=edit, remove=every.remove, rows=every.rows)


ERAS_LIST = KindList(ERAS_SECTION, eras_title, eras_grid, eras_ops)

# -- what it shows --


def view_text(saga: Saga, holder: Neighbour) -> str:
    """What the history leaves out, and whether it shows them."""
    covenant = holder_covenant(saga, holder)
    if covenant is None:
        return ""
    keys = {r.key for r in rows(saga, covenant)}
    out = len(set(left_out(covenant)) & keys)
    if not out:
        line = "[$label]Nothing is left out. Delete on an entry leaves it out.[/]"
    elif shows_left_out(covenant):
        line = (
            f"{out} left out, listed at the foot so one can be put back (Delete on it)."
        )
    else:
        line = f"{out} left out, hidden. Edit to show them and put one back."
    if hidden := _hidden_names(saga, covenant):
        line += "\n" + escape(f"Not showing the entries of {', '.join(hidden)}.")
    return line


def view_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    """Show what's left out, then a tick per record the history reads
    from (the desktop's chips)."""
    hidden = hidden_records(covenant)
    return [
        DialogField(
            "show_left_out",
            "Show what's left out",
            "check",
            shows_left_out(covenant),
            hint="Lists them at the foot of the history, where Delete puts one back.",
        ),
        *(
            DialogField(
                f"from_{index}", f"Entries of {name}", "check", key not in hidden
            )
            for index, (key, name) in enumerate(records(saga, covenant))
        ),
    ]


def edit_view(saga: Saga, holder: Neighbour) -> Command:
    covenant = holder_covenant(saga, holder)
    if covenant is None:
        return Refuse("Gone", "The covenant is gone.")
    found = covenant

    known = records(saga, found)

    def apply(values: dict[str, Any]) -> None:
        if values.get("show_left_out"):
            found.history["show_left_out"] = True
        else:
            found.history.pop("show_left_out", None)
        hidden = hidden_records(found)
        hidden[:] = [key for key in hidden if key not in dict(known)]
        hidden += [
            key
            for index, (key, _name) in enumerate(known)
            if not values.get(f"from_{index}", True)
        ]

    return Form("What the History Shows", lambda: view_fields(saga, found), apply)


VIEW_BLOCK = KindBlock(
    HISTORY_VIEW_SECTION,
    "What It Shows",
    view_text,
    edit_view,
    edit_label="Show or Hide",
    after=HISTORY_SECTION,
)

PANEL = "[dim]Choose an entry to see it in full.[/]"

#: The covenant's History tab, after its Diary.
TAB = KindTab(
    "History",
    TAB_ID,
    (HISTORY_LIST, ERAS_LIST),
    blocks=(VIEW_BLOCK,),
    icon="history",
    panel=PANEL,
)


def covenant_ops(saga: Saga, covenant: Covenant) -> dict[str, SectionOps]:
    """The History tab's two lists' operations, by section."""
    return tab_ops(saga, manors_of(covenant), TAB)
